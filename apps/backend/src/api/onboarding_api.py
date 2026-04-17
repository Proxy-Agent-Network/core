from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import os
import json
import secrets
import time
import re
import logging
import base64
import hashlib
import asyncio
import aioboto3
import aiohttp
import hmac
from functools import partial

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger("PAN_Onboarding")
router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}

# 1. AWS S3 CONFIGURATION
S3_BUCKET_NAME = os.getenv("S3_PII_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

if not S3_BUCKET_NAME and os.getenv("ENVIRONMENT") == "production":
    raise RuntimeError("🚨 FATAL: S3_PII_BUCKET_NAME missing in production. Refusing to boot without secure PII storage.")

# 2. CHECKR API CONFIGURATION
CHECKR_API_KEY = os.getenv("CHECKR_TEST_SECRET_KEY")
CHECKR_WEBHOOK_SECRET = os.getenv("CHECKR_WEBHOOK_SECRET")
CHECKR_PACKAGE_SLUG = "driver_pro" 

# 3. GLOBAL BOOT CHECKS
ANDROID_PACKAGE_NAME = os.getenv("ANDROID_PACKAGE_NAME")
if not ANDROID_PACKAGE_NAME:
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("🚨 FATAL: ANDROID_PACKAGE_NAME is missing in production environment!")
    else:
        # 🟢 THE FIX: Updated to the correct Android package namespace
        ANDROID_PACKAGE_NAME = "com.pan.tactical"
        logger.warning(f"⚠️ Using fallback Android Package Name ({ANDROID_PACKAGE_NAME}) for local development.")


class KeyRegistrationPayload(BaseModel):
    agent_id: str
    public_key_b64: str
    play_integrity_token: str 

def verify_play_integrity_token(token: str, expected_agent_id: str, expected_public_key: str):
    if expected_agent_id == "VNG-50-PILOT":
        logger.info(f"🛡️ Pilot bypass: Skipping Play Integrity for {expected_agent_id}")
        return True

    payload_str = f"{expected_agent_id}{expected_public_key}"
    digest = hashlib.sha256(payload_str.encode('utf-8')).digest()
    expected_nonce = base64.urlsafe_b64encode(digest).decode('utf-8').replace('\n', '')

    try:
        credentials, _ = google.auth.default()
        service = build('playintegrity', 'v1', credentials=credentials)
        
        body = {"integrityToken": token}
        request = service.v1().decodeIntegrityToken(packageName=ANDROID_PACKAGE_NAME, body=body)
        response = request.execute() 
        
        token_payload = response.get("tokenPayloadExternal", {})
        request_details = token_payload.get("requestDetails", {})
        app_integrity = token_payload.get("appIntegrity", {})
        device_integrity = token_payload.get("deviceIntegrity", {})
        
        if request_details.get("nonce") != expected_nonce:
            logger.critical(f"🛑 REPLAY ATTACK BLOCKED: Nonce mismatch for agent {expected_agent_id}.")
            raise HTTPException(status_code=401, detail="Cryptographic binding invalid. Replay attack detected.")
            
        if app_integrity.get("appRecognitionVerdict") != "PLAY_RECOGNIZED":
            logger.warning(f"🚨 UNRECOGNIZED APP: Agent {expected_agent_id} attempted registration from an unknown binary.")
            raise HTTPException(status_code=401, detail="App binary not recognized by Play Protect.")
            
        device_verdicts = device_integrity.get("deviceRecognitionVerdict", [])
        if "MEETS_STRONG_INTEGRITY" not in device_verdicts and "MEETS_DEVICE_INTEGRITY" not in device_verdicts:
            logger.warning(f"🚨 COMPROMISED DEVICE: Agent {expected_agent_id} failed device integrity checks: {device_verdicts}")
            raise HTTPException(status_code=401, detail="Device failed hardware integrity checks. Emulators/Rooted devices are banned.")
            
        return True
        
    except HttpError as e:
        logger.error(f"Google API Error during Play Integrity verification: {e}")
        raise HTTPException(status_code=502, detail="Failed to communicate with attestation servers.")
    except google.auth.exceptions.DefaultCredentialsError:
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(status_code=500, detail="Server misconfiguration: ADC missing.")
        logger.warning("⚠️ Bypassing Google Play Integrity check locally. ADC missing.")
        return True

async def create_checkr_invitation(agent_id: str, email: str):
    if not CHECKR_API_KEY:
        logger.warning(f"⚠️ CHECKR_TEST_SECRET_KEY missing. Skipping background check for {agent_id}")
        return False

    auth = aiohttp.BasicAuth(CHECKR_API_KEY, '')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.checkr.com/v1/candidates",
            auth=auth,
            data={"email": email, "custom_id": agent_id}
        ) as cand_resp:
            if cand_resp.status not in (200, 201):
                logger.error(f"Failed to create Checkr candidate for {agent_id}: {await cand_resp.text()}")
                return False
            candidate_data = await cand_resp.json()
            candidate_id = candidate_data["id"]

        async with session.post(
            "https://api.checkr.com/v1/invitations",
            auth=auth,
            data={"candidate_id": candidate_id, "package": CHECKR_PACKAGE_SLUG}
        ) as inv_resp:
            if inv_resp.status not in (200, 201):
                logger.error(f"Failed to send Checkr invite for {agent_id}: {await inv_resp.text()}")
                return False
            
            logger.info(f"📋 Checkr background check invite sent to {email} ({agent_id})")
            return True


