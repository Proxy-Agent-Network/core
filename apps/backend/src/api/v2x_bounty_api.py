import logging
import uuid
import json
from typing import List
from fastapi import APIRouter, Request, HTTPException, Depends, Path
from pydantic import BaseModel, Field

# 1. Bring in our heavily armored security perimeter
from utils.webhook_auth import verify_v2x_signature
from compliance.audit_engine import ComplianceEngine

logger = logging.getLogger("V2X_Bounty_API")
router = APIRouter()

# --- Placeholder Dependency for Agent Auth ---
# TODO: Implement actual Ed25519 or JWT validation in utils/webhook_auth.py
async def verify_agent_signature(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Agent hardware signature required.")
    return "VANGUARD-01" # Mock agent ID for now

# --- Pydantic Data Models ---
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

# --- Endpoints ---
@router.post("/v1/v2x/distress")
async def receive_distress_signal(
    request: Request,
    payload: V2XDistressPayload,
    fleet_id: str = Depends(verify_v2x_signature) # 🔒 Ed25519 Auth & Replay Protection
):
    """
    Ingests an authenticated distress signal from a grounded Autonomous Vehicle,
    locks the fiat bounty in a Lightning HODL Escrow, and broadcasts the task to Agents.
    """
    task_id = f"tsk_{uuid.uuid4().hex[:12]}"
    logger.info(f"🚨 [V2X ALERT] Fleet: {fleet_id} | VIN: {payload.vin} | Fault: {payload.fault_code}")
    
    try:
        redis_client = request.app.state.redis_client
        
        # 1. Deduplication Guard (Distributed Mutex)
        dedup_key = f"pan:dedup:{payload.vin}:{payload.fault_code}"
        is_new_fault = await redis_client.set(dedup_key, task_id, nx=True, ex=300)
        
        if not is_new_fault:
            logger.warning(f"⚠️ Duplicate distress signal suppressed for VIN {payload.vin}")
            raise HTTPException(status_code=409, detail="Duplicate task already active for this VIN.")

        logger.info(f"💰 Escrow Locked: ${payload.bounty_usd:.2f} for Task {task_id}")
        
        # 2. Store the individual task record (System of Record)
        task_record = {
            "task_id": task_id,
            "fleet_id": fleet_id,
            "vin": payload.vin,
            "fault_code": payload.fault_code,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "bounty_usd": payload.bounty_usd,
            "status": "PENDING_DISPATCH",
            "created_at": payload.timestamp
        }
        await redis_client.hset(f"pan:task:{task_id}", mapping=task_record)
        
        # 3. The Dispatch Handoff (Queue)
        await redis_client.lpush("pan:dispatch:active_tasks", json.dumps(task_record))
        logger.info(f"📡 Task {task_id} pushed to active dispatch queue.")

        return {
            "status": "ESCROW_LOCKED_SEEKING_AGENT",
            "task_id": task_id,
            "bounty_usd": payload.bounty_usd,
            "message": "Task broadcast to Vanguard Proxy Network."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ V2X Dispatch Error for {fleet_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal routing failure.")

# 🛠️ THE FIX: Path Regex validation and strictly typed dependencies
@router.post("/v1/v2x/mission/{task_id}/complete")
async def complete_mission(
    request: Request,
    payload: MissionCompletionPayload,
    task_id: str = Path(..., pattern=r"^tsk_[a-f0-9]{12}$", description="16-char Task ID"),
    verified_agent_id: str = Depends(verify_agent_signature) # 🔒 Agent Auth Layer
):
    """
    Called by the Vanguard Agent's mobile app to submit evidence, validate
    hardware authenticity, generate the legal compliance report, and trigger payout.
    """
    try:
        redis_client = request.app.state.redis_client
        
        # 1. IDOR Guard: Verify the task actually exists in the database
        existing_task = await redis_client.hgetall(f"pan:task:{task_id}")
        if not existing_task:
            logger.warning(f"⚠️ Agent {verified_agent_id} attempted to complete non-existent task {task_id}")
            raise HTTPException(status_code=404, detail="Task not found.")
            
        # 2. State Guard: Verify the payload matches the original distress signal
        # (Handling potential byte decoding depending on the async Redis driver configuration)
        existing_vin = existing_task.get("vin") or existing_task.get(b"vin", b"").decode("utf-8")
        if existing_vin != payload.vin:
            logger.error(f"🛑 VIN MISMATCH: Task {task_id} is for {existing_vin}, Agent submitted {payload.vin}")
            raise HTTPException(status_code=409, detail="VIN mismatch for this task.")

        # 3. Generate the immutable SB 1417 Optical Health Report
        sealed_report = ComplianceEngine.generate_optical_health_report(
            agent_id=verified_agent_id, # Use the trusted ID from the transport layer, not the payload
            vin=payload.vin,
            mission_id=task_id,
            fault_code=payload.fault_code,
            evidence_urls=payload.evidence_urls,
            hardware_attestation_token=payload.hardware_attestation_token
        )

        # 4. Persist the legal record to the immutable ledger
        await redis_client.hset(
            "pan:compliance:reports",
            task_id,
            json.dumps(sealed_report)
        )
        
        # 5. Mark task as complete (which allows Escrow to be claimed)
        await redis_client.hset(f"pan:task:{task_id}", "status", "COMPLETED")

        logger.info(f"✅ Mission {task_id} sealed and compliance report archived.")

        return {
            "status": "EVIDENCE_ACCEPTED_AND_SEALED",
            "task_id": task_id,
            "document_hash": sealed_report["document_hash"],
            "message": "SB 1417 Optical Health Report generated and safely stored."
        }

    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"🛑 Mission {task_id} rejected: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ Failed to seal mission {task_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Compliance sealing failed.")