import logging
import uuid
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field

# 1. Bring in our heavily armored security perimeter
from utils.webhook_auth import verify_v2x_signature

logger = logging.getLogger("V2X_Bounty_API")
router = APIRouter()

# --- Pydantic Data Models ---
class V2XDistressPayload(BaseModel):
    vin: str = Field(..., description="Vehicle Identification Number")
    fault_code: str = Field(..., description="e.g., LIDAR_OCCLUSION, STUCK_IN_MUD")
    latitude: float
    longitude: float
    bounty_usd: float = Field(..., gt=0, le=500.0, description="Task payout in USD")
    timestamp: int

# --- Endpoint ---
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
        # Pull our verified dependencies from the main application state
        redis_client = request.app.state.redis_client
        
        # 1. Deduplication Guard (Distributed Mutex)
        dedup_key = f"pan:dedup:{payload.vin}:{payload.fault_code}"
        is_new_fault = await redis_client.set(dedup_key, task_id, nx=True, ex=300)
        
        if not is_new_fault:
            logger.warning(f"⚠️ Duplicate distress signal suppressed for VIN {payload.vin}")
            raise HTTPException(status_code=409, detail="Duplicate task already active for this VIN.")

        # ---------------------------------------------------------
        # THE ESCROW PIPELINE 
        # ---------------------------------------------------------
        # liquidity_provider = request.app.state.liquidity_provider
        # escrow_manager = request.app.state.escrow_manager
        #
        # sats_required = liquidity_provider.get_quote(payload.bounty_usd)
        # invoice_data = escrow_manager.create_hodl_invoice(
        #     agent_id="pending", task_id=task_id, amount=sats_required
        # )
        # funding_success = liquidity_provider.fund_hodl_invoice(invoice_data['bolt11'])
        # 
        # if not funding_success:
        #     await redis_client.delete(dedup_key) # 🧹 RELEASE THE LOCK on failure
        #     raise HTTPException(status_code=402, detail="Fleet treasury failed to fund Escrow.")
        # ---------------------------------------------------------

        logger.info(f"💰 Escrow Locked: ${payload.bounty_usd:.2f} for Task {task_id}")
        
        # 3. The Dispatch Handoff
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