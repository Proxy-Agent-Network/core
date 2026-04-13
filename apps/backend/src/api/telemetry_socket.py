import os
import time
import logging
import json
import asyncio
from typing import Dict
from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends

from api.v2x_bounty_api import decode_redis_hash
from utils.auth import verify_agent_signature, verify_agent_jwt

logger = logging.getLogger("PAN_TelemetryStream")
router = APIRouter()

AGENT_STATE_TTL_SECONDS = 60 * 60 * 24 * 30

# --- HTTP TELEMETRY INGEST ---

@router.post("/v1/telemetry/ingest")
async def ingest_telemetry(request: Request, agent_identity: dict = Depends(verify_agent_signature)):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    lat = data.get("lat") or data.get("latitude")
    lon = data.get("lon") or data.get("longitude") or data.get("lng")
    
    agent_id = agent_identity if isinstance(agent_identity, str) else agent_identity.get("agent_id")
    
    if not agent_id:
        logger.warning("🚨 [TELEMETRY] Rejecting ingest: Agent identity could not be resolved.")
        raise HTTPException(status_code=401, detail="Agent identity could not be resolved.")

    status = data.get("status", "ONLINE")

    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Missing lat/lon keys")

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        raise HTTPException(status_code=400, detail="Coordinates must be numbers")

    redis_client = request.app.state.redis_client
    
    agent_key = f"pan:agent:{agent_id}"
    await redis_client.hset(agent_key, mapping={"lat": lat, "lon": lon, "status": status})
    await redis_client.expire(agent_key, AGENT_STATE_TTL_SECONDS)

    await redis_client.geoadd("pan:agent_locations", (lon, lat, agent_id))
    
    await redis_client.publish(
        "pan:stream:agent_locations", 
        json.dumps({"agent_id": agent_id, "lat": lat, "lon": lon, "status": status, "heading": 0.0})
    )
    return {"status": "ok", "received": True}


class StatusUpdateRequest(BaseModel):
    status: str
    latitude: float
    longitude: float
    radius: float
    loadout: Dict[str, float]
    signature: str
    timestamp: int


@router.post("/v1/agent/status")
async def update_agent_status(
    payload: StatusUpdateRequest,
    request: Request,
    agent_identity: dict = Depends(verify_agent_signature)
):
    agent_id = agent_identity if isinstance(agent_identity, str) else agent_identity.get("agent_id")
    
    if not agent_id:
        raise HTTPException(status_code=401, detail="Agent identity could not be resolved.")
        
    redis_client = request.app.state.redis_client

    agent_key = f"pan:agent:{agent_id}"
    await redis_client.hset(agent_key, mapping={
        "status": payload.status,
        "lat": payload.latitude,
        "lon": payload.longitude,
        "radius_miles": payload.radius,
        "last_active": payload.timestamp
    })
    await redis_client.expire(agent_key, AGENT_STATE_TTL_SECONDS)

    if payload.loadout:
        await redis_client.hset(f"pan:agent:{agent_id}:loadout", mapping=payload.loadout)

    if payload.status == "ONLINE":
        await redis_client.geoadd("pan:agent_locations", (payload.longitude, payload.latitude, agent_id))
    else:
        await redis_client.zrem("pan:agent_locations", agent_id)

    await redis_client.publish(
        "pan:stream:agent_locations", 
        json.dumps({
            "agent_id": agent_id, 
            "lat": payload.latitude, 
            "lon": payload.longitude, 
            "status": payload.status, 
            "heading": 0.0
        })
    )

    return {"status": "success"}


# --- WEBSOCKET STREAMS ---

@router.websocket("/v1/agent/stream")
async def agent_mission_stream(websocket: WebSocket):
    token = websocket.query_params.get("token")
    agent_id = websocket.query_params.get("agent_id")
    
    if not token or not agent_id:
        logger.warning("🚨 [WEBSOCKET] Agent connection rejected: Missing token or agent_id.")
        await websocket.close(code=1008)
        return

    redis_client = websocket.app.state.redis_client

    # 🟢 THE FIX: Correctly awaited the async verify_agent_jwt with redis_client
    try:
        verified_id = await verify_agent_jwt(token, redis_client) 
        
        if verified_id != agent_id:
            logger.warning(f"🚨 [WEBSOCKET] IDOR Attempt Blocked: Token identity ({verified_id}) does not match requested agent_id ({agent_id}).")
            await websocket.close(code=1008)
            return
    except Exception as e:
        logger.warning(f"🚨 [WEBSOCKET] Invalid JWT provided for {agent_id}: {str(e)}")
        await websocket.close(code=1008)
        return

    await websocket.accept()
    logger.info(f"🟢 [AGENT_WS] Agent {agent_id} successfully authenticated and connected.")
    
    pubsub = redis_client.pubsub()
    
    personal_dispatch_channel = f"pan:agent:{agent_id}:dispatch"
    clear_channel = "pan:stream:mission_cleared"
    
    try:
        await pubsub.subscribe(personal_dispatch_channel, clear_channel)
        
        ping_counter = 0
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is not None:
                payload_str = message["data"]
                channel_str = message["channel"].decode('utf-8') if isinstance(message["channel"], bytes) else message["channel"]
                
                try:
                    parsed_payload = json.loads(payload_str)
                except json.JSONDecodeError:
                    continue
                
                if channel_str == personal_dispatch_channel:
                    await websocket.send_json({"type": "NEW_MISSION", "payload": parsed_payload})
                elif channel_str == clear_channel:
                    if parsed_payload.get("agent_id") == agent_id:
                        await websocket.send_json({"type": "MISSION_CLEARED", "payload": parsed_payload})
            
            ping_counter += 1
            if ping_counter >= 3000:
                await websocket.send_json({"type": "HEARTBEAT"})
                ping_counter = 0
                
            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        logger.info(f"🔴 [AGENT_WS] Agent {agent_id} disconnected.")
    except Exception as e:
        logger.error(f"❌ [AGENT_WS] Stream crashed for {agent_id}: {str(e)}", exc_info=True)
    finally:
        await pubsub.unsubscribe()
        if hasattr(pubsub, 'close'):
            await pubsub.close()


