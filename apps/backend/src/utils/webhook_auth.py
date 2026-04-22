import os
import json
import hmac
import hashlib
import time
import logging
import binascii
from typing import Union
from fastapi import Request, HTTPException, Header

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# PROXY PROTOCOL - ZERO-TRUST WEBHOOK AUTHENTICATION (v1.7)
# Centralized cryptographic validation for all external ingress.
# ----------------------------------------------------

logger = logging.getLogger("WebhookAuth")

def _optional_env(key: str) -> Union[str, None]:
    """Helper to load secrets gracefully. Unconfigured keys safely disable their respective routes."""
    value = os.getenv(key)
    if not value:
        logger.warning(f"⚠️ Optional configuration '{key}' is missing. Associated webhooks will be rejected.")
    return value

class SecurityVault:
    """
    Secure credential management. Gracefully degrades if specific fleet/carrier partners are not active.
    """
    CARRIER_SECRETS = {
        "DHL": _optional_env("WHSEC_DHL"),
        "FEDEX": _optional_env("WHSEC_FEDEX"),
        "UPS": _optional_env("WHSEC_UPS")
    }
    
    V2X_FLEET_PUBKEYS = {
        "WAYMO_MESA_01": _optional_env("PUBKEY_WAYMO_MESA_01"),
        "MAGNA_TEST_01": _optional_env("PUBKEY_MAGNA_TEST_01")
    }

    @classmethod
    def validate_production_readiness(cls):
        """Runs at startup. Prevents deployment with known vulnerabilities."""
        
        # 🟢 Pytest Escape Hatch: Don't crash unit tests missing full environment context
        if os.getenv("PYTEST_CURRENT_TEST"):
            return
            
        is_prod = os.getenv("ENVIRONMENT") == "production"

        if is_prod:
            for carrier, secret in cls.CARRIER_SECRETS.items():
                if secret and secret.startswith("whsec_") and "master" in secret:
                    raise RuntimeError(f"FATAL: Hardcoded default secret detected for {carrier} in production environment!")

        rfc_test_vector = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
        active_pubkeys = [k for k in cls.V2X_FLEET_PUBKEYS.values() if k]
        
        if is_prod and rfc_test_vector in active_pubkeys:
            raise RuntimeError("FATAL: RFC test vector public key detected in production vault. Key compromise is guaranteed.")
            
        if not is_prod and rfc_test_vector in active_pubkeys:
            logger.warning("⚠️ WARNING: Running with insecure RFC 8037 test vectors in development mode.")

# Execute startup checks immediately when the module loads
SecurityVault.validate_production_readiness()


def verify_signature(
    raw_body: Union[str, bytes], 
    signature: str, 
    timestamp: str, 
    secret: str,
    tolerance_seconds: int = 300
) -> bool:
    now = int(time.time())
    try:
        event_time = int(timestamp)
    except (ValueError, TypeError):
        return False
        
    if abs(now - event_time) > tolerance_seconds:
        logger.warning(f"🚨 REPLAY SKEW BLOCKED: Request is {abs(now - event_time)} seconds skewed.")
        return False

    if isinstance(raw_body, str):
        raw_body_bytes = raw_body.encode('utf-8')
    else:
        raw_body_bytes = raw_body

    payload = f"{timestamp}.".encode('utf-8') + raw_body_bytes
    computed_signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(computed_signature, signature)


async def verify_carrier_hmac(
    request: Request, 
    x_proxy_logistics_signature: str = Header(...),
    x_proxy_request_timestamp: str = Header(...)
) -> str:
    carrier_id = request.path_params.get("carrier_id")
    if not carrier_id:
        raise HTTPException(status_code=400, detail="Missing carrier_id in route path.")

    secret = SecurityVault.CARRIER_SECRETS.get(carrier_id.upper())
    if not secret:
        raise HTTPException(status_code=401, detail="Unrecognized carrier ID or missing configuration.")

    raw_body = await request.body()
    
    if not verify_signature(raw_body, x_proxy_logistics_signature.lower(), x_proxy_request_timestamp, secret):
        logger.warning(f"🚨 FORGED CARRIER SIGNAL: Signature mismatch or replay attack for {carrier_id}.")
        raise HTTPException(status_code=401, detail="Invalid cryptographic signature or expired request.")
        
    # Soft-fail Redis for logistics webhooks (prioritize availability over strict idempotency here)
    redis_client = getattr(request.app.state, "redis_client", None)
    if redis_client:
        replay_key = f"carrier_nonce:{x_proxy_logistics_signature}"
        is_replay = await redis_client.get(replay_key)
        
        if is_replay:
            logger.critical(f"🛑 REPLAY ATTACK BLOCKED: Signature already processed for {carrier_id}")
            raise HTTPException(status_code=401, detail="Replay attack detected: signature already processed.")
        
        await redis_client.setex(replay_key, 360, "1")

    return carrier_id


