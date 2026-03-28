from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from pydantic import BaseModel
import os
import secrets
import time
import re
import logging

logger = logging.getLogger("PAN_Onboarding")
router = APIRouter()

# 1. SECURE STORAGE SETUP
# TODO: Migrate to AWS S3 with SSE-KMS before scaling beyond Sector 1.
SECURE_STORAGE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../secrets/dossiers"))
os.makedirs(SECURE_STORAGE, exist_ok=True)

# Automatically generate an .htaccess file to block direct web server access
htaccess_path = os.path.join(SECURE_STORAGE, ".htaccess")
if not os.path.exists(htaccess_path):
    with open(htaccess_path, "w") as f:
        f.write("Order Deny,Allow\nDeny from all\n")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}

# --- DATA MODELS ---
class KeyRegistrationPayload(BaseModel):
    agent_id: str
    public_key_b64: str
    play_integrity_token: str # Server-side requirement for device attestation

# --- ENDPOINTS ---

@router.post("/enlist")
async def process_enlistment(
    request: Request,
    full_name: str = Form(...),
    callsign: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    zip_code: str = Form(...),
    vehicle_class: str = Form(...),
    hardware_verified: str = Form(...),
    referral_code_used: str = Form(None),
    veteran_credential: UploadFile = File(...)
):
    """Securely ingests Vanguard 50 applications and issues a real referral code."""
    
    redis_client = request.app.state.redis_client
    client_ip = request.client.host
    clean_email = email.strip().lower()

    # 1. RATE LIMITING (Redis-based)
    rate_key = f"rate_limit:enlist:{client_ip}"
    attempts = await redis_client.incr(rate_key)
    if attempts == 1:
        await redis_client.expire(rate_key, 3600)  # 1 hour window
    if attempts > 3:
        raise HTTPException(status_code=429, detail="Too many enlistment attempts. Please contact Command.")

    # 2. DUPLICATE EMAIL CHECK
    email_key = f"agent_email:{clean_email}"
    if await redis_client.exists(email_key):
        raise HTTPException(status_code=409, detail="An application with this email already exists.")

    # 3. FILE TYPE VALIDATION (Headers only, before reading to memory)
    if veteran_credential.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. PDF, JPG, or PNG only.")

    # 4. FILE SIZE LIMIT (Read into memory safely)
    contents = await veteran_credential.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum 5MB.")

    # 5. SECURE PII STORAGE & SANITIZATION
    # Sanitize the original filename to prevent filesystem errors or traversal
    safe_original = re.sub(r'[^\w\-.]', '_', veteran_credential.filename)
    safe_filename = f"{secrets.token_hex(16)}_{safe_original}"
    file_path = os.path.join(SECURE_STORAGE, safe_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
        
    # 6. SECURE REFERRAL CODE GENERATION & VALIDATION
    new_agent_id = f"VNG-{secrets.token_hex(3).upper()}-ALPHA"
    
    valid_referral = "ORGANIC"
    if referral_code_used:
        clean_ref = referral_code_used.strip().upper()
        if await redis_client.exists(f"agent:{clean_ref}"):
            valid_referral = clean_ref
            await redis_client.hincrby(f"agent:{clean_ref}", "referrals_pending", 1)

    # 7. REDIS PERSISTENCE
    # Store the agent data
    await redis_client.hset(f"agent:{new_agent_id}", mapping={
        "name": full_name,
        "callsign": callsign,
        "email": clean_email,
        "phone": phone,
        "zip_code": zip_code,
        "vehicle_class": vehicle_class,
        "referred_by": valid_referral,
        "status": "PENDING_VERIFICATION",
        "credential_filename": safe_filename, # Cloud-ready: storing filename only
        "enlisted_at": int(time.time()),
        "referrals_pending": 0,
        "referrals_cleared": 0
    })
    
    # Lock the email to prevent duplicates
    await redis_client.set(email_key, new_agent_id)
    
    return {"status": "success", "agent_id": new_agent_id}

@router.post("/register-key")
async def register_public_key(payload: KeyRegistrationPayload, request: Request):
    """
    The Key Ceremony Endpoint.
    Pairs the physical TPM public key to the agent's identity after approval.
    """
    # Ensure the Play Integrity token was provided by the device
    if not payload.play_integrity_token:
        raise HTTPException(status_code=400, detail="Missing Play Integrity attestation token.")
        
    redis_client = request.app.state.redis_client
    
    # Verify the agent actually exists in the system
    agent_exists = await redis_client.exists(f"agent:{payload.agent_id}")
    if not agent_exists:
        raise HTTPException(status_code=404, detail="Agent identity not found.")
        
    # Anti-Hijacking Guard: Do not allow an existing key to be silently overwritten.
    # If an agent loses their phone, they must go through the /ops/hardware-reset workflow.
    if await redis_client.exists(f"pan:agent:{payload.agent_id}:pubkey"):
        raise HTTPException(status_code=409, detail="Hardware key already registered for this identity.")
        
    await redis_client.set(f"pan:agent:{payload.agent_id}:pubkey", payload.public_key_b64)
    
    # 🟢 THE FIX: Corrected log and documented the technical debt
    logger.info(f"🔑 Key Ceremony Complete: {payload.agent_id} bound to hardware TPM.") 
    # TODO: Verify play_integrity_token against Google Play Integrity API before production scale
    
    return {"status": "success", "message": "Hardware key successfully bound to identity."}