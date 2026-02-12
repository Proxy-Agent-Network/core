import time
import logging
import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# PROXY PROTOCOL - HARDWARE LIFECYCLE API (v1.0)
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Lifecycle Manager",
    description="Orchestrates TPM identity rotation.",
    version="1.0.0"
)

# --- Models ---

class IdentityRotationPayload(BaseModel):
    unit_id: str
    new_alias: str
    auth_token: str

class DecommissionRequest(BaseModel):
    unit_id: str
    reason: str
    wipe_confirmation: bool

# --- Lifecycle Logic ---

class HardwareLifecycleManager:
    """
    Handles the cryptographic transition of hardware nodes.
    """
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("LifecycleManager")

    def rotate_identity(self, payload: IdentityRotationPayload) -> Dict:
        """
        Communicates with the node's local TPM agent.
        """
        # Line 119: This is now explicitly inside the HardwareLifecycleManager class.
        self.logger.info(f"[*] Identity Rotation requested for {payload.unit_id}")
        
        rotation_event_id = hashlib.sha256(f"{payload.unit_id}:{time.time()}".encode()).hexdigest()[:12]
        
        return {
            "status": "ROTATION_PENDING",
            "unit_id": payload.unit_id,
            "event_id": rotation_event_id,
            "next_step": "AWAITING_TPM_PREIMAGE"
        }

    def decommission_unit(self, request: DecommissionRequest) -> Dict:
        """
        Marks a hardware unit as permanently inactive.
        """
        self.logger.warning(f"[!] DECOMMISSION START: Unit {request.unit_id}")
        
        if not request.wipe_confirmation:
            raise ValueError("Wipe confirmation must be True.")

        return {
            "status": "DECOMMISSIONED",
            "unit_id": request.unit_id
        }

# Initialize global instance
lifecycle_manager = HardwareLifecycleManager()

# --- API Endpoints ---

@app.post("/v1/hardware/lifecycle/rotate")
async def rotate_node_identity(payload: IdentityRotationPayload):
    try:
        return lifecycle_manager.rotate_identity(payload)
    except Exception as e:
        lifecycle_manager.logger.error(f"Rotation Failure: {str(e)}")
        raise HTTPException(status_code=500, detail="ROTATION_SERVICE_UNAVAILABLE")

@app.post("/v1/hardware/lifecycle/decommission")
async def decommission_node(request: DecommissionRequest):
    try:
        return lifecycle_manager.decommission_unit(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="DECOMMISSION_SERVICE_FAILURE")

@app.get("/health")
async def health():
    return {"status": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)
