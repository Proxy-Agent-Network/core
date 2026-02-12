import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from enum import Enum

# PROXY PROTOCOL - JURY BOND & ELIGIBILITY ENGINE (v1.2)
# "Economic gatekeeping for the Appellate Court."
# ----------------------------------------------------

class Vote(Enum):
    APPROVE = 1
    REJECT = 0

@dataclass
class JurorState:
    node_id: str
    staked_sats: int
    active_cases: List[str] = field(default_factory=list)
    total_fees_earned: int = 0
    penalty_count: int = 0
    is_locked: bool = False # Set to true if bond is currently in a 30-day exit lock

class JuryBondEngine:
    """
    Manages the collateral and economic eligibility for the Jury Tribunal.
    v1.2 Update: Integrated mandatory eligibility check for High Court selection.
    """
    def __init__(self):
        # Configuration as per specs/v1/economics.md and reputation.md
        self.MIN_JURY_BOND = 2_000_000      # 2M Sats (~$2k USD) required for High Court
        self.SLASH_RATE = 0.30              # Burn 30% of bond for dissenting against consensus
        self.JUROR_FEE_SHARE = 0.10         # Winners split 10% of dispute value
        
        # Internal Ledger
        self.jurors: Dict[str, JurorState] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("JuryBond")

    def register_juror(self, node_id: str, deposit_sats: int) -> Dict:
        """
        Locks funds to enable High Court eligibility.
        Ensures the human has significant skin in the game.
        """
        if deposit_sats < self.MIN_JURY_BOND:
            self.logger.warning(f"[Bond] Registration failed for {node_id}: Insufficient Sats.")
            return {
                "status": "REJECTED", 
                "reason": f"Insufficient Bond. Require {self.MIN_JURY_BOND} Sats for High Court status."
            }
        
        self.jurors[node_id] = JurorState(
            node_id=node_id,
            staked_sats=deposit_sats
        )
        
        self.logger.info(f"[Bond] Juror {node_id} activated with {deposit_sats:,} Sats.")
        return {"status": "ACTIVE", "node_id": node_id, "staked": deposit_sats}

    def verify_high_court_eligibility(self, node_id: str) -> Tuple[bool, str]:
        """
        CRITICAL GATE: Called by core/governance/appellate_vrf.py.
        Verifies that a candidate node has an active and sufficient bond.
        """
        juror = self.jurors.get(node_id)
        
        if not juror:
            return False, "Node not found in Bond Registry."
        
        if juror.staked_sats < self.MIN_JURY_BOND:
            return False, f"Bond below threshold: {juror.staked_sats} < {self.MIN_JURY_BOND}"
        
        if juror.is_locked:
            # Nodes attempting to withdraw their bond are ineligible for new cases
            return False, "Bond is currently in withdrawal lock window."

        return True, "ELIGIBLE"

    def adjudicate_case(self, case_id: str, votes: Dict[str, Vote], dispute_value: int) -> Dict:
        """
        Executes Schelling Point settlement.
        Winners get paid; losers get slashed.
        """
        total_votes = len(votes)
        if total_votes < 3:
            return {"error": "Quorum not met (Min 3 required)"}

        # Tally and Consensus logic
        counts = {Vote.APPROVE: 0, Vote.REJECT: 0}
        for v in votes.values():
            counts[v] += 1
            
        consensus_vote = Vote.APPROVE if counts[Vote.APPROVE] > counts[Vote.REJECT] else Vote.REJECT
        
        winners = [nid for nid, v in votes.items() if v == consensus_vote]
        losers = [nid for nid, v in votes.items() if v != consensus_vote]

        total_slashed = 0
        slashed_details = []

        # 1. Apply Slashes
        for node_id in losers:
            if node_id in self.jurors:
                penalty = int(self.jurors[node_id].staked_sats * self.SLASH_RATE)
                self.jurors[node_id].staked_sats -= penalty
                self.jurors[node_id].penalty_count += 1
                total_slashed += penalty
                slashed_details.append({"id": node_id, "penalty": penalty})

        # 2. Distribute Rewards
        rewarded_details = []
        if winners:
            # 50% of slashed funds go to winners (whistleblower bonus)
            slash_bonus = int((total_slashed * 0.50) / len(winners))
            base_fee = int((dispute_value * self.JUROR_FEE_SHARE) / len(winners))
            
            payout = slash_bonus + base_fee
            
            for node_id in winners:
                if node_id in self.jurors:
                    self.jurors[node_id].total_fees_earned += payout
                    rewarded_details.append({"id": node_id, "payout": payout})

        self.logger.info(f"[Verdict] Case {case_id} settled. Consensus: {consensus_vote.name}")

        return {
            "case_id": case_id,
            "verdict": consensus_vote.name,
            "slashed_nodes": slashed_details,
            "rewarded_nodes": rewarded_details,
            "treasury_burn": int(total_slashed * 0.50)
        }

# --- Operational Simulation ---
if __name__ == "__main__":
    engine = JuryBondEngine()
    
    print("--- HIGH COURT ELIGIBILITY AUDIT ---")
    
    # 1. Register Elite Node
    engine.register_juror("NODE_ELITE_X29", 2500000)
    
    # 2. Register Sub-threshold Node
    engine.register_juror("NODE_POOR_01", 1000000)

    # 3. Test Eligibility for VRF Selection
    for node in ["NODE_ELITE_X29", "NODE_POOR_01", "NODE_GHOST"]:
        eligible, reason = engine.verify_high_court_eligibility(node)
        status = "✅" if eligible else "❌"
        print(f"[{status}] Node: {node:<15} | {reason}")

    # 4. Simulate a Slash Event
    print("\n[!] Event: Consensus Divergence on Case #882...")
    votes = {
        "NODE_ELITE_X29": Vote.APPROVE,
        "NODE_VERIFIED_02": Vote.APPROVE,
        "NODE_DISSENT_03": Vote.REJECT # This node will be slashed
    }
    # Ensure all nodes are in registry for slash math
    engine.register_juror("NODE_VERIFIED_02", 2000000)
    engine.register_juror("NODE_DISSENT_03", 2000000)
    
    report = engine.adjudicate_case("CASE_882", votes, 500000)
    print(f"    -> Slash Applied to {report['slashed_nodes'][0]['id']}: -{report['slashed_nodes'][0]['penalty']} Sats")
