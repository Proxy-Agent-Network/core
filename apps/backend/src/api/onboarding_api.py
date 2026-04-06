from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import os
import secrets
import time
import re
import logging
import base64
import hashlib
import asyncio
import aiohttp
import hmac
from functools import partial

# Added Google SDK imports for server-to-server token verification
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger("PAN_Onboarding")
router = APIRouter()

# 1. SECURE STORAGE SETUP
SECURE_STORAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../secrets/dossiers"))
os.makedirs(SECURE_STORAGE, exist_ok=True)

# Automatically generate an .htaccess file to block direct web server access
htaccess_path = os.path.join(SECURE_STORAGE, ".htaccess")
if not os.path.exists(htaccess_path):
    with open(htaccess_path, "w") as f:
        f.write("Order Deny,Allow\nDeny from all\n")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}

# 2. CHECKR API CONFIGURATION
CHECKR_API_KEY = os.getenv("CHECKR_TEST_SECRET_KEY")
CHECKR_WEBHOOK_SECRET = os.getenv("CHECKR_WEBHOOK_SECRET")
CHECKR_PACKAGE_SLUG = "driver_pro" # driver_pro package: driving record + criminal + county search.

# 3. GLOBAL BOOT CHECKS
ANDROID_PACKAGE_NAME = os.getenv("ANDROID_PACKAGE_NAME")
if not ANDROID_PACKAGE_NAME:
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("🚨 FATAL: ANDROID_PACKAGE_NAME is missing in production environment!")
    else:
        ANDROID_PACKAGE_NAME = "network.proxyagent.pantactical"
        logger.warning("⚠️ Using fallback Android Package Name for local development.")


# --- DATA MODELS ---
class KeyRegistrationPayload(BaseModel):
    agent_id: str
    public_key_b64: str
    play_integrity_token: str # Server-side requirement for device attestation

# --- HELPERS ---

def verify_play_integrity_token(token: str, expected_agent_id: str, expected_public_key: str):
    """
    Verifies the Play Integrity token with Google's servers and ensures the 
    cryptographic nonce matches the requested hardware key to prevent replay attacks.
    """
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
        
        # 1. Verify Nonce Binding
        if request_details.get("nonce") != expected_nonce:
            logger.critical(f"🛑 REPLAY ATTACK BLOCKED: Nonce mismatch for agent {expected_agent_id}.")
            raise HTTPException(status_code=401, detail="Cryptographic binding invalid. Replay attack detected.")
            
        # 2. Verify App Integrity
        if app_integrity.get("appRecognitionVerdict") != "PLAY_RECOGNIZED":
            logger.warning(f"🚨 UNRECOGNIZED APP: Agent {expected_agent_id} attempted registration from an unknown binary.")
            raise HTTPException(status_code=401, detail="App binary not recognized by Play Protect.")
            
        # 3. Verify Device Integrity
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
    """Fires a background check invitation via Checkr."""
    if not CHECKR_API_KEY:
        logger.warning(f"⚠️ CHECKR_TEST_SECRET_KEY missing. Skipping background check for {agent_id}")
        return False

    auth = aiohttp.BasicAuth(CHECKR_API_KEY, '')
    
    async with aiohttp.ClientSession() as session:
        # 1. Create the Candidate
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

        # 2. Send the Invitation
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

# --- ENDPOINTS ---

