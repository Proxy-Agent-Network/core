import time
import logging
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import Dict, List, Optional

# Proxy Protocol Internal Modules
from core.reputation.oracle import ReputationOracle, ReputationAttestation

# PROXY PROTOCOL - REPUTATION API GATEWAY (v1.0)
# "REST interface for signed network credit scores."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Reputation API",
    description="Fetch hardware-signed trust proofs for network participants.",
    version="1.0.0"
)

# Initialize the shared Oracle engine
# In production, this would connect to a shared Redis/Postgres state
oracle = ReputationOracle()

# --- Models ---

class ErrorResponse(BaseModel):
    code: str
    message: str

# --- Endpoints ---

@app.get(
    "/v1/reputation/{node_id}", 
    response_model=ReputationAttestation,
    responses={404: {"model": ErrorResponse}}
)
async def get_node_reputation(
    node_id: str = Path(..., description="The Public Key fingerprint of the Node")
):
    """
    Retrieves a signed attestation for a specific node.
    Agents use this to verify a Node's standing before locking high-value escrows.
    """
    logging.info(f"[*] API Request: Reputation for {node_id}")

    # 1. Fetch Aggregated Metrics
    # Simulation: Normally this queries the Node Registry DB
    raw_data = [
        {"node_id": "NODE_ELITE_X29", "success_count": 241, "failure_count": 0},
        {"node_id": "NODE_BETA_004", "success_count": 12, "failure_count": 1},
    ]
    
    scores = oracle.aggregate_regional_scores(raw_data)
    
    # 2. Check if node exists
    if node_id not in scores:
        raise HTTPException(
            status_code=404, 
            detail={"code": "PX_301", "message": "Node ID not found in current epoch registry."}
        )

    # 3. Generate Signed Proof
    # Tier mapping logic (e.g., > 800 is Tier 3 Elite)
    node_score = scores[node_id]
    node_tier = 3 if node_score > 800 else 1
    
    attestation = oracle.generate_signed_score(node_id, node_score, node_tier)
    
    return attestation

@app.get("/v1/reputation/batch", response_model=Dict[str, int])
async def get_batch_reputation(node_ids: str):
    """
    Helper for mass-dispatchers to check scores for a list of candidate nodes.
    Format: /v1/reputation/batch?node_ids=ID1,ID2,ID3
    """
    id_list = node_ids.split(",")
    
    # Mock lookup
    results = {nid: 500 for nid in id_list} # Default neutral score
    return results

if __name__ == "__main__":
    import uvicorn
    # Launched on a dedicated port for public SDK consumption
    print("[*] Launching Reputation API Gateway on port 8004...")
    uvicorn.run(app, host="0.0.0.0", port=8004)
