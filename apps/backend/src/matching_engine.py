import asyncio
import json
import logging
import time
import os
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

async def _fetch_osrm_duration(session: aiohttp.ClientSession, agent_id: str, patrol_mode: str, 
                               agent_lat: float, agent_lon: float, target_lat: float, target_lon: float):
    profile = "foot" if patrol_mode == "foot" else "driving"
    url = f"{OSRM_BASE_URL}/route/v1/{profile}/{agent_lon},{agent_lat};{target_lon},{target_lat}?overview=false"
    
    # Specific timeouts for connection vs total response time
    timeout = aiohttp.ClientTimeout(total=2.0, connect=1.0)
    
    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("code") == "Ok" and data.get("routes"):
                    return agent_id, data["routes"][0]["duration"]
    except Exception as e:
        logger.warning(f"⚠️ [OSRM] Lookup failed for {agent_id}: {e}")
    
    return agent_id, float('inf')

async def find_best_agent(redis_client, session: aiohttp.ClientSession, lat: float, lon: float, 
                          zone_id: str, required_tier: int = 1, exclude_agent_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Finds best agent using 'Last Resort' hierarchy.
    Returns: (agent_id, status_at_selection)
    """
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
        
        agent_data = await redis_client.hmget(f"agent:{agent_id}", "status", "patrol_mode", "tier")
        status = agent_data[0].decode("utf-8") if agent_data[0] else "OFFLINE"
        mode = agent_data[1].decode("utf-8") if agent_data[1] else "car"
        tier = int(agent_data[2]) if agent_data[2] else 1

        if tier < required_tier or status == "OFFLINE": continue

        if status == "ONLINE":
            idle_candidates.append(_fetch_osrm_duration(session, agent_id, mode, a_lat, a_lon, lat, lon))
        elif status in ["EN_ROUTE", "ON_SCENE"]:
            queue_len = await redis_client.llen(f"agent:{agent_id}:queue")
            if queue_len < config["max_queue_size"]:
                busy_candidates.append(_fetch_osrm_duration(session, agent_id, mode, a_lat, a_lon, lat, lon))

    # Priority 1: Best Idle Agent within SLA
    if idle_candidates:
        results = await asyncio.gather(*idle_candidates)
        valid_idle = sorted([r for r in results if r[1] <= config["sla_threshold_secs"]], key=lambda x: x[1])
        if valid_idle: 
            return valid_idle[0][0], "ONLINE"

    # Priority 2: Busy Agent queueing (Chainable)
    if busy_candidates:
        results = await asyncio.gather(*busy_candidates)
        busy_threshold = config["sla_threshold_secs"] * config["busy_sla_multiplier"]
        valid_busy = sorted([r for r in results if r[1] <= busy_threshold], key=lambda x: x[1])
        if valid_busy:
            return valid_busy[0][0], "BUSY"

    return None, None

async def _process_delayed_retries(redis_client):
    """
    Checks the delayed retry queue for expired tasks and moves them back 
    to the active dispatch queue, preventing the 'Poison Pill' loop.
    """
    now = time.time()
    ready_tasks = await redis_client.zrangebyscore("pan:dispatch:delayed_tasks", "-inf", now)
    
    if ready_tasks:
        for task_bytes in ready_tasks:
            task_id = task_bytes.decode("utf-8")
            # TODO: Make atomic with a Lua script for production hardening
            await redis_client.rpush("pan:dispatch:active_tasks", task_id)
            await redis_client.zrem("pan:dispatch:delayed_tasks", task_id)

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
    
    # --- BIDIRECTIONAL DUAL-DISPATCH EXCLUSION ---
    exclude_agent = None
    incident_id = task_data.get("incident_id")
    
    if incident_id:
        # Check if ANY agent is already assigned to this incident (Primary OR Sentry)
        existing_agents = await redis_client.smembers(f"incident:{incident_id}:assigned_agents")
        if existing_agents:
            # For Vanguard 50, there's max 1 other agent. Grab the first one to exclude.
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
        # Dispatch Primary/Direct task
        await redis_client.hset(f"mission:active:{task_id}", mapping={
            "task_id": task_id, "agent_id": assigned_id, "status": "ASSIGNED",
            "dispatched_at": int(time.time()), "is_sentry": str(is_sentry_subtask)
        })
        await redis_client.hset(f"agent:{assigned_id}", "status", "EN_ROUTE")
        
        # Fire-and-forget Insurance Coverage webhook
        role_type = "SENTRY" if is_sentry_subtask else "PRIMARY"
        asyncio.create_task(insurtech_client.bind_hnoa_policy(session, task_id, assigned_id, role_type))
        
        # Add the newly assigned agent to the incident's exclusion set
        if incident_id:
            incident_agents_key = f"incident:{incident_id}:assigned_agents"
            await redis_client.sadd(incident_agents_key, assigned_id)
            await redis_client.expire(incident_agents_key, 3600) # 1 hr TTL
            
        logger.info(f"✅ Dispatched {task_id} to {assigned_id}")
    else:
        # Append to Agent's sticky queue
        await redis_client.rpush(f"agent:{assigned_id}:queue", task_id)
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