@router.post("/enlist")
async def process_enlistment(
    request: Request,
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    callsign: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    zip_code: str = Form(...),
    vehicle_class: str = Form(...),
    referral_code_used: str = Form(None),
    veteran_credential: UploadFile = File(...)
):
    """Securely ingests Vanguard 50 applications and issues a real referral code."""
    
    redis_client = request.app.state.redis_client
    client_ip = request.client.host
    clean_email = email.strip().lower()

    # 0. INPUT FORMAT VALIDATION
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", clean_email):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    if not re.match(r"^\d{5}(-\d{4})?$", zip_code):
        raise HTTPException(status_code=400, detail="Invalid US zip code format.")
    clean_phone = re.sub(r'\D', '', phone)
    if not re.match(r"^\+?1?\d{10,15}$", clean_phone):
        raise HTTPException(status_code=400, detail="Invalid phone number format.")
    if len(full_name.strip()) < 2 or len(callsign.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name and callsign must be at least 2 characters.")

    # 1. RATE LIMITING (Pipeline Fix)
    rate_key = f"rate_limit:enlist:{client_ip}"
    async with redis_client.pipeline() as pipe:
        pipe.incr(rate_key)
        pipe.expire(rate_key, 3600)
        results = await pipe.execute()
        attempts = results[0]
        
    if attempts > 3:
        raise HTTPException(status_code=429, detail="Too many enlistment attempts. Please contact Command.")

    # 2. DUPLICATE EMAIL CHECK
    email_key = f"agent_email:{clean_email}"
    if await redis_client.exists(email_key):
        raise HTTPException(status_code=409, detail="An application with this email already exists.")

    # 3. FILE TYPE VALIDATION
    if veteran_credential.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. PDF, JPG, or PNG only.")

    # 4. FILE SIZE LIMIT
    contents = await veteran_credential.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum 5MB.")

    # 5. SECURE PII STORAGE & SANITIZATION
    raw_filename = veteran_credential.filename or "upload"
    safe_original = re.sub(r'[^\w\-.]', '_', raw_filename)
    safe_filename = f"{secrets.token_hex(16)}_{safe_original}"
    file_path = os.path.join(SECURE_STORAGE, safe_filename)
    
    new_agent_id = f"VNG-{secrets.token_hex(3).upper()}-ALPHA"
    valid_referral = "ORGANIC"

    # 6. ATOMIC WRITE & ROLLBACK GUARD
    try:
        # Resolve referral inside the atomic scope
        if referral_code_used:
            clean_ref = referral_code_used.strip().upper()
            if await redis_client.exists(f"agent:{clean_ref}"):
                valid_referral = clean_ref
                await redis_client.hincrby(f"agent:{clean_ref}", "referrals_pending", 1)

        # TODO: use aioboto3 for async file I/O during S3 migration
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
            
        await redis_client.hset(f"agent:{new_agent_id}", mapping={
            "name": full_name,
            "callsign": callsign,
            "email": clean_email,
            "phone": phone,
            "zip_code": zip_code,
            "vehicle_class": vehicle_class,
            "referred_by": valid_referral,
            "status": "PENDING_VERIFICATION",
            "credential_filename": safe_filename,
            "enlisted_at": int(time.time()),
            "referrals_pending": 0,
            "referrals_cleared": 0
        })
        
        await redis_client.set(email_key, new_agent_id)
        
        # 7. FIRE BACKGROUND CHECK (Non-Blocking)
        background_tasks.add_task(create_checkr_invitation, new_agent_id, clean_email)
        
        return {"status": "success", "agent_id": new_agent_id}

    except Exception as e:
        # Clean up orphaned file if Redis write failed
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Decrement referral counter if it was incremented
        if valid_referral != "ORGANIC":
            await redis_client.hincrby(f"agent:{valid_referral}", "referrals_pending", -1)
            
        logger.error(f"Enlistment failed for {clean_email}: {e}")
        raise HTTPException(status_code=500, detail="Enlistment processing failed. Please try again.")

@router.post("/register-key")
async def register_public_key(payload: KeyRegistrationPayload, request: Request):
    """
    The Key Ceremony Endpoint.
    Pairs the physical TPM public key to the agent's identity after approval.
    """
    if not payload.play_integrity_token:
        raise HTTPException(status_code=400, detail="Missing Play Integrity attestation token.")
        
    redis_client = request.app.state.redis_client
    
    # Verify agent exists and Checkr clearance status
    agent_data = await redis_client.hgetall(f"agent:{payload.agent_id}")
    if not agent_data:
        raise HTTPException(status_code=404, detail="Agent identity not found.")
        
    # Works regardless of whether redis-py returns bytes or str keys
    raw_status = agent_data.get(b"status") or agent_data.get("status") or ""
    agent_status = raw_status.decode("utf-8") if isinstance(raw_status, bytes) else raw_status
    if agent_status != "VERIFIED_AWAITING_HARDWARE":
        raise HTTPException(
            status_code=403,
            detail="Key Ceremony not available. Background verification must be completed first."
        )

    # Check for duplicate key registration BEFORE Google API call
    if await redis_client.exists(f"pan:agent:{payload.agent_id}:pubkey"):
        raise HTTPException(status_code=409, detail="Hardware key already registered for this identity.")
        
    # Verify Play Integrity Token
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
        
    # Atomic write to prevent race condition
    registered = await redis_client.set(
        f"pan:agent:{payload.agent_id}:pubkey",
        payload.public_key_b64,
        nx=True
    )
    
    if not registered:
        raise HTTPException(status_code=409, detail="Hardware key already registered for this identity.")
    
    logger.info(f"🔑 Key Ceremony Complete: {payload.agent_id} bound to hardware TPM with Google Play verification.") 
    
    return {"status": "success", "message": "Hardware key successfully bound to identity."}

@router.post("/checkr-webhook")
async def checkr_webhook_listener(request: Request):
    """Listens for Checkr background check completions."""
    
    # Checkr might prefix with "sha256=", this defensively strips it if present
    raw_signature = request.headers.get("X-Checkr-Signature", "")
    signature = raw_signature.removeprefix("sha256=")
    
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    raw_body = await request.body()
    
    if not CHECKR_WEBHOOK_SECRET:
        logger.warning("⚠️ Checkr Webhook Secret missing. Rejecting webhook.")
        raise HTTPException(status_code=500, detail="Server misconfiguration")

    expected_sig = hmac.new(
        CHECKR_WEBHOOK_SECRET.encode('utf-8'), 
        raw_body, 
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_sig, signature):
        logger.warning("🚨 Invalid Checkr webhook signature detected.")
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()
    
    if data.get("type") == "report.completed":
        report = data.get("data", {}).get("object", {})
        status = report.get("status")
        agent_id = report.get("custom_id") 
        
        redis_client = request.app.state.redis_client
        
        if agent_id:
            if status == "clear":
                await redis_client.hset(f"agent:{agent_id}", "status", "VERIFIED_AWAITING_HARDWARE")
                logger.info(f"✅ Checkr CLEARED for {agent_id}. Ready for Key Ceremony.")
            else:
                await redis_client.hset(f"agent:{agent_id}", "status", f"CHECKR_{status.upper()}")
                logger.warning(f"⚠️ Checkr flagged {agent_id} with status: {status}")

    return {"status": "received"}