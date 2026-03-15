import time
from datetime import datetime, timedelta
from typing import List, Dict

# PROXY PROTOCOL - REPUTATION DECAY CRON (v1.0)
# "Automated inactivity tax to ensure network vitality."
# ----------------------------------------------------

class ReputationDecayJob:
    """
    Automates the weekly point reductions defined in the Canvas.
    Target Frequency: Run once every 24 hours via systemd-timer or crontab.
    """
    
    def __init__(self):
        self.DECAY_RATE_DAYS = 7
        self.POINTS_PER_DECAY = 1
        self.SUPER_ELITE_THRESHOLD = 951

    def process_node_decay(self, node_profile: Dict) -> Dict:
        """
        Calculates and applies decay for a single node.
        
        Args:
            node_profile: Dict containing 'rep_score', 'last_active_timestamp', 
                         and 'is_super_elite' status.
        """
        node_id = node_profile.get('node_id', 'unknown')
        current_score = node_profile.get('rep_score', 0)
        last_active = datetime.fromisoformat(node_profile.get('last_active_timestamp'))
        
        # 1. Calculate Inactivity Period
        now = datetime.now()
        days_inactive = (now - last_active).days
        
        # 2. Determine Decay Magnitude
        # Section 5: "REP decays by 1 point for every 7 days of inactivity."
        decay_cycles = days_inactive // self.DECAY_RATE_DAYS
        total_decay = decay_cycles * self.POINTS_PER_DECAY
        
        if total_decay <= 0:
            return {"node_id": node_id, "status": "ACTIVE", "decay_applied": 0}

        # 3. Apply Score Reduction
        new_score = max(0, current_score - total_decay)
        
        # 4. Handle Super-Elite Suspension
        # Section 5: "If a Super-Elite node falls below 951 REP, their High Court 
        # eligibility is suspended until the score is restored."
        suspension_triggered = False
        if current_score >= self.SUPER_ELITE_THRESHOLD and new_score < self.SUPER_ELITE_THRESHOLD:
            suspension_triggered = True
        
        return {
            "node_id": node_id,
            "old_score": current_score,
            "new_score": new_score,
            "decay_applied": total_decay,
            "days_inactive": days_inactive,
            "suspension_triggered": suspension_triggered,
            "status": "DECAYED"
        }

    def run_maintenance_sweep(self, all_nodes: List[Dict]):
        """
        Iterates through the entire Node Registry to apply the inactivity tax.
        """
        print(f"[{datetime.now().isoformat()}] 🧹 Starting Reputation Decay Sweep...")
        
        results = []
        for node in all_nodes:
            report = self.process_node_decay(node)
            results.append(report)
            
            if report['decay_applied'] > 0:
                print(f"   [!] Node {report['node_id']}: -{report['decay_applied']} pts "
                      f"(Inactive: {report['days_inactive']} days)")
                
                if report['suspension_triggered']:
                    print(f"       🚨 HIGH COURT ELIGIBILITY SUSPENDED (Score: {report['new_score']})")

        print(f"[*] Sweep complete. Processed {len(all_nodes)} nodes.")
        return results

# --- Production Simulation ---
if __name__ == "__main__":
    job = ReputationDecayJob()
    
    # Mock Database: Nodes with varying levels of inactivity
    mock_registry = [
        {
            "node_id": "node_active_elite",
            "rep_score": 960,
            "last_active_timestamp": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "node_id": "node_lazy_super_elite",
            "rep_score": 951,
            "last_active_timestamp": (datetime.now() - timedelta(days=15)).isoformat()
        },
        {
            "node_id": "node_abandoned_verified",
            "rep_score": 600,
            "last_active_timestamp": (datetime.now() - timedelta(days=100)).isoformat()
        }
    ]
    
    sweep_report = job.run_maintenance_sweep(mock_registry)
