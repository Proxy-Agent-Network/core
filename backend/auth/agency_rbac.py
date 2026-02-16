import uuid
import time
import hashlib
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# PROXY PROTOCOL - AGENCY SUB-ACCOUNT MANAGER (v1)
# "One Master Key to rule them all."
# ----------------------------------------------------

class Permission(Enum):
    CREATE_TASK = "task:create"
    READ_TASK = "task:read"
    CANCEL_TASK = "task:cancel"
    MANAGE_KEYS = "agency:keys"
    VIEW_BILLING = "agency:billing"
    ADMIN_ALL = "admin:*"

@dataclass
class APIKey:
    key_hash: str
    prefix: str # "pk_live_..."
    label: str # "Marketing Bot 1"
    role: str
    scopes: List[Permission]
    created_at: int
    expires_at: Optional[int] = None
    is_active: bool = True

@dataclass
class AgencyAccount:
    agency_id: str
    master_balance_sats: int
    sub_accounts: Dict[str, APIKey] = field(default_factory=dict)
    
    # Billing Controls
    spend_limit_per_key: int = 100_000 # Daily cap per bot
    total_spent_today: int = 0

class RBACEngine:
    def __init__(self):
        self.agencies: Dict[str, AgencyAccount] = {}
        
        # Standard Roles
        self.ROLES = {
            "OWNER": [p for p in Permission], # All permissions
            "MANAGER": [Permission.CREATE_TASK, Permission.READ_TASK, Permission.CANCEL_TASK, Permission.VIEW_BILLING],
            "AGENT_BOT": [Permission.CREATE_TASK, Permission.READ_TASK], # Cannot see billing or manage keys
            "AUDITOR": [Permission.READ_TASK, Permission.VIEW_BILLING]
        }

    def create_agency(self, name: str, initial_deposit: int) -> str:
        agency_id = f"agency_{uuid.uuid4().hex[:8]}"
        self.agencies[agency_id] = AgencyAccount(
            agency_id=agency_id,
            master_balance_sats=initial_deposit
        )
        print(f"[RBAC] Created Agency: {name} ({agency_id})")
        return agency_id

    def issue_sub_key(self, agency_id: str, label: str, role: str) -> str:
        """
        Generates a scoped API key for a specific bot/department.
        """
        if agency_id not in self.agencies:
            raise ValueError("Agency not found")
        
        if role not in self.ROLES:
            raise ValueError(f"Invalid Role. Available: {list(self.ROLES.keys())}")

        # Generate Key
        raw_key = f"sk_live_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        new_key = APIKey(
            key_hash=key_hash,
            prefix=raw_key[:12],
            label=label,
            role=role,
            scopes=self.ROLES[role],
            created_at=int(time.time())
        )
        
        self.agencies[agency_id].sub_accounts[key_hash] = new_key
        print(f"[RBAC] Issued Key for '{label}' (Role: {role})")
        return raw_key

    def verify_access(self, agency_id: str, key_hash: str, required_scope: Permission, cost_sats: int = 0) -> bool:
        """
        The Gatekeeper. Checks Key Validity + Permissions + Budget.
        """
        agency = self.agencies.get(agency_id)
        if not agency:
            return False
            
        key = agency.sub_accounts.get(key_hash)
        if not key or not key.is_active:
            print(f"[RBAC] ⛔ Access Denied: Invalid/Inactive Key")
            return False

        # 1. Check Permissions
        if required_scope not in key.scopes and Permission.ADMIN_ALL not in key.scopes:
            print(f"[RBAC] ⛔ Access Denied: Missing Scope {required_scope}")
            return False

        # 2. Check Budget (If creating a task)
        if cost_sats > 0:
            if agency.master_balance_sats < cost_sats:
                print(f"[RBAC] ⛔ Access Denied: Insufficient Agency Funds")
                return False
            
            # Deduct from Master Balance
            agency.master_balance_sats -= cost_sats
            agency.total_spent_today += cost_sats
            print(f"[RBAC] 💰 Approved. {cost_sats} sats deducted. Remaining: {agency.master_balance_sats}")

        return True

# --- Simulation ---
if __name__ == "__main__":
    rbac = RBACEngine()
    
    print("--- AGENCY SETUP ---")
    # 1. Register "Acme AI Corp"
    acme_id = rbac.create_agency("Acme AI Corp", 5_000_000) # 5M Sats Deposit
    
    # 2. Create Keys
    # The CEO (Can do everything)
    admin_key = rbac.issue_sub_key(acme_id, "Admin Console", "OWNER")
    
    # A Trading Bot (Can only create tasks)
    bot_key = rbac.issue_sub_key(acme_id, "Trading Bot Alpha", "AGENT_BOT")
    
    # An Auditor (Can only read)
    audit_key = rbac.issue_sub_key(acme_id, "Compliance View", "AUDITOR")

    print("\n--- ACCESS TESTS ---")
    
    # Simulate Hashing incoming keys (In prod, this happens in Middleware)
    bot_hash = hashlib.sha256(bot_key.encode()).hexdigest()
    audit_hash = hashlib.sha256(audit_key.encode()).hexdigest()

    # Test 1: Bot tries to spend money (Should Succeed)
    print(f"\n[Test] Bot attempting task (Cost: 5000)...")
    rbac.verify_access(acme_id, bot_hash, Permission.CREATE_TASK, 5000)

    # Test 2: Auditor tries to spend money (Should Fail - Missing Scope)
    print(f"\n[Test] Auditor attempting task (Cost: 5000)...")
    rbac.verify_access(acme_id, audit_hash, Permission.CREATE_TASK, 5000)

    # Test 3: Bot tries to view billing (Should Fail - Missing Scope)
    print(f"\n[Test] Bot accessing billing...")
    rbac.verify_access(acme_id, bot_hash, Permission.VIEW_BILLING)
