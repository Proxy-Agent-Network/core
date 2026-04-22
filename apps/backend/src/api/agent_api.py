"""
Proxy Agent Network — Agent-side utility endpoints.

Scope of this module:
  * POST /agent/fcm-token       — Register a Firebase Cloud Messaging token for
                                  push-notification delivery to the Vanguard
                                  mobile app.
  * POST /agent/evidence/upload — Upload a single JPEG/PNG evidence artifact
                                  to S3 and return a presigned URL the client
                                  can pass back to
                                  POST /agent/missions/{task_id}/complete.

Deliberately NOT in this module:
  * Mission lifecycle endpoints (ack/decline/complete/extend/feedback/diagnose)
    — those live in api/v2x_bounty_api.py.
  * Agent presence/status          — api/v2x_bounty_api.py and
                                      api/telemetry_socket.py.
  * Wallet                         — api/wallet_api.py.
  * Onboarding / key registration  — api/onboarding_api.py.

Author note:
  Evidence uploads are cryptographically tied to the uploading agent via S3
  object metadata and a Redis index (pan:agent:{agent_id}:evidence:{blob_id}).
  Mission-completion handlers SHOULD verify each submitted evidence URL
  belongs to the completing agent — see TODO marker in
  v2x_bounty_api.py::complete_mission.
"""
import os
import re
import time
import uuid
import logging
from typing import Optional

import aioboto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field

from utils.auth import verify_agent_signature

logger = logging.getLogger("PAN_AgentAPI")
router = APIRouter()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Evidence uploads go to their own bucket when configured. If
# S3_EVIDENCE_BUCKET_NAME is absent we fall back to the onboarding PII bucket
# so the module is still functional in current environments — but we log
# loudly because SB 1417 evidence has different retention requirements from
# onboarding PII and the two should eventually be separated.
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

# Upload bounds. JPEG/PNG only — matches onboarding's allow-list and the
# Android client's Bitmap.CompressFormat.JPEG output. 10MB permits ~8MP
# photos at agent-chosen quality; onboarding's 5MB is lower because those
# documents are scanned paperwork.
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024
ALLOWED_EVIDENCE_MIME = {"image/jpeg", "image/png"}

# Magic-byte prefixes — defense against a client that lies about
# Content-Type. This is not a substitute for AV scanning on the receiving
# side, but it catches the most trivial mismatches.
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# Presigned GET URL lifetime — Ops Hub needs to fetch the blob for review;
# one hour is enough for interactive review without leaving the URL
# indefinitely valid if it leaks from a log.
PRESIGNED_URL_TTL_SECONDS = 3600

# Rate limiting. FCM tokens rotate rarely; evidence photos are per-mission
# and may be numerous. These are conservative starting points — tune once
# real Mesa Pilot data is available.
FCM_TOKEN_MAX_PER_HOUR = 5
EVIDENCE_MAX_PER_HOUR = 60

# FCM token TTL. Firebase will reject stale tokens on its own, but a TTL
# prevents long-dead records accumulating in Redis.
FCM_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 90

# Evidence index TTL — evidence blobs in S3 can live longer than the Redis
# index used for ownership checks. 60 days comfortably covers any open
# mission's completion window, while letting Redis keys expire eventually.
EVIDENCE_INDEX_TTL_SECONDS = 60 * 60 * 24 * 60

# FCM tokens are long opaque Firebase strings. We validate format
# superficially — Firebase will do the real validation at send time.
_FCM_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_\-:]{50,4096}$")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class FcmTokenPayload(BaseModel):
    """Matches the Android client's FcmTokenPayload wire format exactly."""

    agent_id: str = Field(..., min_length=1, max_length=64)
    fcm_token: str = Field(..., min_length=50, max_length=4096)


class EvidenceUploadResponse(BaseModel):
    url: str
    blob_id: str
    bytes_stored: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _rate_limit(redis_client, key: str, limit_per_hour: int) -> None:
    """Sliding-window-ish bucket. Shared helper kept local to this module so
    it doesn't leak into unrelated routers."""
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
    """Return the effective content-type after a magic-byte sniff.
    Raises 400 on mismatch — the client cannot override the byte contents."""
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


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/agent/fcm-token")
async def register_fcm_token(
    payload: FcmTokenPayload,
    request: Request,
    authenticated_agent_id: str = Depends(verify_agent_signature),
):
    """Register a Firebase Cloud Messaging token for the authenticated agent.

    The hardware-signed JWT is the authoritative agent identifier — the
    agent_id in the body must match. This prevents an agent with a valid
    token from registering a push channel for a different agent.
    """
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
        raise HTTPException(
            status_code=400,
            detail="Malformed FCM token.",
        )

    redis_client = request.app.state.redis_client
    await _rate_limit(
        redis_client,
        f"rate_limit:fcm_token:{authenticated_agent_id}",
        FCM_TOKEN_MAX_PER_HOUR,
    )

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
        # Only reachable in non-production when neither bucket env var is set.
        logger.error("Evidence upload attempted with no S3 bucket configured.")
        raise HTTPException(
            status_code=503,
            detail="Evidence storage is not configured on this deployment.",
        )

    redis_client = request.app.state.redis_client
    await _rate_limit(
        redis_client,
        f"rate_limit:evidence:{agent_id}",
        EVIDENCE_MAX_PER_HOUR,
    )

    # Stream the first 16 bytes to sniff, then read the rest. `UploadFile`'s
    # SpooledTemporaryFile keeps this cheap for reasonable sizes.
    head = await evidence_file.read(16)
    if not head:
        raise HTTPException(status_code=400, detail="Empty upload.")

    sniffed_mime = _sniff_content_type(head, evidence_file.content_type)

    tail = await evidence_file.read(MAX_EVIDENCE_BYTES - len(head) + 1)
    body = head + tail
    if len(body) > MAX_EVIDENCE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Evidence exceeds {MAX_EVIDENCE_BYTES // (1024 * 1024)}MB limit.",
        )

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
        logger.error("S3 evidence upload failed for %s: %s", agent_id, exc)
        raise HTTPException(
            status_code=502,
            detail="Evidence storage unavailable. Please retry.",
        )

    # Record ownership — the mission-completion handler should consult this
    # when verifying submitted evidence_urls.
    index_key = f"pan:agent:{agent_id}:evidence:{blob_id}"
    await redis_client.set(
        index_key,
        s3_key,
        ex=EVIDENCE_INDEX_TTL_SECONDS,
    )

    logger.info(
        "📎 Evidence uploaded: agent=%s blob=%s bytes=%d mime=%s",
        agent_id,
        blob_id,
        len(body),
        sniffed_mime,
    )

    return EvidenceUploadResponse(
        url=presigned_url,
        blob_id=blob_id,
        bytes_stored=len(body),
    )
