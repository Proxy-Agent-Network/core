import time
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

# PROXY PROTOCOL - IDENTITY AUDITOR API (v1.0)
# "One DID, one Box. Preventing the Sybil Clone."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Identity Auditor",
    description="Detects and quarantines coordinated Sybil identity cloning attempts.",
    version="1.0.0"
)

# --- Models ---

class IdentityAuditReport(BaseModel):
    did: str
    is_cloned: bool
    active_bindings: List[str] # List of Hardware IDs
    risk_level: str # NOMINAL, ELEVATED, CRITICAL
    status: str # ACTIVE, QUARANTINED, INVESTIGATING

class DoubleSignAlert(BaseModel):
    did: str
    hardware_id_a: str
    hardware_id_b: str
    timestamp: int
    proof_hash: str

# --- Internal Auditor Logic ---

class IdentityAuditor:
    """
    Maintains a real-time observation window of DID-to-Hardware heartbeats.
    Identifies if a human is attempting to run their identity on multiple units.
    """
    def __init__(self):
        # Format: { "did": { "active_hw": "ID", "last_ping": float, "history": [] } }
        self.active_session_registry: Dict[str, Dict] = {
            "did:proxy:8A2E1C": {
                "active_hw": "SENTRY-JP-001",
                "last_ping": time.time(),
                "status": "ACTIVE"
            }
        }
        self.quarantine_list: List[str] = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("IdentityAuditor")

    def audit_heartbeat(self, did: str, hardware_id: str) -> Tuple[bool, str]:
        """
        Gatekeeper for incoming telemetry. 
        Checks if the hardware_id matches the current authorized vessel for the DID.
        """
        session = self.active_session_registry.get(did)
        
        if not session:
            # First time seeing this DID in the current epoch
            self.active_session_registry[did] = {
                "active_hw": hardware_id,
                "last_ping": time.time(),
                "status": "ACTIVE"
            }
            return True, "NEW_SESSION_REGISTERED"

        # Check for Mismatch (The Double-Sign)
        if session["active_hw"] != hardware_id:
            # Check if this is a stale session or a simultaneous clone
            time_since_last = time.time() - session["last_ping"]
            
            if time_since_last < 300: # 5 Minute overlap window
                self.logger.critical(f"🚨 CLONE DETECTED: {did} active on {session['active_hw']} AND {hardware_id}")
                session["status"] = "QUARANTINED"
                if did not in self.quarantine_list:
                    self.quarantine_list.append(did)
                return False, "PX_400: SYBIL_IDENTITY_CLONE_DETECTED"
            
            # If time has passed, assume a migration happened without the API notify
            self.logger.warning(f"[*] Informal migration detected for {did}. Updating binding.")
            session["active_hw"] = hardware_id
            
        session["last_ping"] = time.time()
        return True, "STABLE"

    def get_report(self, did: str) -> IdentityAuditReport:
        session = self.active_session_registry.get(did)
        if not session:
            return IdentityAuditReport(
                did=did, is_cloned=False, active_bindings=[], 
                risk_level="UNKNOWN", status="NOT_FOUND"
            )

        is_cloned = session["status"] == "QUARANTINED"
        
        return IdentityAuditReport(
            did=did,
            is_cloned=is_cloned,
            active_bindings=[session["active_hw"]],
            risk_level="CRITICAL" if is_cloned else "NOMINAL",
            status=session["status"]
        )

# Initialize Auditor
auditor = IdentityAuditor()

# --- API Endpoints ---

@app.get("/v1/audit/identity/{did}", response_model=IdentityAuditReport)
async def check_identity_standing(did: str):
    """Returns the current auditing status for a Decentralized Identifier."""
    return auditor.get_report(did)

@app.post("/v1/audit/pulse")
async def ingest_audit_pulse(did: str, hardware_id: str):
    """
    Internal callback for the Telemetry Sink.
    Verifies the hardware-to-identity binding in real-time.
    """
    valid, msg = auditor.audit_heartbeat(did, hardware_id)
    if not valid:
        raise HTTPException(status_code=403, detail=msg)
    return {"status": "VERIFIED", "msg": msg}

@app.get("/v1/audit/quarantine", response_model=List[str])
async def list_quarantined_identities():
    """Returns all DIDs currently suspended due to cloning attempts."""
    return auditor.quarantine_list

@app.get("/health")
async def health():
    return {"status": "online", "auditor_mode": "STRICT_BINDING"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8016 for security orchestration
    print("[*] Launching Protocol Identity Auditor API on port 8016...")
    uvicorn.run(app, host="0.0.0.0", port=8016)
