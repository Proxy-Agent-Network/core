import logging
import json
import time
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from redis.exceptions import WatchError

from utils.webhook_auth import verify_v2x_signature
from compliance.audit_engine import ComplianceEngine
from utils.auth import verify_agent_signature

logger = logging.getLogger("V2X_Bounty_API")
router = APIRouter()

# --- DATA MODELS ---

class DistressPayload(BaseModel):
    vin: str
    fault_code: str
    latitude: float
    longitude: float
    bounty_usd: float = 25.0
    osm_color: str = "GREEN"
    # --- Secondary Agent Dispatch ---
    # Set request_secondary=True when dispatching a T2 or T3 primary agent
    # to simultaneously queue a T1 sentry for traffic direction or scene support.
    # Secondary bid parameters default to the fleet manager's configured T1 values.
    # If not provided, the system uses T1 balanced defaults ($14 start, $2/min, $24 max).
    request_secondary: bool = False
    secondary_start_bid_usd: float = 14.0   # Fleet Manager's T1 starting bid (from Auto-Dispatch Rules)
    secondary_max_bid_usd: float = 24.0     # Fleet Manager's T1 max bid
    secondary_escalation_usd_per_min: float = 2.0  # Fleet Manager's T1 escalation rate

class MissionCompletePayload(BaseModel):
    agent_id: str
    net_payout: float 
    evidence_urls: list = []
    hardware_attestation_token: str = ""
    av_signature_hex: str = ""

class SentryExtensionPayload(BaseModel):
    task_id: str
    extension_minutes: int
    accepted_bounty_usd: float

# --- HELPER ---

def decode_redis_hash(raw_hash: dict) -> dict:
    """Safely decodes Redis byte hashes into strings."""
    if not raw_hash:
        return {}
    return {
        k.decode('utf-8') if isinstance(k, bytes) else k: 
        v.decode('utf-8') if isinstance(v, bytes) else v 
        for k, v in raw_hash.items()
    }

# --- ENDPOINTS ---

