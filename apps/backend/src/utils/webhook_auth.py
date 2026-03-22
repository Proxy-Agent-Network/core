import hmac
import hashlib
import time
from typing import Union

# PROXY PROTOCOL - WEBHOOK HMAC UTILITY (v1)
# "Verify the origin of every instruction."
# ----------------------------------------------------

def verify_signature(
    raw_body: Union[str, bytes], 
    signature: str, 
    timestamp: str, 
    secret: str,
    tolerance_seconds: int = 300
) -> bool:
    """
    Verifies the HMAC-SHA256 signature of an incoming Proxy Protocol webhook.
    
    This utility ensures that:
    1. The sender possesses your secret key.
    2. The message hasn't been modified in transit.
    3. The request is fresh (not a replay of a previous event).
    
    Args:
        raw_body: The raw, unparsed request body (bytes or string).
        signature: The value from the 'X-Proxy-Signature' header.
        timestamp: The value from the 'X-Proxy-Request-Timestamp' header.
        secret: Your 'whsec_...' secret from the Proxy Dashboard.
        tolerance_seconds: Time window in seconds to prevent replay attacks (default 5m).
        
    Returns:
        bool: True if the signature is valid and within the time window.
    """
    
    # 1. Replay Attack Protection
    # Check if the timestamp is within the allowed tolerance window.
    now = int(time.time())
    try:
        event_time = int(timestamp)
    except (ValueError, TypeError):
        return False
        
    if abs(now - event_time) > tolerance_seconds:
        # Request is too old or from the future. Possible replay attack.
        return False

    # 2. Prepare the Signed Payload
    # The standard format is: {timestamp}.{raw_body}
    if isinstance(raw_body, str):
        raw_body_bytes = raw_body.encode('utf-8')
    else:
        raw_body_bytes = raw_body

    # Concatenate timestamp and raw body with a separator
    payload = f"{timestamp}.".encode('utf-8') + raw_body_bytes

    # 3. Compute the Expected Signature
    # We use HMAC-SHA256 with the developer's webhook secret.
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    # 4. Constant-Time Comparison
    # We use hmac.compare_digest to prevent timing attacks where an attacker
    # might guess the signature by measuring the time it takes to compare characters.
    return hmac.compare_digest(computed_signature, signature)

# --- Usage Example (FastAPI / Flask) ---
# 
# from core.utils.webhook_auth import verify_signature
#
# @app.post("/webhook")
# async def webhook_handler(request: Request):
#     # CRITICAL: Use .body() to get raw bytes, NOT .json()
#     body = await request.body()
#     sig = request.headers.get("X-Proxy-Signature")
#     ts = request.headers.get("X-Proxy-Request-Timestamp")
#     
#     if not verify_signature(body, sig, ts, os.getenv("WEBHOOK_SECRET")):
#         raise HTTPException(status_code=401, detail="Invalid HMAC Signature")
#
#     # Now it's safe to parse the JSON
#     data = json.loads(body)
#     ...
