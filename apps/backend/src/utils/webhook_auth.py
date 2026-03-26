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

# PROXY PROTOCOL - ZERO-TRUST WEBHOOK AUTHENTICATION (v1.6)
# Centralized cryptographic validation for all external ingress.
# ----------------------------------------------------

logger = logging.getLogger("WebhookAuth")

def _require_env(key: str) -> str:
    """Helper to enforce explicit environment variable configuration. Fails fast if missing."""
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"FATAL: Required environment variable '{key}' is not set. Cannot start securely.")
    return value

class SecurityVault:
    """
    Secure credential management. Strictly requires explicit environment variables.
    """
    CARRIER_SECRETS = {
        "DHL": _require_env("WHSEC_DHL"),
        "FEDEX": _require_env("WHSEC_FEDEX"),
        "UPS": _require_env("WHSEC_UPS")
    }
    
    V2X_FLEET_PUBKEYS = {
        "WAYMO_MESA_01": _require_env("PUBKEY_WAYMO_MESA_01"),
        "MAGNA_TEST_01": _require_env("PUBKEY_MAGNA_TEST_01")
    }

    @classmethod
    def validate_production_readiness(cls):
        """Runs at startup. Prevents deployment with known vulnerabilities."""
        is_prod = os.getenv("ENVIRONMENT") == "production"

        if is_prod:
            for carrier, secret in cls.CARRIER_SECRETS.items():
                if secret.startswith("whsec_") and "master" in secret:
                    raise RuntimeError(f"FATAL: Hardcoded default secret detected for {carrier} in production environment!")

        rfc_test_vector = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
        
        if is_prod and rfc_test_vector in cls.V2X_FLEET_PUBKEYS.values():
            raise RuntimeError("FATAL: RFC test vector public key detected in production vault. Key compromise is guaranteed.")
            
        if not is_prod and rfc_test_vector in cls.V2X_FLEET_PUBKEYS.values():
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
        logger.warning(f"🚨 REPLAY ATTACK BLOCKED: Request is {abs(now - event_time)} seconds skewed.")
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
        raise HTTPException(status_code=401, detail="Unrecognized carrier ID.")

    raw_body = await request.body()
    
    if not verify_signature(raw_body, x_proxy_logistics_signature.lower(), x_proxy_request_timestamp, secret):
        logger.warning(f"🚨 FORGED CARRIER SIGNAL: Signature mismatch or replay attack for {carrier_id}.")
        raise HTTPException(status_code=401, detail="Invalid cryptographic signature or expired request.")
        
    return carrier_id


async def verify_v2x_signature(
    request: Request,
    x_fleet_id: str = Header(...),
    x_fleet_signature: str = Header(None) # Optional at the FastAPI routing layer so we can handle the logic inside
) -> str:
    """
    FastAPI Dependency: Validates incoming AV telemetry/distress signals.
    Enforces Ed25519 cryptography AND timestamp-based replay protection.
    """
    # 🟢 DEV BYPASS WITH STRICT ENVIRONMENT GUARD
    if x_fleet_id == "DEV-FLEET-01":
        if os.getenv("ENVIRONMENT") == "production":
            logger.critical("🛑 DEV-FLEET-01 attempted dispatch in production. Rejecting.")
            raise HTTPException(status_code=401, detail="Dev fleet ID not permitted in production.")
        logger.info("🟢 Bypassing cryptography for DEV-FLEET-01 (dev environment)")
        return x_fleet_id
        
    # 🛑 STRICT ENFORCEMENT FOR ALL OTHER FLEETS
    if not x_fleet_signature:
        logger.warning(f"🚨 MISSING SIGNATURE: Fleet {x_fleet_id} attempted dispatch without cryptography.")
        raise HTTPException(status_code=422, detail="Missing X-Fleet-Signature header.")

    pubkey_hex = SecurityVault.V2X_FLEET_PUBKEYS.get(x_fleet_id.upper())
    if not pubkey_hex:
        logger.warning(f"🚨 UNREGISTERED FLEET ID ATTEMPTED DISPATCH: {x_fleet_id}")
        raise HTTPException(status_code=401, detail="Unregistered Fleet ID.")
        
    raw_body = await request.body()

    # 1. Semantic Payload Parsing & Replay Protection
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
        logger.warning(f"🚨 V2X REPLAY ATTACK BLOCKED: Request skewed by {abs(now - event_time)}s.")
        raise HTTPException(status_code=401, detail="Request expired or replay attack detected.")
    
    # 2. Cryptographic Verification
    try:
        pubkey_bytes = binascii.unhexlify(pubkey_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pubkey_bytes)
        signature_bytes = binascii.unhexlify(x_fleet_signature)
        
        public_key.verify(signature_bytes, raw_body)
        
        logger.info(f"✅ V2X Signal Verified via Ed25519 for {x_fleet_id}")
        return x_fleet_id
        
    except ValueError:
        logger.error(f"⚠️ Malformed Ed25519 signature payload for {x_fleet_id}")
        raise HTTPException(status_code=400, detail="Malformed cryptographic payload.")
        
    except InvalidSignature:
        logger.critical(f"🛑 FORGED V2X SIGNAL: Ed25519 signature mismatch for {x_fleet_id}!")
        raise HTTPException(status_code=401, detail="Invalid V2X cryptographic signature.")