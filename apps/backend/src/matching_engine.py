import asyncio
import json
import logging
import time

logger = logging.getLogger("PAN_MatchingEngine")

async def run_matching_engine(redis_client):
    pubsub = redis_client.pubsub()
    # Listen to the WebSocket channel where the Ops Hub sends manual dispatch commands
    await pubsub.subscribe("pan:stream:dispatch_commands")
    logger.info("⚙️ [MATCHING_ENGINE] Online and listening for Ops Hub dispatch commands...")

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
                    bounty_usd = task_data_raw.get("bounty_usd", "25.00")
                    vin = task_data_raw.get("vin", "UNKNOWN-VIN")
                    target_lat = float(task_data_raw.get("lat", command.get("lat", 33.415184)))
                    target_lon = float(task_data_raw.get("lon", command.get("lon", -111.831459)))
                    
                    # 2. Hardcode assignment to your specific mobile app for this testing phase
                    assigned_agent_id = "Vanguard-01" 
                    
                    # 3. Create the ACTIVE MISSION record. 
                    # This is what your Android app polls for, and what the SLA Daemon monitors!
                    now = int(time.time())
                    await redis_client.hset(f"mission:active:{task_id}", mapping={
                        "task_id": task_id,
                        "agent_id": assigned_agent_id,
                        "lat": target_lat,
                        "lon": target_lon,
                        "fault_code": fault_code,
                        "bounty": bounty_usd,
                        "vin": vin,
                        "dispatched_at": now,  # <--- THIS STARTS THE 12-MINUTE SLA TIMER!
                        "sla_status": "OK"
                    })
                    
                    # 4. Update the agent's status to EN_ROUTE
                    await redis_client.hset(f"agent:{assigned_agent_id}", "status", "EN_ROUTE")
                    
                    logger.info(f"✅ [MATCHING_ENGINE] Matched {task_id} to {assigned_agent_id}. Awaiting mobile app pickup.")
                    
                except json.JSONDecodeError:
                    logger.error(f"⚠️ [MATCHING_ENGINE] Failed to parse payload: {payload_str[:100]}")
            
            await asyncio.sleep(0.1)
            
    except asyncio.CancelledError:
        logger.info("🛑 [MATCHING_ENGINE] Shutting down...")
    finally:
        try:
            await pubsub.unsubscribe()
            if hasattr(pubsub, 'close'):
                await pubsub.close()
        except Exception as e:
            logger.warning(f"⚠️ [MATCHING_ENGINE] Teardown error: {e}")