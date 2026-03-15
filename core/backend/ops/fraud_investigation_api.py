import time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

# PROXY PROTOCOL - FRAUD INVESTIGATION API (v1.0)
# "Cross-epoch asset correlation for long-term fraud detection."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Fraud Investigation",
    description="Authorized forensic service for detecting slow-burn proof-of-work reuse.",
    version="1.0.0"
)

# --- Models ---

class HistoricalCollision(BaseModel):
    original_task_id: str
    original_timestamp: int
    collision_task_id: str
    collision_timestamp: int
    similarity_score: float
    dhash: str

class FraudInvestigationReport(BaseModel):
    node_id: str
    investigation_start: int
    total_samples_analyzed: int
    detected_collisions: List[HistoricalCollision]
    risk_profile: str # STABLE, SUSPICIOUS, HIGH_PROBABILITY_FARM
    recommendation: str

# --- Internal Investigative Logic ---

class FraudInvestigator:
    """
    Service that crawls the Proof Archive and Task Registry to find 
    visual similarities across a node's entire historical timeline.
    """
    def __init__(self):
        # Simulation: Normally this queries the persistent long-term storage
        # and the perceptual hash index.
        self.dhash_index: Dict[str, List[Dict]] = {
            "0x8A2E1C...F91C": [
                {"tid": "T-9004", "node": "NODE_ELITE_X29", "ts": 1736940000},
                {"tid": "T-9982", "node": "NODE_ELITE_X29", "ts": 1739311200}
            ]
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("FraudInvestigator")

    def run_node_deep_dive(self, node_id: str, depth_days: int = 90) -> FraudInvestigationReport:
        """
        Analyzes every proof submitted by a node over the specified timeframe.
        Identifies "Slow Burn" patterns where hashes are reused months apart.
        """
        self.logger.info(f"[*] Starting Deep Dive: {node_id} (Lookback: {depth_days} days)")
        
        # 1. Fetch Node Task History (Mocked)
        # In prod: tasks = task_registry.get_by_node(node_id, limit=depth_days)
        
        # 2. Correlate Hashes
        # We look for any hash in our index that appears more than once for this node
        collisions = []
        
        # Simulation: Finding the mock collision for the ELITE_X29 node
        if node_id == "NODE_ELITE_X29":
            match = self.dhash_index["0x8A2E1C...F91C"]
            collisions.append(HistoricalCollision(
                original_task_id=match[0]["tid"],
                original_timestamp=match[0]["ts"],
                collision_task_id=match[1]["tid"],
                collision_timestamp=match[1]["ts"],
                similarity_score=98.4,
                dhash="0x8A2E1C...F91C"
            ))

        # 3. Adjudicate Risk
        collision_count = len(collisions)
        risk = "STABLE"
        rec = "No action required."
        
        if collision_count >= 1:
            risk = "SUSPICIOUS"
            rec = "Flag node for double-verification on all future tasks."
        if collision_count >= 3:
            risk = "HIGH_PROBABILITY_FARM"
            rec = "IMMEDIATE_SLASH: Initiate High Court bond liquidation."

        return FraudInvestigationReport(
            node_id=node_id,
            investigation_start=int(time.time()),
            total_samples_analyzed=142, # Mock sample size
            detected_collisions=collisions,
            risk_profile=risk,
            recommendation=rec
        )

# Initialize Investigator
investigator = FraudInvestigator()

# --- API Endpoints ---

@app.get("/v1/forensics/investigate/{node_id}", response_model=FraudInvestigationReport)
async def investigate_node(
    node_id: str, 
    days: int = Query(90, ge=1, le=365)
):
    """
    Primary endpoint for the Security Desk.
    Triggers a cross-epoch correlation scan for a specific Node ID.
    """
    try:
        return investigator.run_node_deep_dive(node_id, days)
    except Exception as e:
        logging.error(f"Investigation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal forensic engine error.")

@app.get("/v1/forensics/global/hot_hashes")
async def get_hot_hashes():
    """Returns hashes that are appearing across multiple unique Node IDs."""
    # This detects "Template Leakage" where a single bot farm is sharing assets
    # across multiple physical units.
    return {
        "timestamp": int(time.time()),
        "global_collisions_detected": 14,
        "critical_subnets": ["45.15.22.0/24"],
        "recommendation": "Cluster Slash authorized for Asia-SE subnets."
    }

@app.get("/health")
async def health():
    return {"status": "online", "forensic_mode": "CROSS_EPOCH_CORRELATION"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8022 for secure forensic traffic
    print("[*] Launching Protocol Fraud Investigation API on port 8022...")
    uvicorn.run(app, host="0.0.0.0", port=8022)
