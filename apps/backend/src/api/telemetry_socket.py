import os
import logging
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("PAN_TelemetryStream")
router = APIRouter()

@router.websocket("/v1/telemetry/stream")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    Maintains a full-duplex live stream to the Ops Hub Command Center.
    Pushes real-time telemetry out, and listens for command inputs in.
    """
    # 🛠️ IMPROVEMENT 4.1: Production-Safe Token Fallback
    expected_token = os.getenv("OPS_HUB_TOKEN")
    if not expected_token:
        if os.getenv("ENVIRONMENT") == "production":
            raise RuntimeError("FATAL: OPS_HUB_TOKEN is not set in production.")
        expected_token = "dev-token-777"
        logger.warning("⚠️ Using insecure dev token. Set OPS_HUB_TOKEN for production.")

    token = websocket.query_params.get("token")
    
    if token != expected_token:
        await websocket.close(code=1008)
        logger.warning("🚫 Unauthorized WebSocket connection attempt rejected.")
        return

    await websocket.accept()
    logger.info("🟢 [OPS_HUB] New Command Center UI connected to telemetry stream.")
    
    redis_client = websocket.app.state.redis_client
    pubsub = redis_client.pubsub()
    
    try:
        await pubsub.subscribe(
            "pan:stream:agent_locations", 
            "pan:stream:distress_alerts",
            "pan:stream:mission_cleared"
        )
        
        async def pubsub_reader():
            ping_counter = 0
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is not None:
                    payload_raw = message["data"]
                    channel_raw = message["channel"]
                    payload_str = payload_raw if isinstance(payload_raw, str) else payload_raw.decode("utf-8")
                    channel = channel_raw if isinstance(channel_raw, str) else channel_raw.decode("utf-8")
                    
                    try:
                        parsed_payload = json.loads(payload_str)
                    except json.JSONDecodeError:
                        logger.error(f"⚠️ [OPS_HUB] Malformed message on channel {channel}: {payload_str[:100]}")
                        continue
                    
                    if "agent_locations" in channel:
                        event_type = "AGENT_LOCATION"
                    elif "mission_cleared" in channel:
                        event_type = "MISSION_CLEARED"
                    else:
                        event_type = "DISTRESS_ALERT"
                    
                    await websocket.send_json({
                        "type": event_type,
                        "payload": parsed_payload
                    })
                
                ping_counter += 1
                if ping_counter >= 3000:  
                    await websocket.send_json({"type": "HEARTBEAT"})
                    ping_counter = 0
                    
                await asyncio.sleep(0.01)

        async def websocket_reader():
            while True:
                try:
                    data = await websocket.receive_json()
                except WebSocketDisconnect:
                    raise
                except Exception as e:
                    logger.error(f"⚠️ Invalid inbound WebSocket frame: {e}")
                    continue

                action = data.get("action")
                if action == "DISPATCH_AGENT":
                    payload = data.get("payload", {})
                    task_id = payload.get("task_id")
                    
                    if not task_id or not isinstance(task_id, str) or not task_id.startswith("tsk_"):
                        logger.warning(f"⚠️ Invalid task_id in dispatch command: {task_id}")
                        continue
                        
                    logger.info(f"🚀 [OPS_HUB] DISPATCH COMMAND RECEIVED! Target: {task_id}")
                    
                    await redis_client.publish(
                        "pan:stream:dispatch_commands", 
                        json.dumps(payload)
                    )

        reader_task = asyncio.create_task(pubsub_reader(), name="pubsub_reader")
        ws_task = asyncio.create_task(websocket_reader(), name="websocket_reader")

        done, pending = await asyncio.wait(
            [reader_task, ws_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        
        for task in pending:
            task.cancel()

        for task in done:
            exc = task.exception()
            if exc:
                if isinstance(exc, WebSocketDisconnect):
                    logger.warning("🔴 [OPS_HUB] Command Center UI disconnected cleanly.")
                else:
                    logger.error(f"❌ Task {task.get_name()} failed: {exc}", exc_info=exc)

    except Exception as e:
        logger.error(f"❌ Telemetry Stream crashed: {str(e)}", exc_info=True)
    finally:
        try:
            await pubsub.unsubscribe()
            if hasattr(pubsub, 'close'):
                await pubsub.close()
        except Exception as teardown_error:
            logger.error(f"⚠️ Error during pubsub teardown: {str(teardown_error)}")