import asyncio
import json
import logging
import time

logger = logging.getLogger("PAN_MatchingEngine")

# ---------------------------------------------------------------------------
# ARCHITECTURAL NOTES FOR MEMORIAL DAY PILOT
# 
# 1. DISPATCH: This engine only processes MANUAL dispatch commands from the Ops Hub UI.
#    Auto-dispatch from pan:dispatch:active_tasks is not implemented in this version.
#    All missions require a dispatcher to click "DEPLOY PROXY AGENT" in the Ops Hub.
#
# 2. PAYMENTS: Ledger deposits are fully delegated to the mobile app.
#    90% bounty deposited via complete_mission() in v2x_bounty_api.py
#    when the agent submits evidence through the mobile app.
# ---------------------------------------------------------------------------

async def consume_orphaned_queue(redis_client):
    """Consumes the active_tasks queue to prevent boundless memory growth."""
    try:
        while True:
            # Safely pop tasks off the queue so it doesn't grow infinitely from the V2X rpush
            task = await redis_client.blpop("pan:dispatch:active_tasks", timeout=1.0)
            if task:
                task_id = task[1].decode("utf-8") if isinstance(task[1], bytes) else task[1]
                logger.debug(f"📥 [MATCHING_ENGINE] Task {task_id} queued. Awaiting MANUAL dispatch from Ops Hub.")
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.error(f"⚠️ [MATCHING_ENGINE] Orphan queue consumer error: {e}")


async def run_matching_engine(redis_client):
    pubsub = redis_client.pubsub()
    # Listen to the WebSocket channel where the Ops Hub sends manual dispatch commands
    await pubsub.subscribe("pan:stream:dispatch_commands")
    logger.info("⚙️ [MATCHING_ENGINE] Online and listening for Ops Hub dispatch commands...")

    # Start the queue consumer to safely drain the rpush from v2x_bounty_api
    consumer_task = asyncio.create_task(consume_orphaned_queue(redis_client))

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            
            if message is not None:
                payload_str = message["data"] if isinstance(message["data"], str) else message["data"].decode("utf-8")
                
                try:
                    command = json.loads(payload_str)
                    task_id = command.get("task_id")
                    
                    if not task_id or not isinstance(task_id, str) or not task_id.startswith("tsk_"):
                        logger.warning(f"⚠️ [MATCHING_ENGINE] Invalid or missing task_id in command: {command}")
                        continue
                    
                    logger.info(f"🔍 [MATCHING_ENGINE] Processing Ops Hub dispatch for {task_id}...")
                    
                    # 1. Look up the original distress signal details from Redis
                    task_data_raw = await redis_client.hgetall(f"pan:task:{task_id}")
                    if not task_data_raw:
                        logger.error(f"⚠️ [MATCHING_ENGINE] Task {task_id} not found in database. Cannot dispatch.")
                        continue
                        
                    fault_code = task_data_raw.get("fault_code", "Unknown Fault")
                    bounty_usd = float(task_data_raw.get("bounty_usd", 25.0))
                    vin = task_data_raw.get("vin", "UNKNOWN-VIN")
                    target_lat = float(task_data_raw.get("lat", command.get("lat", 33.415184)))
                    target_lon = float(task_data_raw.get("lon", command.get("lon", -111.831459)))
                    
                    # 2. Hardcode assignment to your specific mobile app for this testing phase
                    assigned_agent_id = "Vanguard-01" 
                    
                    # 🟢 Cooldown & Surge Bypass Guard
                    cooldown_bounty = await redis_client.get(f"cooldown:{task_id}:{assigned_agent_id}")
                    if cooldown_bounty:
                        if bounty_usd <= float(cooldown_bounty):
                            logger.info(f"⏭️ Skipping {assigned_agent_id} for {task_id} - On cooldown and bounty hasn't surged.")
                            continue
                        else:
                            logger.info(f"💸 Surge Pricing bypass! Re-offering {task_id} to {assigned_agent_id} at higher bounty.")
                    
                    # 3. Create the ACTIVE MISSION record. 
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
                    
                    # 4. Update the agent's status to EN_ROUTE
                    await redis_client.hset(f"agent:{assigned_agent_id}", "status", "EN_ROUTE")
                    
                    logger.info(f"✅ [MATCHING_ENGINE] Matched {task_id} to {assigned_agent_id}. Awaiting mobile app pickup.")
                    
                except json.JSONDecodeError:
                    logger.error(f"⚠️ [MATCHING_ENGINE] Failed to parse payload: {payload_str[:100]}")
            
            await asyncio.sleep(0.1)
            
    except asyncio.CancelledError:
        logger.info("🛑 [MATCHING_ENGINE] Shutting down gracefully.")
        consumer_task.cancel() # Clean up our background consumer
        raise # Re-raise to ensure the main asyncio event loop cleans up the task completely
    finally:
        try:
            await pubsub.unsubscribe()
            if hasattr(pubsub, 'close'):
                await pubsub.close()
        except Exception as e:
            logger.warning(f"⚠️ [MATCHING_ENGINE] Teardown error: {e}")