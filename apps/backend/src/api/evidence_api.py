import os
import uuid
import logging
import aioboto3
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

# Assumes your standard Vanguard agent auth middleware
from utils.auth import verify_agent_signature

logger = logging.getLogger("PAN_Evidence_API")
router = APIRouter()

# 1. AWS S3 CONFIGURATION
S3_BUCKET_NAME = os.getenv("S3_PII_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

MAX_EVIDENCE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

@router.post("/v1/agent/evidence/upload")
async def upload_evidence(
    evidence_file: UploadFile = File(...),
    agent_id: str = Depends(verify_agent_signature)
):
    """
    Securely ingests redacted mission evidence directly to AWS S3.
    Applies SB 1417 compliant 12-month Object Lock (WORM storage).
    Requires valid agent JWT signature.
    """
    if not S3_BUCKET_NAME:
        logger.critical("🚨 Evidence upload failed: S3_PII_BUCKET_NAME is not configured.")
        raise HTTPException(status_code=500, detail="Server misconfiguration: Secure storage unavailable.")

    # 1. Read and validate the image bytes
    try:
        contents = await evidence_file.read()
    except Exception as e:
        logger.error(f"Failed to read evidence upload from {agent_id}: {e}")
        raise HTTPException(status_code=400, detail="Corrupted file payload.")
        
    if len(contents) > MAX_EVIDENCE_SIZE_BYTES:
        logger.warning(f"Agent {agent_id} attempted to upload evidence exceeding 10MB.")
        raise HTTPException(status_code=413, detail="Evidence file exceeds maximum allowed size (10MB).")

    # 2. Generate a secure, opaque S3 Key
    file_ext = ".jpg"
    if evidence_file.content_type == "image/png":
        file_ext = ".png"
        
    s3_key = f"v1/evidence/{agent_id}/evd_{uuid.uuid4().hex}{file_ext}"

    # 3. Stream to AWS S3 with WORM Compliance Lock
    # SB 1417 §28-9710 dictates 12-month tamper-resistant retention
    retention_until = datetime.now(timezone.utc) + timedelta(days=366)
    
    try:
        # TODO(scale): Instantiate aioboto3.Session() globally at app startup instead of per-request
        session = aioboto3.Session()
        async with session.client('s3', region_name=AWS_REGION) as s3_client:
            await s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=contents,
                ContentType=evidence_file.content_type or "image/jpeg",
                ServerSideEncryption='AES256',
                ObjectLockMode='COMPLIANCE',          # COMPLIANCE = immutable, cannot be deleted by anyone
                ObjectLockRetainUntilDate=retention_until
            )

        # 4. Return the internal S3 URI
        secure_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        
        # TODO(post-pilot): Generate a 12-month presigned HTTPS URL instead of returning the raw s3:// URI
        # presigned_url = await s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key}, ExpiresIn=31536000)
        
        logger.info(f"📸 Evidence secured for {agent_id}: {secure_uri} (Locked until {retention_until.strftime('%Y-%m-%d')})")

        return {
            "status": "success", 
            "url": secure_uri 
        }

    except Exception as e:
        logger.error(f"S3 Upload failed for evidence from {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to securely store evidence. Please retry.")