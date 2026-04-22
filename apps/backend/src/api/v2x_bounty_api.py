import os
import logging
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel

from utils.webhook_auth import verify_v2x_signature
from utils.auth import verify_agent_signature
from api.v2x_telemetry_api import freeze_telemetry_buffer

logger = logging.getLogger("V2X_Bounty_API")
router = APIRouter()

# --- DATA MODELS ---

class DistressPayload(BaseModel):
    vin: str
    fault_code: str
    latitude: float
    longitude: float
    bounty_usd: float = 25.0
    osm_color: Literal["RED", "PURPLE", "YELLOW", "ORANGE", "GREEN", "BLUE", "WHITE"] = "GREEN"
    request_secondary: bool = False
    secondary_start_bid_usd: float = 14.0   
    secondary_max_bid_usd: float = 24.0     
    secondary_escalation_usd_per_min: float = 2.0
    intersection: str = "Unknown Location"
    is_near_miss: bool = False  

# --- CORE LOGIC ---

async def process_core_distress(payload: DistressPayload, request: Request, fleet_id: str):
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
            "intersection": payload.intersection,
            "is_near_miss": str(payload.is_near_miss).lower(),
        }
        
        await redis_client.hset(f"pan:task:{task_id}", mapping=task_record)
        await redis_client.rpush("pan:dispatch:active_tasks", task_id)

        if payload.is_near_miss:
            now_utc = datetime.now(timezone.utc)
            quarter = (now_utc.month - 1) // 3 + 1
            index_key = f"pan:compliance:near_misses:{now_utc.year}_Q{quarter}"
            
            await redis_client.sadd(index_key, task_id)
            await redis_client.expire(index_key, 34560000)
            logger.info(f"⚠️ [COMPLIANCE] Near-miss logged for {payload.vin} in {now_utc.year}_Q{quarter}")

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
                "role": "SENTRY",
                "required_tier": 1,     
                "incident_id": incident_id,
                "intersection": payload.intersection,
                "is_near_miss": str(payload.is_near_miss).lower(),
            }
            await redis_client.hset(f"pan:task:{sentry_task_id}", mapping=sentry_record)
            await redis_client.rpush("pan:dispatch:active_tasks", sentry_task_id)

        try:
            await freeze_telemetry_buffer(
                redis_client=redis_client,
                vin=payload.vin,
                incident_id=incident_id,
                fleet_id=fleet_id
            )
        except Exception as e:
            logger.warning(f"⚠️ [COMPLIANCE] Non-fatal error freezing telemetry for {payload.vin}: {e}")

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
            "intersection": payload.intersection,
        }))
        
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

# --- ENDPOINTS ---

@router.post("/v2x/distress")
async def receive_distress_signal(
    payload: DistressPayload, 
    request: Request,
    fleet_id: str = Depends(verify_v2x_signature)  
):
    return await process_core_distress(payload, request, fleet_id)

@router.post("/dev/inject-distress")
async def inject_dev_distress(
    payload: DistressPayload, 
    request: Request,
    agent_id: str = Depends(verify_agent_signature)  
):
    # 🛡️ PHASE 3 FIX: Prevent production spoofing of distress signals
    if os.getenv("ENVIRONMENT") == "production":
        logger.error(f"🚨 Security Alert: Agent {agent_id} attempted to hit dev distress endpoint in production!")
        raise HTTPException(status_code=403, detail="Dev endpoints disabled in production.")
        
    return await process_core_distress(payload, request, "DEV-FLEET-01")