import time
import json
import hashlib
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

# Proxy Protocol Internal Modules
from core.reputation.oracle import ReputationOracle

# PROXY PROTOCOL - REPUTATION MIGRATION ENGINE (v1.0)
# "Identity is persistent; hardware is transient."
# ----------------------------------------------------

@dataclass
class MigrationManifest:
    old_node_id: str
    new_node_id: str
    human_identity_key: str
    original_score: int
    migrated_score: int
    timestamp: int
    manifest_hash: str

class MigrationEngine:
    """
    Handles the transfer of reputation between nodes following a hardware failure.
    Enforces the 'Node Recovery Protocol' (specs/hardware/node_recovery.md).
    """
    STABILITY_PENALTY = 0.10  # 10% penalty for operational instability
    PROBATION_DAYS = 7        # Recertified nodes enter a 7-day probation

    def __init__(self, oracle: ReputationOracle):
        self.oracle = oracle
        self.migration_ledger: Dict[str, MigrationManifest] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("MigrationEngine")

    def validate_migration_request(self, old_id: str, new_id: str, signature: str) -> Tuple[bool, str]:
        """
        Verifies that the migration is authorized by the same human operator.
        Proves Key A (Dead) and Key B (New) are linked to Human Identity X.
        """
        # 1. Check if Old Node actually has reputation to migrate
        # simulation: normally fetch from persistent oracle storage
        if old_id == "NODE_EMPTY":
            return False, "Old Node ID has no established reputation."

        # 2. Verify Cryptographic Link
        # In production, we verify the 'signature' against the Human Identity Key 
        # registered in the KYC/IAM layer.
        is_signature_valid = True # Mock verification
        
        if not is_signature_valid:
            return False, "Signature verification failed. Potential hijacking attempt."

        return True, "Identity Link Verified."

    def execute_migration(self, old_id: str, new_id: str, human_key: str) -> Dict:
        """
        Performs the mathematical migration and records the event.
        Calculates the 10% penalty and initializes probation.
        """
        self.logger.info(f"[*] Initiating migration: {old_id} -> {new_id}")

        # 1. Fetch Source Standing
        # Simulation: In prod, this pulls the score and prevents double-migration
        source_score = 982 # Elite score for the purpose of the demo

        # 2. Apply Penalty (Recovery Protocol Rule 3)
        penalty = int(source_score * self.STABILITY_PENALTY)
        new_score = source_score - penalty

        # 3. Construct Manifest
        timestamp = int(time.time())
        manifest_data = f"{old_id}:{new_id}:{timestamp}:{new_score}"
        manifest_hash = hashlib.sha256(manifest_data.encode()).hexdigest()

        manifest = MigrationManifest(
            old_node_id=old_id,
            new_node_id=new_id,
            human_identity_key=human_key,
            original_score=source_score,
            migrated_score=new_score,
            timestamp=timestamp,
            manifest_hash=manifest_hash
        )

        # 4. Persistence & Oracle Update
        self.migration_ledger[new_id] = manifest
        
        # Tell the Oracle to update the registry and flag for 7-day Probation
        # self.oracle.rebind_identity(old_id, new_id, new_score, probation_days=self.PROBATION_DAYS)

        self.logger.info(f"[✓] Migration Successful. {new_id} initialized with {new_score} REP.")
        
        return {
            "status": "MIGRATED",
            "node_id": new_id,
            "score": new_score,
            "penalty_applied": penalty,
            "probation_active": True,
            "probation_expiry": timestamp + (self.PROBATION_DAYS * 86400),
            "manifest_hash": manifest_hash
        }

# --- Recovery Simulation ---
if __name__ == "__main__":
    from core.reputation.oracle import ReputationOracle
    
    oracle_engine = ReputationOracle()
    engine = MigrationEngine(oracle_engine)

    print("--- NODE RECOVERY CEREMONY (v1.0) ---")
    
    # Scene: Operator's Pi 5 chassis was opened accidentally. TPM wiped.
    old_node = "NODE_ELITE_X29"
    new_node = "NODE_ELITE_REPLACEMENT_01"
    human_id = "IDENTITY_88293_ROB"

    # 1. Validation
    valid, reason = engine.validate_migration_request(old_node, new_node, "SIG_PROOF_DATA")
    
    if valid:
        # 2. Execution
        result = engine.execute_migration(old_node, new_node, human_id)
        
        print(f"\n✅ MIGRATION COMPLETE")
        print(f"   - Previous ID: {old_node}")
        print(f"   - New Unit ID: {result['node_id']}")
        print(f"   - Final Score: {result['score']} (Stability Penalty: -{result['penalty_applied']})")
        print(f"   - Probation:   ACTIVE (7 Days)")
        print(f"   - Audit Hash:  {result['manifest_hash'][:16]}...")
    else:
        print(f"❌ MIGRATION BLOCKED: {reason}")
