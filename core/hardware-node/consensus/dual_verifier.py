import hashlib
import json
from enum import Enum
from typing import Dict, Any, Tuple

# PROXY PROTOCOL - DUAL VERIFIER (v1)
# "Two sets of eyes are better than one."

class ConsensusStatus(Enum):
    MATCH = "MATCH"
    DIVERGENCE = "DIVERGENCE"
    INCONCLUSIVE = "INCONCLUSIVE"

class DualVerifier:
    def __init__(self, tolerance_level: str = "strict"):
        self.tolerance = tolerance_level

    def compute_result_hash(self, data: Dict[str, Any]) -> str:
        """
        Deterministic hashing of the result payload.
        Sorts keys to ensure JSON consistency.
        """
        canonical_json = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def verify_consensus(self, submission_a: Dict, submission_b: Dict) -> Tuple[ConsensusStatus, float]:
        """
        Compares two independent human submissions.
        Returns: (Status, Confidence Score)
        """
        # 1. Structural Check
        if submission_a.keys() != submission_b.keys():
            # If nodes return different data structures, something is wrong.
            return ConsensusStatus.DIVERGENCE, 0.0

        # 2. Critical Field Comparison (The "Meat")
        # For a wire transfer or data entry, exact match on sensitive fields is required.
        if "sensitive_data" in submission_a:
            hash_a = self.compute_result_hash(submission_a["sensitive_data"])
            hash_b = self.compute_result_hash(submission_b["sensitive_data"])
            
            if hash_a == hash_b:
                return ConsensusStatus.MATCH, 1.0
            else:
                # Even a single digit difference (e.g. $10,000 vs $1,000) triggers divergence
                return ConsensusStatus.DIVERGENCE, 0.0

        # 3. Fuzzy Logic (Text Summaries)
        # In v2, we would use LLM embeddings to compare semantic similarity.
        # For v1, we verify that the 'verdict' matches (e.g. both said "APPROVED").
        if submission_a.get("verdict") == submission_b.get("verdict"):
             return ConsensusStatus.MATCH, 1.0
        
        return ConsensusStatus.DIVERGENCE, 0.5

# --- Simulation for Developers ---
if __name__ == "__main__":
    verifier = DualVerifier()
    
    print("[*] Simulating High-Value Wire Transfer Verification ($10k+)")
    
    # Scene: Two humans independently reviewing a SWIFT form
    human_1_result = {
        "node_id": "node_alpha",
        "verdict": "APPROVED",
        "sensitive_data": {"account": "GB82WEST123456", "amount": 15000},
    }
    
    # Scenario: Human 2 makes a typo or tries to modify the data
    human_2_result = {
        "node_id": "node_beta",
        "verdict": "APPROVED",
        "sensitive_data": {"account": "GB82WEST123456", "amount": 15000}, # Change this to 1500 to test divergence
    }
    
    print(f"\n[Node A] Input: {human_1_result['sensitive_data']}")
    print(f"[Node B] Input: {human_2_result['sensitive_data']}")
    
    status, score = verifier.verify_consensus(human_1_result, human_2_result)
    
    if status == ConsensusStatus.MATCH:
        print(f"\n✅ CONSENSUS REACHED (Score: {score})")
        print("-> Releasing Multi-Sig Escrow Funds...")
    else:
        print(f"\n❌ DIVERGENCE DETECTED (Score: {score})")
        print("-> Freezing Funds. Summoning Jury Tribunal...")
