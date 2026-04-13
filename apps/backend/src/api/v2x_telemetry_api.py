import time
import json
import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel, Field

from utils.webhook_auth import verify_v2x_signature

logger = logging.getLogger("V2X_Telemetry_API")
router = APIRouter()

# --- DATA MODELS ---

class V2XTelemetryPayload(BaseModel):
    vin: str
    latitude: float
    longitude: float
    speed_mph: float
    heading_degrees: float
    brake_active: bool
    timestamp: int

class FreezeRequestPayload(BaseModel):
    incident_id: str


# --- SHARED CORE LOGIC ---

async def freeze_telemetry_buffer(redis_client, vin: str, incident_id: str, fleet_id: str) -> dict:
    """
    Locks the rolling 60-second telemetry buffer into a permanent compliance record.
    Uses individual keys with a 48-hour TTL to prevent infinite memory growth.
    """
    buffer_key = f"pan:telemetry:buffer:{vin}"
    
    try:
        # 1. Extract the entire rolling buffer
        raw_data = await redis_client.zrange(buffer_key, 0, -1)

        if not raw_data:
            logger.warning(f"⚠️ [COMPLIANCE] No telemetry buffer found to freeze for {vin}")
            return {"status": "empty", "message": "No telemetry data in buffer."}

        # 2. Parse and format the timeline
        timeline = [
            json.loads(record.decode("utf-8") if isinstance(record, bytes) else record) 
            for record in raw_data
        ]

        frozen_payload = {
            "incident_id": incident_id,
            "vin": vin,
            "fleet_id": fleet_id,
            "frozen_at": int(time.time()),
            "telemetry_timeline": timeline
        }

        # 3. Store the frozen record permanently in an individual Redis key with a 48-hour TTL
        # 🟢 THE FIX: Replaced infinite-growth hash with a cleanly expiring individual key
        frozen_key = f"pan:compliance:frozen:{incident_id}"
        await redis_client.setex(frozen_key, 172800, json.dumps(frozen_payload))

        logger.info(f"🧊 [COMPLIANCE] Froze {len(timeline)} seconds of pre-incident telemetry for {vin} (Incident: {incident_id}).")

        return {"status": "success", "records_frozen": len(timeline)}

    except Exception as e:
        logger.error(f"❌ [COMPLIANCE] Failed to freeze telemetry for {vin}: {e}")
        raise


# --- ENDPOINTS ---

@router.post("/v1/v2x/telemetry/stream")
async def ingest_v2x_telemetry(
    payload: V2XTelemetryPayload,
    request: Request,
    fleet_id: str = Depends(verify_v2x_signature)
):
    """
    High-throughput 1Hz ingest for AV telemetry.
    Maintains a rolling 60-second buffer in memory.
    """
    redis_client = request.app.state.redis_client
    now = int(time.time())

    # Protect against heavily skewed AV clocks
    if abs(now - payload.timestamp) > 5:
        logger.warning(f"⚠️ [TELEMETRY] Skewed timestamp from {payload.vin}. Adjusting to server time.")
        payload.timestamp = now

    buffer_key = f"pan:telemetry:buffer:{payload.vin}"
    
    # 🟢 THE FIX: Safely support both Pydantic v1 and v2
    payload_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    payload_json = json.dumps(payload_dict)

    try:
        # Atomic pipeline for O(log(N)) ingestion and cleanup
        async with redis_client.pipeline(transaction=False) as pipe:
            pipe.zadd(buffer_key, {payload_json: payload.timestamp})
            pipe.zremrangebyscore(buffer_key, "-inf", now - 60)
            pipe.expire(buffer_key, 120)
            await pipe.execute()

        return {"status": "ok", "received": True}
        
    except Exception as e:
        logger.error(f"❌ [TELEMETRY] Failed to ingest for {payload.vin}: {e}")
        raise HTTPException(status_code=500, detail="Internal telemetry error")


@router.post("/v1/v2x/telemetry/{vin}/freeze")
async def trigger_manual_freeze(
    vin: str,
    payload: FreezeRequestPayload,
    request: Request,
    fleet_id: str = Depends(verify_v2x_signature)
):
    """
    Manual override endpoint to lock the telemetry buffer.
    """
    redis_client = request.app.state.redis_client
    try:
        result = await freeze_telemetry_buffer(redis_client, vin, payload.incident_id, fleet_id)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal compliance error")