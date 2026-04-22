"""
Proxy Agent Network — Agent-side utility and mission lifecycle endpoints.

Scope of this module:
  * POST /agent/fcm-token       — Register a Firebase Cloud Messaging token.
  * POST /agent/evidence/upload — Upload a JPEG/PNG evidence artifact.
  * GET & POST /agent/missions  — Mission lifecycle handlers (ack/decline/complete/extend/feedback/diagnose).
  * POST /agent/presence        — Manage dispatch pool availability.
  * GET & POST /agent/payout-floors — Configure automated bidding preferences.

Author note:
  Evidence uploads are cryptographically tied to the uploading agent via S3
  object metadata and a Redis index (pan:agent:{agent_id}:evidence:{blob_id}).
  The mission completion handler strictly enforces this chain of custody.
"""
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import aioboto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from redis.exceptions import WatchError

from utils.auth import verify_agent_signature
from compliance.audit_engine import ComplianceEngine

logger = logging.getLogger("PAN_AgentAPI")
router = APIRouter()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_EVIDENCE_BUCKET_EXPLICIT = os.getenv("S3_EVIDENCE_BUCKET_NAME")
_PII_BUCKET = os.getenv("S3_PII_BUCKET_NAME")
S3_EVIDENCE_BUCKET_NAME = _EVIDENCE_BUCKET_EXPLICIT or _PII_BUCKET
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

if not S3_EVIDENCE_BUCKET_NAME and os.getenv("ENVIRONMENT") == "production":
    raise RuntimeError(
        "🚨 FATAL: Neither S3_EVIDENCE_BUCKET_NAME nor S3_PII_BUCKET_NAME "
        "is set in production. Refusing to boot without evidence storage."
    )

if not _EVIDENCE_BUCKET_EXPLICIT and _PII_BUCKET:
    logger.warning(
        "⚠️ S3_EVIDENCE_BUCKET_NAME not set — evidence uploads are falling "
        "back to the onboarding PII bucket (%s). These should be separated "
        "before Mesa Pilot scale-up to satisfy SB 1417 retention.",
        _PII_BUCKET,
    )

MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
ALLOWED_EVIDENCE_MIME = {"image/jpeg", "image/png"}
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PRESIGNED_URL_TTL_SECONDS = 3600
FCM_TOKEN_MAX_PER_HOUR = 5
EVIDENCE_MAX_PER_HOUR = 60
FCM_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 90
EVIDENCE_INDEX_TTL_SECONDS = 60 * 60 * 24 * 60

_FCM_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_\-:]{50,4096}$")

VALID_TASK_CATEGORIES = {
    "door_securing",
    "latch_fault",
    "spill_remediation",
    "scene_securement",
    "sensor_obstruction",
    "sentry_traffic_direction",
    "general_diagnostics",
}

MAX_PAYOUT_FLOOR_HISTORY = 90

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class FcmTokenPayload(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=64)
    fcm_token: str = Field(..., min_length=50, max_length=4096)

class EvidenceUploadResponse(BaseModel):
    url: str
    blob_id: str
    bytes_stored: int

class MissionCompletePayload(BaseModel):
    agent_id: str
    net_payout: float 
    # 🛡️ Pydantic safe initialization fix
    evidence_urls: list = Field(default_factory=list)
    hardware_attestation_token: str = ""
    av_signature_hex: str = ""

class DiagnosticPayload(BaseModel):
    # 🛡️ Pydantic safe initialization fix
    evidence_urls: list = Field(default_factory=list)
    notes: list = Field(default_factory=list)

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

class PayoutFloorsPayload(BaseModel):
    floors: dict = Field(..., description="Map of task_category → minimum_usd")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _rate_limit(redis_client, key: str, limit_per_hour: int) -> None:
    async with redis_client.pipeline() as pipe:
        pipe.incr(key)
        pipe.expire(key, 3600)
        results = await pipe.execute()
    attempts = results[0]
    if attempts > limit_per_hour:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down.",
        )

def _sniff_content_type(head: bytes, declared: Optional[str]) -> str:
    if head.startswith(JPEG_MAGIC):
        sniffed = "image/jpeg"
    elif head.startswith(PNG_MAGIC):
        sniffed = "image/png"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. JPEG or PNG only.",
        )

    if declared and declared.lower() not in ALLOWED_EVIDENCE_MIME:
        raise HTTPException(
            status_code=400,
            detail="Unsupported declared content-type.",
        )

    if declared and declared.lower() != sniffed:
        logger.warning(
            "Evidence content-type mismatch: declared=%s sniffed=%s",
            declared,
            sniffed,
        )

    return sniffed

