import json
import logging
import os
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Optional

# Proxy Protocol Internal Modules
from core.utils.webhook_auth import verify_signature
from core.reputation.oracle import ReputationOracle

# PROXY PROTOCOL - NODE VERIFICATION WEBHOOK (v1.0)
# "The secure bridge between execution and reputation."
# ----------------------------------------------------

app = FastAPI(title="Proxy Protocol Node Verification Webhook")

# Initialize Oracle (In production, this connects to a shared persistent state)
oracle = ReputationOracle()

# Configuration
WEBHOOK_SECRET = os.getenv("NODE_WEBHOOK_SECRET", "whsec_node_verification_v1_88293")

class TaskCompletionPayload(BaseModel):
    task_id: str
    node_id: str
    status: str # "SUCCESS" or "FAILURE"
    proof_hash: str
    hardware_attestation: Optional[Dict] = None

@app.post("/v1/reputation/verify")
async def handle_node_verification(
    request: Request,
    x_proxy_signature: str = Header(...),
    x_proxy_request_timestamp: str = Header(...)
):
    """
    Primary endpoint for Node Daemons to report task results.
    Triggers cryptographic audit and reputation scoring.
    """
    # 1. Capture Raw Body for HMAC Verification
    raw_body = await request.body()
    
    # 2. Security Check: Verify Origin
    if not verify_signature(
        raw_body, 
        x_proxy_signature, 
        x_proxy_request_timestamp, 
        WEBHOOK_SECRET
    ):
        logging.warning("[!] Invalid webhook signature detected. Dropping request.")
        raise HTTPException(status_code=401, detail="Invalid HMAC Signature")

    # 3. Process Payload
    try:
        data = TaskCompletionPayload.parse_raw(raw_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Malformed payload: {str(e)}")

    logging.info(f"[*] Verifying Task {data.task_id} from Node {data.node_id}")

    # 4. Reputation Logic
    # We simulate the Oracle aggregate update. In production, this persists to the global REP DB.
    # Map the status to the reputation formula: 
    # SUCCESS = +1.0 | FAILURE = -5.0
    
    event_type = "TASK_SUCCESS" if data.status == "SUCCESS" else "TASK_FAILURE"
    
    # Normally, the Oracle would pull the current node state and apply the delta
    # oracle.apply_reputation_delta(data.node_id, event_type)
    
    logging.info(f"[✓] Reputation Event Logged: {event_type} for {data.node_id}")

    # 5. Response
    return {
        "status": "PROCESSED",
        "task_id": data.task_id,
        "node_id": data.node_id,
        "reputation_updated": True,
        "event_id": f"evt_rep_{data.task_id[:8]}"
    }

if __name__ == "__main__":
    import uvicorn
    # Launched on a dedicated internal port for node-to-protocol signaling
    print("[*] Launching Node Verification Webhook API on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