@router.post("/v1/v2x/distress")
async def receive_distress_signal(
    payload: DistressPayload, 
    request: Request,
    fleet_id: str = Depends(verify_v2x_signature)
):
    """
    Receives V2X distress signals from autonomous fleets.

    For T2/T3 incidents, fleet managers may optionally set request_secondary=True
    to simultaneously queue a T1 sentry agent for traffic direction or scene support.
    The sentry is dispatched as a separate task linked to the same incident_id,
    with its own bid parameters and HNOA policy binding (role=SENTRY).
    """
    try:
        redis_client = request.app.state.redis_client
        
        dedup_key = f"pan:dedup:{payload.vin}:{payload.fault_code}"
        if not await redis_client.set(dedup_key, "active", nx=True, ex=300):
            raise HTTPException(status_code=409, detail="Duplicate task already active.")

        task_id = f"tsk_{uuid.uuid4().hex[:12]}"

        # Generate incident_id at receipt time — not at primary dispatch.
        # This is required so that:
        # (a) the sentry task can reference the incident before any agent is assigned, and
        # (b) the matching engine can write incident:{id}:primary_agent_id immediately
        #     on primary dispatch without needing a separate ID generation step.
        incident_id = f"inc_{uuid.uuid4().hex[:10]}"
        
        task_record = {
            "fleet_id": fleet_id,
            "vin": payload.vin,
            "fault_code": payload.fault_code,
            "lat": payload.latitude,
            "lon": payload.longitude,
            "bounty_usd": payload.bounty_usd,
            "base_bounty_usd": payload.bounty_usd,
            "osm_color": payload.osm_color.upper(),
            "timestamp": int(time.time()),
            "status": "pending",
            "role": "PRIMARY",
            "incident_id": incident_id,
        }
        
        await redis_client.hset(f"pan:task:{task_id}", mapping=task_record)
        await redis_client.rpush("pan:dispatch:active_tasks", task_id)

        # --- Optional Secondary Agent (Sentry) Dispatch ---
        sentry_task_id = None
        if payload.request_secondary:
            sentry_task_id = f"tsk_{uuid.uuid4().hex[:12]}"
            sentry_record = {
                "fleet_id": fleet_id,
                "vin": payload.vin,
                # Fault code is always SENTRY_TRAFFIC_DIRECTION regardless of the primary fault.
                # The sentry's job is scene support — they don't resolve the primary fault.
                "fault_code": "SENTRY_TRAFFIC_DIRECTION",
                "lat": payload.latitude,
                "lon": payload.longitude,
                "bounty_usd": payload.secondary_start_bid_usd,
                "base_bounty_usd": payload.secondary_start_bid_usd,
                "max_bounty_usd": payload.secondary_max_bid_usd,
                "escalation_usd_per_min": payload.secondary_escalation_usd_per_min,
                "osm_color": payload.osm_color.upper(),
                "timestamp": int(time.time()),
                "status": "pending",
                "role": "sentry",       # matching_engine.py reads this to set exclude_agent_id
                "required_tier": 1,     # Sentry is always a T1 agent
                "incident_id": incident_id,  # Links to primary for exclusion and joint SB 1417 report
            }
            await redis_client.hset(f"pan:task:{sentry_task_id}", mapping=sentry_record)
            await redis_client.rpush("pan:dispatch:active_tasks", sentry_task_id)
            logger.info(
                f"🚨 [SENTRY] Secondary T1 agent queued for incident {incident_id}. "
                f"Task: {sentry_task_id} | Starting bid: ${payload.secondary_start_bid_usd:.2f} "
                f"| Max: ${payload.secondary_max_bid_usd:.2f}"
            )

        await redis_client.publish("pan:stream:distress_alerts", json.dumps({
            "task_id": task_id,
            "incident_id": incident_id,
            "vin": payload.vin,
            "fault_code": payload.fault_code,
            "lat": payload.latitude,
            "lon": payload.longitude,
            "bounty_usd": payload.bounty_usd,
            "osm_color": payload.osm_color.upper(),
            "sla_status": "OK",
            "sentry_task_id": sentry_task_id,    # None if no secondary requested
            "secondary_requested": payload.request_secondary,
        }))
        
        logger.info(
            f"🚨 [V2X ALERT] Fleet: {fleet_id} | VIN: {payload.vin} | "
            f"Fault: {payload.fault_code} | OSM: {payload.osm_color.upper()} | "
            f"Incident: {incident_id} | Secondary: {payload.request_secondary}"
        )

        response = {
            "status": "success",
            "task_id": task_id,
            "incident_id": incident_id,
        }
        if sentry_task_id:
            response["sentry_task_id"] = sentry_task_id

        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [V2X] Failed to process distress signal for {payload.vin}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal routing failure.")

