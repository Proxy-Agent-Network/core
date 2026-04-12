import os
import time
import logging
import json
import asyncio
from typing import Dict
from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends

# TODO(refactor): Move decode_redis_hash to utils/redis_helpers.py — importing from
# business logic is a layering violation that will break if v2x_bounty_api.py is refactored.
from api.v2x_bounty_api import decode_redis_hash
from utils.auth import verify_agent_signature

logger = logging.getLogger("PAN_TelemetryStream")
router = APIRouter()

# Agent state TTL: 30 days. Resets on every status update so active agents
# never expire. Prevents stale agent hashes accumulating in Redis indefinitely.
AGENT_STATE_TTL_SECONDS = 60 * 60 * 24 * 30

# --- HTTP TELEMETRY INGEST ---

@router.post("/v1/telemetry/ingest")
async def ingest_telemetry(request: Request, agent_identity: dict = Depends(verify_agent_signature)):
    """Receives 1Hz GPS pings from the mobile app and flexibly extracts coordinates."""
    
    try:
        data = await request.json()
    except Exception:
        # 🛡️ FIX: Return proper 400 so the Android client knows the request failed
        raise HTTPException(status_code=400, detail="Invalid JSON")

    lat = data.get("lat") or data.get("latitude")
    lon = data.get("lon") or data.get("longitude") or data.get("lng")
    
    # Cryptographically enforce the Agent ID from the validated token,
    # preventing location spoofing by malicious actors.
    # 🟢 PILOT BYPASS: Handle raw string returned by the pilot mock token
    agent_id = agent_identity if isinstance(agent_identity, str) else agent_identity.get("agent_id")
    status = data.get("status", "ONLINE")

    # 🛡️ FIX: Raise HTTP 400 (not 200) so the Android client sees a real failure
    # and can log it. Returning 200 with an error body was masking silent GPS failures.
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Missing lat/lon keys")

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        raise HTTPException(status_code=400, detail="Coordinates must be numbers")

    redis_client = request.app.state.redis_client
    
    # 🛡️ FIX: Standardized key to pan:agent:{id} namespace — was agent:{id} which
    # broke the pan: prefix convention used everywhere else in the codebase.
    agent_key = f"pan:agent:{agent_id}"
    await redis_client.hset(agent_key, mapping={"lat": lat, "lon": lon, "status": status})
    # Reset TTL on every ping so active agents never expire
    await redis_client.expire(agent_key, AGENT_STATE_TTL_SECONDS)

    await redis_client.geoadd("pan:agent_locations", (lon, lat, agent_id))
    
    # Broadcast to Ops Hub via PubSub
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
    """
    Handles the 'GO ONLINE' / 'GO OFFLINE' toggle from the mobile app.
    Syncs the agent's current location, service radius, and hardware loadout.
    """
    # 🟢 PILOT BYPASS: Handle raw string returned by the pilot mock token
    agent_id = agent_identity if isinstance(agent_identity, str) else agent_identity.get("agent_id")
    redis_client = request.app.state.redis_client

    # 1. Update Core Agent State
    # 🛡️ FIX: Standardized key to pan:agent:{id} — was agent:{id} which broke the
    # pan: prefix convention and made the WebSocket SCAN miss these keys.
    agent_key = f"pan:agent:{agent_id}"
    await redis_client.hset(agent_key, mapping={
        "status": payload.status,
        "lat": payload.latitude,
        "lon": payload.longitude,
        "radius_miles": payload.radius,
        "last_active": payload.timestamp
    })
    # 🛡️ FIX: Reset 30-day TTL on every status update so active agents never expire
    await redis_client.expire(agent_key, AGENT_STATE_TTL_SECONDS)

    # 2. Sync Hardware Loadout
    if payload.loadout:
        await redis_client.hset(f"pan:agent:{agent_id}:loadout", mapping=payload.loadout)

    # 3. Update Geospatial Dispatch Index
    if payload.status == "ONLINE":
        await redis_client.geoadd("pan:agent_locations", (payload.longitude, payload.latitude, agent_id))
    else:
        # Remove offline agents from the spatial index so the Matching Engine ignores them
        await redis_client.zrem("pan:agent_locations", agent_id)

    # 4. Broadcast to Ops Hub UI
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


# --- WEBSOCKET STREAM ---

@router.websocket("/v1/telemetry/stream")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    # Production Token Fallback Guard (Ops Hub UI Auth)
    # Note: query param tokens appear in access logs. Acceptable for internal
    # Ops Hub — do not use this pattern for external-facing WebSocket endpoints.
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
        # 🛡️ FIX: Updated SCAN pattern to pan:agent:* to match standardized key convention.
        # Was agent:* which only worked because of the old naming inconsistency.
        # TODO(scale): Replace SCAN with SMEMBERS pan:agents:active index before fleet-scale
        # deployment — SCAN is O(N) and will slow down rehydration at high agent counts.
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="pan:agent:*", count=100)
            for key in keys:
                # Skip sub-keys like pan:agent:{id}:loadout and pan:agent:{id}:orders
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                if key_str.count(':') != 2:
                    continue

                raw_agent = await redis_client.hgetall(key)
                if raw_agent:
                    agent = decode_redis_hash(raw_agent)
                    lat = agent.get("lat") or agent.get("latitude")
                    lon = agent.get("lon") or agent.get("longitude")
                    
                    if lat is not None and lon is not None:
                        await websocket.send_json({
                            "type": "AGENT_LOCATION",
                            "payload": {
                                "agent_id": key_str.split(":")[-1], 
                                "lat": float(lat), 
                                "lon": float(lon), 
                                "status": agent.get("status", "OFFLINE")
                            }
                        })
            if int(cursor) == 0:
                break
            
        # Sync Active Distress Signals
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
                
                # Keepalive Heartbeat (~30 seconds at 10ms sleep)
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
                    # 🛡️ FIX: Log exceptions instead of silently swallowing them.
                    # Silent swallow was masking dispatch command failures during live ops.
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
        except Exception:
            pass