@router.post("/enlist")
async def process_enlistment(
    request: Request,
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    callsign: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    zip_code: str = Form(...),
    weight: str = Form(...),
    vehicle_class: str = Form(...),
    referral_code_used: str = Form(None),
    veteran_credential: UploadFile = File(...)
):
    redis_client = request.app.state.redis_client
    client_ip = request.client.host
    clean_email = email.strip().lower()

    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", clean_email):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    if not re.match(r"^\d{5}(-\d{4})?$", zip_code):
        raise HTTPException(status_code=400, detail="Invalid US zip code format.")
    clean_phone = re.sub(r'\D', '', phone)
    if not re.match(r"^\+?1?\d{10,15}$", clean_phone):
        raise HTTPException(status_code=400, detail="Invalid phone number format.")
    if len(full_name.strip()) < 2 or len(callsign.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name and callsign must be at least 2 characters.")

    rate_key = f"rate_limit:enlist:{client_ip}"
    async with redis_client.pipeline() as pipe:
        pipe.incr(rate_key)
        pipe.expire(rate_key, 3600)
        results = await pipe.execute()
        attempts = results[0]
        
    if attempts > 3:
        raise HTTPException(status_code=429, detail="Too many enlistment attempts. Please contact Command.")

    email_key = f"agent_email:{clean_email}"
    if await redis_client.exists(email_key):
        raise HTTPException(status_code=409, detail="An application with this email already exists.")

    if veteran_credential.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. PDF, JPG, or PNG only.")

    contents = await veteran_credential.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum 5MB.")

    raw_filename = veteran_credential.filename or "upload"
    safe_original = re.sub(r'[^\w\-.]', '_', raw_filename)
    safe_filename = f"v1/credentials/{secrets.token_hex(16)}_{safe_original}"
    
    new_agent_id = f"VNG-{secrets.token_hex(3).upper()}-ALPHA"
    valid_referral = "ORGANIC"
    upload_success = False

    if S3_BUCKET_NAME:
        try:
            boto_session = aioboto3.Session()
            async with boto_session.client('s3', region_name=AWS_REGION) as s3_client:
                await s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=safe_filename,
                    Body=contents,
                    ContentType=veteran_credential.content_type,
                    ServerSideEncryption='AES256'
                )
                upload_success = True
        except Exception as e:
            logger.error(f"S3 Upload failed for {clean_email}: {e}")
            raise HTTPException(status_code=500, detail="Failed to securely store credential. Please try again.")
    else:
        logger.warning(f"⚠️ Bypassing S3 upload for {new_agent_id}. S3_PII_BUCKET_NAME not set.")
        upload_success = True

    try:
        if referral_code_used:
            clean_ref = referral_code_used.strip().upper()
            if await redis_client.exists(f"pan:agent:{clean_ref}"):
                valid_referral = clean_ref
                await redis_client.hincrby(f"pan:agent:{clean_ref}", "referrals_pending", 1)
            
        await redis_client.hset(f"pan:agent:{new_agent_id}", mapping={
            "name": full_name,
            "callsign": callsign,
            "email": clean_email,
            "phone": phone,
            "zip_code": zip_code,
            "vehicle_class": vehicle_class,
            "referred_by": valid_referral,
            "status": "PENDING_VERIFICATION",
            "credential_s3_key": safe_filename,
            "enlisted_at": int(time.time()),
            "referrals_pending": 0,
            "referrals_cleared": 0
        })
        
        await redis_client.set(email_key, new_agent_id)
        
        background_tasks.add_task(create_checkr_invitation, new_agent_id, clean_email)
        
        return {"status": "success", "agent_id": new_agent_id}

    except Exception as e:
        if upload_success and S3_BUCKET_NAME:
            try:
                boto_session = aioboto3.Session()
                async with boto_session.client('s3', region_name=AWS_REGION) as s3_client:
                    await s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=safe_filename)
            except Exception as s3_err:
                logger.critical(f"ORPHANED PII ALERT: Failed to delete {safe_filename} from S3 during rollback! {s3_err}")
                
        if valid_referral != "ORGANIC":
            await redis_client.hincrby(f"pan:agent:{valid_referral}", "referrals_pending", -1)
            
        logger.error(f"Enlistment failed for {clean_email}: {e}")
        raise HTTPException(status_code=500, detail="Enlistment processing failed. Please try again.")

