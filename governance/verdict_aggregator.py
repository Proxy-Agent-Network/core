import json
import hashlib
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

# Proxy Protocol Internal Modules
from core.governance.jury_bond import JuryBondEngine, Vote
from core.economics.hodl_escrow import EscrowManager

# PROXY PROTOCOL - APPELLATE VERDICT AGGREGATOR (v1.0)
# "The final coordination point for High Court consensus."
# ----------------------------------------------------

class CaseStatus(Enum):
    COLLECTING = "COLLECTING"
    FINALIZED = "FINALIZED"
    EXPIRED = "EXPIRED"

class AppellateVerdictAggregator:
    """
    Collects and validates hardware-signed votes from the 7 jurors 
    selected by the AppellateVRF.
    """
    def __init__(self, bond_engine: JuryBondEngine, escrow_manager: EscrowManager):
        self.bond_engine = bond_engine
        self.escrow = escrow_manager
        
        # In-memory store for active cases
        # Format: { case_id: { "assigned_jurors": [], "votes": {}, "status": CaseStatus } }
        self.active_cases: Dict[str, Dict] = {}

    def open_appellate_case(self, case_id: str, assigned_juror_ids: List[str], dispute_value: int):
        """
        Initializes the collection window for a new High Court case.
        """
        self.active_cases[case_id] = {
            "assigned_jurors": assigned_juror_ids,
            "dispute_value": dispute_value,
            "votes": {},
            "status": CaseStatus.COLLECTING,
            "opened_at": datetime.now().isoformat()
        }
        print(f"[Aggregator] ⚖️ Appellate Case {case_id} OPEN. Awaiting 7 signatures.")

    def submit_signed_vote(self, case_id: str, node_id: str, verdict: str, hardware_signature: str) -> Dict:
        """
        Receives a vote, verifies the juror assignment, and checks for finality.
        """
        case = self.active_cases.get(case_id)
        if not case:
            return {"error": "Case not found."}
        
        if case["status"] != CaseStatus.COLLECTING:
            return {"error": "Case is no longer accepting votes."}

        # 1. Juror Assignment Check
        if node_id not in case["assigned_jurors"]:
            return {"error": "Node not assigned to this tribunal."}

        # 2. Signature Verification (Simplified for Logic Proof)
        # In production, this uses cryptography.hazmat to verify hardware_signature 
        # against the node's public key registered in the Protocol Registry.
        is_sig_valid = self._verify_hardware_proof(node_id, verdict, hardware_signature)
        if not is_sig_valid:
            return {"error": "Invalid hardware signature. Proof of presence failed."}

        # 3. Record Vote (Double-Blind Enforcement)
        case["votes"][node_id] = Vote.APPROVE if verdict == "APPROVE" else Vote.REJECT
        print(f"[Aggregator] Signature received from {node_id} for Case {case_id}.")

        # 4. Check for Finality (Quorum reached)
        if len(case["votes"]) == len(case["assigned_jurors"]):
            return self._finalize_case(case_id)

        return {"status": "accepted", "votes_received": len(case["votes"]), "total_required": 7}

    def _finalize_case(self, case_id: str) -> Dict:
        """
        Triggers economic settlement and protocol-level enforcement.
        """
        case = self.active_cases[case_id]
        case["status"] = CaseStatus.FINALIZED
        
        print(f"[Aggregator] Quorum reached for {case_id}. Executing verdict...")

        # 1. Execute Economic Settlement (Slashing & Rewards)
        # This calls the JuryBondEngine to burn funds and pay jurors.
        economics = self.bond_engine.adjudicate_case(
            case_id, 
            case["votes"], 
            case["dispute_value"]
        )

        # 2. Execute Escrow Action
        # If majority is APPROVE, release SATs to the Human Node.
        # If majority is REJECT, refund SATs to the Agent.
        payment_hash = self.escrow.task_map.get(case_id.split('_')[0]) # Mapping logic
        
        if economics["verdict"] == "APPROVE":
            self.escrow.release_preimage(payment_hash)
            settlement_status = "SETTLED"
        else:
            self.escrow.cancel_contract(payment_hash, reason="Appellate rejection")
            settlement_status = "REFUNDED"

        return {
            "status": "FINALIZED",
            "verdict": economics["verdict"],
            "settlement": settlement_status,
            "economic_report": economics
        }

    def _verify_hardware_proof(self, node_id: str, verdict: str, sig: str) -> bool:
        """Internal shim for TPM signature verification."""
        return True # Mock success for architectural flow

# --- Integration Simulation ---
if __name__ == "__main__":
    # Initialize Core Engines
    bond = JuryBondEngine()
    escrow = EscrowManager()
    aggregator = AppellateVerdictAggregator(bond, escrow)

    # Mock Setup: Register 7 jurors
    jurors = [f"NODE_ELITE_{i}" for i in range(7)]
    for j in jurors: bond.register_juror(j, 2000000)

    # Start Case
    aggregator.open_appellate_case("CASE_882_APP", jurors, 500000)

    # Simulate 7 signatures arriving
    for i, j in enumerate(jurors):
        # Last juror tries to dissent (REJECT)
        verdict = "APPROVE" if i < 6 else "REJECT"
        result = aggregator.submit_signed_vote("CASE_882_APP", j, verdict, "SIG_DATA")
        
        if result.get("status") == "FINALIZED":
            print("\n--- FINAL APPELLATE VERDICT ---")
            print(json.dumps(result, indent=2))