@router.get("/v1/agent/missions")
async def fetch_agent_missions(request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Polled by the mobile app to pick up missions assigned by the Ops Hub."""
    redis_client = request.app.state.redis_client
    cursor = 0
    active_missions = []
    
    # TODO: Replace SCAN with a per-agent mission index (e.g., SMEMBERS pan:agent:{id}:missions)
    # SCAN is acceptable for Vanguard 50 but becomes O(N) at scale.
    while True:
        cursor, keys = await redis_client.scan(cursor=cursor, match="mission:active:*", count=100)
        for key in keys:
            raw_mission = await redis_client.hgetall(key)
            mission = decode_redis_hash(raw_mission)
            
            if mission and mission.get("agent_id") == agent_id:
                key_str = key.decode("utf-8") if isinstance(key, bytes) else key
                task_id = key_str.split("mission:active:")[-1] 
                
                active_missions.append({
                    "task_id": task_id,
                    "incident_id": str(mission.get("incident_id", f"inc_{task_id}")),
                    "lat": float(mission.get("lat", 0.0)),
                    "lon": float(mission.get("lon", 0.0)),
                    "error_code": str(mission.get("fault_code", "Unknown Fault")),
                    "bounty_usd": float(mission.get('bounty_usd', 25.0)), 
                    "intersection": str(mission.get("vin", "Target Location")),
                    "role": str(mission.get("role", "PRIMARY")).upper(),
                    "status": str(mission.get("status", "ASSIGNED")).upper()
                })
        if cursor == 0:
            break
            
    if active_missions:
        logger.info(f"📤 Sending to Agent {agent_id}: {active_missions}")
        
    return active_missions

@router.post("/v1/agent/missions/{task_id}/complete")
async def complete_mission(task_id: str, payload: MissionCompletePayload, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Fired when the agent physically secures the vehicle and completes the task."""
    try:
        redis_client = request.app.state.redis_client
        
        raw_task_data = await redis_client.hgetall(f"pan:task:{task_id}")
        if not raw_task_data:
            raise HTTPException(status_code=404, detail="Task not found.")
            
        task_data = decode_redis_hash(raw_task_data)
            
        # IDOR Guard
        mission_key = f"mission:active:{task_id}"
        raw_mission_data = await redis_client.hgetall(mission_key)
        mission_data = decode_redis_hash(raw_mission_data)
        
        if not mission_data:
            raise HTTPException(status_code=404, detail="Mission not found.")
            
        if mission_data.get("agent_id") != agent_id:
            logger.warning(f"⚠️ [SECURITY] Agent {agent_id} attempted to snipe mission {task_id} assigned to {mission_data.get('agent_id')}.")
            raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

        vin = task_data.get("vin", "UNKNOWN_VIN")
        fault_code = task_data.get("fault_code", "UNKNOWN_FAULT")
        
        raw_bounty = float(task_data.get("bounty_usd", 25.0))
        actual_payout = round(raw_bounty * 0.90, 2) 

        await redis_client.hset(f"pan:task:{task_id}", "status", "COMPLETED")
        await redis_client.delete(mission_key)
        
        sealed_report = ComplianceEngine.generate_optical_health_report(
            agent_id=agent_id,
            vin=vin,
            mission_id=task_id,
            fault_code=fault_code,
            evidence_urls=payload.evidence_urls, 
            hardware_attestation_token=payload.hardware_attestation_token
        )
        
        await redis_client.hset("pan:compliance:reports", task_id, json.dumps(sealed_report))
        
        # --- ATOMIC FINANCIAL SETTLEMENT ---
        wallet_key = f"pan:agent:{agent_id}:wallet"
        
        async with redis_client.pipeline() as pipe:
            for attempt in range(10):
                try:
                    await pipe.watch(wallet_key)
                    
                    wallet_raw = await pipe.get(wallet_key)
                    if wallet_raw:
                        wallet = json.loads(wallet_raw)
                    else:
                        wallet = {"balance": 0.0, "linkedCard": None, "history": []}
                        
                    wallet["balance"] += actual_payout
                    
                    role = task_data.get("role", "PRIMARY").upper()
                    role_label = "Sentry Assist" if role == "SENTRY" else "Bounty"

                    tx_record = {
                        "id": f"tx_{int(time.time())}",
                        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                        "amount": f"+${actual_payout:.2f}",
                        "description": f"{role_label}: {fault_code} ({vin})"
                    }
                    wallet["history"].insert(0, tx_record)
                    wallet["history"] = wallet["history"][:50]
                    
                    pipe.multi()
                    pipe.set(wallet_key, json.dumps(wallet))
                    await pipe.execute()
                    break
                except WatchError:
                    if attempt == 9:
                        raise HTTPException(status_code=503, detail="Wallet temporarily unavailable. Payout queued.")
                    continue
                    
        logger.info(f"💸 [WALLET] Deposited ${actual_payout:.2f} to {agent_id}. New Balance: ${wallet['balance']:.2f}")

        await redis_client.hset(f"agent:{agent_id}", "status", "ONLINE")
        
        await redis_client.publish(
            "pan:stream:mission_cleared", 
            json.dumps({"task_id": task_id, "agent_id": agent_id, "reason": "completed"})
        )
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [V2X] Failed to execute settlement for {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal routing failure.")

@router.post("/v1/agent/missions/{task_id}/ack")
async def acknowledge_mission(task_id: str, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Phase 2 ACK: Fired silently by the mobile app the millisecond the mission UI renders."""
    redis_client = request.app.state.redis_client
    mission_key = f"mission:active:{task_id}"

    raw_mission_data = await redis_client.hgetall(mission_key)
    mission_data = decode_redis_hash(raw_mission_data)
    
    if not mission_data:
        raise HTTPException(status_code=404, detail="Mission not found or already revoked.")

    if mission_data.get("agent_id") != agent_id:
        raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

    await redis_client.hset(mission_key, mapping={
        "ack_status": "ACKNOWLEDGED",
        "ack_timestamp": int(time.time())
    })

    logger.info(f"📡 [DISPATCH] Agent {agent_id} ACKed mission {task_id}. Dispatch secure.")
    return {"status": "success", "message": "Mission acknowledged."}

@router.post("/v1/agent/missions/{task_id}/decline")
async def decline_mission(task_id: str, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Allows an agent to reject a mission, placing them on a price-sensitive cooldown."""
    redis_client = request.app.state.redis_client
    
    raw_task_data = await redis_client.hgetall(f"pan:task:{task_id}")
    task_data = decode_redis_hash(raw_task_data)
    
    if not task_data:
        return {"status": "ignored", "message": "Task no longer exists."}
        
    rejected_bounty = float(task_data.get("bounty_usd", 25.0))
    
    cooldown_key = f"cooldown:{task_id}:{agent_id}"
    await redis_client.setex(cooldown_key, 900, str(rejected_bounty))
    
    mission_key = f"mission:active:{task_id}"
    raw_mission_data = await redis_client.hgetall(mission_key)
    mission_data = decode_redis_hash(raw_mission_data)
    
    if mission_data and mission_data.get("agent_id") == agent_id:
        await redis_client.delete(mission_key)
        await redis_client.hset(f"agent:{agent_id}", "status", "ONLINE")
        await redis_client.publish(
            "pan:stream:mission_cleared", 
            json.dumps({"task_id": task_id, "agent_id": agent_id, "reason": "declined"})
        )

    logger.info(f"🚫 [V2X] Agent {agent_id} declined {task_id} at ${rejected_bounty:.2f}. 15-Min Cooldown active.")
    return {"status": "success", "message": "Mission declined."}

@router.post("/v1/agent/missions/{task_id}/extend")
async def extend_sentry_mission(
    task_id: str, 
    payload: SentryExtensionPayload, 
    request: Request, 
    agent_id: str = Depends(verify_agent_signature)
):
    """Processes an accepted tactical time extension for a Sentry role."""
    redis_client = request.app.state.redis_client
    mission_key = f"mission:active:{task_id}"

    raw_mission_data = await redis_client.hgetall(mission_key)
    mission_data = decode_redis_hash(raw_mission_data)
    
    if not mission_data or mission_data.get("agent_id") != agent_id:
        raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

    if mission_data.get("role", "PRIMARY").upper() != "SENTRY":
        raise HTTPException(status_code=403, detail="Extension only valid for SENTRY role missions.")

    # Guard against exceeding the fleet manager's configured max bid for this sentry task
    raw_task_data = await redis_client.hgetall(f"pan:task:{task_id}")
    task_data = decode_redis_hash(raw_task_data)
    max_bounty = float(task_data.get("max_bounty_usd", float('inf')))

    current_bounty = float(mission_data.get("bounty_usd", 0.0))
    new_bounty = current_bounty + payload.accepted_bounty_usd

    if new_bounty > max_bounty:
        raise HTTPException(
            status_code=400,
            detail=f"Extension would exceed fleet max bid of ${max_bounty:.2f} for this sentry task."
        )

    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.hset(mission_key, mapping={
            "bounty_usd": new_bounty,
            "extension_minutes_added": payload.extension_minutes
        })
        pipe.hset(f"pan:task:{task_id}", "bounty_usd", new_bounty)
        await pipe.execute()

    logger.info(
        f"⏱️ [SENTRY] Agent {agent_id} accepted +{payload.extension_minutes}m extension "
        f"for ${payload.accepted_bounty_usd:.2f}. New total: ${new_bounty:.2f} "
        f"(fleet max: ${max_bounty:.2f})"
    )
    return {"status": "success", "new_bounty_usd": new_bounty}