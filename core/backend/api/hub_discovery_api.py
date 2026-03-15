import time
import logging
import requests
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

# PROXY PROTOCOL - HUB DISCOVERY API (v1.0)
# "Zero-config onboarding for the biological fleet."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Hub Discovery",
    description="Authorized discovery service for Node-to-Hub peer selection.",
    version="1.0.0"
)

# --- Models ---

class HubEndpoint(BaseModel):
    hub_id: str
    region_name: str
    endpoint_url: str
    current_latency_ms: int
    status: str # OPTIMAL, STABLE, DEGRADED
    priority: int # 1 is highest

class DiscoveryResponse(BaseModel):
    timestamp: int
    client_ip: str
    suggested_hubs: List[HubEndpoint]
    protocol_version: str = "v2.9.7"

# --- Internal Discovery Logic ---

class DiscoveryEngine:
    """
    Analyzes node location and network health to suggest the best entry point.
    In production, this integrates with core/ops/regional_traffic_controller.py.
    """
    def __init__(self):
        # Canonical Hub Registry (Mocked)
        self.hubs = {
            "US_EAST": {"name": "US East (VA)", "url": "https://va.proxyagent.network", "lat": 38.0, "lon": -77.0},
            "US_WEST": {"name": "US West (OR)", "url": "https://or.proxyagent.network", "lat": 45.0, "lon": -120.0},
            "EU_WEST": {"name": "Europe (UK)", "url": "https://ldn.proxyagent.network", "lat": 51.5, "lon": -0.1},
            "ASIA_SE": {"name": "Asia (SG)", "url": "https://sg.proxyagent.network", "lat": 1.3, "lon": 103.8}
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("HubDiscovery")

    def _get_geo_for_ip(self, ip: str) -> Dict:
        """
        Performs IP-to-Geo lookup with exponential backoff.
        """
        # Simulation: In production, uses MaxMind or a secure internal GeoIP mirror.
        # Defaulting to a central point if lookup fails.
        return {"lat": 39.8, "lon": -98.5} 

    def find_best_hubs(self, client_ip: str) -> List[HubEndpoint]:
        """
        Calculates distance and factors in Hub Health (Status).
        """
        self.logger.info(f"[*] Discovery requested for Node: {client_ip}")
        
        # 1. Get Client Location
        client_geo = self._get_geo_for_ip(client_ip)
        
        # 2. Fetch Live Health from TrafficController (Mocked)
        # In prod: health_map = traffic_controller.hub_states
        health_map = {
            "US_EAST": {"status": "OPTIMAL", "latency": 18},
            "US_WEST": {"status": "STABLE", "latency": 84},
            "EU_WEST": {"status": "STABLE", "latency": 142},
            "ASIA_SE": {"status": "DEGRADED", "latency": 1240}
        }

        # 3. Prioritization Logic
        # Sort based on Health first, then Latency.
        discovery_list = []
        for hub_id, meta in self.hubs.items():
            status_data = health_map.get(hub_id, {"status": "UNKNOWN", "latency": 9999})
            
            discovery_list.append(HubEndpoint(
                hub_id=hub_id,
                region_name=meta["name"],
                endpoint_url=meta["url"],
                current_latency_ms=status_data["latency"],
                status=status_data["status"],
                priority=0 # Placeholder
            ))

        # Ranking logic:
        # 1. OPTIMAL hubs come first.
        # 2. Within statuses, sort by latency.
        # 3. DEGRADED hubs are moved to bottom regardless of latency.
        
        def rank_key(h):
            status_rank = {"OPTIMAL": 0, "STABLE": 1, "DEGRADED": 2, "UNKNOWN": 3}
            return (status_rank.get(h.status, 3), h.current_latency_ms)

        discovery_list.sort(key=rank_key)
        
        # Assign formal priority index
        for idx, h in enumerate(discovery_list):
            h.priority = idx + 1
            
        return discovery_list

# Initialize Engine
engine = DiscoveryEngine()

# --- API Endpoints ---

@app.get("/v1/discovery", response_model=DiscoveryResponse)
async def get_hub_discovery(request: Request):
    """
    Returns the optimized hub list for the calling Node.
    """
    client_ip = request.client.host
    
    # Optional Header for testing (since localhost returns 127.0.0.1)
    test_ip = request.headers.get("X-Forwarded-For", client_ip)
    
    suggested = engine.find_best_hubs(test_ip)
    
    return DiscoveryResponse(
        timestamp=int(time.time()),
        client_ip=test_ip,
        suggested_hubs=suggested
    )

@app.get("/health")
async def health():
    return {"status": "online", "orchestrator_sync": True}

if __name__ == "__main__":
    import uvicorn
    # Launched on a dedicated port for Node onboarding traffic
    print("[*] Launching Protocol Hub Discovery API on port 8009...")
    uvicorn.run(app, host="0.0.0.0", port=8009)
