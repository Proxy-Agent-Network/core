import os
import logging
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends

# 🟢 THE FIX 2: Import decode_redis_hash to handle byte/string variances defensively
from api.v2x_bounty_api import decode_redis_hash
# 🟢 THE FIX 1: Import the standard agent auth dependency
from utils.auth import verify_agent_signature

logger = logging.getLogger("PAN_TelemetryStream")
router = APIRouter()

# --- HTTP TELEMETRY INGEST ---

@router.post("/v1/telemetry/ingest")
async def ingest_telemetry(request: Request, agent_identity: dict = Depends(verify_agent_signature)):
    """Receives 1Hz GPS pings from the mobile app and flexibly extracts coordinates."""
    
    try:
        data = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    lat = data.get("lat") or data.get("latitude")
    lon = data.get("lon") or data.get("longitude") or data.get("lng")
    
    # 🟢 THE FIX 1: Cryptographically enforce the Agent ID from the validated token, 
    # preventing location spoofing by malicious actors.
    agent_id = agent_identity.get("agent_id")
    status = data.get("status", "ONLINE")

    if lat is None or lon is None:
        return {"status": "error", "message": "Missing lat/lon keys"}

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return {"status": "error", "message": "Coordinates must be numbers"}

    redis_client = request.app.state.redis_client
    
    # Update agent state
    await redis_client.hset(f"agent:{agent_id}", mapping={"lat": lat, "lon": lon, "status": status})
    await redis_client.geoadd("pan:agent_locations", (lon, lat, agent_id))
    
    # Broadcast to Ops Hub via PubSub
    await redis_client.publish(
        "pan:stream:agent_locations", 
        json.dumps({"agent_id": agent_id, "lat": lat, "lon": lon, "status": status, "heading": 0.0})
    )
    return {"status": "ok", "received": True}


# --- WEBSOCKET STREAM ---

@router.websocket("/v1/telemetry/stream")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    # Production Token Fallback Guard (Ops Hub UI Auth)
    expected_token = os.getenv("OPS_HUB_TOKEN")
    if not expected_token:
        if os.getenv("ENVIRONMENT") == "production":
            raise RuntimeError("FATAL: OPS_HUB_TOKEN is not set in production.")
        expected_token = "dev-token-777"
        logger.warning("⚠️ Using insecure dev token. Set OPS_HUB_TOKEN for production.")
        
    token = websocket.query_params.get("token")
    
    if token != expected_token:
        logger.warning("🚨 Unauthorized WebSocket connection attempt blocked.")
        await websocket.close(code=1008)
        return

    await websocket.accept()
    logger.info("🟢 [OPS_HUB] New Command Center UI connected to telemetry stream.")
    
    redis_client = websocket.app.state.redis_client
    
    # --- 1. STATE REHYDRATION ---
    try:
        # Sync Active Agents
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="agent:*", count=100)
            for key in keys:
                raw_agent = await redis_client.hgetall(key)
                if raw_agent:
                    # 🟢 THE FIX 2: Defensively decode the Redis hash
                    agent = decode_redis_hash(raw_agent)
                    lat = agent.get("lat") or agent.get("latitude")
                    lon = agent.get("lon") or agent.get("longitude")
                    
                    if lat is not None and lon is not None:
                        # Ensure key is a string
                        key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                        await websocket.send_json({
                            "type": "AGENT_LOCATION",
                            "payload": {
                                "agent_id": key_str.split(":")[-1], 
                                "lat": float(lat), 
                                "lon": float(lon), 
                                "status": agent.get("status", "OFFLINE")
                            }
                        })
            if int(cursor) == 0: break
            
        # Sync Active Distress Signals
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="pan:task:*", count=100)
            for key in keys:
                raw_task = await redis_client.hgetall(key)
                if raw_task:
                    # 🟢 THE FIX 2: Defensively decode the Redis hash
                    task = decode_redis_hash(raw_task)
                    status = task.get("status", "")
                    if status in ["COMPLETED", "declined", "CANCELLED"]:
                        continue # Skip resolved tasks

                    lat = task.get("lat") or task.get("latitude")
                    lon = task.get("lon") or task.get("longitude")
                    
                    if lat is not None and lon is not None:
                        key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                        task_id = key_str.split("pan:task:")[-1]
                        
                        sla_status = "OK"
                        raw_mission = await redis_client.hgetall(f"mission:active:{task_id}")
                        if raw_mission:
                            mission_data = decode_redis_hash(raw_mission)
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

    # --- 2. LIVE STREAM LISTENERS ---
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
                    
                    # Safely handle byte channels
                    channel_str = channel.decode('utf-8') if isinstance(channel, bytes) else channel
                    
                    try:
                        parsed_payload = json.loads(payload_str)
                    except json.JSONDecodeError:
                        continue
                    
                    # Map Redis PubSub channels to React UI Event Types
                    if "agent_locations" in channel_str: event_type = "AGENT_LOCATION"
                    elif "mission_cleared" in channel_str: event_type = "MISSION_CLEARED"
                    elif "sla_alerts" in channel_str: event_type = parsed_payload.get("type", "SLA_ALERT")
                    else: event_type = "DISTRESS_ALERT"
                    
                    await websocket.send_json({"type": event_type, "payload": parsed_payload})
                
                # Keepalive Heartbeat
                ping_counter += 1
                if ping_counter >= 3000:  
                    await websocket.send_json({"type": "HEARTBEAT"})
                    ping_counter = 0
                    
                await asyncio.sleep(0.01)

        async def websocket_reader():
            while True:
                try:
                    data = await websocket.receive_json()
                    
                    # Wire Ops Hub Manual Dispatch directly to the matching engine queue
                    if data.get("action") == "DISPATCH_AGENT":
                        payload = data.get("payload", {})
                        task_id = payload.get("task_id")
                        
                        if not task_id or not isinstance(task_id, str) or not task_id.startswith("tsk_"):
                            logger.warning(f"⚠️ Invalid task_id in dispatch command: {task_id}")
                            continue
                            
                        logger.info(f"🚀 Ops Command triggered manual dispatch for {task_id}")
                        
                        # Push to the live matching engine queue
                        await redis_client.rpush("pan:dispatch:active_tasks", task_id)
                        
                        # Also broadcast the command logging
                        await redis_client.publish("pan:stream:dispatch_commands", json.dumps(payload))
                        
                except WebSocketDisconnect:
                    logger.info("🔴 [OPS_HUB] Command Center UI disconnected cleanly.")
                    break
                except Exception:
                    continue

        # Run both listeners concurrently
        reader_task = asyncio.create_task(pubsub_reader(), name="pubsub_reader")
        ws_task = asyncio.create_task(websocket_reader(), name="websocket_reader")

        done, pending = await asyncio.wait([reader_task, ws_task], return_when=asyncio.FIRST_COMPLETED)
        
        # Cleanup
        for task in pending: task.cancel()

    except Exception as e:
        logger.error(f"❌ Telemetry Stream crashed: {str(e)}", exc_info=True)
    finally:
        try:
            await pubsub.unsubscribe()
            if hasattr(pubsub, 'close'): await pubsub.close()
        except Exception:
            pass