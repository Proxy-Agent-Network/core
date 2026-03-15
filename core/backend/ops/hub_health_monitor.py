import asyncio
import logging
import time
import requests
import hashlib
from typing import Dict, List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

# PROXY PROTOCOL - HUB HEALTH MONITOR (v1.0)
# "Auditing the watchmen: Ensuring edge-node consistency."
# --------------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Hub Health Monitor",
    description="Background auditor for regional firewall gateway consistency.",
    version="1.0.0"
)

# --- Configuration ---
CHECK_INTERVAL_SEC = 300 # 5-minute audit cycle
HUB_ENDPOINTS = {
    "US_EAST": "http://va-hub:8021/v1/firewall",
    "US_WEST": "http://or-hub:8021/v1/firewall",
    "EU_WEST": "http://ldn-hub:8021/v1/firewall",
    "ASIA_SE": "http://sg-hub:8021/v1/firewall"
}

class HubVitals(BaseModel):
    hub_id: str
    status: str # OPERATIONAL, DRIFT_DETECTED, UNREACHABLE
    latency_ms: float
    active_blocks: int
    state_hash: str
    last_audit: int

class FleetHealthReport(BaseModel):
    timestamp: int
    global_sync_score: float # 0.0 to 1.0
    hub_details: List[HubVitals]

# --- Internal Auditor Logic ---

class HubHealthAuditor:
    """
    Orchestrates periodic sanity checks across all regional jurisdictional gateways.
    Detects if a hub is falling behind on global ban-list updates (State Drift).
    """
    def __init__(self):
        self.health_ledger: Dict[str, HubVitals] = {}
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("HubMonitor")

    async def _audit_hub(self, hub_id: str, url: str) -> HubVitals:
        """Pings a hub and compares its local blacklist hash to the global root."""
        start_time = time.time()
        try:
            # Simulation: requests.get(f"{url}/status", timeout=5)
            # We simulate a response from regional_firewall_gateway_api.py
            latency = (time.time() - start_time) * 1000
            
            # Mocking a potential drift in ASIA_SE for demonstration
            status = "OPERATIONAL"
            if hub_id == "ASIA_SE" and time.time() % 600 < 60: # Simulate periodic drift
                status = "DRIFT_DETECTED"
            
            # Simulate state hash calculation of the hub's local ledger
            mock_hash = hashlib.md5(f"{hub_id}:STATE_ROOT_V1".encode()).hexdigest()[:8]

            return HubVitals(
                hub_id=hub_id,
                status=status,
                latency_ms=round(latency, 2),
                active_blocks=842, # Mock value
                state_hash=mock_hash,
                last_audit=int(time.time())
            )
        except Exception as e:
            self.logger.error(f"[!] Hub {hub_id} is UNREACHABLE: {str(e)}")
            return HubVitals(
                hub_id=hub_id,
                status="UNREACHABLE",
                latency_ms=0.0,
                active_blocks=0,
                state_hash="ERROR",
                last_audit=int(time.time())
            )

    async def run_fleet_audit(self) -> FleetHealthReport:
        """Executes a parallel check of all configured gateways."""
        self.logger.info("[*] Initiating Global Hub Audit...")
        
        tasks = [self._audit_hub(hid, url) for hid, url in HUB_ENDPOINTS.items()]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            self.health_ledger[res.hub_id] = res

        # Calculate global parity (how many hubs are OPERATIONAL)
        operational_count = len([h for h in results if h.status == "OPERATIONAL"])
        sync_score = operational_count / len(HUB_ENDPOINTS)

        return FleetHealthReport(
            timestamp=int(time.time()),
            global_sync_score=sync_score,
            hub_details=results
        )

# Initialize Auditor
auditor = HubHealthAuditor()

# --- Background Task ---

async def monitor_loop():
    """Permanent background worker thread."""
    while True:
        await auditor.run_fleet_audit()
        await asyncio.sleep(CHECK_INTERVAL_SEC)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_loop())

# --- API Endpoints ---

@app.get("/v1/monitor/vitals", response_model=FleetHealthReport)
async def get_latest_vitals():
    """Returns the current health status of the global enforcement edge."""
    return await auditor.run_fleet_audit()

@app.get("/v1/monitor/drift-alerts")
async def get_drift_alerts():
    """Lists hubs currently reporting state-drift or connectivity issues."""
    return {
        "timestamp": int(time.time()),
        "alerts": [v for v in auditor.health_ledger.values() if v.status != "OPERATIONAL"]
    }

@app.get("/health")
async def health():
    return {"status": "online", "auditor": "ACTIVE", "managed_hubs": len(HUB_ENDPOINTS)}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8033 for security ops
    print("[*] Launching Protocol Hub Health Monitor on port 8033...")
    uvicorn.run(app, host="0.0.0.0", port=8033)
