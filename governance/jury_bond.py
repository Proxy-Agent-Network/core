import time
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

# PROXY PROTOCOL - JURY BOND & SLASHING ENGINE (v1.1)
# "Economic finality for the decentralized High Court."
# ----------------------------------------------------

class Vote(Enum):
    APPROVE = 1
    REJECT = 0

@dataclass
class JurorState:
    node_id: str
    staked_sats: int
    active_cases: List[str]
    total_fees_earned: int = 0
    penalty_count: int = 0

class JuryBondEngine:
    """
    Manages the collateral and economic rewards/penalties for the Jury Tribunal.
    Aligns with the 'Super-Elite' tier (REP > 950) requirements.
    """
    def __init__(self):
        # Configuration as per specs/v1/economics.md
        self.MIN_JURY_BOND = 2_000_000  # 2M Sats (~$2k USD) required for Judge status
        self.SLASH_RATE = 0.30          # Burn 30% of bond if voting against consensus
        self.JUROR_FEE_SHARE = 0.10     # Winners split 10% of the original dispute value
        self.SLASH_REWARD = 0.50        # Winners split 50% of the slashed funds (Whistleblower Bonus)
        self.TREASURY_TAX = 0.50        # Remaining 50% of slash goes to protocol burn

        # Internal Ledger (In prod: backed by Lightning/On-chain multisig)
        self.jurors: Dict[str, JurorState] = {}

    def register_juror(self, node_id: str, deposit_sats: int) -> Dict:
        """
        Locks funds to enable Jury eligibility.
        Ensures the human has skin in the game before adjudicating AI instructions.
        """
        if deposit_sats < self.MIN_JURY_BOND:
            return {
                "status": "REJECTED", 
                "reason": f"Insufficient Bond. Require {self.MIN_JURY_BOND} Sats."
            }
        
        self.jurors[node_id] = JurorState(
            node_id=node_id,
            staked_sats=deposit_sats,
            active_cases=[]
        )
        
        print(f"[Bond] Juror {node_id} registered with {deposit_sats:,} Sats.")
        return {"status": "ACTIVE", "node_id": node_id, "staked": deposit_sats}

    def adjudicate_case(self, case_id: str, votes: Dict[str, Vote], dispute_value: int) -> Dict:
        """
        Determines the Schelling Point (Truth) based on majority consensus.
        Slashes the minority to punish coordination failure.
        Rewards the majority for honest validation.
        """
        # 1. Quorum Check
        total_votes = len(votes)
        if total_votes < 3:
            return {"error": "Quorum not met (Min 3 jurors required)"}

        # 2. Tally Votes
        counts = {Vote.APPROVE: 0, Vote.REJECT: 0}
        for v in votes.values():
            counts[v] += 1
            
        # 3. Determine Consensus (The "Truth")
        consensus_vote = Vote.APPROVE if counts[Vote.APPROVE] > counts[Vote.REJECT] else Vote.REJECT
        
        winners = []
        losers = []
        
        for node_id, vote in votes.items():
            if vote == consensus_vote:
                winners.append(node_id)
            else:
                losers.append(node_id)

        # 4. Economic Settlement Logic
        results = {
            "case_id": case_id,
            "verdict": consensus_vote.name,
            "slashed_nodes": [],
            "rewarded_nodes": [],
            "summary": {
                "total_jurors": total_votes,
                "consensus": f"{max(counts.values())}/{total_votes}"
            }
        }

        # Step A: Slash the Dissenters (Minority)
        total_slashed_pool = 0
        for node_id in losers:
            if node_id in self.jurors:
                penalty = int(self.jurors[node_id].staked_sats * self.SLASH_RATE)
                self.jurors[node_id].staked_sats -= penalty
                self.jurors[node_id].penalty_count += 1
                total_slashed_pool += penalty
                results["slashed_nodes"].append({"id": node_id, "penalty": penalty})

        # Step B: Reward the Truth-Tellers (Majority)
        if winners:
            # Base adjudication fee from the task escrow
            base_fee_reward = int((dispute_value * self.JUROR_FEE_SHARE) / len(winners))
            # Bonus from the pool of slashed funds
            slash_bonus = int((total_slashed_pool * self.SLASH_REWARD) / len(winners))
            
            total_payout_per_winner = base_fee_reward + slash_bonus
            
            for node_id in winners:
                if node_id in self.jurors:
                    self.jurors[node_id].total_fees_earned += total_payout_per_winner
                    # In production, this triggers a Lightning Keysend
                    results["rewarded_nodes"].append({
                        "id": node_id, 
                        "payout": total_payout_per_winner,
                        "breakdown": {"fee": base_fee_reward, "bonus": slash_bonus}
                    })

        # Step C: Protocol Burn
        results["treasury_burn"] = total_slashed_pool - (slash_bonus * len(winners))

        return results

# --- Protocol Simulation ---
if __name__ == "__main__":
    engine = JuryBondEngine()
    
    print("--- HIGH COURT ADJUDICATION SIMULATION ---")
    
    # 1. Setup Jury Pool
    jurors = ["node_alpha", "node_beta", "node_gamma", "node_delta", "node_attacker"]
    for j in jurors:
        engine.register_juror(j, 2_000_000)

    # 2. Simulation Scenario: Case #992
    # Agent claims a photo of a document is fake.
    # 4 Jurors correctly identify it as REAL (APPROVE).
    # 1 Juror (Attacker) tries to grief the human node (REJECT).
    votes_cast = {
        "node_alpha": Vote.APPROVE,
        "node_beta": Vote.APPROVE,
        "node_gamma": Vote.APPROVE,
        "node_delta": Vote.APPROVE,
        "node_attacker": Vote.REJECT  # Malicious/Dishonest vote
    }
    
    # Value of contested task: 500,000 Sats
    decision = engine.adjudicate_case("case_992", votes_cast, dispute_value=500_000)
    
    print(f"\nVerdict: {decision['verdict']} ({decision['summary']['consensus']})")
    print("-" * 50)
    
    print("💀 SLASHED (Attacker Cluster):")
    for s in decision['slashed_nodes']:
        print(f"   - {s['id']}: -{s['penalty']:,} Sats")
        
    print("\n🏆 REWARDED (Truthful Elite):")
    for r in decision['rewarded_nodes']:
        print(f"   - {r['id']}: +{r['payout']:,} Sats")
        
    print("-" * 50)
    print(f"🏦 Protocol Treasury Burn: {decision['treasury_burn']:,} Sats")
