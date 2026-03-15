import time
import logging
import json
import statistics
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

# PROXY PROTOCOL - INSURANCE ACTUARY API (v1.0)
# "Programmatic solvency through dynamic risk weighting."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Insurance Actuary",
    description="Real-time risk assessment and dynamic levy adjustment service.",
    version="1.0.0"
)

# --- Models ---

class NetworkVitals(BaseModel):
    velocity_sats_sec: float
    mempool_saturation: float
    failure_rate: float
    active_disputes: int
    pool_balance_sats: int

class ActuarialAudit(BaseModel):
    audit_id: str
    timestamp: int
    default_probability: float
    recommended_levy: float
    solvency_index: float # 0.0 to 1.0 (Target is 1.0)
    risk_classification: str # NOMINAL, ELEVATED, CRITICAL

# --- Internal Actuarial Logic ---

class InsuranceActuaryEngine:
    """
    Automates the calculation of network-wide financial risk.
    Drives the 'Active Tax Controller' logic in the Solvency Dashboard.
    """
    def __init__(self):
        # Constants from core/ops/insurance_actuary.py (v1.0 logic)
        self.BASE_LEVY = 0.001       # 0.1%
        self.MAX_LEVY = 0.005        # 0.5% cap
        self.SOLVENCY_TARGET_SATS = 100_000_000 # 1.0 BTC target
        self.VELOCITY_STRESS_THRESHOLD = 5000 
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ActuaryAPI")

    def run_analysis(self, vitals: NetworkVitals) -> ActuarialAudit:
        """
        Calculates the required premium adjustment based on Bayesian probability.
        """
        self.logger.info("[*] Running systemic solvency analysis...")

        # 1. Calculate Default Probability
        # Factor A: Throughput Stress
        velocity_risk = min(1.0, vitals.velocity_sats_sec / (self.VELOCITY_STRESS_THRESHOLD * 2))
        # Factor B: Network Reliability
        failure_risk = min(1.0, vitals.failure_rate / 0.15) # 15% is system failure limit
        # Factor C: Adjudication Stress
        dispute_risk = min(1.0, vitals.active_disputes / 10)

        prob = (velocity_risk * 0.3) + (failure_risk * 0.5) + (dispute_risk * 0.2)
        prob = round(max(0.0, min(1.0, prob)), 4)

        # 2. Determine Dynamic Levy
        # Increase tax by up to 5x if risk is 1.0
        risk_adjustment = prob * self.MAX_LEVY
        
        # Solvency boost: increase collection if pool is shallow
        solvency_index = vitals.pool_balance_sats / self.SOLVENCY_TARGET_SATS
        solvency_multiplier = 1.0 + (1.0 - min(1.0, solvency_index))
        
        final_levy = (self.BASE_LEVY + risk_adjustment) * solvency_multiplier
        clamped_levy = round(max(0.0001, min(self.MAX_LEVY, final_levy)), 6)

        # 3. Classify Risk
        classification = "NOMINAL"
        if prob > 0.6 or solvency_index < 0.2:
            classification = "CRITICAL"
        elif prob > 0.3 or solvency_index < 0.5:
            classification = "ELEVATED"

        audit_id = f"ACT-{int(time.time())}-{classification[:1]}"

        return ActuarialAudit(
            audit_id=audit_id,
            timestamp=int(time.time()),
            default_probability=prob,
            recommended_levy=clamped_levy,
            solvency_index=round(solvency_index, 4),
            risk_classification=classification
        )

# Initialize Engine
engine = InsuranceActuaryEngine()

# --- API Endpoints ---

@app.post("/v1/actuary/audit", response_model=ActuarialAudit)
async def perform_risk_audit(vitals: NetworkVitals):
    """
    Primary endpoint for the Master Orchestrator.
    Generates the risk profile used to adjust protocol fees.
    """
    try:
        return engine.run_analysis(vitals)
    except Exception as e:
        logging.error(f"Actuarial failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal actuarial error.")

@app.get("/v1/actuary/levy/current")
async def get_active_levy():
    """
    Public lookup for Agent SDKs.
    Returns the current insurance tax required for task broadcasting.
    """
    # Simulation: Normally this pulls the last finalized audit from cache
    return {
        "active_levy": 0.0014,
        "base_levy": 0.001,
        "surcharge": 0.0004,
        "reason": "ELEVATED_FAILURE_RATE_ASIA_SE",
        "timestamp": int(time.time())
    }

@app.get("/v1/actuary/projections")
async def get_solvency_projections():
    """Returns predictive data for the Solvency Dashboard's sensitivity curve."""
    return {
        "time_to_insolvency": "> 365 Days",
        "burn_rate_avg_sats_hour": 12500,
        "collection_rate_avg_sats_hour": 42000,
        "net_surplus_active": True
    }

@app.get("/health")
async def health():
    return {"status": "online", "model_version": "BAYES_SOLVENCY_V1"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8024 for economic orchestration
    print("[*] Launching Protocol Insurance Actuary API on port 8024...")
    uvicorn.run(app, host="0.0.0.0", port=8024)