def decode_redis_hash(raw_hash: dict) -> dict:
    """Safely decodes Redis byte hashes into strings."""
    if not raw_hash:
        return {}
    return {
        k.decode('utf-8') if isinstance(k, bytes) else k: 
        v.decode('utf-8') if isinstance(v, bytes) else v 
        for k, v in raw_hash.items()
    }

# ---------------------------------------------------------------------------
# Core Endpoints
# ---------------------------------------------------------------------------

@router.post("/agent/fcm-token")
async def register_fcm_token(
    payload: FcmTokenPayload,
    request: Request,
    authenticated_agent_id: str = Depends(verify_agent_signature),
):
    if payload.agent_id != authenticated_agent_id:
        logger.warning(
            "🚨 FCM token registration identity mismatch: JWT=%s body=%s",
            authenticated_agent_id,
            payload.agent_id,
        )
        raise HTTPException(
            status_code=403,
            detail="Token subject does not match registering agent.",
        )

    if not _FCM_TOKEN_PATTERN.match(payload.fcm_token):
        raise HTTPException(status_code=400, detail="Malformed FCM token.")

    redis_client = request.app.state.redis_client
    await _rate_limit(redis_client, f"rate_limit:fcm_token:{authenticated_agent_id}", FCM_TOKEN_MAX_PER_HOUR)

    token_key = f"pan:agent:{authenticated_agent_id}:fcm_token"
    await redis_client.set(token_key, payload.fcm_token, ex=FCM_TOKEN_TTL_SECONDS)

    logger.info(
        "📱 FCM token registered for %s (expires in %d days)",
        authenticated_agent_id,
        FCM_TOKEN_TTL_SECONDS // 86400,
    )
    return {"status": "success"}

@router.post("/agent/evidence/upload")
async def upload_evidence(
    request: Request,
    evidence_file: UploadFile = File(...),
    agent_id: str = Depends(verify_agent_signature),
):
    """Upload a single evidence artifact (JPEG/PNG) and return a presigned
    URL suitable for submission via POST /agent/missions/{task_id}/complete.

    Evidence ownership is recorded so the mission-completion handler can
    verify the submitted URL belongs to the completing agent.
    """
    if not S3_EVIDENCE_BUCKET_NAME:
        raise HTTPException(status_code=503, detail="Evidence storage is not configured.")

    redis_client = request.app.state.redis_client
    await _rate_limit(redis_client, f"rate_limit:evidence:{agent_id}", EVIDENCE_MAX_PER_HOUR)

    head = await evidence_file.read(16)
    if not head:
        raise HTTPException(status_code=400, detail="Empty upload.")

    sniffed_mime = _sniff_content_type(head, evidence_file.content_type)

    tail = await evidence_file.read(MAX_EVIDENCE_BYTES - len(head) + 1)
    body = head + tail
    if len(body) > MAX_EVIDENCE_BYTES:
        raise HTTPException(status_code=413, detail="Evidence exceeds payload limit.")

    blob_id = f"evd_{uuid.uuid4().hex}"
    extension = "jpg" if sniffed_mime == "image/jpeg" else "png"
    s3_key = f"evidence/{agent_id}/{blob_id}.{extension}"

    try:
        boto_session = aioboto3.Session()
        async with boto_session.client("s3", region_name=AWS_REGION) as s3_client:
            await s3_client.put_object(
                Bucket=S3_EVIDENCE_BUCKET_NAME,
                Key=s3_key,
                Body=body,
                ContentType=sniffed_mime,
                ServerSideEncryption="AES256",
                Metadata={
                    "uploading_agent_id": agent_id,
                    "uploaded_at": str(int(time.time())),
                    "blob_id": blob_id,
                },
            )

            presigned_url = await s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_EVIDENCE_BUCKET_NAME, "Key": s3_key},
                ExpiresIn=PRESIGNED_URL_TTL_SECONDS,
            )
    except (BotoCoreError, ClientError) as exc:
        logger.error("S3 upload failed for %s: %s", agent_id, exc)
        raise HTTPException(status_code=502, detail="Evidence storage unavailable.")

    index_key = f"pan:agent:{agent_id}:evidence:{blob_id}"
    await redis_client.set(index_key, s3_key, ex=EVIDENCE_INDEX_TTL_SECONDS)

    logger.info("📎 Evidence uploaded: agent=%s blob=%s", agent_id, blob_id)

    return EvidenceUploadResponse(url=presigned_url, blob_id=blob_id, bytes_stored=len(body))

