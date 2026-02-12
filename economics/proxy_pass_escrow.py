import time
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from enum import Enum

# PROXY PROTOCOL - PROXY-PASS ESCROW CONTRACT (v1.0)
# "Managing long-term Satoshi liquidity and Reputation Yield."
# ----------------------------------------------------

class PassTier(Enum):
    STARTER = "STARTER"
    PRO = "PRO"
    ELITE = "ELITE"

@dataclass
class ProxyPass:
    pass_id: str
    owner_id: str
    tier: PassTier
    locked_sats: int
    start_timestamp: float
    last_yield_claim: float
    expiry_timestamp: float
    is_active: bool = True

class ProxyPassEscrow:
    """
    Backend logic for time-locking Satoshi deposits.
    Calculates Reputation Yield and manages API rate-limit boosts.
    """
    # Reputation Yield is 0.5% per epoch (one week)
    WEEKLY_YIELD_RATE = 0.005 
    SECONDS_IN_WEEK = 604800
    PASS_DURATION_SECONDS = 30 * 24 * 60 * 60 # 30 Days

    def __init__(self):
        # In production, these are backed by a persistent database (PostgreSQL/Redis)
        self.active_passes: Dict[str, ProxyPass] = {}
        self.yield_ledger: List[Dict] = []

    def provision_pass(self, owner_id: str, amount_sats: int, tier: PassTier) -> Dict:
        """
        Locks funds into the protocol escrow.
        Calculates expiry and returns the pass metadata.
        """
        pass_id = f"PASS-{hashlib.sha256(f'{owner_id}:{time.time()}'.encode()).hexdigest()[:8].upper()}"
        now = time.time()
        
        new_pass = ProxyPass(
            pass_id=pass_id,
            owner_id=owner_id,
            tier=tier,
            locked_sats=amount_sats,
            start_timestamp=now,
            last_yield_claim=now,
            expiry_timestamp=now + self.PASS_DURATION_SECONDS
        )
        
        self.active_passes[pass_id] = new_pass
        print(f"[Escrow] 🎟️ Provisioned {tier.value} Pass for {owner_id}. ID: {pass_id}")
        
        return asdict(new_pass)

    def get_accrued_yield(self, pass_id: str) -> int:
        """
        Calculates pending Satoshi yield.
        Formula: (Amount * Rate) * (Time_Since_Last_Claim / Week)
        """
        p_pass = self.active_passes.get(pass_id)
        if not p_pass or not p_pass.is_active:
            return 0
            
        elapsed = time.time() - p_pass.last_yield_claim
        weeks_elapsed = elapsed / self.SECONDS_IN_WEEK
        
        # Yield accrues based on the weekly rate
        accrued = int(p_pass.locked_sats * self.WEEKLY_YIELD_RATE * weeks_elapsed)
        return accrued

    def claim_yield(self, pass_id: str) -> Dict:
        """
        Realizes the yield and resets the claim timer.
        Returns a receipt of the transaction.
        """
        p_pass = self.active_passes.get(pass_id)
        if not p_pass:
            return {"error": "Pass not found"}

        yield_sats = self.get_accrued_yield(pass_id)
        p_pass.last_yield_claim = time.time()
        
        receipt = {
            "pass_id": pass_id,
            "owner_id": p_pass.owner_id,
            "yield_realized": yield_sats,
            "timestamp": time.time()
        }
        
        self.yield_ledger.append(receipt)
        print(f"[Escrow] 💰 Yield Claimed: {yield_sats} Sats for Pass {pass_id}")
        return receipt

    def get_tier_multipliers(self, tier: PassTier) -> Dict[str, float]:
        """
        Returns the performance boosts associated with each tier.
        """
        if tier == PassTier.ELITE:
            return {"rate_limit_mult": 10.0, "priority_weight": 5.0}
        if tier == PassTier.PRO:
            return {"rate_limit_mult": 3.0, "priority_weight": 2.0}
        return {"rate_limit_mult": 1.5, "priority_weight": 1.1}

    def check_validity(self, pass_id: str) -> bool:
        """Checks if a pass is still within its 30-day window."""
        p_pass = self.active_passes.get(pass_id)
        if not p_pass: return False
        
        if time.time() > p_pass.expiry_timestamp:
            p_pass.is_active = False
            return False
            
        return p_pass.is_active

# --- Internal Integration Test ---
if __name__ == "__main__":
    escrow = ProxyPassEscrow()
    
    # Simulate a developer buying an Elite Pass
    dev_id = "DEV_8829_X"
    pass_meta = escrow.provision_pass(dev_id, 2000000, PassTier.ELITE)
    
    print(f"[*] Provisioned {pass_meta['pass_id']} for {dev_id}")
    
    # Simulate time travel (1 week)
    escrow.active_passes[pass_meta['pass_id']].last_yield_claim -= 604800
    accrued = escrow.get_accrued_yield(pass_meta['pass_id'])
    print(f"[*] Accrued Yield (1 week): {accrued} Sats (Expected: 10,000)")
