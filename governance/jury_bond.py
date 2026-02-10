import time
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

# PROXY PROTOCOL - JURY BOND & SLASHING ENGINE (v1)
# "Skin in the game ensures truth in the verdict."

class Vote(Enum):
    APPROVE = 1
    REJECT = 0

class JuryBondEngine:
    def __init__(self):
        # Configuration
        self.MIN_JURY_BOND = 2_000_000  # 2M Sats (~$2k) required to be a Judge
        self.SLASH_RATE = 0.30          # Burn 30% of bond if you vote against consensus
        self.JUROR_FEE_SHARE = 0.10     # Winners split 10% of the dispute value
        self.SLASH_REWARD = 0.50        # Winners get 50% of the slashed funds (Whistleblower Bonus)

    def register_juror(self, node_id: str, deposit_sats: int) -> Dict:
        """Lock funds to enable Jury eligibility."""
        if deposit_sats < self.MIN_JURY_BOND:
            return {
                "status": "REJECTED", 
                "reason": f"Insufficient Bond. Require {self.MIN_JURY_BOND} Sats."
            }
        return {"status": "ACTIVE", "node_id": node_id, "staked": deposit_sats}

    def adjudicate_case(self, case_id: str, votes: Dict[str, Vote], dispute_value: int) -> Dict:
        """
        Determines the Schelling Point (Truth) based on majority consensus.
        Slashes the minority. Rewards the majority.
        """
        # 1. Tally Votes
        counts = {Vote.APPROVE: 0, Vote.REJECT: 0}
        for v in votes.values():
            counts[v] += 1
            
        total_votes = len(votes)
        if total_votes < 3:
            return {"error": "Quorum not met (Min 3 jurors)"}

        # 2. Determine Truth (Consensus)
        consensus_vote = Vote.APPROVE if counts[Vote.APPROVE] > counts[Vote.REJECT] else Vote.REJECT
        
        winners = []
        losers = []
        
        for node_id, vote in votes.items():
            if vote == consensus_vote:
                winners.append(node_id)
            else:
                losers.append(node_id)

        # 3. Execute Economic Logic
        results = {
            "case_id": case_id,
            "verdict": consensus_vote.name,
            "slashed_nodes": [],
            "rewarded_nodes": []
        }

        # Slash Losers
        total_slashed_pool = 0
        for node in losers:
            # In production, this triggers a Lightning Penalty Transaction
            penalty = int(self.MIN_JURY_BOND * self.SLASH_RATE)
            total_slashed_pool += penalty
            results["slashed_nodes"].append({"id": node, "amount": penalty})

        # Reward Winners (Dispute Fee + Portion of Slashed Funds)
        if winners:
            base_fee_reward = int((dispute_value * self.JUROR_FEE_SHARE) / len(winners))
            slash_bonus = int((total_slashed_pool * self.SLASH_REWARD) / len(winners))
            
            total_payout = base_fee_reward + slash_bonus
            for node in winners:
                results["rewarded_nodes"].append({"id": node, "amount": total_payout})

        # The remaining slashed funds go to the Protocol Treasury
        results["treasury_burn"] = total_slashed_pool - (slash_bonus * len(winners))

        return results

# --- Simulation for Economic Stress Testing ---
if __name__ == "__main__":
    engine = JuryBondEngine()
    
    print("[*] Tribunal Session Started: Case #992")
    print(f"[*] Minimum Bond: {engine.MIN_JURY_BOND:,} Sats")
    print(f"[*] Slash Rate: {engine.SLASH_RATE*100}%")
    
    # Scenario: 5 Jurors. 4 vote APPROVE (Real), 1 votes REJECT (Malicious/Lazy).
    # This represents a Sybil attacker trying to disrupt a valid task.
    votes_cast = {
        "juror_alice": Vote.APPROVE,
        "juror_bob": Vote.APPROVE,
        "juror_charlie": Vote.APPROVE,
        "juror_dave": Vote.APPROVE,
        "juror_eve": Vote.REJECT  # The Dissenter
    }
    
    print(f"\n[*] Casting Votes: {votes_cast}")
    
    decision = engine.adjudicate_case("case_992", votes_cast, dispute_value=500_000)
    
    print(f"\nVerdict: {decision['verdict']}")
    print("-" * 40)
    print("💀 SLASHED (Minority Voters):")
    for s in decision['slashed_nodes']:
        print(f"   - {s['id']}: -{s['amount']:,} Sats (Burned)")
        
    print("\n🏆 REWARDED (Majority Voters):")
    for r in decision['rewarded_nodes']:
        print(f"   - {r['id']}: +{r['amount']:,} Sats (Fee + Slash Bonus)")
        
    print("-" * 40)
    print(f"🏦 Treasury Burn: {decision['treasury_burn']:,} Sats")
