import asyncio
import json
import logging
import time
from typing import Optional

logger = logging.getLogger("PAN_MatchingEngine")

# ---------------------------------------------------------------------------
# ARCHITECTURAL NOTES FOR MESA PILOT (v2026.1)
# 
# 1. DISPATCH: Fully Autonomous Geospatial Routing.
#    The engine monitors the `pan:dispatch:active_tasks` queue and immediately
#    executes a Redis GEOSEARCH to find the nearest online agent.
#
# 2. GEOFENCE SLA: 8km macro-routing radius (approx. 12-min drive time).
# ---------------------------------------------------------------------------

async def find_nearest_available_agent(redis_client, lat: float, lon: float, radius_km: float = 8.0) -> Optional[str]:
    """
    Executes a spatial index search to find the closest online agent to the AV.
    """
    try:
        # 1. Query the geospatial index (populated by mobile app telemetry)
        # Returns a list of [agent_id, distance_km] sorted nearest to farthest
        nearby_agents = await redis_client.geosearch(
            "pan:agent_locations",
            longitude=lon,
            latitude=lat,
            radius=radius_km,
            unit="km",
            withdist=True,
            sort="ASC"
        )
        
        if not nearby_agents:
            return None
            
        # 2. Filter for availability (Must be exactly "ONLINE")
        for agent_record in nearby_agents:
            # Handle byte decoding dynamically depending on the Redis-py version
            agent_id = agent_record[0].decode("utf-8") if isinstance(agent_record[0], bytes) else agent_record[0]
            distance = agent_record[1]
            
            agent_status = await redis_client.hget(f"agent:{agent_id}", "status")
            if agent_status:
                status_str = agent_status.decode("utf-8") if isinstance(agent_status, bytes) else agent_status
                
                if status_str == "ONLINE":
                    logger.info(f"📍 Agent {agent_id} found {distance:.2f}km away. Status: {status_str}")
                    return agent_id
                    
        return None
        
    except Exception as e:
        logger.error(f"⚠️ [MATCHING_ENGINE] Spatial query failed: {e}")
        return None

async def _matching_engine_loop(redis_client):
    """
    The core autonomous dispatch loop. Pops orphaned tasks and matches them 
    to the nearest physical Vanguard Agent.
    """
    while True:
        # 1. Pop the next unassigned distress signal
        # Block for 1 second, then loop if empty
        task = await redis_client.blpop("pan:dispatch:active_tasks", timeout=1.0)
        
        if task:
            task_id = task[1].decode("utf-8") if isinstance(task[1], bytes) else task[1]
            logger.info(f"🔍 [MATCHING_ENGINE] Processing Dispatch for {task_id}...")
            
            # 2. Look up the original distress signal details
            task_data_raw = await redis_client.hgetall(f"pan:task:{task_id}")
            if not task_data_raw:
                logger.error(f"⚠️ [MATCHING_ENGINE] Task {task_id} not found in database. Dropping.")
                continue
            
            # Decode the raw redis hash map
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

            # 3. Geospatial Auto-Dispatch
            assigned_agent_id = await find_nearest_available_agent(redis_client, target_lat, target_lon)
            
            if not assigned_agent_id:
                logger.warning(f"⏳ [MATCHING_ENGINE] No online agents within 8km for {task_id}. Re-queuing...")
                # Delay slightly to prevent thrashing the CPU on a dead queue
                await asyncio.sleep(2.0)
                
                # 🟢 THE FIX: Stale Task Guard
                task_status = await redis_client.hget(f"pan:task:{task_id}", "status")
                # Handle bytes vs string safely
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
                    # Re-queue and try again later
                    await asyncio.sleep(1.0)
                    
                    # 🟢 THE FIX: Stale Task Guard
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
            
            # 6. Update the agent's status to EN_ROUTE so they aren't double-booked
            await redis_client.hset(f"agent:{assigned_agent_id}", "status", "EN_ROUTE")
            
            logger.info(f"✅ [MATCHING_ENGINE] Matched {task_id} to {assigned_agent_id}. SLA Timer Started.")
            
        else:
            # No tasks in queue. Yield to the event loop.
            await asyncio.sleep(0.1)

# 🟢 THE FIX: Outer supervisor loop to recover from fatal exceptions
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