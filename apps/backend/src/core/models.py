from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

# ---------------------------------------------------------------------------
# PHASE 5 ORCHESTRATION MODELS
# 
# 1. 1:N ARCHITECTURE: An AV distress signal creates one `Incident`. That 
#    Incident contains multiple `TaskSlot`s (e.g., 1 Primary, 1 Sentry).
# 2. STICKY DISPATCH: Agents now possess a `task_queue` to hold their next 
#    chained mission, and an `auto_accept_enabled` reputation flag.
# ---------------------------------------------------------------------------

# Reputation thresholds for Vanguard Agents
AUTO_ACCEPT_MIN_JOBS = 25
AUTO_ACCEPT_MIN_COMPLETION_RATE = 0.90

class TaskRole(Enum):
    PRIMARY = "PRIMARY"     # The Tier 3 mechanic / main problem solver
    SENTRY = "SENTRY"       # The Tier 1 safety perimeter / traffic redirector

class TaskStatus(Enum):
    OPEN = "OPEN"           # Waiting for a Vanguard Agent
    QUEUED = "QUEUED"       # Assigned to a busy agent's queue (Sticky Dispatch)
    ASSIGNED = "ASSIGNED"   # Agent matched and En Route (formerly MATCHED)
    ACTIVE = "ACTIVE"       # Agent is on-scene performing the task
    PENDING_VERIFICATION = "PENDING_VERIFICATION" # Awaiting Escrow/Oracle crypto-verification
    SETTLED = "SETTLED"     # Bounty transferred, task closed
    CANCELLED = "CANCELLED" # Task aborted or SLA rip-and-replace triggered

class AgentStatus(Enum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"       # Idle, ready for dispatch
    EN_ROUTE = "EN_ROUTE"   # Traveling to an active task
    ON_SCENE = "ON_SCENE"   # Actively working a task

class PatrolMode(Enum):
    CAR = "car"
    FOOT = "foot"

@dataclass
class TaskSlot:
    """
    Represents a specific role/mission within a broader AV Incident.
    (The 'N' side of the 1:N Incident architecture)
    """
    task_id: str
    incident_id: str
    role: TaskRole           # PRIMARY or SENTRY
    task_type: str           # e.g., 'tire_change', 'sensor_wipe', 'scene_security'
    bounty_usd: float        # USD bounty (converted/backed by sats in the smart contract)
    required_tier: int       # 1, 2, or 3
    assigned_agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.OPEN
    # Using Dict[str, Any] to accommodate nested JSON from the evidence payload
    metadata: Dict[str, Any] = field(default_factory=dict) 

@dataclass
class Incident:
    """
    The parent distress signal from an Autonomous Vehicle.
    (The '1' side of the 1:N Incident architecture)
    """
    incident_id: str
    vehicle_id: str          # VIN or fleet ID of the stranded Autonomous Vehicle
    fault_code: str          # e.g., 'LIDAR_CRITICAL_FAULT'
    lat: float
    lon: float
    # An incident can hold multiple tasks (e.g., [Primary Repair, Sentry Perimeter])
    tasks: List[TaskSlot] = field(default_factory=list) 

@dataclass
class VanguardAgent:
    """
    Agent profile tracking reputation, status, and the Phase 5 Sticky Queue.
    """
    agent_id: str
    tier: int
    status: AgentStatus = AgentStatus.OFFLINE
    patrol_mode: PatrolMode = PatrolMode.CAR
    active_task_id: Optional[str] = None
    
    # The 'Last Resort' queue for chaining missions
    task_queue: List[str] = field(default_factory=list) 
    
    # Progression/Reputation lock: Unlocked at AUTO_ACCEPT_MIN_JOBS & AUTO_ACCEPT_MIN_COMPLETION_RATE
    auto_accept_enabled: bool = False