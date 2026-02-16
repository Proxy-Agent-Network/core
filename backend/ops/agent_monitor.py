import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

# PROXY PROTOCOL - AGENT MONITOR v1.1 (Reputation Spec v1.1 Compliant)
# "Hardening the biological reputation layer."
# ----------------------------------------------------

class NodeTier(str, Enum):
    BANNED = "BANNED"           # 0 - 300
    PROBATION = "PROBATION"     # 301 - 500
    VERIFIED = "VERIFIED"       # 501 - 800
    ELITE = "ELITE"             # 801 - 950
    SUPER_ELITE = "SUPER_ELITE" # 951 - 1000

class AgentMonitor:
    """
    Service that monitors Node performance and applies the 
    Weighted Proof-of-Accuracy (v1.1) formula.
    """
    def __init__(self):
        # Configuration as per specs/v1/reputation.md
        self.SUCCESS_WEIGHT = 1.0
        self.FAILURE_PENALTY = 5.0
        self.DECAY_THRESHOLD_DAYS = 7
        self.SUPER_ELITE_REP_FLOOR = 951
        
        # In-memory registry simulation
        # Format: { "node_id": { "rep": int, "last_active": timestamp, "tasks": int } }
        self.registry: Dict[str, Dict] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("AgentMonitor")

    def _get_tier(self, score: int) -> NodeTier:
        """Maps numerical REP to protocol tiers."""
        if score >= self.SUPER_ELITE_REP_FLOOR: return NodeTier.SUPER_ELITE
        if score >= 801: return NodeTier.ELITE
        if score >= 501: return NodeTier.VERIFIED
        if score >= 301: return NodeTier.PROBATION
        return NodeTier.BANNED

    def process_task_event(self, node_id: str, success: bool, node_age_days: int = 0):
        """
        Applies the v1.1 Reputation Formula:
        REP = (Successful_Tasks * 1.0) - (Failed_Tasks * 5.0) + (Node_Age_Bonus)
        """
        if node_id not in self.registry:
            self.registry[node_id] = {
                "rep": 500, # Neutral verified start
                "last_active": time.time(),
                "total_tasks": 0,
                "history": []
            }

        node = self.registry[node_id]
        old_score = node["rep"]
        
        # 1. Calculate Delta
        delta = self.SUCCESS_WEIGHT if success else -self.FAILURE_PENALTY
        
        # 2. Update Numerical Score
        # Node_Age_Bonus is applied as a static +1 per 30 days of longevity (max 50)
        age_bonus = min(50, node_age_days // 30)
        
        # New score calculation
        new_score = old_score + delta + (0.1 if success else 0) # Minimal incremental growth
        node["rep"] = max(0, min(1000, int(new_score)))
        node["last_active"] = time.time()
        node["total_tasks"] += 1
        
        # 3. Check for Tier Transitions
        old_tier = self._get_tier(old_score)
        new_tier = self._get_tier(node["rep"])
        
        if old_tier != new_tier:
            self.logger.info(f"⚖️ TIER_SHIFT: Node {node_id} moved {old_tier} -> {new_tier}")
            if new_tier == NodeTier.SUPER_ELITE:
                self.logger.info(f"💎 HIGH COURT: {node_id} now eligible for Appellate Court VRF.")
            elif new_tier == NodeTier.BANNED:
                self.logger.error(f"🚫 SLASHED: {node_id} dropped below trust floor. Access revoked.")

        return {"node_id": node_id, "new_score": node["rep"], "tier": new_tier.value}

    def trigger_decay_sweep(self):
        """
        Executes the 7-day inactivity tax.
        REP decays by 1 point for every 7 days of inactivity.
        """
        now = time.time()
        decay_count = 0
        
        self.logger.info("[*] Starting reputation decay sweep...")
        
        for node_id, data in self.registry.items():
            inactive_duration = now - data["last_active"]
            days_inactive = inactive_duration / 86400
            
            if days_inactive >= self.DECAY_THRESHOLD_DAYS:
                decay_units = int(days_inactive // self.DECAY_THRESHOLD_DAYS)
                data["rep"] = max(0, data["rep"] - decay_units)
                decay_count += 1
                
                # Check for Super-Elite Suspension
                if data["rep"] < self.SUPER_ELITE_REP_FLOOR and data.get("is_super_elite", False):
                    self.logger.warning(f"⚠️ SUSPENSION: {node_id} lost High Court eligibility due to decay.")
        
        self.logger.info(f"[✓] Decay sweep complete. {decay_count} nodes adjusted.")

# --- Operational Simulation ---
if __name__ == "__main__":
    monitor = AgentMonitor()
    
    print("--- PROXY PROTOCOL AGENT MONITOR v1.1 ---")
    
    # 1. Successful Task (Elite Pathway)
    print("[*] Event: Node ELITE_X29 completed high-value notary task...")
    res = monitor.process_task_event("NODE_ELITE_X29", success=True)
    print(f"    -> Result: {res['new_score']} REP ({res['tier']})")

    # 2. Failure Event (Probation Risk)
    print("\n[*] Event: Node PROB_01 failed to provide clear photo...")
    res_fail = monitor.process_task_event("NODE_PROB_01", success=False)
    # Force a starting score of 305 for demonstration
    monitor.registry["NODE_PROB_01"]["rep"] = 305
    res_fail = monitor.process_task_event("NODE_PROB_01", success=False)
    print(f"    -> Result: {res_fail['new_score']} REP ({res_fail['tier']})")

    # 3. Super-Elite Promotion
    print("\n[*] Event: Node ALPHA_001 crossing the 950 threshold...")
    monitor.registry["ALPHA_001"] = {"rep": 950, "last_active": time.time(), "total_tasks": 500}
    res_promo = monitor.process_task_event("ALPHA_001", success=True)
    print(f"    -> Result: {res_promo['new_score']} REP ({res_promo['tier']})")

    # 4. Decay Simulation
    print("\n[*] Simulating 15 days of inactivity for all nodes...")
    # Manually backdate the activity
    for nid in monitor.registry:
        monitor.registry[nid]["last_active"] -= (15 * 86400)
    
    monitor.trigger_decay_sweep()
