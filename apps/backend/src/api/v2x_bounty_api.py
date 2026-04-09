import logging
import json
import time
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel, Field
from redis.exceptions import WatchError

from utils.webhook_auth import verify_v2x_signature
from compliance.audit_engine import ComplianceEngine
from utils.auth import verify_agent_signature
from reputation.reputation_engine import ReputationEngine

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
    request_secondary: bool = False
    secondary_start_bid_usd: float = 14.0   
    secondary_max_bid_usd: float = 24.0     
    secondary_escalation_usd_per_min: float = 2.0  

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

class FeedbackPayload(BaseModel):
    is_positive: bool
    category: str = ""
    label: str = ""
    vent_text: str = Field(default="", max_length=280)

class DeclinePayload(BaseModel):
    reason: str = Field(default="No reason provided", description="Agent's selected reason for aborting/declining")

class PresencePayload(BaseModel):
    is_online: bool = Field(..., description="True to enter the dispatch pool, False to exit")

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
    try:
        redis_client = request.app.state.redis_client
        
        dedup_key = f"pan:dedup:{payload.vin}:{payload.fault_code}"
        if not await redis_client.set(dedup_key, "active", nx=True, ex=300):
            raise HTTPException(status_code=409, detail="Duplicate task already active.")

        task_id = f"tsk_{uuid.uuid4().hex[:12]}"
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

        sentry_task_id = None
        if payload.request_secondary:
            sentry_task_id = f"tsk_{uuid.uuid4().hex[:12]}"
            sentry_record = {
                "fleet_id": fleet_id,
                "vin": payload.vin,
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
                "role": "SENTRY",       # 🛡️ BUG FIXED: Uppercase to match Kotlin TaskRole enum
                "required_tier": 1,     
                "incident_id": incident_id,  
            }
            await redis_client.hset(f"pan:task:{sentry_task_id}", mapping=sentry_record)
            await redis_client.rpush("pan:dispatch:active_tasks", sentry_task_id)
            logger.info(f"🚨 [SENTRY] Secondary T1 agent queued for incident {incident_id}.")

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
            "sentry_task_id": sentry_task_id,    
            "secondary_requested": payload.request_secondary,
        }))
        
        logger.info(f"🚨 [V2X ALERT] Fleet: {fleet_id} | VIN: {payload.vin} | Fault: {payload.fault_code}")

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
    redis_client = request.app.state.redis_client
    cursor = 0
    active_missions = []
    
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
                    "fleet_id": str(mission.get("fleet_id", "Vanguard Network Partner")),
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
    try:
        redis_client = request.app.state.redis_client
        
        raw_task_data = await redis_client.hgetall(f"pan:task:{task_id}")
        if not raw_task_data:
            raise HTTPException(status_code=404, detail="Task not found.")
            
        task_data = decode_redis_hash(raw_task_data)
            
        mission_key = f"mission:active:{task_id}"
        raw_mission_data = await redis_client.hgetall(mission_key)
        mission_data = decode_redis_hash(raw_mission_data)
        
        if not mission_data:
            raise HTTPException(status_code=404, detail="Mission not found.")
            
        if mission_data.get("agent_id") != agent_id:
            logger.warning(f"⚠️ [SECURITY] Agent {agent_id} attempted to snipe mission {task_id}.")
            raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

        vin = task_data.get("vin", "UNKNOWN_VIN")
        fault_code = task_data.get("fault_code", "UNKNOWN_FAULT")
        raw_bounty = float(task_data.get("bounty_usd", 25.0))
        actual_payout = round(raw_bounty * 0.90, 2) 

        await redis_client.hset(f"pan:task:{task_id}", mapping={
            "status": "COMPLETED",
            "agent_id": agent_id
        })
        
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
        
        wallet_key = f"pan:agent:{agent_id}:wallet"
        missions_key = f"pan:agent:{agent_id}:missions_completed"
        
        async with redis_client.pipeline() as pipe:
            for attempt in range(10):
                try:
                    await pipe.watch(wallet_key)
                    wallet_raw = await pipe.get(wallet_key)
                    wallet = json.loads(wallet_raw) if wallet_raw else {"balance": 0.0, "linkedCard": None, "history": []}
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
                    pipe.incr(missions_key)
                    pipe.set(f"pan:agent:{agent_id}:last_active", int(time.time()))
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
    redis_client = request.app.state.redis_client
    mission_key = f"mission:active:{task_id}"

    raw_mission_data = await redis_client.hgetall(mission_key)
    mission_data = decode_redis_hash(raw_mission_data)
    
    if not mission_data:
        raise HTTPException(status_code=404, detail="Mission not found.")

    if mission_data.get("agent_id") != agent_id:
        raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

    await redis_client.hset(mission_key, mapping={
        "ack_status": "ACKNOWLEDGED",
        "ack_timestamp": int(time.time())
    })
    return {"status": "success"}

