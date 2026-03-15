import time
import logging
import json
import hashlib
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# PROXY PROTOCOL - SECURITY INCIDENT API (v1.0)
# "The forensic record of node compromise."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Security Incident API",
    description="Aggregates and adjudicates physical security breaches and tamper events.",
    version="1.0.0"
)

# --- Models ---

class IncidentType(str):
    CHASSIS_INTRUSION = "CHASSIS_INTRUSION"
    GEOFENCE_VIOLATION = "GEOFENCE_VIOLATION"
    PCR_DRIFT = "PCR_DRIFT"
    BRUTE_FORCE_DETECTED = "BRUTE_FORCE_DETECTED"

class IncidentIngest(BaseModel):
    unit_id: str
    incident_type: str
    evidence_b64: Optional[str] = None # Binary proof from TPM2_Clear or Logs
    coordinates: Optional[str] = None
    telemetry_snapshot: Dict = {}

class IncidentRecord(BaseModel):
    incident_id: str
    unit_id: str
    type: str
    severity: str # CRITICAL, ELEVATED, LOW
    status: str # ACTIVE, RESOLVED, BANNED
    timestamp: int
    coordinates: Optional[str] = None
    insurance_claim_eligible: bool = False
    rejection_reason: Optional[str] = None

# --- Internal Security Logic ---

class SecurityIncidentManager:
    """
    Handles the lifecycle of security breaches.
    Coordinates with the InsuranceEngine to automatically reject claims 
    arising from physical tampering.
    """
    def __init__(self):
        # Format: { "incident_id": IncidentRecord }
        self.ledger: Dict[str, IncidentRecord] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SecurityIncident")

    def log_breach(self, data: IncidentIngest) -> IncidentRecord:
        """
        Creates a permanent record of a hardware breach.
        """
        now = int(time.time())
        incident_id = f"INT-{hashlib.md5(f'{data.unit_id}:{now}'.encode()).hexdigest()[:8].upper()}"
        
        # Automated Rule: Physical tamper events (Intrusion) are NEVER insurance eligible
        eligible = False
        rejection = None
        
        if data.incident_type == "CHASSIS_INTRUSION":
            rejection = "PX_ERR: Insurance explicitly excluded for physical chassis compromise (Rule 8.4)."
        
        severity = "CRITICAL" if data.incident_type in ["CHASSIS_INTRUSION", "BRUTE_FORCE_DETECTED"] else "ELEVATED"

        record = IncidentRecord(
            incident_id=incident_id,
            unit_id=data.unit_id,
            type=data.incident_type,
            severity=severity,
            status="IDENTITY_WIPED" if severity == "CRITICAL" else "INVESTIGATING",
            timestamp=now,
            coordinates=data.coordinates,
            insurance_claim_eligible=eligible,
            rejection_reason=rejection
        )
        
        self.ledger[incident_id] = record
        self.logger.critical(f"🚨 BREACH RECORDED: {incident_id} for unit {data.unit_id} ({data.incident_type})")
        
        return record

    def get_incidents_for_node(self, unit_id: str) -> List[IncidentRecord]:
        return [i for i in self.ledger.values() if i.unit_id == unit_id]

# Initialize Manager
sec_manager = SecurityIncidentManager()

# --- API Endpoints ---

@app.post("/v1/security/incident", response_model=IncidentRecord)
async def log_incident(payload: IncidentIngest):
    """
    Callback for node_daemon.py and tamper_listener.py.
    Records the 'Dying Breath' or geofence violation of a node.
    """
    return sec_manager.log_breach(payload)

@app.get("/v1/security/incidents", response_model=List[IncidentRecord])
async def list_all_incidents():
    """Returns the full history for the Tamper Sentinel dashboard."""
    return list(sec_manager.ledger.values())

@app.get("/v1/security/incidents/{incident_id}", response_model=IncidentRecord)
async def get_incident(incident_id: str):
    """Retrieves forensic details for a specific breach."""
    record = sec_manager.ledger.get(incident_id)
    if not record:
        raise HTTPException(status_code=404, detail="Incident ID not found.")
    return record

@app.get("/v1/security/audit/insurance/{unit_id}")
async def audit_insurance_eligibility(unit_id: str):
    """
    Internal check for the Insurance Engine.
    Determines if a node's claim should be auto-rejected based on historical breaches.
    """
    breaches = sec_manager.get_incidents_for_node(unit_id)
    critical_breaches = [b for b in breaches if b.severity == "CRITICAL"]
    
    return {
        "unit_id": unit_id,
        "has_physical_tamper_history": len(critical_breaches) > 0,
        "recommended_payout_action": "REJECT" if critical_breaches else "ALLOW_REVIEW",
        "breach_count": len(breaches)
    }

@app.get("/health")
async def health():
    return {"status": "online", "watchdog": "active", "security_standard": "PX_SILICON_V1"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8020 for security/ops traffic
    print("[*] Launching Protocol Security Incident API on port 8020...")
    uvicorn.run(app, host="0.0.0.0", port=8020)
