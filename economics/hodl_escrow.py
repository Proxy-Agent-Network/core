import hashlib
import secrets
import time
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, List

# PROXY PROTOCOL - HODL ESCROW STATE MACHINE (v1.2)
# "Programmable value transfer with cryptographic finality."
# ----------------------------------------------------

class EscrowState(Enum):
    """
    Lifecycle stages for a HODL Invoice.
    """
    OPEN = "OPEN"               # Invoice created, awaiting payment from Agent
    ACCEPTED = "ACCEPTED"       # Payment detected and held by LND (HODL state)
    IN_PROGRESS = "IN_PROGRESS" # Human Node has accepted the task and is executing
    SETTLED = "SETTLED"         # Proof verified; preimage revealed; funds moved
    CANCELLED = "CANCELLED"     # Task failed or timed out; funds returned to Agent

@dataclass
class HodlContract:
    contract_id: str
    payment_hash: str
    preimage: str           # The cryptographic key (MUST remain server-side)
    amount_sats: int
    agent_id: str
    task_id: str
    expiry: int
    state: EscrowState = EscrowState.OPEN
    node_id: Optional[str] = None
    created_at: float = time.time()

class EscrowManager:
    """
    Coordinates the generation, monitoring, and settlement of Lightning HODL invoices.
    Interacts with the LND gateway to lock and release HTLCs.
    """
    
    def __init__(self):
        # In-memory registry (In production: backed by high-availability Redis/PostgreSQL)
        self.contracts: Dict[str, HodlContract] = {}
        self.DEFAULT_EXPIRY = 14400 # 4-hour standard task window

    def create_invoice(self, agent_id: str, task_id: str, amount_sats: int) -> Dict:
        """
        1. Generate a random secret (Preimage).
        2. Generate the Payment Hash (The Lock).
        3. Store the contract state and return BOLT11 details.
        """
        # Generate 32-byte secure preimage
        preimage_bytes = secrets.token_bytes(32)
        preimage_hex = preimage_bytes.hex()
        
        # Calculate SHA-256 Payment Hash
        payment_hash = hashlib.sha256(preimage_bytes).hexdigest()
        
        contract = HodlContract(
            contract_id=f"escrow_{payment_hash[:12]}",
            payment_hash=payment_hash,
            preimage=preimage_hex,
            amount_sats=amount_sats,
            agent_id=agent_id,
            task_id=task_id,
            expiry=int(time.time()) + self.DEFAULT_EXPIRY
        )
        
        self.contracts[payment_hash] = contract
        
        print(f"[Escrow] 🟢 Contract Created: {contract.contract_id}")
        print(f"         Task: {task_id} | Amount: {amount_sats} SATS")

        return {
            "payment_hash": payment_hash,
            "contract_id": contract.contract_id,
            "expiry": contract.expiry,
            # In a real impl, this would be a BOLT11 string signed by the LN node
            "bolt11": f"lnbc{amount_sats}n1...{payment_hash[:8]}..." 
        }

    def update_state(self, payment_hash: str, new_state: EscrowState, node_id: Optional[str] = None):
        """
        Manages valid state transitions.
        """
        if payment_hash not in self.contracts:
            raise ValueError(f"Unknown payment hash: {payment_hash}")
            
        contract = self.contracts[payment_hash]
        
        # Validation Logic: Prevent illegal state jumps
        # e.g., Cannot settle a contract that hasn't been ACCEPTED (locked)
        if new_state == EscrowState.SETTLED and contract.state not in [EscrowState.ACCEPTED, EscrowState.IN_PROGRESS]:
            raise PermissionError(f"Cannot settle invoice in state {contract.state}")

        contract.state = new_state
        if node_id:
            contract.node_id = node_id

        print(f"[Escrow] 🔄 {contract.contract_id} transitioned to {new_state.value}")

    def settle_contract(self, payment_hash: str) -> str:
        """
        Reveals the secret preimage to the Lightning Network.
        This triggers the final movement of funds to the Node.
        """
        contract = self.contracts.get(payment_hash)
        if not contract:
            return None

        # 1. Update Internal State
        self.update_state(payment_hash, EscrowState.SETTLED)

        # 2. Trigger LND Settlement
        # In production: self.lnd_client.settle_invoice(contract.preimage)
        print(f"[Escrow] 💸 Preimage Revealed: {contract.preimage[:16]}...")
        print(f"         SATS released to Node: {contract.node_id}")
        
        return contract.preimage

    def cancel_contract(self, payment_hash: str, reason: str = "Timeout"):
        """
        Instructs LND to cancel the invoice, returning funds to the Agent.
        """
        contract = self.contracts.get(payment_hash)
        if not contract:
            return

        self.update_state(payment_hash, EscrowState.CANCELLED)
        
        # In production: self.lnd_client.cancel_invoice(payment_hash)
        print(f"[Escrow] 🛑 Invoice Cancelled. Reason: {reason}")
        print(f"         Funds refunded to Agent: {contract.agent_id}")

    def get_contract_status(self, payment_hash: str) -> Optional[Dict]:
        """Returns a public view of the escrow state."""
        contract = self.contracts.get(payment_hash)
        if not contract:
            return None
            
        return {
            "id": contract.contract_id,
            "task_id": contract.task_id,
            "state": contract.state.value,
            "amount_sats": contract.amount_sats,
            "is_locked": contract.state != EscrowState.OPEN,
            "time_remaining": max(0, contract.expiry - int(time.time()))
        }

# --- Task Lifecycle Simulation ---
if __name__ == "__main__":
    manager = EscrowManager()
    
    print("--- 1. INITIATION ---")
    # Agent requests an SMS verification
    invoice_info = manager.create_invoice(
        agent_id="agent_alpha_v1", 
        task_id="task_88293", 
        amount_sats=1500
    )
    p_hash = invoice_info['payment_hash']

    print("\n--- 2. ESCROW LOCKING ---")
    # Simulate LND reporting that the Agent has paid the HODL invoice
    manager.update_state(p_hash, EscrowState.ACCEPTED)

    print("\n--- 3. TASK EXECUTION ---")
    # Simulate a Node accepting the task
    manager.update_state(p_hash, EscrowState.IN_PROGRESS, node_id="node_bob_elite")

    print("\n--- 4. SETTLEMENT ---")
    # Task verified! Reveal the secret.
    manager.settle_contract(p_hash)
    
    # Check final status
    final_status = manager.get_contract_status(p_hash)
    print(f"\n[Final Status] {json.dumps(final_status, indent=2)}")
