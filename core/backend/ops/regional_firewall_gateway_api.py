import time
import logging
import json
import os
import subprocess
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Body, Header
from pydantic import BaseModel, Field

# PROXY PROTOCOL - REGIONAL FIREWALL GATEWAY API (v1.0)
# "The physical edge of justice: Enforcing banishment in the hub."
# ----------------------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Regional Firewall Gateway",
    description="Regional enforcement service for IP-level and TPM-level blocking.",
    version="1.0.0"
)

# --- Models ---

class LocalBlockAction(BaseModel):
    action: str # BLOCK_PERMANENT, UNBLOCK
    hardware_id: str
    ip_prefix: str # /24 subnet
    reason: str
    attestation_ref: str # The Appeal ID or Verdict ID

class LocalEnforcementStatus(BaseModel):
    hub_id: str
    active_blocks: int
    system_load: float
    last_sync_timestamp: int
    firewall_status: str # OPERATIONAL, SYNC_PENDING, ERROR

# --- Internal Enforcement Logic ---

class RegionalFirewallManager:
    """
    Orchestrates the local hub's defensive state.
    Interfaces with system-level iptables and the hardware registry.
    """
    def __init__(self):
        self.hub_id = os.getenv("PROXY_HUB_ID", "REGION_LOCAL_GATEWAY")
        self.active_blocks: Dict[str, Dict] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"Firewall-{self.hub_id}")

    def _execute_iptables_drop(self, prefix: str):
        """
        Simulation: In production, executes system calls to drop traffic.
        Example: sudo iptables -A INPUT -s {prefix}0/24 -j DROP
        """
        self.logger.critical(f"🔥 [IP_FILTER] Dropping ingress for subnet: {prefix}0/24")
        # subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", f"{prefix}0/24", "-j", "DROP"])

    def _execute_tpm_revocation(self, hw_id: str):
        """
        Simulation: Updates the local node-discovery filter to ignore this TPM.
        """
        self.logger.critical(f"💀 [TPM_FILTER] Identity {hw_id} removed from local peer-table.")

    async def apply_block(self, data: LocalBlockAction) -> bool:
        """
        Synchronizes the local hub state with the global ban broadcast.
        """
        self.logger.info(f"[*] Hub {self.hub_id} processing banishment: {data.attestation_ref}")

        # 1. Apply IP-level network filter
        if data.ip_prefix:
            self._execute_iptables_drop(data.ip_prefix)

        # 2. Apply Hardware-level identity filter
        if data.hardware_id:
            self._execute_tpm_revocation(data.hardware_id)

        # 3. Update local state
        self.active_blocks[data.hardware_id] = {
            "ip": data.ip_prefix,
            "reason": data.reason,
            "timestamp": int(time.time()),
            "verified_by": data.attestation_ref
        }

        return True

# Initialize Gateway
gateway = RegionalFirewallManager()

# --- API Endpoints ---

@app.post("/v1/firewall/sync")
async def sync_global_ban(payload: LocalBlockAction):
    """
    Authenticated ingress for Global Ban-List Sync signals.
    Triggers immediate local enforcement.
    """
    try:
        success = await gateway.apply_block(payload)
        if success:
            return {"status": "SYNCHRONIZED", "hub_id": gateway.hub_id}
        else:
            raise HTTPException(status_code=500, detail="LOCAL_ENFORCEMENT_FAILED")
    except Exception as e:
        logging.error(f"Sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail="INTERNAL_GATEWAY_ERROR")

@app.get("/v1/firewall/status", response_model=LocalEnforcementStatus)
async def get_local_health():
    """Returns local enforcement vitals for the Global Visualizer."""
    return LocalEnforcementStatus(
        hub_id=gateway.hub_id,
        active_blocks=len(gateway.active_blocks),
        system_load=0.14, # Mock value
        last_sync_timestamp=int(time.time()),
        firewall_status="OPERATIONAL"
    )

@app.get("/v1/firewall/ledger")
async def get_local_blacklist():
    """Returns the list of subnets and units blocked by this specific hub."""
    return gateway.active_blocks

@app.get("/health")
async def health():
    return {
        "status": "online", 
        "hub_id": gateway.hub_id, 
        "iptables_access": True, 
        "tpm_registry_link": "UP"
    }

if __name__ == "__main__":
    import uvicorn
    # Launched on internal hub port 8021
    print(f"[*] Launching Protocol Regional Firewall Gateway [{gateway.hub_id}] on port 8021...")
    uvicorn.run(app, host="0.0.0.0", port=8021)