@router.websocket("/v1/telemetry/stream")
async def websocket_telemetry_endpoint(websocket: WebSocket):
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
        active_agent_ids = await redis_client.zrange("pan:agent_locations", 0, -1)
        for agent_id_bytes in active_agent_ids:
            agent_id = agent_id_bytes.decode('utf-8') if isinstance(agent_id_bytes, bytes) else agent_id_bytes
            
            raw_agent = await redis_client.hgetall(f"pan:agent:{agent_id}")
            if raw_agent:
                agent = decode_redis_hash(raw_agent)
                lat = agent.get("lat") or agent.get("latitude")
                lon = agent.get("lon") or agent.get("longitude")
                
                if lat is not None and lon is not None:
                    await websocket.send_json({
                        "type": "AGENT_LOCATION",
                        "payload": {
                            "agent_id": agent_id, 
                            "lat": float(lat), 
                            "lon": float(lon), 
                            "status": agent.get("status", "OFFLINE")
                        }
                    })
            
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="pan:task:*", count=100)
            for key in keys:
                raw_task = await redis_client.hgetall(key)
                if raw_task:
                    task = decode_redis_hash(raw_task)
                    status = task.get("status", "")
                    if status in ["COMPLETED", "declined", "CANCELLED"]:
                        continue

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
            if int(cursor) == 0:
                break

    except Exception as e:
        logger.error(f"⚠️ Failed to sync initial state: {e}")

    # --- 2. LIVE STREAM LISTENERS ---
    pubsub = redis_client.pubsub()
    try:
        await pubsub.subscribe(
            "pan:stream:agent_locations",
            "pan:stream:distress_alerts",
            "pan:stream:mission_cleared",
            "pan:stream:sla_alerts"
        )
        
        async def pubsub_reader():
            ping_counter = 0
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is not None:
                    payload_str = message["data"]
                    channel = message["channel"]
                    
                    channel_str = channel.decode('utf-8') if isinstance(channel, bytes) else channel
                    
                    try:
                        parsed_payload = json.loads(payload_str)
                    except json.JSONDecodeError:
                        continue
                    
                    if "agent_locations" in channel_str:
                        event_type = "AGENT_LOCATION"
                    elif "mission_cleared" in channel_str:
                        event_type = "MISSION_CLEARED"
                    elif "sla_alerts" in channel_str:
                        event_type = parsed_payload.get("type", "SLA_ALERT")
                    else:
                        event_type = "DISTRESS_ALERT"
                    
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
                        payload = data.get("payload", {})
                        task_id = payload.get("task_id")
                        
                        if not task_id or not isinstance(task_id, str) or not task_id.startswith("tsk_"):
                            logger.warning(f"⚠️ Invalid task_id in dispatch command: {task_id}")
                            continue
                            
                        logger.info(f"🚀 Ops Command triggered manual dispatch for {task_id}")
                        await redis_client.rpush("pan:dispatch:active_tasks", task_id)
                        await redis_client.publish("pan:stream:dispatch_commands", json.dumps(payload))
                        
                except WebSocketDisconnect:
                    logger.info("🔴 [OPS_HUB] Command Center UI disconnected cleanly.")
                    break
                except Exception as e:
                    logger.error(f"[OPS_HUB] websocket_reader error: {e}")
                    continue

        reader_task = asyncio.create_task(pubsub_reader(), name="pubsub_reader")
        ws_task = asyncio.create_task(websocket_reader(), name="websocket_reader")

        done, pending = await asyncio.wait([reader_task, ws_task], return_when=asyncio.FIRST_COMPLETED)
        
        for task in pending:
            task.cancel()

    except Exception as e:
        logger.error(f"❌ Telemetry Stream crashed: {str(e)}", exc_info=True)
    finally:
        try:
            await pubsub.unsubscribe()
            if hasattr(pubsub, 'close'):
                await pubsub.close()