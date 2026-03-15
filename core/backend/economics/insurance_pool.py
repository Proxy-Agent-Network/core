from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

# PROXY PROTOCOL - NODE INSURANCE POOL (v1)
# "Safety net for protocol-level failures."
# ----------------------------------------------------

@dataclass
class InsuranceClaim:
    claim_id: str
    node_id: str
    loss_amount_sats: int
    incident_report: str
    status: str = "PENDING" # PENDING, APPROVED, REJECTED
    timestamp: str = ""

class InsuranceEngine:
    def __init__(self):
        # Configuration
        self.TAX_RATE = 0.001  # 0.1% Tax on all task volume
        self.pool_balance_sats = 10_000_000 # Seeded with 0.1 BTC by the Foundation
        self.claims: Dict[str, InsuranceClaim] = {}

    def process_task_tax(self, task_amount_sats: int) -> int:
        """
        Calculates and deducts the insurance premium from a task settlement.
        Called automatically by the Settlement Layer.
        """
        premium = int(task_amount_sats * self.TAX_RATE)
        # In prod: Lightning payment routed to Insurance Wallet
        self.pool_balance_sats += premium
        print(f"[Insurance] Collected {premium} sats. Pool Total: {self.pool_balance_sats}")
        return premium

    def file_claim(self, node_id: str, amount_sats: int, proof_log: str) -> str:
        """
        Node submits a claim for funds lost due to a demonstrable protocol bug.
        (e.g., LND channel force-closure error, HODL invoice stuck state).
        """
        claim_id = f"claim_{len(self.claims) + 1}"
        claim = InsuranceClaim(
            claim_id=claim_id,
            node_id=node_id,
            loss_amount_sats=amount_sats,
            incident_report=proof_log,
            timestamp=datetime.now().isoformat()
        )
        self.claims[claim_id] = claim
        return claim_id

    def adjudicate_claim(self, claim_id: str, approved: bool, admin_note: str = ""):
        """
        Governance or Security Team reviews the claim validity.
        """
        if claim_id not in self.claims:
            print(f"[Insurance] Error: Claim {claim_id} not found.")
            return
        
        claim = self.claims[claim_id]
        
        if approved:
            if self.pool_balance_sats >= claim.loss_amount_sats:
                # In prod: Lightning Keysend to Node
                self.pool_balance_sats -= claim.loss_amount_sats
                claim.status = "APPROVED - PAID"
                print(f"[Insurance] 🛡️ CLAIM PAID: {claim.loss_amount_sats} sats sent to {claim.node_id}.")
                print(f"   -> New Pool Balance: {self.pool_balance_sats}")
            else:
                claim.status = "APPROVED - INSOLVENT"
                print("[Insurance] 🚨 CRITICAL: Pool insolvent. Cannot pay claim.")
        else:
            claim.status = "REJECTED"
            print(f"[Insurance] Claim rejected: {admin_note}")

# --- CLI Simulation ---
if __name__ == "__main__":
    insurance = InsuranceEngine()
    
    print("[*] Simulating Network Activity (Tax Collection)...")
    # Simulate high volume of small tasks
    for i in range(1000):
        # Random task values between 1k and 10k sats
        insurance.process_task_tax(5000)
        if i % 200 == 0:
            print("    -> Batch processing...")
        
    print(f"\n[*] Current Pool Depth: {insurance.pool_balance_sats:,} Sats")

    print("\n[*] Simulating Protocol Bug Incident...")
    # Scenario: Node lost 50,000 sats due to a rare HODL invoice timelock bug
    claim_id = insurance.file_claim(
        "node_victim_01", 
        50000, 
        "Error Log: HTLC timeout failed to refund due to logic error in v0.9.1. Transaction hash: abc123..."
    )
    print(f"    -> Claim Filed: {claim_id}")
    
    print("\n[*] Adjudicating Claim...")
    # Simulate manual review confirming the bug
    insurance.adjudicate_claim(claim_id, True, "Confirmed core protocol bug via logs.")
