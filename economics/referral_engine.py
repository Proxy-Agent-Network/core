import json
from dataclasses import dataclass
from typing import Dict, List, Optional

# PROXY PROTOCOL - GROWTH & REFERRAL ENGINE (v1)
# "Incentivizing the physical layer expansion."

@dataclass
class ReferralBond:
    referrer_id: str
    new_node_id: str
    jurisdiction: str
    status: str = "VESTING"  # VESTING, PAYABLE, PAID
    tasks_completed: int = 0

class ReferralEngine:
    def __init__(self):
        # Configuration
        self.BASE_REFERRAL_SATS = 50_000  # ~$50 bonus
        # "Bounty Zones": Jurisdictions where we need more nodes
        self.TARGET_ZONES = ["BR", "IN", "JP", "NG", "SG"] 
        self.ZONE_MULTIPLIER = 2.0        # 2x bonus for target zones
        self.VESTING_THRESHOLD = 10       # New node must complete 10 valid tasks to unlock bonus

        # Mock Database
        self.bonds: Dict[str, ReferralBond] = {}

    def register_referral(self, referrer_id: str, new_node_id: str, region: str) -> Dict:
        """
        Links a new node to an existing operator (Referrer).
        """
        if new_node_id in self.bonds:
            return {"error": "Node already referred"}

        bond = ReferralBond(
            referrer_id=referrer_id,
            new_node_id=new_node_id,
            jurisdiction=region
        )
        self.bonds[new_node_id] = bond
        
        is_target = region in self.TARGET_ZONES
        potential_value = self.BASE_REFERRAL_SATS * (self.ZONE_MULTIPLIER if is_target else 1.0)

        return {
            "status": "REGISTERED",
            "jurisdiction": region,
            "is_target_zone": is_target,
            "potential_payout_sats": int(potential_value),
            "vesting_condition": f"Complete {self.VESTING_THRESHOLD} tasks"
        }

    def process_task_completion(self, node_id: str):
        """
        Called whenever a node completes a task. Updates vesting progress.
        """
        if node_id not in self.bonds:
            return
        
        bond = self.bonds[node_id]
        if bond.status != "VESTING":
            return

        bond.tasks_completed += 1
        print(f"[Growth] {node_id} vesting progress: {bond.tasks_completed}/{self.VESTING_THRESHOLD}")
        
        if bond.tasks_completed >= self.VESTING_THRESHOLD:
            bond.status = "PAYABLE"
            print(f"[Growth] 💰 VESTING COMPLETE! {bond.referrer_id} earned bonus for {node_id}")

    def claim_rewards(self, referrer_id: str) -> int:
        """
        Calculates total payable sats for a referrer and marks as PAID.
        """
        total_payout = 0
        
        for node_id, bond in self.bonds.items():
            if bond.referrer_id == referrer_id and bond.status == "PAYABLE":
                multiplier = self.ZONE_MULTIPLIER if bond.jurisdiction in self.TARGET_ZONES else 1.0
                payout = int(self.BASE_REFERRAL_SATS * multiplier)
                total_payout += payout
                bond.status = "PAID"
                
        return total_payout

# --- CLI Simulation ---
if __name__ == "__main__":
    growth = ReferralEngine()
    
    print("[*] Registering New Node in Brazil (Target Zone)...")
    # A US veteran recruits a new node in Brazil
    reg = growth.register_referral("node_usa_veteran", "node_brazil_new", "BR")
    print(json.dumps(reg, indent=2))
    
    print("\n[*] Simulating Task Activity for New Node...")
    # Simulate 10 tasks to hit vesting threshold
    for i in range(1, 12):
        growth.process_task_completion("node_brazil_new")
        if i == 10:
            print("    -> Threshold Crossed.")

    print("\n[*] Referrer Claiming Rewards...")
    payout = growth.claim_rewards("node_usa_veteran")
    print(f"    -> Lightning Invoice Paid: {payout} Sats")
