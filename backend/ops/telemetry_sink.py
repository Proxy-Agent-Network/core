import time
import hashlib
import json
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# PROXY PROTOCOL - TELEMETRY INGESTION SINK (v1.0)
# "Real-time hardware drift detection for SEV-1 prevention."
# ----------------------------------------------------

app = FastAPI(title="Proxy Protocol Telemetry Sink")

# --- Configuration ---
GOLDEN_PCR_VALUES = {
    "RPI5_STOCK": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "JETSON_ORIN": "3b7c89..." # Placeholder for Jetson platform
}

class HeartbeatPayload(BaseModel):
    node_id: str
    timestamp: int
    hw_secured: bool
    pcr_digest: str # The composite hash of PCR 0, 1, and 7
    signature: str  # Hardware-signed proof of the digest
    telemetry: Dict # CPU, Temp, WiFi Entropy

class TelemetrySink:
    def __init__(self):
        self.node_states: Dict[str, Dict] = {}
        self.drift_events: List[Dict] = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TelemetrySink")

    def ingest_heartbeat(self, data: HeartbeatPayload) -> Dict:
        """
        Validates the hardware state of a node against the protocol whitelist.
        Returns a 'Threat Level' that feeds the Master Orchestrator.
        """
        node_id = data.node_id
        received_pcr = data.pcr_digest
        
        # 1. PCR Drift Analysis
        # Check if the node is running a recognized, untampered OS kernel/firmware
        is_trusted = any(received_pcr == val for val in GOLDEN_PCR_VALUES.values())
        
        # 2. State Management
        self.node_states[node_id] = {
            "last_seen": int(time.time()),
            "is_trusted": is_trusted,
            "metrics": data.telemetry
        }

        if not is_trusted:
            self.logger.warning(f"🚨 PCR DRIFT DETECTED: Node {node_id}")
            drift_report = {
                "node_id": node_id,
                "timestamp": data.timestamp,
                "received_pcr": received_pcr,
                "type": "HARDWARE_TAMPER_SUSPECTED"
            }
            self.drift_events.append(drift_report)
            return {"status": "ANOMALY", "alert": True, "details": drift_report}

        return {"status": "STABLE", "alert": False}

    def get_fleet_vitals(self) -> Dict:
        """Aggregates metrics for the Master Protocol Orchestrator."""
        total_nodes = len(self.node_states)
        untrusted_nodes = len([n for n in self.node_states.values() if not n['is_trusted']])
        
        return {
            "online_nodes": total_nodes,
            "pcr_drift_count": untrusted_nodes,
            "system_integrity": 1.0 - (untrusted_nodes / total_nodes) if total_nodes > 0 else 1.0,
            "recent_drifts": self.drift_events[-5:] # Latest 5 events
        }

# --- API Layer ---

sink = TelemetrySink()

@app.post("/v1/telemetry/heartbeat")
async def post_heartbeat(payload: HeartbeatPayload):
    """Entry point for global node fleet telemetry."""
    result = sink.ingest_heartbeat(payload)
    return result

@app.get("/v1/telemetry/vitals")
async def get_vitals():
    """Endpoint for the MasterOrchestrator to poll vital signs."""
    return sink.get_fleet_vitals()

if __name__ == "__main__":
    import uvicorn
    # Launched on port 8003 to handle high-frequency pulse traffic
    print("[*] Launching Protocol Telemetry Sink on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
