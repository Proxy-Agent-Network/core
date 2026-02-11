import hashlib
import secrets
import time
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, List

# PROXY PROTOCOL - HODL ESCROW STATE MACHINE (v1.5)
# "Programmable value transfer with automated insurance recovery."
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
    retry_count: int = 0
    insurance_claim_id: Optional[str] = None

class EscrowManager:
    """
    Coordinates the generation, monitoring, and settlement of Lightning HODL invoices.
    Interacts with the LND gateway to lock and release HTLCs.
    """
    
    def __init__(self, insurance_engine=None):
        # In-memory registry (In production: backed by high-availability Redis/PostgreSQL)
        self.contracts: Dict[str, HodlContract] = {}
        # Map task_id to payment_hash for fast webhook lookups
        self.task_map: Dict[str, str] = {}
        # Queue for failed settlement attempts (Preimage revelation)
        self.retry_queue: List[str] = []
        
        # Integration with core/economics/insurance_pool.py
        self.insurance = insurance_engine
        
        self.DEFAULT_EXPIRY = 14400 # 4-hour standard task window
        self.MAX_RETRY_ATTEMPTS = 5

    def create_invoice(self, agent_id: str, task_id: str, amount_sats: int) -> Dict:
        """
        1. Generate a random secret (Preimage).
        2. Generate the Payment Hash (The Lock).
        3. Store the contract state and return BOLT11 details.
        """
        preimage_bytes = secrets.token_bytes(32)
        preimage_hex = preimage_bytes.hex()
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
        self.task_map[task_id] = payment_hash
        
        print(f"[Escrow] 🟢 Contract Created: {contract.contract_id}")
        return {
            "payment_hash": payment_hash,
            "contract_id": contract.contract_id,
            "expiry": contract.expiry,
            "bolt11": f"lnbc{amount_sats}n1...{payment_hash[:8]}..." 
        }

    def update_state(self, payment_hash: str, new_state: EscrowState, node_id: Optional[str] = None):
        """Manages valid state transitions."""
        if payment_hash not in self.contracts:
            raise ValueError(f"Unknown payment hash: {payment_hash}")
            
        contract = self.contracts[payment_hash]
        
        if new_state == EscrowState.SETTLED and contract.state not in [EscrowState.ACCEPTED, EscrowState.IN_PROGRESS]:
            raise PermissionError(f"Cannot settle invoice in state {contract.state}")

        contract.state = new_state
        if node_id:
            contract.node_id = node_id

        print(f"[Escrow] 🔄 {contract.contract_id} transitioned to {new_state.value}")

    def handle_webhook_event(self, event_payload: Dict):
        """Integration for webhook_simulator.py flows."""
        event_type = event_payload.get("type")
        data = event_payload.get("data", {})
        task_id = data.get("task_id")
        
        if not task_id or task_id not in self.task_map:
            print(f"[Escrow] ⚠️ Received webhook for unknown task: {task_id}")
            return

        payment_hash = self.task_map[task_id]

        if event_type == "task.matched":
            self.update_state(payment_hash, EscrowState.IN_PROGRESS, node_id=data.get("node_id"))
        
        elif event_type == "task.completed":
            print(f"[Escrow] ✅ Webhook confirmed completion for {task_id}.")
            self.settle_contract(payment_hash)
            
        elif event_type == "task.failed":
            self.cancel_contract(payment_hash, reason=data.get("reason", "Unknown failure"))

    def settle_contract(self, payment_hash: str, simulate_fail: bool = False) -> bool:
        """
        Reveals the secret preimage to the Lightning Network.
        Includes a retry mechanism for unreachable Lightning nodes.
        """
        contract = self.contracts.get(payment_hash)
        if not contract or contract.state == EscrowState.SETTLED:
            return False

        # 1. Attempt LND Broadcast
        if simulate_fail:
            print(f"[Escrow] 🚨 SETTLEMENT FAILURE: LND Node Unreachable for {contract.contract_id}")
            if payment_hash not in self.retry_queue:
                self.retry_queue.append(payment_hash)
            return False

        # 2. Update Internal State on Success
        self.update_state(payment_hash, EscrowState.SETTLED)
        
        # 3. Secure Cleanup
        if payment_hash in self.retry_queue:
            self.retry_queue.remove(payment_hash)

        print(f"[Escrow] 💸 Preimage Revealed: {contract.preimage[:16]}...")
        print(f"         SATS released to Node: {contract.node_id}")
        return True

    def process_retry_queue(self):
        """
        Worker function to clear the retry queue. 
        Automatically triggers Insurance Claims for systemic failures.
        """
        if not self.retry_queue:
            return

        print(f"\n[Escrow Worker] 🛠️ Processing Retry Queue ({len(self.retry_queue)} items)...")
        
        for p_hash in list(self.retry_queue):
            contract = self.contracts[p_hash]
            contract.retry_count += 1
            
            # --- INSURANCE TRIGGER ---
            if contract.retry_count > self.MAX_RETRY_ATTEMPTS:
                print(f"[Escrow Worker] 💀 Max retries exceeded for {contract.contract_id}.")
                
                if self.insurance and contract.node_id:
                    print(f"[Escrow Worker] 🏥 Filing Insurance Claim for Node {contract.node_id}...")
                    
                    proof_log = (
                        f"Systemic Settlement Failure. Task: {contract.task_id}. "
                        f"Retries: {contract.retry_count}. Preimage: {contract.preimage[:12]}..."
                    )
                    
                    claim_id = self.insurance.file_claim(
                        node_id=contract.node_id,
                        amount_sats=contract.amount_sats,
                        proof_log=proof_log
                    )
                    contract.insurance_claim_id = claim_id
                    print(f"[Escrow Worker] ✅ Claim Secured: {claim_id}. Escalating to SEV-2.")
                
                self.retry_queue.remove(p_hash)
                continue

            print(f"   -> Retry attempt {contract.retry_count} for {contract.contract_id}...")
            self.settle_contract(p_hash, simulate_fail=False)

    def cancel_contract(self, payment_hash: str, reason: str = "Timeout"):
        """Instructs LND to cancel the invoice, returning funds to the Agent."""
        contract = self.contracts.get(payment_hash)
        if not contract:
            return

        self.update_state(payment_hash, EscrowState.CANCELLED)
        print(f"[Escrow] 🛑 Invoice Cancelled. Reason: {reason}")

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
            "node_id": contract.node_id,
            "retry_pending": payment_hash in self.retry_queue,
            "retries": contract.retry_count,
            "insurance_claim": contract.insurance_claim_id
        }

