import time
import logging
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

# PROXY PROTOCOL - GLOBAL REPUTATION REGISTRY API (v1.0)
# "The definitive public record of biological node standing."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Reputation Registry",
    description="Authorized lookup service for node reliability and trust tiers.",
    version="1.0.0"
)

# --- Models & Enums ---

class NodeTier(str, Enum):
    BANNED = "BANNED"           # 0-300
    PROBATION = "PROBATION"     # 301-500
    VERIFIED = "VERIFIED"       # 501-800
    ELITE = "ELITE"             # 801-950
    SUPER_ELITE = "SUPER_ELITE" # 951-1000

class ReputationProfile(BaseModel):
    node_id: str = Field(..., description="Public Key fingerprint of the node")
    reputation_score: int = Field(..., ge=0, le=1000)
    tier: NodeTier
    tasks_completed: int
    success_rate: float
    is_high_court_eligible: bool
    last_updated: int

class RegistryResponse(BaseModel):
    timestamp: int
    data: Optional[ReputationProfile] = None
    status: str = "OK"

# --- Internal Logic ---

class ReputationManager:
    """
    Simulation of the central reputation database.
    In production, this connects to the global state-tree.
    """
    def __init__(self):
        # Mock Registry Data
        self.registry = {
            "NODE_ELITE_X29": {
                "score": 982, "tasks": 1420, "success": 0.998
            },
            "NODE_ALPHA_001": {
                "score": 845, "tasks": 2104, "success": 0.965
            },
            "NODE_PROB_77": {
                "score": 410, "tasks": 12, "success": 0.850
            }
        }

    def get_tier(self, score: int) -> NodeTier:
        if score > 950: return NodeTier.SUPER_ELITE
        if score > 800: return NodeTier.ELITE
        if score > 500: return NodeTier.VERIFIED
        if score > 300: return NodeTier.PROBATION
        return NodeTier.BANNED

    def fetch_node(self, node_id: str) -> Optional[ReputationProfile]:
        data = self.registry.get(node_id)
        if not data:
            return None
        
        return ReputationProfile(
            node_id=node_id,
            reputation_score=data["score"],
            tier=self.get_tier(data["score"]),
            tasks_completed=data["tasks"],
            success_rate=data["success"],
            is_high_court_eligible=data["score"] >= 951,
            last_updated=int(time.time())
        )

# Initialize Backend
manager = ReputationManager()

# --- Endpoints ---

@app.get(
    "/v1/registry/{node_id}", 
    response_model=RegistryResponse,
    summary="Fetch Node Reputation Profile"
)
async def get_node_reputation(
    node_id: str = Path(..., description="The ID of the Node to verify")
):
    """
    Retrieves the full reputation profile for a specific human node.
    Used by Agents to verify eligibility for Tier 2/3 tasks.
    """
    profile = manager.fetch_node(node_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Node ID not found in global registry.")
    
    return RegistryResponse(
        timestamp=int(time.time()),
        data=profile
    )

@app.get(
    "/v1/registry/batch", 
    response_model=Dict[str, int],
    summary="Batch Reputation Check"
)
async def get_batch_reputation(
    node_ids: str = Query(..., description="Comma-separated list of Node IDs")
):
    """
    Lightweight endpoint for high-frequency dispatchers.
    Returns only ID-to-Score mappings.
    """
    ids = node_ids.split(",")
    results = {}
    for nid in ids:
        profile = manager.fetch_node(nid)
        results[nid] = profile.reputation_score if profile else 0
        
    return results

@app.get("/health")
async def health_check():
    return {"status": "online", "sync_epoch": 88293}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port for protocol synchronization
    print("[*] Launching Global Reputation Registry API on port 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8006)