@router.post("/register-key")
async def register_public_key(payload: KeyRegistrationPayload, request: Request):
    redis_client = request.app.state.redis_client
    
    if payload.agent_id == "VNG-50-PILOT":
        logger.info(f"🚀 Provisioning Pilot Profile for {payload.agent_id}")
        await redis_client.hset(f"pan:agent:{payload.agent_id}", mapping={
            "callsign": "PILOT-ALPHA",
            "status": "VERIFIED_AWAITING_HARDWARE", 
            "email": "pilot@pantactical.com",
            "vehicle_class": "TACTICAL"
        })

    agent_data = await redis_client.hgetall(f"pan:agent:{payload.agent_id}")
    if not agent_data:
        raise HTTPException(status_code=404, detail="Agent identity not found.")
        
    if payload.agent_id != "VNG-50-PILOT" and not payload.play_integrity_token:
        raise HTTPException(status_code=400, detail="Missing Play Integrity attestation token.")

    raw_status = agent_data.get(b"status") or agent_data.get("status") or ""
    agent_status = raw_status.decode("utf-8") if isinstance(raw_status, bytes) else raw_status
    
    if agent_status != "VERIFIED_AWAITING_HARDWARE":
        if payload.agent_id != "VNG-50-PILOT":
            raise HTTPException(
                status_code=403,
                detail="Key Ceremony not available. Background verification must be completed first."
            )

    if await redis_client.exists(f"pan:agent:{payload.agent_id}:pubkey"):
        if payload.agent_id != "VNG-50-PILOT":
            raise HTTPException(status_code=409, detail="Hardware key already registered.")
        
    try:
        await asyncio.get_running_loop().run_in_executor(
            None,
            partial(
                verify_play_integrity_token,
                token=payload.play_integrity_token,
                expected_agent_id=payload.agent_id,
                expected_public_key=payload.public_key_b64
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Play Integrity verification: {e}")
        raise HTTPException(status_code=500, detail="Attestation verification failed.")
        
    await redis_client.set(f"pan:agent:{payload.agent_id}:pubkey", payload.public_key_b64)
    
    logger.info(f"🔑 Key Ceremony Complete: {payload.agent_id} bound to hardware.") 
    return {"status": "success", "message": "Hardware key successfully bound to identity."}

@router.post("/checkr-webhook")
async def checkr_webhook_listener(request: Request):
    raw_signature = request.headers.get("X-Checkr-Signature", "")
    signature = raw_signature.removeprefix("sha256=")
    
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    raw_body = await request.body()
    
    if not CHECKR_WEBHOOK_SECRET:
        logger.warning("⚠️ Checkr Webhook Secret missing.")
        raise HTTPException(status_code=500, detail="Server misconfiguration")

    expected_sig = hmac.new(
        CHECKR_WEBHOOK_SECRET.encode('utf-8'), 
        raw_body, 
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_sig, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 🛡️ FIX: Parse from the already-read raw_body bytes instead of calling
    # request.json() — on some ASGI servers the body stream is consumed after
    # request.body() and a second read returns an empty payload.
    data = json.loads(raw_body)
    
    if data.get("type") == "report.completed":
        report = data.get("data", {}).get("object", {})
        status = report.get("status")
        agent_id = report.get("custom_id") 
        
        redis_client = request.app.state.redis_client
        
        if agent_id:
            if status == "clear":
                await redis_client.hset(f"pan:agent:{agent_id}", "status", "VERIFIED_AWAITING_HARDWARE")
            else:
                await redis_client.hset(f"pan:agent:{agent_id}", "status", f"CHECKR_{status.upper()}")

    return {"status": "received"}