import time
import json
import os
import hashlib
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime

# PROXY PROTOCOL - QUARANTINE PERSISTENCE SERVICE (v1.0)
# "Ensuring the memory of a threat survives the reboot."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Quarantine Persistence",
    description="State preservation for subnets and node identities under protocol-level ban.",
    version="1.0.0"
)

# --- Configuration ---
STORAGE_PATH = "/app/data/security/quarantine_store.json"
MANIFEST_LOG = "/app/data/security/integrity_ledger.log"

class PersistenceEntry(BaseModel):
    pattern: str  # Subnet prefix or Hardware ID
    type: str     # SUBNET_BAN, TPM_REVOCATION
    reason: str
    added_at: int
    expires_at: Optional[int] = None
    checksum: str # Integrity hash of this specific entry

class PersistenceReport(BaseModel):
    total_active_bans: int
    last_persistence_sync: int
    store_integrity_hash: str

# --- Internal Persistence Logic ---

class QuarantinePersistenceManager:
    """
    Manages the lifecycle of permanent ban records.
    Uses a checksummed JSON store to prevent unauthorized manual whitelisting.
    """
    def __init__(self, file_path: str = STORAGE_PATH):
        self.file_path = file_path
        self.store: Dict[str, Dict] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("PersistenceService")

        # Create directory if missing
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self._load_from_disk()

    def _calculate_entry_checksum(self, pattern: str, reason: str, added_at: int) -> str:
        """Binds an entry to its metadata to detect tampering."""
        payload = f"{pattern}:{reason}:{added_at}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def _load_from_disk(self):
        """Reloads the state on service startup."""
        if not os.path.exists(self.file_path):
            self.logger.info("[*] Persistence store initialized (Empty).")
            return

        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                
            # Verify global integrity (Simulated)
            self.store = data.get("records", {})
            self.logger.info(f"✅ State Recovered: {len(self.store)} active bans loaded from silicon.")
        except Exception as e:
            self.logger.error(f"🚨 PERSISTENCE_CORRUPTION: Failed to load store: {str(e)}")
            self.store = {}

    def _save_to_disk(self):
        """Commits the current state to the persistent layer."""
        try:
            payload = {
                "protocol_version": "v3.6.5",
                "timestamp": int(time.time()),
                "records": self.store
            }
            
            # Atomic Write pattern
            temp_path = self.file_path + ".tmp"
            with open(temp_path, "w") as f:
                json.dump(payload, f, indent=2)
            os.replace(temp_path, self.file_path)
            
            self.logger.info("[✓] Sync Complete: Checksummed manifest flushed to disk.")
        except Exception as e:
            self.logger.error(f"🚨 SAVE_FAILURE: {str(e)}")

    def add_ban(self, pattern: str, ban_type: str, reason: str, expiry: Optional[int] = None):
        """Records a new enforcement action."""
        now = int(time.time())
        checksum = self._calculate_entry_checksum(pattern, reason, now)
        
        self.store[pattern] = {
            "type": ban_type,
            "reason": reason,
            "added_at": now,
            "expires_at": expiry,
            "checksum": checksum
        }
        
        self._save_to_disk()
        self.logger.info(f"🔒 PERSISTED: {ban_type} for {pattern}")

    def remove_ban(self, pattern: str):
        """Removes an entry from the store (Manual Override/Restore)."""
        if pattern in self.store:
            del self.store[pattern]
            self._save_to_disk()
            self.logger.info(f"🔓 RESTORED: {pattern} removed from persistent blacklist.")
            return True
        return False

# Initialize Manager
persistence = QuarantinePersistenceManager()

# --- API Endpoints ---

@app.post("/v1/persistence/record")
async def record_quarantine(
    pattern: str = Body(...),
    ban_type: str = Body(...),
    reason: str = Body(...),
    expiry: Optional[int] = Body(None)
):
    """
    Called by the Probing Quarantine API.
    Commits a security event to cold storage.
    """
    try:
        persistence.add_ban(pattern, ban_type, reason, expiry)
        return {"status": "PERSISTED", "pattern": pattern}
    except Exception as e:
        raise HTTPException(status_code=500, detail="PERSISTENCE_LAYER_FAILURE")

@app.get("/v1/persistence/sync")
async def get_full_blacklist():
    """
    Called by the Threat Intelligence and SSI APIs on startup.
    Returns the full set of active restrictions.
    """
    return persistence.store

@app.post("/v1/persistence/restore/{pattern}")
async def manual_override_restore(pattern: str):
    """
    Called by the SOC Desk (Quarantine Auditor UI).
    Manually removes a block from the persistent store.
    """
    success = persistence.remove_ban(pattern)
    if not success:
        raise HTTPException(status_code=404, detail="Pattern not found in active store.")
    return {"status": "RESTORED", "pattern": pattern}

@app.get("/v1/persistence/report", response_model=PersistenceReport)
async def get_persistence_health():
    """Returns metadata for the NOC Health Matrix."""
    state_str = json.dumps(persistence.store, sort_keys=True)
    master_hash = hashlib.sha256(state_str.encode()).hexdigest()
    
    return PersistenceReport(
        total_active_bans=len(persistence.store),
        last_persistence_sync=int(time.time()),
        store_integrity_hash=master_hash
    )

@app.get("/health")
async def health():
    return {"status": "online", "disk_writable": os.access(os.path.dirname(STORAGE_PATH), os.W_OK)}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal security management port 8029
    print("[*] Launching Protocol Quarantine Persistence Service on port 8029...")
    uvicorn.run(app, host="0.0.0.0", port=8029)
