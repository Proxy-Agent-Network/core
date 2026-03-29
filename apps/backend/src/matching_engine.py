import asyncio
import json
import logging
import time
import os
import aiohttp
from typing import Optional

logger = logging.getLogger("PAN_MatchingEngine")

# ---------------------------------------------------------------------------
# ARCHITECTURAL NOTES FOR MESA PILOT (v2026.1)
# 
# 1. DISPATCH: Geospatial Routing via OSRM (Open Source Routing Machine).
#    The engine pre-filters candidates using Redis GEOSEARCH (15km macro-radius).
# 
# 2. PATROL MODES: Agents define 'car' or 'foot' patrol modes with custom radii.
#    OSRM dynamically selects the driving vs walking profile to calculate 
#    true ETA to strictly enforce the 15-minute SLA.
# ---------------------------------------------------------------------------

# Fallback to the public demo router if the private container isn't configured
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org")

async def _fetch_osrm_duration(session: aiohttp.ClientSession, agent_id: str, patrol_mode: str, agent_lat: float, agent_lon: float, target_lat: float, target_lon: float):
    """Queries OSRM for true road-network/footpath travel time between two coordinates."""
    
    # Dynamically select the OSRM routing profile based on agent status
    profile = "foot" if patrol_mode == "foot" else "driving"
    url = f"{OSRM_BASE_URL}/route/v1/{profile}/{agent_lon},{agent_lat};{target_lon},{target_lat}?overview=false"
    
    try:
        async with session.get(url, timeout=2.0) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    duration_sec = data["routes"][0]["duration"]
                    return agent_id, duration_sec
    except Exception as e:
        logger.warning(f"⚠️ [OSRM] {profile.upper()} Lookup failed for {agent_id}: {e}")
    
    # Return infinite duration on failure so the agent gets sorted to the back
    return agent_id, float('inf')

async def find_nearest_available_agent(redis_client, lat: float, lon: float, max_travel_time_secs: float = 900.0) -> Optional[str]:
    """
    Executes a spatial index search, filters by Agent's custom radius, 
    then checks OSRM to find the closest online agent within the 15-minute SLA boundary.
    """
    try:
        # 1. Macro-Routing: Pre-filter using Redis to get all agents within 15km
        nearby_agents = await redis_client.geosearch(
            "pan:agent_locations",
            longitude=lon,
            latitude=lat,
            radius=15.0,
            unit="km",
            withdist=True,
            withcoord=True, 
            sort="ASC"
        )
        
        if not nearby_agents:
            return None
            
        candidate_tasks = []
        
        # 2. Status Check, Radius Filtering & Prepare OSRM Queries
        async with aiohttp.ClientSession() as session:
            for agent_record in nearby_agents:
                # Unpack the geosearch result safely
                agent_id = agent_record[0].decode("utf-8") if isinstance(agent_record[0], bytes) else agent_record[0]
                distance_km = agent_record[1]
                
                # GEOSEARCH withcoord returns (longitude, latitude) — note: lon first
                agent_lon, agent_lat = agent_record[2]
                
                # Fetch agent's complete operational profile in one call
                agent_data = await redis_client.hmget(
                    f"agent:{agent_id}", 
                    "status", "patrol_mode", "patrol_radius_mi"
                )
                status_bytes, mode_bytes, radius_bytes = agent_data
                
                status_str = status_bytes.decode("utf-8") if status_bytes else None
                if status_str != "ONLINE":
                    continue
                
                patrol_mode = mode_bytes.decode("utf-8").lower() if mode_bytes else "car"
                
                # Apply custom agent boundaries with defaults
                if radius_bytes:
                    radius_mi = float(radius_bytes.decode("utf-8"))
                else:
                    radius_mi = 0.5 if patrol_mode == "foot" else 5.0
                    
                # Convert Agent's miles to km for comparison against Redis geosearch distance
                radius_km = radius_mi * 1.60934
                
                if distance_km > radius_km:
                    logger.debug(f"⏭️ Skipping {agent_id}: Task is {distance_km:.2f}km away, exceeding their {radius_mi}mi {patrol_mode} radius.")
                    continue

                # Agent is Online and task is within their personal radius. Queue for OSRM.
                candidate_tasks.append(
                    _fetch_osrm_duration(session, agent_id, patrol_mode, agent_lat, agent_lon, lat, lon)
                )
            
            if not candidate_tasks:
                return None
                
            # 3. Concurrent OSRM Execution
            results = await asyncio.gather(*candidate_tasks)
        
        # 4. Enforce the 15-Minute SLA
        valid_candidates = [r for r in results if r[1] <= max_travel_time_secs]
        
        # Sort by fastest physical travel time
        valid_candidates.sort(key=lambda x: x[1])
        
        if valid_candidates:
            best_agent_id, best_duration = valid_candidates[0]
            logger.info(f"📍 Agent {best_agent_id} matched via OSRM. True travel time: {best_duration / 60:.1f} minutes.")
            return best_agent_id
            
        logger.warning(f"⚠️ [OSRM] No online agents within the {max_travel_time_secs / 60:.0f}-minute SLA boundary.")
        return None
        
    except Exception as e:
        logger.error(f"⚠️ [MATCHING_ENGINE] Spatial/OSRM query failed: {e}", exc_info=True)
        return None

