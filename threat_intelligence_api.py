import time
import logging
import json
import hashlib
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# PROXY PROTOCOL - THREAT INTELLIGENCE API (v1.0)
# "Pre-filtering the noise. Defending the biological perimeter."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Threat Intelligence",
    description="Aggregates global threat feeds to provide risk scoring for incoming node telemetry.",
    version="1.0.0"
)

# --- Models ---

class RiskScore(BaseModel):
    ip_address: str
    risk_level: float = Field(..., ge=0.0, le=1.0) # 0.0 (Clean) to 1.0 (Blacklisted)
    classification: str # TOR, VPN, DATA_CENTER, KNOWN_SYBIL, NOMINAL
    is_blacklisted: bool
    confidence: float
    timestamp: int

class ThreatSourceUpdate(BaseModel):
    source_name: str
    target_pattern: str # IP, Subnet, or Hardware ID
    reason: str
    expiry: Optional[int] = None

# --- Internal Intelligence Logic ---

class ThreatIntelManager:
    """
    Maintains a high-performance in-memory cache of malicious patterns.
    Used for sub-millisecond filtering of node heartbeats.
    """
    def __init__(self):
        # Format: { "pattern": { "type": str, "expiry": int } }
        self.blacklist_cache: Dict[str, Dict] = {
            "185.220.101.": {"type": "TOR_EXIT_NODE", "expiry": None}, # Common Tor Exit Prefix
            "45.15.22.": {"type": "KNOWN_SYBIL_CLUSTER", "expiry": int(time.time() + 86400)},
            "HW-8829-PX-04": {"type": "REVOKED_TPM_CHIP", "expiry": None}
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ThreatIntel")

    def analyze_ip(self, ip_address: str) -> RiskScore:
        """
        Performs multi-vector analysis on an incoming IP address.
        """
        # 1. Prefix Matching (Subnet Intelligence)
        prefix_24 = ".".join(ip_address.split(".")[:3]) + "."
        
        threat = self.blacklist_cache.get(prefix_24)
        
        if threat:
            self.logger.warning(f"[!] THREAT_HIT: IP {ip_address} matches {threat['type']}")
            return RiskScore(
                ip_address=ip_address,
                risk_level=0.95 if threat['type'] == 'KNOWN_SYBIL_CLUSTER' else 0.80,
                classification=threat['type'],
                is_blacklisted=True,
                confidence=1.0,
                timestamp=int(time.time())
            )

        # 2. Heuristic Analysis (Simulation)
        # In production, this would query MaxMind, IPQualityScore, or internal behavioral logs
        risk = 0.05 # Baseline noise
        
        return RiskScore(
            ip_address=ip_address,
            risk_level=risk,
            classification="NOMINAL",
            is_blacklisted=False,
            confidence=0.9,
            timestamp=int(time.time())
        )

    def update_blacklist(self, update: ThreatSourceUpdate):
        """Adds a new malicious pattern to the sentinel cache."""
        self.blacklist_cache[update.target_pattern] = {
            "type": update.reason,
            "expiry": update.expiry
        }
        self.logger.info(f"[*] Intelligence Updated: {update.target_pattern} flagged as {update.reason}")

# Initialize Manager
intel_manager = ThreatIntelManager()

# --- API Endpoints ---

@app.get("/v1/threat/check", response_model=RiskScore)
async def check_ip_risk(ip: str = Query(..., description="The IP address to audit")):
    """
    Primary endpoint for the Anomaly Engine.
    Pre-filters nodes before they are allowed to sign tasks.
    """
    return intel_manager.analyze_ip(ip)

@app.post("/v1/threat/update")
async def ingest_threat_signal(payload: ThreatSourceUpdate):
    """
    Internal endpoint for automated security scanners or human SOC desk.
    Updates the global blacklist in real-time.
    """
    intel_manager.update_blacklist(payload)
    return {"status": "SUCCESS", "pattern": payload.target_pattern}

@app.get("/v1/threat/active_counts")
async def get_intel_summary():
    """Returns metadata on the size of the current blocklists."""
    return {
        "blacklist_patterns": len(intel_manager.blacklist_cache),
        "last_sync_timestamp": int(time.time()),
        "active_monitors": ["TOR", "VPN", "SYBIL_FINGERPRINTS"]
    }

@app.get("/health")
async def health():
    return {"status": "online", "intel_mode": "STRICT_FILTERING"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8021 for high-frequency pre-filtering
    print("[*] Launching Protocol Threat Intelligence API on port 8021...")
    uvicorn.run(app, host="0.0.0.0", port=8021)