async def verify_v2x_signature(
    request: Request,
    x_fleet_id: str = Header(...),
    x_fleet_signature: str = Header(...) 
) -> str:
    """
    FastAPI Dependency: Validates incoming AV telemetry/distress signals.
    Enforces Ed25519 cryptography AND strict Redis-backed fail-closed replay protection.
    """
    
    # 🟢 PILOT BYPASS: Bypasses Ed25519 crypto verification (C4 FIX: ENVIRONMENT GATED)
    if x_fleet_id == "DEV-FLEET-01":
        if os.getenv("ENVIRONMENT") != "production":
            logger.info("🚀 V2X Security Bypass engaged for DEV-FLEET-01. Skipping crypto verification.")
            return x_fleet_id
        else:
            logger.critical("🛑 DEV-FLEET-01 BYPASS ATTEMPTED IN PRODUCTION! Hard-failing request.")
            raise HTTPException(status_code=403, detail="Development fleet ID not permitted in production.")
    
    pubkey_hex = SecurityVault.V2X_FLEET_PUBKEYS.get(x_fleet_id.upper())
    if not pubkey_hex:
        logger.warning(f"🚨 UNREGISTERED OR UNCONFIGURED FLEET ID ATTEMPTED DISPATCH: {x_fleet_id}")
        raise HTTPException(status_code=401, detail="Unregistered Fleet ID.")
        
    raw_body = await request.body()

    # 1. Semantic Payload Parsing & Timestamp Skew Protection
    try:
        body_data = json.loads(raw_body)
    except json.JSONDecodeError:
        logger.warning(f"⚠️ V2X payload is not valid JSON from {x_fleet_id}")
        raise HTTPException(status_code=400, detail="Malformed JSON payload.")

    raw_timestamp = body_data.get("timestamp")
    if raw_timestamp is None:
        logger.warning(f"⚠️ V2X payload explicitly missing timestamp from {x_fleet_id}")
        raise HTTPException(status_code=400, detail="Invalid or missing timestamp in payload.")

    try:
        event_time = int(raw_timestamp)
    except (ValueError, TypeError):
        logger.warning(f"⚠️ V2X payload timestamp is malformed from {x_fleet_id}")
        raise HTTPException(status_code=400, detail="Malformed timestamp format.")

    now = int(time.time())
    if abs(now - event_time) > 300:
        logger.warning(f"🚨 V2X SKEW REJECTED: Request skewed by {abs(now - event_time)}s.")
        raise HTTPException(status_code=401, detail="Request expired or timestamp skew detected.")
    
    # 2. Cryptographic Verification
    try:
        pubkey_bytes = binascii.unhexlify(pubkey_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pubkey_bytes)
        signature_bytes = binascii.unhexlify(x_fleet_signature)
        
        public_key.verify(signature_bytes, raw_body)
        
    except ValueError:
        logger.error(f"⚠️ Malformed Ed25519 signature payload for {x_fleet_id}")
        raise HTTPException(status_code=400, detail="Malformed cryptographic payload.")
        
    except InvalidSignature:
        logger.critical(f"🛑 FORGED V2X SIGNAL: Ed25519 signature mismatch for {x_fleet_id}!")
        raise HTTPException(status_code=401, detail="Invalid V2X cryptographic signature.")
        
    # 3. Redis-based Replay Protection (🟢 THE FIX: Fail-Closed Enforced)
    redis_client = getattr(request.app.state, "redis_client", None)
    if not redis_client:
        logger.critical(f"🛑 REDIS UNAVAILABLE: Cannot enforce V2X replay protection for {x_fleet_id}. Hard-failing request.")
        raise HTTPException(status_code=503, detail="Security subsystem unavailable. Cannot safely process dispatch.")

    # Treat the verified signature as the ultimate idempotency key
    replay_key = f"v2x_nonce:{x_fleet_signature}"
    is_replay = await redis_client.get(replay_key)
    
    if is_replay:
        logger.critical(f"🛑 V2X REPLAY ATTACK BLOCKED: Distress signal duplicated for {x_fleet_id}")
        raise HTTPException(status_code=401, detail="Replay attack detected: exact payload already dispatched.")
    
    # Store signature in Redis for slightly longer than the 300s timestamp skew window
    await redis_client.setex(replay_key, 360, "1")

    logger.info(f"✅ V2X Signal Verified via Ed25519 for {x_fleet_id}")
    return x_fleet_id