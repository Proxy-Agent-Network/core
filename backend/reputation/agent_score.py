import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

# PROXY PROTOCOL - AGENT REPUTATION ENGINE (v1)
# "Protecting the humans from the machines."
# ----------------------------------------------------

class AgentStatus(Enum):
    GOOD = "GOOD"
    WARNING = "WARNING"
    RESTRICTED = "RESTRICTED" # Can only hire Tier 3 nodes (who charge more risk premium)
    BANNED = "BANNED"

@dataclass
class AgentProfile:
    agent_id: str
    total_tasks: int = 0
    completed_tasks: int = 0
    cancelled_tasks: int = 0
    disputes_lost: int = 0
    reputation_score: float = 100.0

class AgentScorer:
    def __init__(self):
        # Configuration
        self.CANCELLATION_PENALTY = 5.0
        self.DISPUTE_PENALTY = 20.0
        self.COMPLETION_REWARD = 1.0
        
        self.BAN_THRESHOLD = 30.0
        self.RESTRICTED_THRESHOLD = 60.0
        
        # Mock Database
        self.db: Dict[str, AgentProfile] = {}

    def get_or_create_profile(self, agent_id: str) -> AgentProfile:
        if agent_id not in self.db:
            self.db[agent_id] = AgentProfile(agent_id=agent_id)
        return self.db[agent_id]

    def record_event(self, agent_id: str, event_type: str):
        profile = self.get_or_create_profile(agent_id)
        
        if event_type == "TASK_COMPLETE":
            profile.total_tasks += 1
            profile.completed_tasks += 1
            # Logarithmic capping could go here, keeping simple for v1
            profile.reputation_score = min(100.0, profile.reputation_score + self.COMPLETION_REWARD)
            
        elif event_type == "TASK_CANCELLED_LATE":
            # Agent cancelled after human accepted + timeout
            profile.total_tasks += 1
            profile.cancelled_tasks += 1
            profile.reputation_score -= self.CANCELLATION_PENALTY
            
        elif event_type == "DISPUTE_LOST":
            # Jury ruled against Agent
            profile.total_tasks += 1
            profile.disputes_lost += 1
            profile.reputation_score -= self.DISPUTE_PENALTY

        # Clamp score to 0
        profile.reputation_score = max(0.0, profile.reputation_score)
        self.db[agent_id] = profile
        
        print(f"[*] Event '{event_type}' for {agent_id}. New Score: {profile.reputation_score:.1f}")

    def get_agent_standing(self, agent_id: str) -> Dict:
        profile = self.get_or_create_profile(agent_id)
        score = profile.reputation_score
        
        status = AgentStatus.GOOD
        if score <= self.BAN_THRESHOLD:
            status = AgentStatus.BANNED
        elif score <= self.RESTRICTED_THRESHOLD:
            status = AgentStatus.RESTRICTED
        elif score < 80.0: # Soft warning
            status = AgentStatus.WARNING
            
        return {
            "agent_id": agent_id,
            "score": f"{score:.1f}/100",
            "status": status.value,
            "history": {
                "completed": profile.completed_tasks,
                "cancelled": profile.cancelled_tasks,
                "disputes_lost": profile.disputes_lost
            }
        }

# --- Simulation ---
if __name__ == "__main__":
    scorer = AgentScorer()
    
    bad_agent = "agent_chaos_v1"
    
    print(f"--- Monitoring Agent: {bad_agent} ---")
    
    # 1. Good Start
    scorer.record_event(bad_agent, "TASK_COMPLETE")
    scorer.record_event(bad_agent, "TASK_COMPLETE")
    
    # 2. The Griefing Begins (Cancelling tasks after acceptance)
    print("\n[!] Detected Pattern: Late Cancellations...")
    for _ in range(3):
        scorer.record_event(bad_agent, "TASK_CANCELLED_LATE")
        
    # 3. Major Dispute
    print("\n[!] Jury Verdict: Agent refused valid proof.")
    scorer.record_event(bad_agent, "DISPUTE_LOST")
    scorer.record_event(bad_agent, "DISPUTE_LOST")
    
    # 4. Check Status
    report = scorer.get_agent_standing(bad_agent)
    print("\n--- FINAL REPORT ---")
    print(f"Status: {report['status']}")
    print(f"Score: {report['score']}")
    
    if report['status'] == "BANNED":
        print("🚫 ACCESS DENIED. Protocol firewall active.")