@router.post("/v1/agent/missions/{task_id}/decline")
async def decline_mission(
    task_id: str, 
    request: Request, 
    payload: DeclinePayload = None,
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client
    abort_reason = payload.reason if payload else "No reason provided"
    
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
            json.dumps({
                "task_id": task_id, 
                "agent_id": agent_id, 
                "reason": "declined",
                "abort_reason": abort_reason
            })
        )

    logger.info(f"🚫 [V2X] Agent {agent_id} aborted {task_id} at ${rejected_bounty:.2f}. Reason: '{abort_reason}'.")
    return {"status": "success", "message": "Mission aborted."}

@router.post("/v1/agent/missions/{task_id}/extend")
async def extend_sentry_mission(
    task_id: str, 
    payload: SentryExtensionPayload, 
    request: Request, 
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client
    mission_key = f"mission:active:{task_id}"

    raw_mission_data = await redis_client.hgetall(mission_key)
    mission_data = decode_redis_hash(raw_mission_data)
    
    if not mission_data or mission_data.get("agent_id") != agent_id:
        raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

    if mission_data.get("role", "PRIMARY").upper() != "SENTRY":
        raise HTTPException(status_code=403, detail="Extension only valid for SENTRY role missions.")

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

    return {"status": "success", "new_bounty_usd": new_bounty}

@router.post("/v1/agent/missions/{task_id}/feedback")
async def submit_mission_feedback(
    task_id: str,
    payload: FeedbackPayload,
    request: Request,
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client
    
    raw_task_data = await redis_client.hgetall(f"pan:task:{task_id}")
    if not raw_task_data:
        raise HTTPException(status_code=404, detail="Task not found.")
        
    task_data = decode_redis_hash(raw_task_data)
    
    if task_data.get("status", "").upper() != "COMPLETED":
        raise HTTPException(status_code=400, detail="Feedback can only be submitted for COMPLETED tasks.")
        
    assigned_agent = task_data.get("agent_id")
    incident_id = task_data.get("incident_id")
    
    is_assigned = False
    if incident_id:
        is_assigned = await redis_client.sismember(f"incident:{incident_id}:assigned_agents", agent_id)
            
    is_authorized = (assigned_agent == agent_id) or bool(is_assigned)
        
    if not is_authorized:
        logger.error(f"🚨 [SECURITY] IDOR Attempt: Agent {agent_id} tried to rate task {task_id}")
        raise HTTPException(status_code=403, detail="IDOR Blocked: Mission not assigned to this agent.")
        
    engine = request.app.state.reputation_engine
    target_entity_id = task_data.get("fleet_id")
    
    if not target_entity_id:
        raise HTTPException(status_code=500, detail="Task is missing fleet_id target.")
        
    result = await engine.submit_feedback(
        task_id=task_id,
        submitter_entity_id=agent_id,
        target_entity_id=target_entity_id,
        is_positive=payload.is_positive,
        feedback_direction="BUYER",
        category=payload.category,
        label=payload.label,
        vent_text=payload.vent_text
    )
    
    await redis_client.set(f"pan:agent:{agent_id}:last_active", int(time.time()))
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("reason"))
        
    return result

@router.post("/v1/agent/presence")
async def update_presence(
    payload: PresencePayload,
    request: Request,
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client
    status_str = "ONLINE" if payload.is_online else "OFFLINE"
    await redis_client.hset(f"agent:{agent_id}", "status", status_str)
    return {"status": "success", "is_online": payload.is_online}