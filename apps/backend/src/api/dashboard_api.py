import time
import random
from fastapi import FastAPI, HTTPException
from typing import Dict, List, Any
from pydantic import BaseModel

# PROXY PROTOCOL - PROTOCOL DASHBOARD API (v1.0)
# "Real-time data aggregation for the Network Analytics Dashboard."
# ----------------------------------------------------

app = FastAPI(title="Proxy Protocol Dashboard API")

class GlobalMetrics(BaseModel):
    total_volume_sats: int
    active_escrows_sats: int
    insurance_pool_sats: int
    avg_reputation: float
    total_nodes: int
    online_nodes: int
    active_governance_cases: int
    uptime_days: int

class FlowPoint(BaseModel):
    timestamp: int
    inflow: int
    outflow: int

@app.get("/v1/analytics/summary", response_model=GlobalMetrics)
async def get_analytics_summary():
    """
    Aggregates global KPIs from the EscrowManager and NodeRegistry.
    Feeds the primary KPI grid in the Analytics Dashboard.
    """
    # In production, these are calculated via Redis aggregators
    return {
        "total_volume_sats": 124508900,
        "active_escrows_sats": 4200500,
        "insurance_pool_sats": 10450200,
        "avg_reputation": 942.5,
        "total_nodes": 1248,
        "online_nodes": 1182,
        "active_governance_cases": 3,
        "uptime_days": 142
    }

@app.get("/v1/analytics/velocity", response_model=List[FlowPoint])
async def get_satoshi_velocity():
    """
    Returns time-series data for Satoshi inflow/payout charting.
    Supports the 'Satoshi Flow Velocity' visualizer.
    """
    now = int(time.time())
    data = []
    for i in range(24):
        data.append({
            "timestamp": now - (i * 3600),
            "inflow": random.randint(200000, 800000),
            "outflow": random.randint(150000, 700000)
        })
    return data

@app.get("/v1/analytics/governance")
async def get_governance_snapshot():
    """
    Fetches the status of active High Court cases from the VerdictAggregator.
    """
    return {
        "active_cases": [
            {"id": "CASE-882", "type": "HARDWARE_AUDIT", "status": "COLLECTING_SIGNATURES", "quorum": "5/7"},
            {"id": "CASE-885", "type": "PII_LEAK_DISPUTE", "status": "FINALIZING", "quorum": "7/7"},
            {"id": "PIP-882", "type": "PROTOCOL_UPGRADE", "status": "VOTING_ACTIVE", "support": "74.6%"}
        ],
        "total_slashed_24h": 1200000,
        "total_rewards_24h": 600000
    }

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8002 to isolate analytics traffic
    print("[*] Launching Protocol Dashboard API on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
