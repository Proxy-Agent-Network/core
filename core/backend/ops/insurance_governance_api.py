import time
import logging
import json
import hashlib
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from datetime import datetime

# PROXY PROTOCOL - INSURANCE GOVERNANCE API (v1.0)
# "Human oversight for algorithmic economics."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Insurance Governance",
    description="Authorized override service for actuary fees and liquidity management.",
    version="1.0.0"
)

# --- UI Component Definitions (Wrapped to prevent Syntax Errors) ---
# These are used by the dashboard to render the governance status.

GOVERNANCE_WIDGET_TEMPLATE = """
<div className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${prop.severity === 'CRITICAL' ? 'bg-red-500/10 border-red-500/20 text-red-500' : 'bg-amber-500/10 border-amber-500/20 text-amber-500'}`}>
    {prop.label}
</div>
"""

# --- Models ---

class FeeOverride(BaseModel):
    juror_id: str
    target_levy: float = Field(..., ge=0.0001, le=0.01) # Max 1% manual cap
    jurisdiction_filter: Optional[str] = None # e.g. "ASIA_SE"
    duration_minutes: int = 1440 # Default 24h
    reason: str
    hardware_attestation: str # TPM-signed proof of juror identity

class LiquidityFreeze(BaseModel):
    juror_id: str
    freeze_type: str # FULL_RESERVE, REGIONAL_OUTFLOW, NEW_CLAIMS_ONLY
    target_hub: Optional[str] = None
    quarantine_proof: str # Hash of the anomaly report triggering the freeze
    juror_signature: str

class GovernanceStatus(BaseModel):
    is_frozen: bool
    active_overrides: List[Dict]
    last_action_timestamp: int
    quorum_id: str

# --- Internal Governance Logic ---

class InsuranceGovernanceManager:
    """
    Manages the manual intervention layer for the Protocol's economy.
    Communicates with the Actuary API and Escrow Manager to enforce overrides.
    """
    def __init__(self):
        self.is_frozen = False
        self.active_overrides: Dict[str, Dict] = {}
        self.action_history: List[Dict] = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("InsuranceGov")

    def authorize_fee_override(self, data: FeeOverride) -> str:
        """
        Sets a manual ceiling or floor on the actuary-calculated tax.
        Requires Super-Elite (950+ REP) juror signatures.
        """
        now = int(time.time())
        override_id = f"OVR-{hashlib.md5(f'{data.juror_id}:{now}'.encode()).hexdigest()[:8].upper()}"
        
        override_entry = {
            "id": override_id,
            "juror": data.juror_id,
            "levy_limit": data.target_levy,
            "region": data.jurisdiction_filter or "GLOBAL",
            "expires_at": now + (data.duration_minutes * 60),
            "reason": data.reason
        }
        
        self.active_overrides[override_id] = override_entry
        self.logger.critical(f"⚖️ ECONOMIC_OVERRIDE: {override_id} set by {data.juror_id} (Limit: {data.target_levy*100:.4f}%)")
        
        return override_id

    def trigger_emergency_freeze(self, data: LiquidityFreeze) -> bool:
        """
        Executes a "Scorched Earth" liquidity lock.
        Immediately stops all keysend payouts from the insurance pool.
        """
        self.is_frozen = True
        event = {
            "type": "LIQUIDITY_FREEZE",
            "freeze_scope": data.freeze_type,
            "juror": data.juror_id,
            "timestamp": int(time.time()),
            "hub": data.target_hub or "GLOBAL"
        }
        self.action_history.append(event)
        self.logger.critical(f"🚨 LIQUIDITY_FREEZE: Executed by {data.juror_id}. Scope: {data.freeze_type}")
        
        return True

# Initialize Manager
gov_manager = InsuranceGovernanceManager()

# --- API Endpoints ---

@app.post("/v1/governance/fee/override")
async def apply_fee_override(payload: FeeOverride):
    """
    High Court endpoint to manually adjust or cap the protocol levy.
    """
    # 1. Verify Juror Eligibility (Mocked)
    # 2. Process Override
    override_id = gov_manager.authorize_fee_override(payload)
    return {"status": "ACTIVE", "override_id": override_id}

@app.post("/v1/governance/emergency/freeze")
async def activate_liquidity_freeze(payload: LiquidityFreeze):
    """
    Emergency kill-switch for Satoshi outflows during a systemic exploit.
    """
    success = gov_manager.trigger_emergency_freeze(payload)
    if not success:
        raise HTTPException(status_code=500, detail="Freeze command execution failed.")
    return {"status": "FROZEN", "timestamp": int(time.time())}

@app.get("/v1/governance/status", response_model=GovernanceStatus)
async def get_governance_summary():
    """Returns the current state of manual overrides for the Health Matrix."""
    return GovernanceStatus(
        is_frozen=gov_manager.is_frozen,
        active_overrides=list(gov_manager.active_overrides.values()),
        last_action_timestamp=int(time.time()) if not gov_manager.action_history else gov_manager.action_history[-1]["timestamp"],
        quorum_id="HIGH_COURT_QUORUM_V3"
    )

@app.get("/health")
async def health():
    return {"status": "online", "governance_mode": "MANUAL_OVERRIDE_ENABLED"}

if __name__ == "__main__":
    import uvicorn
    # Launched on port 8025 for economic governance traffic
    print("[*] Launching Protocol Insurance Governance API on port 8025...")
    uvicorn.run(app, host="0.0.0.0", port=8025)
