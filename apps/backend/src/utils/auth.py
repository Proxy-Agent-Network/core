import logging
import jwt
import base64
from cryptography.x509 import load_der_x509_certificate
from cryptography.hazmat.backends import default_backend
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("PAN_Auth")
security = HTTPBearer(auto_error=False)

async def verify_agent_jwt(token: str, redis_client) -> str:
    """
    Core cryptographic verification of the hardware JWT.
    Can be used by HTTP dependencies and WebSockets.
    """
    agent_id = None 
    
    try:
        # 1. Extract agent_id without verifying (yet)
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        agent_id = unverified_payload.get("sub")
        
        if not agent_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject (agent_id)")
            
        # 2. Fetch the agent's Public Key from Redis
        pub_key_b64 = await redis_client.get(f"pan:agent:{agent_id}:pubkey")
        
        if not pub_key_b64:
            raise HTTPException(status_code=401, detail="Hardware public key not found. Please re-run Key Ceremony.")
            
        # 3. Convert Android's Base64 DER X.509 Certificate to a Cryptography Public Key
        try:
            cert_der = base64.urlsafe_b64decode(pub_key_b64)
            cert = load_der_x509_certificate(cert_der, default_backend())
            public_key = cert.public_key()
        except Exception as e:
            logger.error(f"Failed to parse public key for {agent_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal key resolution error.")
            
        # 4. Cryptographic Verification
        jwt.decode(token, public_key, algorithms=["ES256"], audience="pan_ops_hub")
        
        logger.info(f"🔐 Hardware JWT validated for {agent_id}")
        return agent_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Hardware token expired. Please sync device time.")
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT Verification failed for agent '{agent_id}': {e}")
        raise HTTPException(status_code=401, detail="Cryptographic verification failed. Possible tampering detected.")


async def verify_agent_signature(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verifies the incoming hardware JWT from HTTP Authorization headers.
    Protects the fleet bounty escrows from spoofing attacks.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required.")
        
    token = credentials.credentials
    redis_client = request.app.state.redis_client
    
    # Pass the token and Redis client to our new core validation function
    return await verify_agent_jwt(token, redis_client)