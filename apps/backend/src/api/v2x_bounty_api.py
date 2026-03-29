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
from core.economics.escrow_oracle import EscrowOracle

logger = logging.getLogger("V2X_Bounty_API")
router = APIRouter()

# --- DATA MODELS ---

class DistressPayload(BaseModel):
    vin: str
    fault_code: str
    latitude: float
    longitude: float
    bounty_usd: float = 25.0

class MissionCompletePayload(BaseModel):
    agent_id: str
    netPayout: float 
    evidence_urls: list = []
    hardware_attestation_token: str = ""
    av_signature_hex: str = ""

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
    """Receives V2X distress signals from autonomous fleets."""
    try:
        redis_client = request.app.state.redis_client
        
        dedup_key = f"pan:dedup:{payload.vin}:{payload.fault_code}"
        if not await redis_client.set(dedup_key, "active", nx=True, ex=300):
            raise HTTPException(status_code=409, detail="Duplicate task already active.")
            
        task_id = f"tsk_{uuid.uuid4().hex[:12]}"
        
        task_record = {
            "fleet_id": fleet_id,
            "vin": payload.vin,
            "fault_code": payload.fault_code,
            "lat": payload.latitude,
            "lon": payload.longitude,
            "bounty_usd": payload.bounty_usd,
            "timestamp": int(time.time()),
            "status": "pending"
        }
        
        await redis_client.hset(f"pan:task:{task_id}", mapping=task_record)
        await redis_client.rpush("pan:dispatch:active_tasks", task_id)
        
        await redis_client.publish("pan:stream:distress_alerts", json.dumps({
            "task_id": task_id,
            "vin": payload.vin,
            "fault_code": payload.fault_code,
            "lat": payload.latitude,
            "lon": payload.longitude,
            "bounty_usd": payload.bounty_usd,
            "sla_status": "OK"
        }))
        
        logger.info(f"🚨 [V2X ALERT] Fleet: {fleet_id} | VIN: {payload.vin} | Fault: {payload.fault_code}")
        return {"status": "success", "task_id": task_id}
        
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
    
    while True:
        cursor, keys = await redis_client.scan(cursor=cursor, match="mission:active:*", count=100)
        for key in keys:
            raw_mission = await redis_client.hgetall(key)
            mission = decode_redis_hash(raw_mission)
            
            if mission and mission.get("agent_id") == agent_id:
                # Handle bytes key splitting just in case
                key_str = key.decode("utf-8") if isinstance(key, bytes) else key
                task_id = key_str.split("mission:active:")[-1] 
                
                active_missions.append({
                    "taskId": task_id,
                    "lat": float(mission.get("lat", 0.0)),
                    "lon": float(mission.get("lon", 0.0)),
                    "errorCode": str(mission.get("fault_code", "Unknown Fault")),
                    "bounty": f"${float(mission.get('bounty_usd', 25.0)):.2f}", 
                    "intersection": str(mission.get("vin", "Target Location"))
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
        
        # 1. Grab task details
        raw_task_data = await redis_client.hgetall(f"pan:task:{task_id}")
        if not raw_task_data:
            raise HTTPException(status_code=404, detail="Task not found.")
            
        task_data = decode_redis_hash(raw_task_data)
            
        # IDOR Guard
        mission_key = f"mission:active:{task_id}"
        raw_mission_data = await redis_client.hgetall(mission_key)
        mission_data = decode_redis_hash(raw_mission_data)
        
        if mission_data and mission_data.get("agent_id") != agent_id:
            logger.warning(f"⚠️ [SECURITY] Agent {agent_id} attempted to snipe mission {task_id} assigned to {mission_data.get('agent_id')}.")
            raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

        vin = task_data.get("vin", "UNKNOWN_VIN")
        fault_code = task_data.get("fault_code", "UNKNOWN_FAULT")
        payment_hash = task_data.get("payment_hash")
        
        if not payment_hash:
            raise HTTPException(status_code=500, detail="Fatal: Mission lacks escrow payment hash.")
        
        # Zero-Trust Validation
        oracle = request.app.state.escrow_oracle
        oracle_verdict = await oracle.finalize_task(
            task_id=task_id,
            payment_hash=payment_hash,
            proof_payload={
                "agent_id": agent_id,
                "hardware_attestation_token": payload.hardware_attestation_token,
                "evidence_urls": payload.evidence_urls,
                "av_signature_hex": payload.av_signature_hex
            }
        )
        
        if oracle_verdict.get("status") != "settled":
            logger.error(f"🛑 [ORACLE REJECTED] Mission {task_id}: {oracle_verdict.get('message')}")
            raise HTTPException(status_code=403, detail=oracle_verdict.get("message", "Cryptographic settlement failed."))

        raw_bounty = float(task_data.get("bounty_usd", 25.0))
        actual_payout = round(raw_bounty * 0.90, 2) 

        # 2. Update status and generate SB 1417 audit trails
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
        
        # --- 3. ATOMIC FINANCIAL SETTLEMENT ---
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
                    
                    tx_record = {
                        "id": f"tx_{int(time.time())}",
                        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                        "amount": f"+${actual_payout:.2f}",
                        "description": f"Bounty: {fault_code} ({vin})"
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

        # 4. Return agent to the available pool
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
        logger.warning(f"⚠️ [SECURITY] Agent {agent_id} attempted to ACK mission {task_id} assigned to {mission_data.get('agent_id')}.")
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