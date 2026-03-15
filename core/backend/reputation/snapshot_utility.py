import json
import hashlib
import time
import os
from datetime import datetime
from typing import List, Dict

# PROXY PROTOCOL - REPUTATION SNAPSHOT UTILITY (v1.0)
# "Immutable historical state-root of the human network."
# ----------------------------------------------------

class ReputationSnapshotter:
    """
    Cron-compatible utility that generates a daily snapshot of all 
    Node REP scores. Used for forensics and historical trend analysis.
    """
    def __init__(self, archive_path: str = "/app/data/snapshots/"):
        self.archive_path = archive_path
        if not os.path.exists(self.archive_path):
            os.makedirs(self.archive_path)

    def capture_network_state(self, node_registry: List[Dict]) -> Dict:
        """
        Creates a structured snapshot of the current reputation landscape.
        """
        timestamp = datetime.now().isoformat()
        
        # 1. Sort nodes for deterministic hashing
        sorted_nodes = sorted(node_registry, key=lambda x: x['node_id'])
        
        # 2. Build the state payload
        state_payload = {
            "protocol_version": "v2.6.9",
            "snapshot_timestamp": timestamp,
            "node_count": len(sorted_nodes),
            "reputation_set": sorted_nodes
        }

        # 3. Generate State Root (SHA-256 Hash of the entire set)
        raw_json = json.dumps(state_payload, sort_keys=True)
        state_hash = hashlib.sha256(raw_json.encode()).hexdigest()
        
        return {
            "manifest": {
                "state_hash": state_hash,
                "generated_at": timestamp,
                "block_height_ref": 882931 # Simulated BTC block height
            },
            "data": state_payload
        }

    def save_snapshot(self, snapshot: Dict) -> str:
        """
        Persists the snapshot to disk with the state hash as the filename.
        """
        filename = f"rep_state_{snapshot['manifest']['state_hash'][:16]}.json"
        full_path = os.path.join(self.archive_path, filename)
        
        with open(full_path, "w") as f:
            json.dump(snapshot, f, indent=2)
            
        print(f"✅ Snapshot Saved: {full_path}")
        return full_path

    def verify_integrity(self, file_path: str) -> bool:
        """
        Validates that a historical snapshot hasn't been tampered with.
        """
        with open(file_path, "r") as f:
            snapshot = json.load(f)
            
        stored_hash = snapshot['manifest']['state_hash']
        
        # Re-calculate hash of the data segment
        raw_data = json.dumps(snapshot['data'], sort_keys=True)
        recalculated_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        
        return stored_hash == recalculated_hash

# --- Execution Simulation ---
if __name__ == "__main__":
    snapshotter = ReputationSnapshotter()

    # Mock Data: The current network state
    active_nodes = [
        {"node_id": "NODE_ELITE_X29", "rep": 982, "tier": "SUPER_ELITE"},
        {"node_id": "NODE_ALPHA_001", "rep": 845, "tier": "ELITE"},
        {"node_id": "NODE_PROB_77", "rep": 410, "tier": "PROBATION"}
    ]

    print("[*] Generating daily network reputation snapshot...")
    snap = snapshotter.capture_network_state(active_nodes)
    
    # Save to disk
    path = snapshotter.save_snapshot(snap)
    
    # Audit verification
    if snapshotter.verify_integrity(path):
        print(f"[*] Audit Check: PASSED. State Hash {snap['manifest']['state_hash'][:16]} is authentic.")
    else:
        print("🚨 Audit Check: FAILED. Snapshot corruption detected.")
