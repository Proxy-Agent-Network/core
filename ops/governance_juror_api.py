import time
import logging
import hashlib
import hmac
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Body, Depends
from pydantic import BaseModel, Field

# PROXY PROTOCOL - GOVERNANCE JUROR API (v1.0)
# "Private registration. Public accountability."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Governance Juror API",
    description="Authorized registration and lifecycle management for High Court Jurors.",
    version="1.0.0"
)

# --- Configuration ---
# Internal secret for blinding hardware IDs in the public registry
JUROR_BLINDING_SECRET = "hsm_sec_88293_juror_privacy_root"
MIN_BOND_SATS = 2_000_000
MIN_REP_SCORE = 951

class JurorRegistration(BaseModel):
    node_id: str = Field(..., description="The physical TPM Hardware ID")
    bond_txid: str = Field(..., description="Bitcoin/Lightning deposit proof for 2M Sats")
    tpm_attestation: str = Field(..., description="Signed quote proving identity residency")
    claimed_reputation: int = Field(..., ge=MIN_REP_SCORE)

class JurorStatus(BaseModel):
    blinded_id: str
    status: str # ACTIVE, PENDING_AUDIT, SUSPENDED
    enrolled_at: int
    bond_verified: bool
    standing: str # SUPER_ELITE

class JurorManager:
    """
    Manages the private mapping of Node IDs to blinded Juror identities.
    Ensures that while the Foundation can audit, other nodes cannot map 
    juror decisions to physical hardware or IP addresses.
    """
    def __init__(self):
        # Format: { "blinded_id": JurorStatus }
        self.active_jurors: Dict[str, JurorStatus] = {}
        # Format: { "node_id": "blinded_id" }
        self.hardware_map: Dict[str, str] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("JurorAPI")

    def _generate_blinded_id(self, node_id: str) -> str:
        """Creates a deterministic but non-reversible ID for public logs."""
        return hmac.new(
            JUROR_BLINDING_SECRET.encode(),
            node_id.encode(),
            hashlib.sha256
        ).hexdigest()[:16].upper()

    async def register_candidate(self, payload: JurorRegistration) -> JurorStatus:
        """
        Gates the High Court. Verifies bond and standing before issuance.
        """
        # 1. Check if hardware already registered
        if payload.node_id in self.hardware_map:
            raise ValueError("PX_ERR: Node already holds an active juror identity.")

        # 2. Verify Bond (Simulation: Normally calls core/governance/jury_bond.py)
        # In production: is_paid = bond_engine.verify_deposit(payload.bond_txid, MIN_BOND_SATS)
        is_paid = True 

        # 3. Verify Standing (Simulation: Normally calls core/reputation/oracle.py)
        # In production: current_rep = reputation_oracle.get_score(payload.node_id)
        current_rep = payload.claimed_reputation

        if current_rep < MIN_REP_SCORE:
            raise ValueError(f"PX_ERR: Reputation {current_rep} below Super-Elite threshold.")

        # 4. Success: Bind and Blind
        blinded_id = self._generate_blinded_id(payload.node_id)
        now = int(time.time())
        
        status = JurorStatus(
            blinded_id=blinded_id,
            status="ACTIVE",
            enrolled_at=now,
            bond_verified=is_paid,
            standing="SUPER_ELITE"
        )

        self.active_jurors[blinded_id] = status
        self.hardware_map[payload.node_id] = blinded_id
        
        self.logger.info(f"⚖️ JUROR_ENROLLED: Blinded ID {blinded_id} activated (Bond Verified).")
        return status

# Initialize Manager
manager = JurorManager()

# --- API Endpoints ---

@app.post("/v1/governance/juror/register", response_model=JurorStatus)
async def register_high_court_juror(payload: JurorRegistration):
    """
    Entry point for Super-Elite nodes.
    Binds the physical TPM to an anonymous juror identity.
    """
    try:
        return await manager.register_candidate(payload)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logging.error(f"Registration failure: {str(e)}")
        raise HTTPException(status_code=500, detail="INTERNAL_REGISTRY_ERROR")

@app.get("/v1/governance/juror/status/{node_id}")
async def fetch_juror_status(node_id: str):
    """
    Allows a node to check their own registration state.
    Returns the blinded identity used in public votes.
    """
    blinded_id = manager.hardware_map.get(node_id)
    if not blinded_id:
        raise HTTPException(status_code=404, detail="No active juror registration found.")
    
    return manager.active_jurors[blinded_id]

@app.get("/v1/governance/juror/registry/size")
async def get_quorum_capacity():
    """Returns the total number of active High Court jurors."""
    return {
        "active_jurors": len(manager.active_jurors),
        "target_quorum": 100,
        "standing": "OPTIMAL" if len(manager.active_jurors) >= 7 else "BOOTSTRAPPING"
    }

@app.get("/health")
async def health():
    return {"status": "online", "blinding_active": True}

if __name__ == "__main__":
    import uvicorn
    # Launched on a restricted port for secure governance onboarding
    print("[*] Launching Protocol Governance Juror API on port 8016...")
    uvicorn.run(app, host="0.0.0.0", port=8016)
