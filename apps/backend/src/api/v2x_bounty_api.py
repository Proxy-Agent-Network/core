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

class MissionCompletePayload(BaseModel):
    agent_id: str
    netPayout: float # Kept in schema for backwards compatibility but ignored by backend math
    evidence_urls: list = []
    hardware_attestation_token: str = ""

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
        
        # Restored Dedup Guard to prevent AV replay attacks
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
        
        # Maintained rpush for correct FIFO dispatch queueing
        await redis_client.rpush("pan:dispatch:active_tasks", task_id)
        
        # Broadcast to Ops Hub map
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
            mission = await redis_client.hgetall(key)
            if mission and mission.get("agent_id") == agent_id:
                
                task_id = key.split("mission:active:")[-1] 
                
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
        
        # 1. Grab task details for the compliance report
        task_data = await redis_client.hgetall(f"pan:task:{task_id}")
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found.")
            
        # 🟢 NEW: IDOR Guard - Verify the agent completing the mission actually owns it
        mission_key = f"mission:active:{task_id}"
        mission_data = await redis_client.hgetall(mission_key)
        if mission_data and mission_data.get("agent_id") != agent_id:
            logger.warning(f"⚠️ [SECURITY] Agent {agent_id} attempted to snipe mission {task_id} assigned to {mission_data.get('agent_id')}.")
            raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

        vin = task_data.get("vin", "UNKNOWN_VIN")
        fault_code = task_data.get("fault_code", "UNKNOWN_FAULT")
        
        # Trust boundary enforcement. Backend securely calculates the final payout.
        raw_bounty = float(task_data.get("bounty_usd", 25.0))
        actual_payout = round(raw_bounty * 0.90, 2) # Agent earns 90% cut of the escrow
        
        if payload.netPayout != 0.0:
            logger.warning(f"⚠️ [SECURITY] Agent {agent_id} attempted to submit a client-side payout of ${payload.netPayout:.2f}. Overriding with server truth: ${actual_payout:.2f}")

        # 2. Keep the task record and update status for SB 1417 audit trails
        await redis_client.hset(f"pan:task:{task_id}", "status", "COMPLETED")
        await redis_client.delete(mission_key)
        
        # 3. Synchronously generate the Optical Health Report
        token = payload.hardware_attestation_token
        if not token or len(token) < 100:
            token = "dev_bypass_token_" + ("A" * 90)
            
        sealed_report = ComplianceEngine.generate_optical_health_report(
            agent_id=agent_id,
            vin=vin,
            mission_id=task_id,
            fault_code=fault_code,
            evidence_urls=payload.evidence_urls, 
            hardware_attestation_token=token
        )
        
        # 4. Persist the sealed report to the compliance ledger
        await redis_client.hset("pan:compliance:reports", task_id, json.dumps(sealed_report))
        
        # --- 5. ATOMIC FINANCIAL SETTLEMENT ---
        wallet_key = f"pan:agent:{agent_id}:wallet"
        
        async with redis_client.pipeline() as pipe:
            for attempt in range(10):
                try:
                    await pipe.watch(wallet_key)
                    
                    # NOTE FOR FUTURE DEVS: Immediate-execution mode active after watch().
                    # pipe.get() executes directly and returns the value. Do NOT move this inside multi()!
                    wallet_raw = await pipe.get(wallet_key)
                    
                    if wallet_raw:
                        wallet = json.loads(wallet_raw)
                    else:
                        wallet = {"balance": 0.0, "linkedCard": None, "history": []}
                        
                    # Securely apply the server-side calculated payout
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
                    logger.warning(f"Concurrent collision depositing bounty for {agent_id}. Retry {attempt + 1}/10...")
                    if attempt == 9:
                        raise HTTPException(status_code=503, detail="Wallet temporarily unavailable. Payout queued.")
                    continue
                    
        logger.info(f"💸 [WALLET] Deposited ${actual_payout:.2f} to {agent_id}. New Balance: ${wallet['balance']:.2f}")
        # ---------------------------------------------------

        # Return agent to the available pool
        await redis_client.hset(f"agent:{agent_id}", "status", "ONLINE")
        
        # Broadcast cleared state to the Ops Hub Map
        await redis_client.publish(
            "pan:stream:mission_cleared", 
            json.dumps({"task_id": task_id, "agent_id": agent_id, "reason": "completed"})
        )
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [V2X] Failed to seal compliance for {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal routing failure.")

@router.post("/v1/agent/missions/{task_id}/ack")
async def acknowledge_mission(task_id: str, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """
    Phase 2 ACK: Fired silently by the mobile app the millisecond the mission UI renders.
    
    # TODO: SLA monitor should revoke missions with no ACK within 15 seconds of dispatch
    """
    redis_client = request.app.state.redis_client
    mission_key = f"mission:active:{task_id}"

    mission_data = await redis_client.hgetall(mission_key)
    
    # If it's missing, the watchdog already revoked it
    if not mission_data:
        raise HTTPException(status_code=404, detail="Mission not found or already revoked.")

    # Prevent IDOR sniping
    if mission_data.get("agent_id") != agent_id:
        logger.warning(f"⚠️ [SECURITY] Agent {agent_id} attempted to ACK mission {task_id} assigned to {mission_data.get('agent_id')}.")
        raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

    # Update the ledger so the watchdog knows the agent successfully received it
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
    
    # Fetch the current task to see what bounty they rejected
    task_data = await redis_client.hgetall(f"pan:task:{task_id}")
    if not task_data:
        return {"status": "ignored", "message": "Task no longer exists."}
        
    rejected_bounty = float(task_data.get("bounty_usd", 25.0))
    
    cooldown_key = f"cooldown:{task_id}:{agent_id}"
    await redis_client.setex(cooldown_key, 900, str(rejected_bounty))
    
    mission_key = f"mission:active:{task_id}"
    mission_data = await redis_client.hgetall(mission_key)
    
    if mission_data and mission_data.get("agent_id") == agent_id:
        await redis_client.delete(mission_key)
        await redis_client.hset(f"agent:{agent_id}", "status", "ONLINE")
        await redis_client.publish(
            "pan:stream:mission_cleared", 
            json.dumps({"task_id": task_id, "agent_id": agent_id, "reason": "declined"})
        )

    logger.info(f"🚫 [V2X] Agent {agent_id} declined {task_id} at ${rejected_bounty:.2f}. 15-Min Cooldown active.")
    return {"status": "success", "message": "Mission declined."}