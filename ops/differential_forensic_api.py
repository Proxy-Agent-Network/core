import time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# PROXY PROTOCOL - DIFFERENTIAL FORENSIC API (v1.0)
# "Measuring the mathematical distance between judgments."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Differential Forensics",
    description="Authorized calculation of forensic deltas and probing detection.",
    version="1.0.0"
)

# --- Models ---

class ForensicDelta(BaseModel):
    field: str
    case_a_val: str
    case_b_val: str
    is_mismatch: bool
    risk_weight: float # Contribution to total distance

class ComparisonReport(BaseModel):
    case_a_id: str
    case_b_id: str
    forensic_distance: float # 0.0 (Identical) to 1.0 (Completely Different)
    deltas: List[ForensicDelta]
    probing_probability: float
    conclusion: str
    timestamp: int

# --- Internal Forensic Logic ---

class DifferentialForensicEngine:
    """
    Analyzes two signed manifests to identify if an attacker is 
    iteratively testing the protocol's edge cases.
    """
    def __init__(self):
        # Configuration for "Probing Detection"
        self.PROBING_THRESHOLD = 0.15 # If distance is < 15%, it's likely an iterative probe
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("DiffForensics")

    def calculate_distance(self, manifest_a: Dict, manifest_b: Dict) -> Tuple[float, List[ForensicDelta]]:
        """
        Calculates a weighted distance score based on telemetry and consensus.
        """
        deltas = []
        total_weight = 0
        total_mismatch_weight = 0

        # Field definitions: (key, human_name, weight)
        weights = [
            ("pcr_state", "Hardware Attestation", 0.4),
            ("consensus", "Quorum Alignment", 0.2),
            ("region", "Jurisdiction", 0.1),
            ("payout_action", "Settlement Logic", 0.3)
        ]

        for key, label, weight in weights:
            val_a = str(manifest_a.get(key, "N/A"))
            val_b = str(manifest_b.get(key, "N/A"))
            mismatch = val_a != val_b
            
            deltas.append(ForensicDelta(
                field=label,
                case_a_val=val_a,
                case_b_val=val_b,
                is_mismatch=mismatch,
                risk_weight=weight if mismatch else 0.0
            ))
            
            total_weight += weight
            if mismatch:
                total_mismatch_weight += weight

        distance = total_mismatch_weight / total_weight if total_weight > 0 else 1.0
        return round(distance, 4), deltas

    def detect_probing(self, distance: float, manifest_a: Dict, manifest_b: Dict) -> float:
        """
        Calculates probability that these two cases are part of a probing sequence.
        Probing is high when distance is low but hashes/node_ids differ.
        """
        # If the same node is involved in two very similar failed cases
        if manifest_a.get("node_id") == manifest_b.get("node_id") and distance < 0.2:
            return 0.95
        
        # If the distance is low but they are from the same subnet (mock check)
        if distance < self.PROBING_THRESHOLD:
            return 0.75
            
        return 0.05

# Initialize Engine
engine = DifferentialForensicEngine()

# --- API Endpoints ---

@app.get("/v1/forensics/compare", response_model=ComparisonReport)
async def compare_cases(
    case_a: str = Query(..., description="ID of the first case"),
    case_b: str = Query(..., description="ID of the second case")
):
    """
    Calculates the forensic delta between two High Court judgments.
    Powers the comparison logic in the UI.
    """
    self.logger.info(f"[*] Analyzing Forensic Distance: {case_a} vs {case_b}")

    # 1. Fetch Manifests (Simulation: Normally calls AdjudicationArchivist)
    # We mock the retrieval for the architectural proof
    mock_data = {
        "CASE-8829-APP": {"pcr_state": "DRIFT_PCR_7", "consensus": "6/7", "region": "ASIA_SE", "payout_action": "SLASH", "node_id": "NODE_ELITE_X29"},
        "CASE-8421-APP": {"pcr_state": "STABLE", "consensus": "5/7", "region": "US_WEST", "payout_action": "SLASH", "node_id": "NODE_WHALE_04"}
    }

    m_a = mock_data.get(case_a)
    m_b = mock_data.get(case_b)

    if not m_a or not m_b:
        raise HTTPException(status_code=404, detail="One or more manifests not found in archive.")

    # 2. Run Analysis
    distance, deltas = engine.calculate_distance(m_a, m_b)
    probing_prob = engine.detect_probing(distance, m_a, m_b)

    conclusion = "NOMINAL_VARIANCE"
    if probing_prob > 0.7:
        conclusion = "ITERATIVE_PROBING_DETECTED"
    elif distance > 0.8:
        conclusion = "DIVERGENT_PRECEDENT"

    return ComparisonReport(
        case_a_id=case_a,
        case_b_id=case_b,
        forensic_distance=distance,
        deltas=deltas,
        probing_probability=probing_prob,
        conclusion=conclusion,
        timestamp=int(time.time())
    )

@app.get("/health")
async def health():
    return {"status": "online", "engine": "DIFF_FORENSIC_V1", "probing_threshold": 0.15}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8024 for security desk access
    print("[*] Launching Protocol Differential Forensic API on port 8024...")
    uvicorn.run(app, host="0.0.0.0", port=8024)
