import logging
import statistics
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime

# PROXY PROTOCOL - INSURANCE ACTUARY ENGINE (v1.0)
# "Ensuring systemic solvency through dynamic risk-pricing."
# ----------------------------------------------------

@dataclass
class RiskProfile:
    timestamp: float
    flow_velocity_sats_sec: float
    mempool_saturation: float
    default_probability: float
    recommended_levy: float

class InsuranceActuary:
    """
    Calculates the required protocol insurance tax based on 
    real-time network stress and Satoshi movement velocity.
    """
    def __init__(self):
        # Configuration
        self.BASE_LEVY = 0.001       # 0.1%
        self.MIN_LEVY = 0.0001       # 0.01%
        self.MAX_LEVY = 0.005        # 0.5%
        self.SOLVENCY_TARGET_SATS = 100_000_000 # 1.0 BTC target for the pool
        
        # Risk thresholds
        self.VELOCITY_STRESS_THRESHOLD = 5000  # Sats/sec
        self.FAILURE_STRESS_THRESHOLD = 0.15   # 15% network failure rate
        
        self.history: List[RiskProfile] = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("InsuranceActuary")

    def calculate_default_probability(self, stats: Dict) -> float:
        """
        Bayesian probability of a SEV-1 event requiring mass payout.
        Considers velocity, failure rates, and active governance disputes.
        """
        velocity = stats.get('velocity', 0)
        failure_rate = stats.get('failure_rate', 0.02)
        active_disputes = stats.get('active_disputes', 0)
        
        # Basic linear risk model for v1
        # Risk increases with velocity and failure frequency
        velocity_risk = min(1.0, velocity / (self.VELOCITY_STRESS_THRESHOLD * 2))
        failure_risk = min(1.0, failure_rate / self.FAILURE_STRESS_THRESHOLD)
        dispute_risk = min(1.0, active_disputes / 10)
        
        prob = (velocity_risk * 0.3) + (failure_risk * 0.5) + (dispute_risk * 0.2)
        return round(max(0.0, min(1.0, prob)), 4)

    def determine_dynamic_levy(self, prob: float, pool_balance: int) -> float:
        """
        Adjusts the 0.1% tax based on default probability and pool depth.
        """
        # 1. Base adjustment from probability
        # As probability hits 1.0, levy moves toward MAX_LEVY
        risk_adjustment = prob * self.MAX_LEVY
        
        # 2. Solvency adjustment
        # If pool is below target, increase levy to replenish
        solvency_multiplier = 1.0
        if pool_balance < self.SOLVENCY_TARGET_SATS:
            # Increase tax by up to 2x if pool is empty
            solvency_multiplier = 1.0 + (1.0 - (pool_balance / self.SOLVENCY_TARGET_SATS))
            
        final_levy = (self.BASE_LEVY + risk_adjustment) * solvency_multiplier
        
        # Clamp to bounds
        clamped_levy = max(self.MIN_LEVY, min(self.MAX_LEVY, final_levy))
        return round(clamped_levy, 6)

    def generate_risk_audit(self, stats: Dict, pool_balance: int) -> RiskProfile:
        """
        Standardized output for the Protocol Health Matrix.
        """
        prob = self.calculate_default_probability(stats)
        levy = self.determine_dynamic_levy(prob, pool_balance)
        
        profile = RiskProfile(
            timestamp=time.time(),
            flow_velocity_sats_sec=stats.get('velocity', 0),
            mempool_saturation=stats.get('saturation', 0.1),
            default_probability=prob,
            recommended_levy=levy
        )
        
        self.history.append(profile)
        if len(self.history) > 100: self.history.pop(0)
        
        self.logger.info(f"[*] Risk Audit: Default Prob: {prob*100:.2f}% | Adjusted Levy: {levy*100:.4f}%")
        return profile

# --- Simulation for Protocol Operations ---
if __name__ == "__main__":
    actuary = InsuranceActuary()
    
    print("--- PROTOCOL INSURANCE ACTUARIAL TEST ---")
    
    # Current Pool: 10.45M Sats (from treasury_audit.jsx)
    current_pool = 10_450_200 
    
    scenarios = [
        {"name": "Midnight Stable", "stats": {"velocity": 120, "failure_rate": 0.01, "active_disputes": 0, "saturation": 0.05}},
        {"name": "Standard Load", "stats": {"velocity": 850, "failure_rate": 0.04, "active_disputes": 2, "saturation": 0.15}},
        {"name": "Volatility Spike", "stats": {"velocity": 4500, "failure_rate": 0.12, "active_disputes": 5, "saturation": 0.45}},
        {"name": "Mass Sybil Pulse", "stats": {"velocity": 8200, "failure_rate": 0.28, "active_disputes": 12, "saturation": 0.85}},
    ]

    for s in scenarios:
        print(f"\n[Scenario: {s['name']}]")
        audit = actuary.generate_risk_audit(s['stats'], current_pool)
        print(f"    -> Probability of Default: {audit.default_probability:.2%}")
        print(f"    -> Dynamic Network Levy:   {audit.recommended_levy:.4%}")
        
        # Simulate pool growth (simplified)
        current_pool += int(audit.flow_velocity_sats_sec * 3600 * audit.recommended_levy)
