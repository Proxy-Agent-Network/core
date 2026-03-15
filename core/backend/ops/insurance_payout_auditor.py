import logging
import json
import time
from typing import Dict, List, Optional
from datetime import datetime

# PROXY PROTOCOL - INSURANCE PAYOUT AUDITOR (v1.0)
# "Preventing double-spending of the protocol insurance pool."
# ----------------------------------------------------

class PayoutAuditor:
    """
    Independent audit service that validates payout requests before
    authorizing the final Lightning Network transmission.
    """
    def __init__(self):
        # In-memory history to prevent re-entrancy / double-claims
        # Format: { "claim_id": { "settled_at": float, "txid": str } }
        self.payout_ledger: Dict[str, Dict] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("PayoutAuditor")

    def _fetch_verdict_manifest(self, verdict_id: str) -> Optional[Dict]:
        """
        Queries the Verdict Registry to ensure the judgment is valid.
        Simulation: In production, calls GET /v1/registry/verdicts/{id}
        """
        # Mocking a valid High Court verdict for the simulation
        if verdict_id == "VERDICT-8829-APP":
            return {
                "id": verdict_id,
                "status": "APPROVED",
                "payout_authorized": 50000,
                "node_id": "NODE_ELITE_X29",
                "manifest_hash": "e3b0c442..."
            }
        return None

    def validate_payout_request(self, claim_id: str, verdict_id: str, node_id: str, amount_sats: int) -> Dict:
        """
        The triple-gate check:
        1. Does the claim ID exist in our processed ledger? (Anti-Double Claim)
        2. Does the verdict ID exist and is it 'APPROVED'?
        3. Does the requested amount match the verdict's authorized value?
        """
        self.logger.info(f"[*] Auditing payout request for Claim: {claim_id}")

        # Gate 1: Check for duplicate settlement
        if claim_id in self.payout_ledger:
            return {
                "authorized": False,
                "code": "PX_202",
                "message": f"Claim {claim_id} has already been settled."
            }

        # Gate 2: Verify against Case Law (Verdict Registry)
        manifest = self._fetch_verdict_manifest(verdict_id)
        if not manifest:
            return {
                "authorized": False,
                "code": "PX_301",
                "message": f"Verdict manifest {verdict_id} not found."
            }

        # Gate 3: Integrity Check (Amount & Recipient)
        if manifest["payout_authorized"] != amount_sats:
            return {
                "authorized": False,
                "code": "PX_203",
                "message": "Requested amount mismatch with authorized verdict value."
            }

        if manifest["node_id"] != node_id:
            return {
                "authorized": False,
                "code": "PX_100",
                "message": "Node ID mismatch. Payout must be sent to the original victim."
            }

        self.logger.info(f"✅ Payout request for {claim_id} AUTHORIZED.")
        return {"authorized": True, "manifest": manifest}

    def record_settlement(self, claim_id: str, txid: str):
        """Finalizes the audit entry once the Lightning transaction is broadcast."""
        self.payout_ledger[claim_id] = {
            "settled_at": time.time(),
            "txid": txid
        }
        self.logger.info(f"[✓] Settlement recorded for {claim_id}. Multi-spend protection active.")

# --- Operational Simulation ---
if __name__ == "__main__":
    auditor = PayoutAuditor()
    
    print("--- INSURANCE PAYOUT AUDIT TEST ---")
    
    # 1. Successful Payout Audit
    print("[*] Scenario: Legitimate claim for Node X29...")
    auth_result = auditor.validate_payout_request(
        claim_id="CLAIM-882-1",
        verdict_id="VERDICT-8829-APP",
        node_id="NODE_ELITE_X29",
        amount_sats=50000
    )
    
    if auth_result["authorized"]:
        print(f"    -> Authorized. Dispatching SATs...")
        auditor.record_settlement("CLAIM-882-1", "tx_lnd_keysend_88293")
    
    # 2. Re-entrancy Attempt (Double-Claim)
    print("\n[*] Scenario: Attacker attempts to claim the same ID again...")
    attack_result = auditor.validate_payout_request(
        claim_id="CLAIM-882-1",
        verdict_id="VERDICT-8829-APP",
        node_id="NODE_ELITE_X29",
        amount_sats=50000
    )
    
    if not attack_result["authorized"]:
        print(f"    -> Blocked: {attack_result['message']} ({attack_result['code']})")

    # 3. Amount Mismatch
    print("\n[*] Scenario: Incorrect amount requested...")
    mismatch_result = auditor.validate_payout_request(
        claim_id="CLAIM-882-2",
        verdict_id="VERDICT-8829-APP",
        node_id="NODE_ELITE_X29",
        amount_sats=999999
    )
    
    if not mismatch_result["authorized"]:
        print(f"    -> Blocked: {mismatch_result['message']}")
