import time
import logging
import json
import requests
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field

# PROXY PROTOCOL - PROBING QUARANTINE API (v1.0)
# "Automated containment for coordinated forensic attacks."
# --------------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Probing Quarantine",
    description="Automated enforcement service triggered by differential forensic anomalies.",
    version="1.0.0"
)

# --- Configuration ---
# Thresholds for automated action
AUTO_QUARANTINE_THRESHOLD = 0.90 # 90% probability triggers instant lock
SUBNET_PREFIX_LENGTH = 24

# Internal API Endpoints
THREAT_INTEL_URL = "http://localhost:8021/v1/threat/update"
HARDWARE_REGISTRY_URL = "http://localhost:8010/v1/hardware"

class QuarantineRequest(BaseModel):
    investigation_id: str
    target_node_id: str
    target_ip: str
    probing_probability: float
    forensic_distance: float
    evidence_summary: str

class QuarantineReceipt(BaseModel):
    action_id: str
    status: str # QUARANTINED, REVOKED, ESCALATED
    blacklisted_pattern: str
    tpm_revoked: bool
    timestamp: int

class QuarantineManager:
    """
    Orchestrates the automated lockout of malicious actors.
    Interfaces with the Threat Intelligence and Hardware Registry layers.
    """
    def __init__(self):
        self.action_history: List[Dict] = []
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("QuarantineAPI")

    def _blacklist_subnet(self, ip: str, reason: str) -> bool:
        """Calls the Threat Intel API to block the /24 prefix."""
        prefix = ".".join(ip.split(".")[:3]) + "."
        payload = {
            "source_name": "AUTO_QUARANTINE_ENGINE",
            "target_pattern": prefix,
            "reason": f"PROBING_SEQUENCE_DETECTED: {reason}",
            "expiry": int(time.time() + 604800) # 7-day initial lock
        }
        
        try:
            # Simulation: requests.post(THREAT_INTEL_URL, json=payload)
            self.logger.critical(f"🚫 BLACKLISTED: Subnet {prefix}0/{SUBNET_PREFIX_LENGTH}")
            return True
        except Exception as e:
            self.logger.error(f"[!] Threat Intel sync failed: {str(e)}")
            return False

    def _revoke_tpm_identity(self, node_id: str) -> bool:
        """Marks a TPM ID as permanently untrusted."""
        try:
            # Simulation: requests.patch(f"{HARDWARE_REGISTRY_URL}/{node_id}/status", json={"status": "TAMPERED"})
            self.logger.critical(f"💀 REVOKED: Node {node_id} attestation authority cancelled.")
            return True
        except Exception as e:
            self.logger.error(f"[!] Registry sync failed: {str(e)}")
            return False

    async def execute_containment(self, data: QuarantineRequest) -> QuarantineReceipt:
        """
        Decision engine for automated enforcement.
        """
        now = int(time.time())
        action_id = f"QRN-{data.investigation_id[:4]}-{now}"
        
        # 1. High Probability Containment
        if data.probing_probability >= AUTO_QUARANTINE_THRESHOLD:
            self.logger.warning(f"[*] Executing Scorched Earth for {data.target_node_id}")
            
            # Action A: Block Network Access
            net_success = self._blacklist_subnet(data.target_ip, data.evidence_summary)
            
            # Action B: Brute-Force Identity Revocation
            tpm_success = self._revoke_tpm_identity(data.target_node_id)
            
            receipt = QuarantineReceipt(
                action_id=action_id,
                status="REVOKED",
                blacklisted_pattern=".".join(data.target_ip.split(".")[:3]) + ".0/24",
                tpm_revoked=tpm_success,
                timestamp=now
            )
        else:
            # 2. Moderate Probability Escalation
            self.logger.info(f"[*] Escalating {data.investigation_id} to High Court for manual review.")
            receipt = QuarantineReceipt(
                action_id=action_id,
                status="ESCALATED",
                blacklisted_pattern="NONE",
                tpm_revoked=False,
                timestamp=now
            )

        self.action_history.append(receipt.dict())
        return receipt

# Initialize Manager
manager = QuarantineManager()

# --- API Endpoints ---

@app.post("/v1/quarantine/enforce", response_model=QuarantineReceipt)
async def trigger_quarantine(payload: QuarantineRequest):
    """
    Endpoint for the Differential Forensic API or SOC Desk.
    Initiates automated node/subnet lockout.
    """
    try:
        return await manager.execute_containment(payload)
    except Exception as e:
        logging.error(f"Quarantine execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail="INTERNAL_CONTAINMENT_ERROR")

@app.get("/v1/quarantine/ledger")
async def get_quarantine_history():
    """Returns a list of all automated enforcement actions."""
    return manager.action_history

@app.get("/health")
async def health():
    return {"status": "online", "auto_enforcement": "STRICT"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal security port 8028
    print("[*] Launching Protocol Probing Quarantine API on port 8028...")
    uvicorn.run(app, host="0.0.0.0", port=8028)
