import time
import logging
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

# PROXY PROTOCOL - HARDWARE REGISTRY API (v1.0)
# "Tracking the physical lifecycle of the biological node fleet."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Hardware Registry",
    description="Authorized tracking of Proxy Sentry hardware deployments.",
    version="1.0.0"
)

# --- Models & Enums ---

class UnitStatus(str, Enum):
    MANUFACTURED = "MANUFACTURED"
    IN_TRANSIT = "IN_TRANSIT"
    DEPLOYED = "DEPLOYED"
    DECOMMISSIONED = "DECOMMISSIONED"
    TAMPERED = "TAMPERED"

class HardwareUnit(BaseModel):
    unit_id: str = Field(..., description="Unique serial ID bound to the TPM")
    public_key_fingerprint: str
    target_region: str
    status: UnitStatus
    last_ping: Optional[int] = None
    shipment_tracking: Optional[str] = None

# --- Internal Registry Logic ---

class HardwareRegistry:
    """
    Maintains the state of all official Proxy Foundation hardware.
    In production, this is backed by a secure PostgreSQL instance.
    """
    def __init__(self):
        # Mock Inventory
        self.inventory: Dict[str, HardwareUnit] = {
            "SENTRY-JP-001": HardwareUnit(
                unit_id="SENTRY-JP-001",
                public_key_fingerprint="8A2E1C...F91C",
                target_region="JP_EAST",
                status=UnitStatus.IN_TRANSIT,
                shipment_tracking="DHL_8829310"
            ),
            "SENTRY-SG-005": HardwareUnit(
                unit_id="SENTRY-SG-005",
                public_key_fingerprint="3B7C89...D2A1",
                target_region="ASIA_SE",
                status=UnitStatus.IN_TRANSIT,
                shipment_tracking="FEDEX_992182"
            ),
            "SENTRY-VA-042": HardwareUnit(
                unit_id="SENTRY-VA-042",
                public_key_fingerprint="E3B0C4...427A",
                target_region="US_EAST",
                status=UnitStatus.DEPLOYED,
                last_ping=int(time.time() - 300)
            )
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("HardwareRegistry")

    def get_all_units(self) -> List[HardwareUnit]:
        return list(self.inventory.values())

    def update_status(self, unit_id: str, status: UnitStatus) -> Optional[HardwareUnit]:
        if unit_id in self.inventory:
            self.inventory[unit_id].status = status
            self.logger.info(f"[*] Unit {unit_id} status updated to {status}")
            return self.inventory[unit_id]
        return None

    def provision_new_unit(self, region: str, tracking: str) -> HardwareUnit:
        """Called when a new shipment leaves the factory."""
        unit_id = f"SENTRY-{region}-{int(time.time()) % 1000:03d}"
        new_unit = HardwareUnit(
            unit_id=unit_id,
            public_key_fingerprint="PENDING_BINDING",
            target_region=region,
            status=UnitStatus.IN_TRANSIT,
            shipment_tracking=tracking
        )
        self.inventory[unit_id] = new_unit
        self.logger.info(f"[+] Provisioned {unit_id} for shipment to {region}")
        return new_unit

# Initialize Registry
registry = HardwareRegistry()

# --- API Endpoints ---

@app.get("/v1/hardware/units", response_model=List[HardwareUnit])
async def list_units():
    """Returns the full fleet status for the Hotspot Visualizer."""
    return registry.get_all_units()

@app.get("/v1/hardware/region/{region_code}", response_model=List[HardwareUnit])
async def list_units_by_region(region_code: str):
    """Filters units by target destination."""
    units = [u for u in registry.get_all_units() if u.target_region == region_code.upper()]
    return units

@app.post("/v1/hardware/provision")
async def provision_shipment(region: str, tracking: str):
    """Foundation endpoint to authorize new hardware shipments."""
    return registry.provision_new_unit(region, tracking)

@app.patch("/v1/hardware/{unit_id}/status")
async def update_unit_status(unit_id: str, status: UnitStatus):
    """Updates the status of a specific unit (e.g., from In-Transit to Deployed)."""
    unit = registry.update_status(unit_id, status)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit ID not found.")
    return unit

@app.get("/health")
async def health():
    return {"status": "online", "registry_sync": True}

if __name__ == "__main__":
    import uvicorn
    # Launched on a dedicated port for Foundation Logistics traffic
    print("[*] Launching Protocol Hardware Registry API on port 8010...")
    uvicorn.run(app, host="0.0.0.0", port=8010)