# --- End-to-End Insurance Recovery Simulation ---
if __name__ == "__main__":
    # Mock Insurance Engine to test the integration
    from core.economics.insurance_pool import InsuranceEngine
    
    mock_insurance = InsuranceEngine()
    manager = EscrowManager(insurance_engine=mock_insurance)
    
    # 1. SETUP
    TASK_ID = "task_insurance_demo_505"
    invoice = manager.create_invoice("agent_test", TASK_ID, 10000)
    p_hash = invoice['payment_hash']
    manager.update_state(p_hash, EscrowState.ACCEPTED)
    manager.update_state(p_hash, EscrowState.IN_PROGRESS, node_id="node_unlucky_operator")

    print("\n--- SCENARIO: SYSTEMIC LND FAILURE (LOOPING RETRIES) ---")
    # Simulate first failure
    manager.settle_contract(p_hash, simulate_fail=True)
    
    # Simulate worker trying until max attempts reached
    for _ in range(6):
        manager.process_retry_queue()
    
    # Final Audit
    final_status = manager.get_contract_status(p_hash)
    print(f"\n[Audit Report]")
    print(f"State:            {final_status['state']}")
    print(f"Retries recorded: {final_status['retries']}")
    print(f"Insurance Claim:  {final_status['insurance_claim']}")
    
    if final_status['insurance_claim']:
        print("\n✅ Integration Verified: Failed settlement successfully triggered protocol insurance.")
