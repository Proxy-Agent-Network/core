from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    OPEN = "OPEN"           # Waiting for a human node
    MATCHED = "MATCHED"     # Node has accepted, awaiting execution
    ACTIVE = "ACTIVE"       # Node is currently performing the task
    PENDING_VERIFICATION = "PENDING_VERIFICATION" # Awaiting High Court/Oracle check
    SETTLED = "SETTLED"     # Sats transferred, task closed
    CANCELLED = "CANCELLED"

@dataclass
class PhysicalTask:
    task_id: str
    principal_agent_id: str  # The ID of the Autonomous Agent
    task_type: str           # e.g., 'notarization', 'visual_audit', 'sms_relay'
    bid_amount_sats: int
    required_tier: int       # 1, 2, or 3
    geofence_lat: float      # Required location
    geofence_lon: float
    geofence_radius: int     # Meters
    metadata: dict           # Encrypted instructions for the human
