import time
import logging
import json
import os
import base64
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# PROXY PROTOCOL - PROOF ARCHIVE API (v1.0)
# "Containing toxic data; enforcing the 24h purge."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Proof Archive",
    description="Authorized temporary storage for task evidence forensics.",
    version="1.0.0"
)

# --- Models ---

class ProofIngest(BaseModel):
    task_id: str
    node_id: str
    dhash: str  # Perceptual hash from tamper_listener.py
    image_b64: str
    metadata: Dict = {}

class ProofMetadata(BaseModel):
    task_id: str
    node_id: str
    dhash: str
    stored_at: int
    expires_at: int
    purged: bool = False

class ArchiveStatus(BaseModel):
    active_proofs: int
    pending_purges: int
    total_purged_lifetime: int
    storage_utilization: str

# --- Internal Storage Logic ---

class ProofArchiveManager:
    """
    Handles the lifecycle of visual evidence.
    Evidence is stored in-memory (simulated) or encrypted filesystem.
    """
    def __init__(self):
        self.RETENTION_WINDOW_SEC = 86400  # 24 Hours
        # Simulation: In-memory store for high-velocity logic demonstration
        # format: { "task_id": { "blob": str, "meta": ProofMetadata } }
        self.vault: Dict[str, Dict] = {}
        self.purge_count = 0
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ProofArchive")

    def store_proof(self, data: ProofIngest) -> ProofMetadata:
        """Saves a proof and calculates its vaporization timestamp."""
        now = int(time.time())
        expiry = now + self.RETENTION_WINDOW_SEC
        
        meta = ProofMetadata(
            task_id=data.task_id,
            node_id=data.node_id,
            dhash=data.dhash,
            stored_at=now,
            expires_at=expiry
        )
        
        self.vault[data.task_id] = {
            "blob": data.image_b64,
            "meta": meta
        }
        
        self.logger.info(f"[*] Proof Archived: {data.task_id} (Expires in 24h)")
        return meta

    def get_proof(self, task_id: str) -> Optional[Dict]:
        """Retrieves proof for the Fraud Dashboard comparison."""
        entry = self.vault.get(task_id)
        if not entry:
            return None
            
        # Check if expired but not yet swept
        if int(time.time()) > entry["meta"].expires_at:
            self.logger.warning(f"[!] Access Denied: Proof {task_id} has expired.")
            return None
            
        return entry

    def execute_maintenance_sweep(self) -> int:
        """
        The 'Toxic Waste' Purge.
        Irreversibly deletes expired evidence from memory/disk.
        """
        now = int(time.time())
        expired_keys = [
            tid for tid, entry in self.vault.items() 
            if now > entry["meta"].expires_at
        ]
        
        for tid in expired_keys:
            # Overwrite logic (Simulation)
            self.vault[tid]["blob"] = "NULL_WIPED"
            del self.vault[tid]
            self.purge_count += 1
            self.logger.info(f"[X] SCORCHED EARTH: Proof {tid} irreversibly purged.")
            
        return len(expired_keys)

# Initialize Manager
archive = ProofArchiveManager()

# --- API Endpoints ---

@app.post("/v1/archive/ingest", response_model=ProofMetadata)
async def ingest_proof(payload: ProofIngest):
    """
    Called by the Settlement Oracle after hardware verification.
    Moves the proof into the temporary forensic archive.
    """
    return archive.store_proof(payload)

@app.get("/v1/archive/proof/{task_id}")
async def fetch_proof(task_id: str):
    """
    Internal forensic endpoint for the Fraud Dashboard.
    Returns the B64 image blob for visual comparison.
    """
    entry = archive.get_proof(task_id)
    if not entry:
        raise HTTPException(status_code=410, detail="Proof expired or never archived.")
    
    return {
        "task_id": task_id,
        "image_data": entry["blob"],
        "metadata": entry["meta"]
    }

@app.get("/v1/archive/status", response_model=ArchiveStatus)
async def get_archive_status():
    """Returns metadata about the containment pool."""
    active = len(archive.vault)
    return ArchiveStatus(
        active_proofs=active,
        pending_purges=len([t for t in archive.vault.values() if int(time.time()) > t["meta"].expires_at]),
        total_purged_lifetime=archive.purge_count,
        storage_utilization="NOMINAL"
    )

@app.post("/v1/archive/purge")
async def trigger_manual_purge(background_tasks: BackgroundTasks):
    """Admin endpoint to force a maintenance sweep."""
    purged = archive.execute_maintenance_sweep()
    return {"status": "SUCCESS", "records_destroyed": purged}

@app.get("/health")
async def health():
    return {"status": "online", "retention_policy": "24H_SCRUB"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8012 for ops-level access
    print("[*] Launching Protocol Proof Archive API on port 8012...")
    uvicorn.run(app, host="0.0.0.0", port=8012)
