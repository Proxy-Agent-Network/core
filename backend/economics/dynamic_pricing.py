import math
import time
from dataclasses import dataclass
from typing import Dict

# PROXY PROTOCOL - DYNAMIC PRICING ENGINE (v1)
# "Supply and Demand Equilibrium."
# ----------------------------------------------------

@dataclass
class MarketState:
    region: str
    active_human_nodes: int
    pending_task_queue: int
    base_fee_sats: int

class PricingEngine:
    def __init__(self):
        # Configuration
        self.TARGET_UTILIZATION = 0.70  # Ideal load (70% of humans busy)
        self.MAX_MULTIPLIER = 10.0      # Cap price at 10x to prevent insanity
        self.ELASTICITY = 4.0           # How aggressive the price jumps (Higher = Steeper)

    def calculate_utilization(self, state: MarketState) -> float:
        """
        Calculate network load.
        Utilization = Demand / Supply
        """
        if state.active_human_nodes == 0:
            return 2.0  # Infinite demand (Force Max Multiplier)
        
        return state.pending_task_queue / state.active_human_nodes

    def get_surge_multiplier(self, utilization: float) -> float:
        """
        Determines the price multiplier based on utilization.
        Uses an exponential curve to discourage spam when near capacity.
        
        Logic:
        - Below Target (70%): Multiplier is 1.0 (Base Price).
        - Above Target: Multiplier grows exponentially.
        """
        if utilization <= self.TARGET_UTILIZATION:
            return 1.0
        
        # Exponential curve starting from the target point
        # Multiplier = 1 + (Utilization - Target)^Elasticity
        delta = utilization - self.TARGET_UTILIZATION
        surge = 1.0 + (delta ** 2) * self.ELASTICITY
        
        return min(round(surge, 2), self.MAX_MULTIPLIER)

    def quote_price(self, state: MarketState) -> Dict:
        utilization = self.calculate_utilization(state)
        multiplier = self.get_surge_multiplier(utilization)
        final_price = int(state.base_fee_sats * multiplier)
        
        return {
            "region": state.region,
            "status": "SURGE" if multiplier > 1.0 else "NORMAL",
            "base_fee": state.base_fee_sats,
            "current_load": f"{utilization*100:.1f}%",
            "multiplier": f"{multiplier}x",
            "final_price_sats": final_price
        }

# --- Simulation for Economic Modeling ---
if __name__ == "__main__":
    engine = PricingEngine()
    base_sats = 5000 # ~$5.00
    
    print(f"[*] Starting Market Simulation (Base: {base_sats} sats)\n")
    print(f"{'SCENARIO':<20} | {'NODES':<5} | {'TASKS':<5} | {'LOAD':<6} | {'MULT':<5} | {'PRICE'}")
    print("-" * 75)

    scenarios = [
        ("Quiet Night", 100, 20),    # 20% Load
        ("Standard Day", 100, 65),   # 65% Load
        ("Busy Hour", 100, 80),      # 80% Load (Surge starts)
        ("Viral Event", 100, 150),   # 150% Load (Heavy Surge)
        ("Network Crisis", 100, 300) # 300% Load (Max Cap)
    ]

    for name, nodes, tasks in scenarios:
        state = MarketState("US_WEST", nodes, tasks, base_sats)
        quote = engine.quote_price(state)
        
        print(f"{name:<20} | {nodes:<5} | {tasks:<5} | {quote['current_load']:<6} | {quote['multiplier']:<5} | {quote['final_price_sats']} sats")
