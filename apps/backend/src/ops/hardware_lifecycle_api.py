import time
import logging
import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# PROXY PROTOCOL - HARDWARE LIFECYCLE API (v1.0)
# "Managing the rotation of the silicon shadow."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Lifecycle Manager",
    description="Orchestrates TPM identity rotation and unit decommissioning.",
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
    Handles the cryptographic transition of hardware nodes
    from 'Active' to 'Rotated' or 'Decommissioned'.
    """
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("LifecycleManager")

   # Ensure 'self' is the first word inside the parentheses here!
    def rotate_identity(self, payload: IdentityRotationPayload) -> Dict:
        """
        Communicates with the node's local TPM agent...
        """
        # This is where 'self' was failing because it wasn't in the line above
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
        Marks a hardware unit as permanently inactive in the global registry.
        Requires a wipe confirmation from the local TPM proxy.
        """
        self.logger.warning(f"[!] DECOMMISSION START: Unit {request.unit_id}")
        
        if not request.wipe_confirmation:
            raise ValueError("Wipe confirmation must be True to decommission hardware.")

        return {
            "status": "DECOMMISSIONED",
            "unit_id": request.unit_id,
            "registry_update": "FINALIZED"
        }

# Initialize the Manager instance
lifecycle_manager = HardwareLifecycleManager()

# --- API Endpoints ---

@app.post("/v1/hardware/lifecycle/rotate")
async def rotate_node_identity(payload: IdentityRotationPayload):
    """
    Endpoint for periodic identity rotation as mandated by PIP-015.
    """
    try:
        return lifecycle_manager.rotate_identity(payload)
    except Exception as e:
        lifecycle_manager.logger.error(f"Rotation Failure: {str(e)}")
        raise HTTPException(status_code=500, detail="ROTATION_SERVICE_UNAVAILABLE")

@app.post("/v1/hardware/lifecycle/decommission")
async def decommission_node(request: DecommissionRequest):
    """
    Removes a node from the network and revokes its Hardware ID.
    """
    try:
        return lifecycle_manager.decommission_unit(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="DECOMMISSION_SERVICE_FAILURE")

@app.get("/health")
async def health():
    return {"status": "online", "subsystem": "lifecycle_manager"}

# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn
    # Launched on port 8019 for lifecycle orchestration
    print("[*] Launching Protocol Hardware Lifecycle API on port 8019...")
    uvicorn.run(app, host="0.0.0.0", port=8019)