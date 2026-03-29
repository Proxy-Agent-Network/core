import os
import asyncio
import time
import logging
import json
import redis.asyncio as redis
from datetime import datetime, timezone

# --- CONFIGURATION ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
SLA_TIMEOUT_SECONDS = 15
SWEEP_INTERVAL_SECONDS = 2
PENALTY_COOLDOWN_SECONDS = 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [SLA_WATCHDOG] - %(message)s")
logger = logging.getLogger("SLA_Watchdog")

async def connect_redis():
    """Establishes connection to the Redis matching engine with infinite retry."""
    while True:
        try:
            redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            await redis_client.ping()
            logger.info(f"✅ Watchdog connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            return redis_client
        except redis.ConnectionError:
            logger.error(f"❌ Watchdog failed to connect to Redis. Retrying in 5 seconds...")
            await asyncio.sleep(5)

async def sweep_active_missions(redis_client):
    """Scans all active dispatches to ensure Two-Phase ACK compliance."""
    cursor = 0
    while True:
        cursor, keys = await redis_client.scan(cursor=cursor, match="mission:active:*", count=100)
        
        for mission_key in keys:
            task_id = mission_key.split("mission:active:")[-1]
            mission_data = await redis_client.hgetall(mission_key)
            
            if not mission_data:
                continue
                
            agent_id = mission_data.get("agent_id")
            ack_status = mission_data.get("ack_status", "PENDING")
            
            # If the mission is already ACKed, the agent is securely on-scene or en route
            if ack_status == "ACKNOWLEDGED":
                continue
                
            # 🟢 THE FIX 1: Corrected schema field to match matching_engine.py
            dispatch_time = float(mission_data.get("dispatched_at", mission_data.get("timestamp", time.time())))
            elapsed_time = time.time() - dispatch_time
            
            if elapsed_time > SLA_TIMEOUT_SECONDS:
                logger.warning(f"⚠️ [SLA BREACH] Task {task_id} unacknowledged by Agent {agent_id} for {elapsed_time:.1f}s. Revoking...")
                
                # 1. Revoke the mission from the unresponsive agent
                await redis_client.delete(mission_key)
                
                # 2. Place the unresponsive agent in a brief timeout penalty box
                cooldown_key = f"cooldown:{task_id}:{agent_id}"
                await redis_client.setex(cooldown_key, PENALTY_COOLDOWN_SECONDS, "timeout_penalty")
                
                # Update their status to prevent generic dispatch matching during the penalty
                await redis_client.hset(f"agent:{agent_id}", "status", "OFFLINE_TIMEOUT")
                
                # 3. 🟢 THE FIX 2: Guard against re-queuing zombie tasks
                task_data = await redis_client.hgetall(f"pan:task:{task_id}")
                if task_data and task_data.get("status") not in ("COMPLETED", "declined"):
                    await redis_client.rpush("pan:dispatch:active_tasks", task_id)
                    logger.info(f"🔄 [RE-ROUTING] Task {task_id} returned to global dispatch queue.")
                else:
                    logger.info(f"🚫 [SKIP] Task {task_id} was already resolved. Skipping re-queue.")
                
                # 4. Broadcast the revocation to the Ops Hub map so Command sees the UI update
                await redis_client.publish(
                    "pan:stream:mission_cleared", 
                    json.dumps({"task_id": task_id, "agent_id": agent_id, "reason": "timeout_revoked"})
                )
                
                logger.info(f"🛑 Agent {agent_id} penalized 60s for dropped dispatch.")

        if cursor == 0:
            break

async def run_watchdog(redis_client=None):
    """Main daemon loop."""
    logger.info("🛡️ Two-Phase ACK SLA Watchdog initialized. Commencing sweeps...")
    
    # 🟢 THE FIX 3: Dependency Injection
    # Uses the shared pool if provided by the supervisor, otherwise creates its own.
    owns_redis = False
    if redis_client is None:
        redis_client = await connect_redis()
        owns_redis = True
    
    while True:
        try:
            await sweep_active_missions(redis_client)
        except redis.ConnectionError:
            logger.error("❌ Redis connection lost. Reconnecting...")
            if owns_redis:
                redis_client = await connect_redis()
            else:
                logger.error("❌ Fatal: Injected Redis client disconnected. Yielding to supervisor.")
                raise
        except Exception as e:
            logger.error(f"❌ Watchdog sweep failed: {e}")
            
        # Non-blocking async sleep
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_watchdog())