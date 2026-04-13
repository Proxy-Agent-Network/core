import asyncio
import json
import logging
import time
import os
import math
import aiohttp
from typing import Optional, Tuple

logger = logging.getLogger("PAN_MatchingEngine")

# ---------------------------------------------------------------------------
# ARCHITECTURAL NOTES FOR MESA PILOT (v2026.1)
# 
# 1. DISPATCH: Geospatial Routing via OSRM.
# 2. SENTRY LOGIC: Supports multi-agent dispatch (Primary + Sentry).
# 3. JOB CHAINING: Implements "Last Resort" queuing.
# 4. REGIONAL CONFIG: Policy lookups for queue limits and SLA multipliers.
# ---------------------------------------------------------------------------

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org")

RETRY_LUA_SCRIPT = """
local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
if #tasks > 0 then
    for i=1, #tasks do
        redis.call('RPUSH', KEYS[2], tasks[i])
        redis.call('ZREM', KEYS[1], tasks[i])
    end
end
return tasks
"""

async def get_regional_config(redis_client, zone_id: str = "mesa_az"):
    """Fetches regional policy. Defaults to Mesa Pilot constraints."""
    config = await redis_client.hgetall(f"pan:config:zone:{zone_id}")
    if not config:
        return {
            "max_queue_size": 1,
            "sla_threshold_secs": 720.0,
            "busy_sla_multiplier": 1.5,  # Tunable buffer for chained tasks
            "sentry_enabled": True
        }
    return {
        "max_queue_size": int(config.get(b"max_queue_size", 1)),
        "sla_threshold_secs": float(config.get(b"sla_threshold_secs", 720.0)),
        "busy_sla_multiplier": float(config.get(b"busy_sla_multiplier", 1.5)),
        "sentry_enabled": config.get(b"sentry_enabled") == b"true"
    }

def estimate_fallback_duration(lat1: float, lon1: float, lat2: float, lon2: float, patrol_mode: str) -> float:
    """Calculates Haversine distance and estimates travel time."""
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_meters = R * c
    
    # 30 mph is ~13.4 m/s. Walking is ~1.4 m/s.
    speed_m_s = 1.4 if patrol_mode == "foot" else 13.4
    
    # Add a 25% penalty to straight-line distance to account for street routing
    routing_penalty = 1.25 
    
    estimated_seconds = (distance_meters * routing_penalty) / speed_m_s
    return estimated_seconds

async def _fetch_osrm_duration(session: aiohttp.ClientSession, agent_id: str, patrol_mode: str, 
                               agent_lat: float, agent_lon: float, target_lat: float, target_lon: float):
    profile = "foot" if patrol_mode == "foot" else "driving"
    url = f"{OSRM_BASE_URL}/route/v1/{profile}/{agent_lon},{agent_lat};{target_lon},{target_lat}?overview=false"
    
    timeout = aiohttp.ClientTimeout(total=2.0, connect=1.0)
    
    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    return agent_id, data["routes"][0]["duration"]
                else:
                    logger.warning(f"⚠️ [OSRM] No Route found for {agent_id}. AV may be off-road. Executing fallback.")
            else:
                logger.warning(f"⚠️ [OSRM] API returned HTTP {response.status}. Executing fallback.")
    except Exception as e:
        logger.warning(f"⚠️ [OSRM] Network failure for {agent_id}: {e}. Executing fallback.")
    
    fallback_time = estimate_fallback_duration(agent_lat, agent_lon, target_lat, target_lon, patrol_mode)
    logger.info(f"🧮 [FALLBACK] Generated straight-line ETA for {agent_id}: {fallback_time:.1f}s")
    
    return agent_id, fallback_time

