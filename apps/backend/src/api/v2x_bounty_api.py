import logging
import uuid
import json
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Request, HTTPException, Depends, Path
from pydantic import BaseModel, Field

from utils.webhook_auth import verify_v2x_signature
from compliance.audit_engine import ComplianceEngine

logger = logging.getLogger("V2X_Bounty_API")
router = APIRouter()

async def verify_agent_signature(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Agent hardware signature required.")
    return "Vanguard-01" 

class V2XDistressPayload(BaseModel):
    vin: str = Field(..., description="Vehicle Identification Number")
    fault_code: str = Field(..., description="e.g., LIDAR_OCCLUSION, STUCK_IN_MUD")
    latitude: float
    longitude: float
    bounty_usd: float = Field(..., gt=0, le=500.0, description="Task payout in USD")
    timestamp: int

class MissionCompletionPayload(BaseModel):
    agent_id: str = Field(..., description="The verified Vanguard Agent UID")
    vin: str = Field(..., description="The stranded vehicle's VIN")
    fault_code: str = Field(..., description="The original distress fault code")
    evidence_urls: List[str] = Field(..., description="Array of ImgBB photo URLs proving completion")
    hardware_attestation_token: str = Field(..., description="JWS token from Google Play Integrity API")

@router.post("/v1/v2x/distress")
async def receive_distress_signal(request: Request, payload: V2XDistressPayload, fleet_id: str = Depends(verify_v2x_signature)):
    task_id = f"tsk_{uuid.uuid4().hex[:12]}"
    logger.info(f"🚨 [V2X ALERT] Fleet: {fleet_id} | VIN: {payload.vin} | Fault: {payload.fault_code}")
    
    try:
        redis_client = request.app.state.redis_client
        dedup_key = f"pan:dedup:{payload.vin}:{payload.fault_code}"
        if not await redis_client.set(dedup_key, task_id, nx=True, ex=300):
            raise HTTPException(status_code=409, detail="Duplicate task already active.")

        task_record = {
            "task_id": task_id, "fleet_id": fleet_id, "vin": payload.vin,
            "fault_code": payload.fault_code, "latitude": payload.latitude,
            "longitude": payload.longitude, "bounty_usd": payload.bounty_usd,
            "status": "PENDING_DISPATCH", "created_at": payload.timestamp
        }
        await redis_client.hset(f"pan:task:{task_id}", mapping=task_record)
        await redis_client.lpush("pan:dispatch:active_tasks", json.dumps(task_record))
        
        await redis_client.publish("pan:stream:distress_alerts", json.dumps({
            "task_id": task_id, "vin": payload.vin, "fault_code": payload.fault_code,
            "lat": payload.latitude, "lon": payload.longitude, "bounty_usd": payload.bounty_usd,
            "sla_status": "OK"
        }))
        logger.info(f"📡 Task {task_id} broadcast to Ops Hub Map.")
        return {"status": "ESCROW_LOCKED_SEEKING_AGENT", "task_id": task_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal routing failure.")

# 🟢 THE FIX: Perfecting the JSON payload for the Kotlin parser
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
                
                # We must ensure the keys match exactly what Kotlin expects
                active_missions.append({
                    "lat": float(mission.get("lat", 0.0)),
                    "lon": float(mission.get("lon", 0.0)),
                    "errorCode": str(mission.get("fault_code", "Unknown Fault")),
                    "bounty": f"${float(mission.get('bounty', 25.0)):.2f}",
                    "intersection": str(mission.get("vin", "Target Location"))
                })
        if cursor == 0:
            break
            
    # CRITICAL: We must print the payload so we can see exactly what Kotlin is rejecting
    logger.info(f"📤 Sending to Agent: {active_missions}")
    return active_missions

@router.post("/v1/v2x/mission/{task_id}/complete")
async def complete_mission(request: Request, payload: MissionCompletionPayload, task_id: str = Path(...), verified_agent_id: str = Depends(verify_agent_signature)):
    try:
        redis_client = request.app.state.redis_client
        existing_task = await redis_client.hgetall(f"pan:task:{task_id}")
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found.")

        sealed_report = ComplianceEngine.generate_optical_health_report(
            agent_id=verified_agent_id, vin=payload.vin, mission_id=task_id,
            fault_code=payload.fault_code, evidence_urls=payload.evidence_urls,
            hardware_attestation_token=payload.hardware_attestation_token
        )

        await redis_client.hset("pan:compliance:reports", task_id, json.dumps(sealed_report))
        await redis_client.hset(f"pan:task:{task_id}", "status", "COMPLETED")
        
        # We also need to clear the active mission lock so the SLA daemon stops ticking
        await redis_client.delete(f"mission:active:{task_id}")

        bounty_usd = float(existing_task.get("bounty_usd", 25.00))
        agent_cut = bounty_usd * 0.90 

        wallet_key = f"pan:agent:{verified_agent_id}:wallet"
        wallet_data = await redis_client.get(wallet_key)
        wallet = json.loads(wallet_data) if wallet_data else {"balance": 0.0, "linkedCard": None, "history": []}

        tx_record = {
            "id": f"dep_{task_id[-6:]}_{int(datetime.now(timezone.utc).timestamp())}",
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "amount": f"+${agent_cut:.2f}",
            "description": f"Smart Contract Payout: {task_id}"
        }

        wallet["balance"] += agent_cut
        wallet["history"].insert(0, tx_record)
        wallet["history"] = wallet["history"][:50] 

        await redis_client.set(wallet_key, json.dumps(wallet))
        logger.info(f"💰 [LEDGER] Escrow cleared. Deposited ${agent_cut:.2f} into {verified_agent_id}'s wallet.")
        await redis_client.publish("pan:stream:mission_cleared", json.dumps({"task_id": task_id, "status": "RESOLVED"}))

        return {"status": "EVIDENCE_ACCEPTED_AND_SEALED", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Compliance sealing failed.")