async def _matching_engine_loop(redis_client):
    """
    The core autonomous dispatch loop. Pops orphaned tasks and matches them 
    to the nearest physical Vanguard Agent.
    """
    while True:
        # 1. Pop the next unassigned distress signal
        task = await redis_client.blpop("pan:dispatch:active_tasks", timeout=1.0)
        
        if task:
            task_id = task[1].decode("utf-8") if isinstance(task[1], bytes) else task[1]
            logger.info(f"🔍 [MATCHING_ENGINE] Processing Dispatch for {task_id}...")
            
            # 2. Look up the original distress signal details
            task_data_raw = await redis_client.hgetall(f"pan:task:{task_id}")
            if not task_data_raw:
                logger.error(f"⚠️ [MATCHING_ENGINE] Task {task_id} not found in database. Dropping.")
                continue
            
            task_data = {
                k.decode('utf-8') if isinstance(k, bytes) else k: 
                v.decode('utf-8') if isinstance(v, bytes) else v 
                for k, v in task_data_raw.items()
            }
                
            fault_code = task_data.get("fault_code", "Unknown")
            bounty_usd = float(task_data.get("bounty_usd", 25.0))
            vin = task_data.get("vin", "UNKNOWN")
            target_lat = float(task_data.get("lat", 0.0))
            target_lon = float(task_data.get("lon", 0.0))
            
            if target_lat == 0.0 or target_lon == 0.0:
                logger.error(f"⚠️ [MATCHING_ENGINE] Task {task_id} missing GPS coordinates. Cannot route.")
                continue

            # 3. Geospatial Auto-Dispatch (Now powered by OSRM)
            assigned_agent_id = await find_nearest_available_agent(redis_client, target_lat, target_lon)
            
            if not assigned_agent_id:
                logger.warning(f"⏳ [MATCHING_ENGINE] No online agents within SLA boundary for {task_id}. Re-queuing...")
                await asyncio.sleep(2.0)
                
                # Stale Task Guard
                task_status = await redis_client.hget(f"pan:task:{task_id}", "status")
                if task_status in (b"COMPLETED", b"declined", b"CANCELLED", "COMPLETED", "declined", "CANCELLED"):
                    logger.info(f"🚫 [MATCHING_ENGINE] Task {task_id} already resolved. Skipping re-queue.")
                    continue
                    
                await redis_client.rpush("pan:dispatch:active_tasks", task_id)
                continue
            
            # 4. Cooldown & Surge Bypass Guard
            cooldown_bounty = await redis_client.get(f"cooldown:{task_id}:{assigned_agent_id}")
            if cooldown_bounty:
                if bounty_usd <= float(cooldown_bounty):
                    logger.info(f"⏭️ Skipping {assigned_agent_id} for {task_id} - On cooldown and bounty hasn't surged.")
                    await asyncio.sleep(1.0)
                    
                    # Stale Task Guard
                    task_status = await redis_client.hget(f"pan:task:{task_id}", "status")
                    if task_status in (b"COMPLETED", b"declined", b"CANCELLED", "COMPLETED", "declined", "CANCELLED"):
                        logger.info(f"🚫 [MATCHING_ENGINE] Task {task_id} already resolved. Skipping re-queue.")
                        continue
                        
                    await redis_client.rpush("pan:dispatch:active_tasks", task_id)
                    continue
                else:
                    logger.info(f"💸 Surge Pricing bypass! Re-offering {task_id} to {assigned_agent_id} at higher bounty.")
            
            # 5. Lock the assignment
            now = int(time.time())
            await redis_client.hset(f"mission:active:{task_id}", mapping={
                "task_id": task_id,
                "agent_id": assigned_agent_id,
                "lat": target_lat,
                "lon": target_lon,
                "fault_code": fault_code,
                "bounty_usd": bounty_usd,
                "vin": vin,
                "dispatched_at": now,
                "sla_status": "OK"
            })
            
            # 6. Update the agent's status to EN_ROUTE
            await redis_client.hset(f"agent:{assigned_agent_id}", "status", "EN_ROUTE")
            
            logger.info(f"✅ [MATCHING_ENGINE] Matched {task_id} to {assigned_agent_id}. SLA Timer Started.")
            
        else:
            await asyncio.sleep(0.1)

# Outer supervisor loop to recover from fatal exceptions
async def run_matching_engine(redis_client):
    logger.info("⚙️ [MATCHING_ENGINE] Autonomous Geospatial Routing Supervisor Online...")
    while True:
        try:
            await _matching_engine_loop(redis_client)
        except asyncio.CancelledError:
            logger.info("🛑 [MATCHING_ENGINE] Shutting down gracefully.")
            raise
        except Exception as e:
            logger.error(f"⚠️ [MATCHING_ENGINE] Restarting after fatal error: {e}")
            await asyncio.sleep(5.0)