async def find_best_agent(redis_client, session: aiohttp.ClientSession, lat: float, lon: float, 
                          zone_id: str, required_tier: int = 1, exclude_agent_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    config = await get_regional_config(redis_client, zone_id)
    
    nearby_agents = await redis_client.geosearch(
        "pan:agent_locations", longitude=lon, latitude=lat,
        radius=15.0, unit="km", withdist=True, withcoord=True, sort="ASC"
    )
    
    if not nearby_agents: return None, None

    idle_candidates = []
    busy_candidates = []

    for agent_record in nearby_agents:
        agent_id = agent_record[0].decode("utf-8")
        
        if agent_id == exclude_agent_id:
            continue
            
        a_lon, a_lat = agent_record[2]
        
        agent_data = await redis_client.hmget(f"pan:agent:{agent_id}", "status", "patrol_mode", "tier")
        status = agent_data[0].decode("utf-8") if agent_data[0] else "OFFLINE"
        mode = agent_data[1].decode("utf-8") if agent_data[1] else "car"
        tier = int(agent_data[2]) if agent_data[2] else 1

        if tier < required_tier or status == "OFFLINE": continue

        if status == "ONLINE":
            idle_candidates.append(_fetch_osrm_duration(session, agent_id, mode, a_lat, a_lon, lat, lon))
        elif status in ["EN_ROUTE", "ON_SCENE"]:
            queue_len = await redis_client.llen(f"pan:agent:{agent_id}:queue")
            if queue_len < config["max_queue_size"]:
                busy_candidates.append(_fetch_osrm_duration(session, agent_id, mode, a_lat, a_lon, lat, lon))

    if idle_candidates:
        results = await asyncio.gather(*idle_candidates)
        valid_idle = sorted([r for r in results if r[1] <= config["sla_threshold_secs"]], key=lambda x: x[1])
        if valid_idle: 
            return valid_idle[0][0], "ONLINE"

    if busy_candidates:
        results = await asyncio.gather(*busy_candidates)
        busy_threshold = config["sla_threshold_secs"] * config["busy_sla_multiplier"]
        valid_busy = sorted([r for r in results if r[1] <= busy_threshold], key=lambda x: x[1])
        if valid_busy:
            return valid_busy[0][0], "BUSY"

    return None, None

async def _process_delayed_retries(redis_client):
    now = time.time()
    await redis_client.eval(
        RETRY_LUA_SCRIPT, 
        2, 
        "pan:dispatch:delayed_tasks", 
        "pan:dispatch:active_tasks", 
        now
    )

async def _matching_engine_loop(redis_client, session: aiohttp.ClientSession, insurtech_client):
    
    await _process_delayed_retries(redis_client)
    
    task_pop = await redis_client.blpop("pan:dispatch:active_tasks", timeout=1.0)
    if not task_pop: return

    task_id = task_pop[1].decode("utf-8")
    task_data_raw = await redis_client.hgetall(f"pan:task:{task_id}")
    if not task_data_raw: return

    task_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in task_data_raw.items()}
    t_lat, t_lon = float(task_data["lat"]), float(task_data["lon"])
    zone_id = task_data.get("zone_id", "mesa_az")
    
    required_tier = int(task_data.get("required_tier", 1))
    
    is_sentry_subtask = task_data.get("role") == "sentry"
    
    exclude_agent = None
    incident_id = task_data.get("incident_id")
    
    if incident_id:
        existing_agents = await redis_client.smembers(f"incident:{incident_id}:assigned_agents")
        if existing_agents:
            exclude_agent = list(existing_agents)[0].decode("utf-8")
            logger.info(f"🛡️ Excluding Agent {exclude_agent} from task {task_id} to prevent dual-dispatch collision.")

    assigned_id, selection_status = await find_best_agent(
        redis_client, session, t_lat, t_lon, zone_id, required_tier, exclude_agent
    )

    if not assigned_id:
        retry_timestamp = time.time() + 2.0
        await redis_client.zadd("pan:dispatch:delayed_tasks", {task_id: retry_timestamp})
        logger.info(f"⏳ No agents available for {task_id}. Delaying retry.")
        return

    if selection_status == "ONLINE":
        
        # 🟢 THE FIX: Corrected signature and required parameters for policy binding
        if insurtech_client:
            try:
                await insurtech_client.bind_mission_policy(
                    agent_id=assigned_id,
                    mission_id=task_id,
                    fault_code=task_data.get("fault_code", "unknown"),
                    lat=t_lat,
                    lon=t_lon,
                    estimated_duration_minutes=12,  # SLA target
                    redis_client=redis_client
                )
                logger.info(f"🛡️ [COMPLIANCE] Bound $5M liability policy for {task_id} to {assigned_id}")
            except Exception as e:
                logger.error(f"⚠️ [COMPLIANCE] Failed to bind policy for {task_id}: {e}")

        await redis_client.hset(f"mission:active:{task_id}", mapping={
            "task_id": task_id, "agent_id": assigned_id, "status": "ASSIGNED",
            "dispatched_at": int(time.time()), "is_sentry": str(is_sentry_subtask)
        })
        
        await redis_client.hset(f"pan:agent:{assigned_id}", "status", "EN_ROUTE")
        await redis_client.sadd(f"pan:agent:{assigned_id}:missions", task_id)
        
        if incident_id:
            incident_agents_key = f"incident:{incident_id}:assigned_agents"
            await redis_client.sadd(incident_agents_key, assigned_id)
            await redis_client.expire(incident_agents_key, 3600) # 1 hr TTL
            
        logger.info(f"✅ Dispatched {task_id} to {assigned_id}")

        await redis_client.publish(f"pan:agent:{assigned_id}:dispatch", json.dumps({
            "task_id": task_id,
            "status": "ASSIGNED"
        }))
    else:
        await redis_client.rpush(f"pan:agent:{assigned_id}:queue", task_id)
        await redis_client.hset(f"pan:task:{task_id}", "status", "QUEUED")
        logger.info(f"📌 Queued {task_id} for busy agent {assigned_id}")

async def run_matching_engine(redis_client, insurtech_client):
    logger.info("⚙️ [PHASE 5] Orchestration Engine Online...")
    
    consecutive_errors = 0
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await _matching_engine_loop(redis_client, session, insurtech_client)
                consecutive_errors = 0
            except asyncio.CancelledError:
                logger.info("🛑 [MATCHING_ENGINE] Shutting down gracefully.")
                raise
            except Exception as e:
                consecutive_errors += 1
                backoff = min(5.0 * consecutive_errors, 60.0)
                logger.error(f"⚠️ [MATCHING_ENGINE] Error #{consecutive_errors}: {e}")
                await asyncio.sleep(backoff)