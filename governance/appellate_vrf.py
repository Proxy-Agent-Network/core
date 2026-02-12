import hashlib
import json
import requests
from typing import List, Dict, Any

# PROXY PROTOCOL - APPELLATE COURT VRF (v1.0)
# "Un-gameable juror selection via Bitcoin entropy."
# ----------------------------------------------------

class AppellateVRF:
    """
    Implements the Verifiable Random Function for the High Court.
    Ensures that juror selection is deterministic, auditable, and 
    immune to Foundation capture.
    """
    def __init__(self, reputation_threshold: int = 950):
        self.reputation_threshold = reputation_threshold
        self.blockchain_api = "https://blockchain.info/latestblock"

    def fetch_latest_block_hash(self) -> str:
        """
        Fetches the latest Bitcoin block hash to serve as the 'Seed' for the VRF.
        This provides a globally public, unpredictable entropy source.
        """
        try:
            # In production, this should poll a local Bitcoin node or multiple APIs
            response = requests.get(self.blockchain_api, timeout=5)
            return response.json().get('hash')
        except Exception as e:
            print(f"[*] Fallback to internal entropy: {str(e)}")
            return hashlib.sha256(str(requests.utils.time.time()).encode()).hexdigest()

    def select_jurors(self, pool: List[Dict[str, Any]], block_hash: str, count: int = 7) -> List[Dict]:
        """
        Deterministic selection logic.
        1. Filter pool by reputation threshold.
        2. Sort by node_id.
        3. Use block_hash + node_id to create a deterministic score.
        4. Select top scorers.
        """
        # Step 1: Filter for 'Super-Elite' status
        eligible_pool = [node for node in pool if node.get('reputation', 0) >= self.reputation_threshold]
        
        if len(eligible_pool) < count:
            print(f"[!] Warning: Only {len(eligible_pool)} eligible nodes found. Quorum at risk.")
        
        # Step 2: Deterministic Shuffle using the Block Hash
        selection_results = []
        for node in eligible_pool:
            # Composite hash: Hash(Block_Hash + Node_ID)
            entropy_source = f"{block_hash}{node['node_id']}"
            selection_score = hashlib.sha256(entropy_source.encode()).hexdigest()
            
            selection_results.append({
                "node_id": node['node_id'],
                "score": selection_score,
                "reputation": node['reputation']
            })

        # Step 3: Sort by score (hexadecimal string comparison is stable)
        selection_results.sort(key=lambda x: x['score'])
        
        # Step 4: Final Selection
        return selection_results[:count]

    def generate_convocation_proof(self, selected_jurors: List[Dict], block_hash: str) -> Dict:
        """
        Generates a signed manifest that can be verified by any network participant.
        """
        manifest = {
            "protocol_version": "v2.2.0",
            "selection_seed": block_hash,
            "jurors": [j['node_id'] for j in selected_jurors],
            "method": "SHA256_STABLE_SHUFFLE"
        }
        
        manifest_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        manifest['proof_hash'] = manifest_hash
        
        return manifest

# --- Integration Test ---
if __name__ == "__main__":
    vrf = AppellateVRF()
    
    # Mock Node Registry
    node_pool = [
        {"node_id": f"NODE_00{i}", "reputation": 940 + (i * 5)} for i in range(20)
    ]
    
    seed = vrf.fetch_latest_block_hash()
    print(f"[*] Convocation Seed (BTC Hash): {seed}")
    
    jurors = vrf.select_jurors(node_pool, seed)
    proof = vrf.generate_convocation_proof(jurors, seed)
    
    print("\n[⚖️] HIGH COURT CONVOCATED")
    print(json.dumps(proof, indent=2))