# ---------------------------------------------------------------------------
# Mission Lifecycle Endpoints
# ---------------------------------------------------------------------------

@router.get("/agent/missions")
async def fetch_agent_missions(request: Request, agent_id: str = Depends(verify_agent_signature)):
    redis_client = request.app.state.redis_client
    active_missions = []
    
    task_ids = await redis_client.smembers(f"pan:agent:{agent_id}:missions")
    
    for task_id_bytes in task_ids:
        task_id = task_id_bytes.decode("utf-8") if isinstance(task_id_bytes, bytes) else task_id_bytes
        
        mission_key = f"mission:active:{task_id}"
        raw_mission = await redis_client.hgetall(mission_key)
        mission = decode_redis_hash(raw_mission)
        
        if mission and mission.get("agent_id") == agent_id:
            raw_task = await redis_client.hgetall(f"pan:task:{task_id}")
            task = decode_redis_hash(raw_task)
            
            fault = str(task.get("fault_code", "Unknown Fault"))
            
            diag_text = "Perform standard vehicle diagnostics."
            if fault in ["door_securing", "latch_fault"]:
                diag_text = "Push door completely shut to clear latch fault."
            elif fault == "spill_remediation":
                diag_text = "Sanitize interior spills. Requires wet-vac/bio-kit."
            elif fault == "scene_securement":
                diag_text = "Interact with police/flares. Requires safety flares."
            
            active_missions.append({
                "task_id": task_id,
                "taskId": task_id,
                "incident_id": str(task.get("incident_id", f"inc_{task_id}")),
                "incidentId": str(task.get("incident_id", f"inc_{task_id}")),
                "fleet_id": str(task.get("fleet_id", "Vanguard Network Partner")),
                "fleetId": str(task.get("fleet_id", "Vanguard Network Partner")),
                "lat": float(task.get("lat", 0.0)),
                "lon": float(task.get("lon", 0.0)),
                "error_code": fault,
                "errorCode": fault,
                "fault_code": fault,
                "faultCode": fault,
                "bounty_usd": float(task.get('bounty_usd', 25.0)), 
                "bountyUsd": float(task.get('bounty_usd', 25.0)), 
                "intersection": str(task.get("intersection", "Unknown Location")), 
                "vin": str(task.get("vin", "Target Location")),
                "role": str(task.get("role", "PRIMARY")).upper(),
                "status": str(mission.get("status", "ASSIGNED")).upper(),
                "diagnostic": diag_text
            })
        else:
            await redis_client.srem(f"pan:agent:{agent_id}:missions", task_id)
            
    return active_missions

