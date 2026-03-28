import os
import logging
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException

logger = logging.getLogger("PAN_TelemetryStream")
router = APIRouter()

# --- HTTP TELEMETRY INGEST ---

@router.post("/v1/telemetry/ingest")
async def ingest_telemetry(request: Request):
    """Receives 1Hz GPS pings from the mobile app and flexibly extracts coordinates."""
    # 6. Auth Guard for Telemetry Ingest
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    expected = os.getenv("OPS_HUB_TOKEN")
    if not expected:
        expected = "dev-token-777"
        
    if token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        data = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    lat = data.get("lat") or data.get("latitude")
    lon = data.get("lon") or data.get("longitude") or data.get("lng")
    agent_id = data.get("agent_id", "Vanguard-01")
    status = data.get("status", "ONLINE")

    if lat is None or lon is None:
        return {"status": "error", "message": "Missing lat/lon keys"}

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return {"status": "error", "message": "Coordinates must be numbers"}

    redis_client = request.app.state.redis_client
    
    await redis_client.hset(f"agent:{agent_id}", mapping={"lat": lat, "lon": lon, "status": status})
    await redis_client.geoadd("agents:locations", (lon, lat, agent_id))
    
    await redis_client.publish(
        "pan:stream:agent_locations", 
        json.dumps({"agent_id": agent_id, "lat": lat, "lon": lon, "status": status, "heading": 0.0})
    )
    return {"status": "ok", "received": True}


# --- WEBSOCKET STREAM ---

@router.websocket("/v1/telemetry/stream")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    # 1. Production Token Fallback Guard
    expected_token = os.getenv("OPS_HUB_TOKEN")
    if not expected_token:
        if os.getenv("ENVIRONMENT") == "production":
            raise RuntimeError("FATAL: OPS_HUB_TOKEN is not set in production.")
        expected_token = "dev-token-777"
        logger.warning("⚠️ Using insecure dev token. Set OPS_HUB_TOKEN for production.")
        
    token = websocket.query_params.get("token")
    
    if token != expected_token:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    logger.info("🟢 [OPS_HUB] New Command Center UI connected to telemetry stream.")
    
    redis_client = websocket.app.state.redis_client
    
    # 🟢 STATE REHYDRATION
    try:
        # Sync Active Agents
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="agent:*", count=100)
            for key in keys:
                # 2. & 5. Removed byte decoding and agents:locations check
                agent = await redis_client.hgetall(key)
                
                if agent:
                    lat = agent.get("lat") or agent.get("latitude")
                    lon = agent.get("lon") or agent.get("longitude")
                    
                    if lat is not None and lon is not None:
                        await websocket.send_json({
                            "type": "AGENT_LOCATION",
                            "payload": {
                                "agent_id": key.split(":")[-1], 
                                "lat": float(lat), 
                                "lon": float(lon), 
                                "status": agent.get("status", "ONLINE")
                            }
                        })
            if int(cursor) == 0: break
            
        # Sync Active Distress Signals
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="pan:task:*", count=100)
            for key in keys:
                task = await redis_client.hgetall(key)
                if task:
                    lat = task.get("lat") or task.get("latitude")
                    lon = task.get("lon") or task.get("longitude")
                    
                    if lat is not None and lon is not None:
                        task_id = key.split("pan:task:")[-1]
                        
                        sla_status = "OK"
                        mission_data = await redis_client.hgetall(f"mission:active:{task_id}")
                        if mission_data:
                            sla_status = mission_data.get("sla_status", "OK")
                            
                        await websocket.send_json({
                            "type": "DISTRESS_ALERT",
                            "payload": {
                                "task_id": task_id, 
                                "vin": task.get("vin", "UNKNOWN"),
                                "fault_code": task.get("fault_code", "unknown_fault"),
                                "lat": float(lat), 
                                "lon": float(lon),
                                "bounty_usd": float(task.get("bounty_usd", 25.0)),
                                "sla_status": sla_status
                            }
                        })
            if int(cursor) == 0: break
    except Exception as e:
        logger.error(f"⚠️ Failed to sync initial state: {e}")

    # Standard Live Stream Listeners
    pubsub = redis_client.pubsub()
    try:
        await pubsub.subscribe("pan:stream:agent_locations", "pan:stream:distress_alerts", "pan:stream:mission_cleared", "pan:stream:sla_alerts")
        
        async def pubsub_reader():
            ping_counter = 0
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is not None:
                    payload_str = message["data"]
                    channel = message["channel"]
                    
                    try:
                        parsed_payload = json.loads(payload_str)
                    except json.JSONDecodeError:
                        continue
                    
                    if "agent_locations" in channel: event_type = "AGENT_LOCATION"
                    elif "mission_cleared" in channel: event_type = "MISSION_CLEARED"
                    elif "sla_alerts" in channel: event_type = parsed_payload.get("type", "SLA_ALERT")
                    else: event_type = "DISTRESS_ALERT"
                    
                    await websocket.send_json({"type": event_type, "payload": parsed_payload})
                
                ping_counter += 1
                if ping_counter >= 3000:  
                    await websocket.send_json({"type": "HEARTBEAT"})
                    ping_counter = 0
                    
                await asyncio.sleep(0.01)

        async def websocket_reader():
            while True:
                try:
                    data = await websocket.receive_json()
                    if data.get("action") == "DISPATCH_AGENT":
                        # 3. Payload and task_id validation
                        payload = data.get("payload", {})
                        task_id = payload.get("task_id")
                        if not task_id or not isinstance(task_id, str) or not task_id.startswith("tsk_"):
                            logger.warning(f"⚠️ Invalid task_id in dispatch command: {task_id}")
                            continue
                        await redis_client.publish("pan:stream:dispatch_commands", json.dumps(payload))
                except WebSocketDisconnect:
                    # 4. Graceful disconnect logging
                    logger.info("🔴 [OPS_HUB] Command Center UI disconnected cleanly.")
                    break
                except Exception:
                    continue

        reader_task = asyncio.create_task(pubsub_reader(), name="pubsub_reader")
        ws_task = asyncio.create_task(websocket_reader(), name="websocket_reader")

        done, pending = await asyncio.wait([reader_task, ws_task], return_when=asyncio.FIRST_COMPLETED)
        for task in pending: task.cancel()

    except Exception as e:
        logger.error(f"❌ Telemetry Stream crashed: {str(e)}", exc_info=True)
    finally:
        try:
            await pubsub.unsubscribe()
            if hasattr(pubsub, 'close'): await pubsub.close()
        except Exception:
            pass