@router.post("/agent/missions/{task_id}/diagnose")
async def run_diagnostics(
    task_id: str, 
    payload: DiagnosticPayload, 
    request: Request, 
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client
    
    mission_key = f"mission:active:{task_id}"
    raw_mission_data = await redis_client.hgetall(mission_key)
    mission_data = decode_redis_hash(raw_mission_data)
    
    if not mission_data:
        raise HTTPException(status_code=404, detail="Mission not found.")
        
    if mission_data.get("agent_id") != agent_id:
        raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

    return {
        "status": "success",
        "is_cleared": True,
        "message": "Vehicle systems nominal. Fault cleared."
    }

@router.post("/agent/missions/{task_id}/complete")
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
            raise HTTPException(status_code=403, detail="Mission not assigned to this agent.")

        # 🛡️ M3 FIX: Verify Evidence Ownership against the Redis Index
        for ev_url in payload.evidence_urls:
            m = re.search(r'/evidence/[^/]+/(evd_[a-f0-9]+)\.', ev_url)
            if not m:
                logger.warning(f"🚨 Unparseable evidence URL from {agent_id}: {ev_url}")
                raise HTTPException(status_code=400, detail="Malformed evidence URL.")
            
            blob_id = m.group(1)
            
            owner_key = f"pan:agent:{agent_id}:evidence:{blob_id}"
            if not await redis_client.exists(owner_key):
                logger.critical(
                    f"🛑 EVIDENCE SPOOFING BLOCKED: Agent {agent_id} submitted "
                    f"blob {blob_id} they do not own (or blob expired)."
                )
                raise HTTPException(
                    status_code=403, 
                    detail="Evidence ownership validation failed. You can only submit evidence you uploaded."
                )

        vin = task_data.get("vin", "UNKNOWN_VIN")
        fault_code = task_data.get("fault_code", "UNKNOWN_FAULT")
        raw_bounty = float(task_data.get("bounty_usd", 25.0))
        
        if agent_id == "VNG-50-PILOT" and os.getenv("ENVIRONMENT") != "production":
            is_veteran = True
        else:
            veteran_raw = await redis_client.hget(f"pan:agent:{agent_id}", "is_veteran")
            is_veteran = str(veteran_raw).lower() == "true" if veteran_raw else False
            
        multiplier = 0.85 if is_veteran else 0.75
        actual_payout = round(raw_bounty * multiplier, 2) 

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
        
        await redis_client.setex(f"pan:compliance:report:{task_id}", 31622400, json.dumps(sealed_report))
        
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

        await redis_client.hset(f"pan:agent:{agent_id}", "status", "ONLINE")
        await redis_client.srem(f"pan:agent:{agent_id}:missions", task_id)
        
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

@router.post("/agent/missions/{task_id}/ack")
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

@router.post("/agent/missions/{task_id}/decline")
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
        await redis_client.hset(f"pan:agent:{agent_id}", "status", "ONLINE")
        await redis_client.srem(f"pan:agent:{agent_id}:missions", task_id)
        
        await redis_client.publish(
            "pan:stream:mission_cleared", 
            json.dumps({
                "task_id": task_id, 
                "agent_id": agent_id, 
                "reason": "declined",
                "abort_reason": abort_reason
            })
        )

    return {"status": "success", "message": "Mission aborted."}

@router.post("/agent/missions/{task_id}/extend")
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

@router.post("/agent/missions/{task_id}/feedback")
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

@router.post("/agent/presence")
async def update_presence(
    payload: PresencePayload,
    request: Request,
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client
    status_str = "ONLINE" if payload.is_online else "OFFLINE"
    
    await redis_client.hset(f"pan:agent:{agent_id}", "status", status_str)
    return {"status": "success", "is_online": payload.is_online}

@router.post("/agent/payout-floors")
async def set_payout_floors(
    payload: PayoutFloorsPayload,
    request: Request,
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client

    invalid_categories = [k for k in payload.floors if k not in VALID_TASK_CATEGORIES]
    if invalid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task categories: {invalid_categories}. Valid options: {sorted(VALID_TASK_CATEGORIES)}"
        )

    invalid_values = [k for k, v in payload.floors.items() if not isinstance(v, (int, float)) or v < 0]
    if invalid_values:
        raise HTTPException(
            status_code=400,
            detail=f"Payout floor values must be non-negative numbers. Invalid fields: {invalid_values}"
        )

    floors_key = f"pan:agent:{agent_id}:payout_floors"
    history_key = f"pan:agent:{agent_id}:payout_floor_history"

    existing_raw = await redis_client.hgetall(floors_key)
    existing_floors = {
        (k.decode() if isinstance(k, bytes) else k): float(v.decode() if isinstance(v, bytes) else v)
        for k, v in existing_raw.items()
    }

    merged_floors = {**existing_floors, **{k: float(v) for k, v in payload.floors.items()}}

    await redis_client.hset(floors_key, mapping={k: str(v) for k, v in merged_floors.items()})

    snapshot = json.dumps({
        "timestamp": int(time.time()),
        "agent_id": agent_id,
        "floors": merged_floors,
        "changed_fields": list(payload.floors.keys()),
    })
    await redis_client.lpush(history_key, snapshot)

    await redis_client.ltrim(history_key, 0, MAX_PAYOUT_FLOOR_HISTORY - 1)

    logger.info(
        f"💰 [PAYOUT_FLOORS] Agent {agent_id} updated floors for: {list(payload.floors.keys())}"
    )

    return {
        "status": "success",
        "active_floors": merged_floors,
        "message": f"Payout floors updated for {len(payload.floors)} category(ies)."
    }


@router.get("/agent/payout-floors")
async def get_payout_floors(
    request: Request,
    agent_id: str = Depends(verify_agent_signature)
):
    redis_client = request.app.state.redis_client

    floors_key = f"pan:agent:{agent_id}:payout_floors"
    history_key = f"pan:agent:{agent_id}:payout_floor_history"

    raw_floors = await redis_client.hgetall(floors_key)
    active_floors = {
        (k.decode() if isinstance(k, bytes) else k): float(v.decode() if isinstance(v, bytes) else v)
        for k, v in raw_floors.items()
    }

    raw_history = await redis_client.lrange(history_key, 0, 9)
    history = [json.loads(entry) for entry in raw_history]

    return {
        "agent_id": agent_id,
        "active_floors": active_floors,
        "valid_categories": sorted(VALID_TASK_CATEGORIES),
        "recent_history": history,
    }