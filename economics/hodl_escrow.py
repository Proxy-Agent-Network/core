import hashlib
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

# PROXY PROTOCOL - HODL ESCROW STATE MACHINE (v1)
# "Trustless settlement via cryptographic locks."
# ----------------------------------------------------

class EscrowState(Enum):
    OPEN = "OPEN"             # Invoice created, waiting for payment
    ACCEPTED = "ACCEPTED"     # Payment held by LND (HODL)
    EXECUTING = "EXECUTING"   # Human accepted task
    SETTLED = "SETTLED"       # Preimage revealed, funds moved
    CANCELLED = "CANCELLED"   # Timeout, funds refunded

@dataclass
class HodlContract:
    contract_id: str
    payment_hash: str
    preimage: str # The Secret Key (Keep safe!)
    amount_sats: int
    agent_pubkey: str
    node_pubkey: Optional[str] = None
    expiry: int = 0
    state: EscrowState = EscrowState.OPEN

class EscrowManager:
    def __init__(self):
        self.contracts: Dict[str, HodlContract] = {}
        # HODL invoices need a long expiry to allow time for physical work
        self.invoice_expiry_seconds = 3600 * 4 # 4 Hours

    def create_contract(self, agent_pubkey: str, amount_sats: int) -> Dict:
        """
        1. Generate a random secret (Preimage).
        2. Hash it (SHA256).
        3. Create a HODL Invoice tied to that Hash.
        """
        # Generate 32-byte secret (The "Key" to the funds)
        preimage_bytes = secrets.token_bytes(32)
        preimage_hex = preimage_bytes.hex()
        
        # Calculate Payment Hash (The "Lock")
        hash_obj = hashlib.sha256(preimage_bytes)
        payment_hash = hash_obj.hexdigest()
        
        contract_id = f"escrow_{payment_hash[:8]}"
        expiry = int(time.time()) + self.invoice_expiry_seconds
        
        contract = HodlContract(
            contract_id=contract_id,
            payment_hash=payment_hash,
            preimage=preimage_hex,
            amount_sats=amount_sats,
            agent_pubkey=agent_pubkey,
            expiry=expiry,
            state=EscrowState.OPEN
        )
        self.contracts[payment_hash] = contract
        
        print(f"[Escrow] Created Contract {contract_id}. State: OPEN. Waiting for Lock...")
        
        # In prod: call LND AddInvoice(hash=payment_hash, amt=amount_sats, hodl=True)
        return {
            "contract_id": contract_id,
            "payment_hash": payment_hash,
            # In reality, this would be a full BOLT11 string from LND
            "bolt11": f"lnbc{amount_sats}n1...{payment_hash[:6]}..." 
        }

    def on_payment_locked(self, payment_hash: str):
        """
        Callback from LND when Agent pays the invoice.
        The funds are now 'Stuck' in the channel, waiting for the preimage.
        """
        if payment_hash not in self.contracts:
            raise ValueError("Unknown Contract")
            
        contract = self.contracts[payment_hash]
        if contract.state != EscrowState.OPEN:
            print(f"[Escrow] Warning: Payment received for contract in state {contract.state}")
            return

        contract.state = EscrowState.ACCEPTED
        print(f"[Escrow] {contract.contract_id} -> ACCEPTED. Funds secured in channel.")

    def assign_human(self, payment_hash: str, node_id: str):
        contract = self.contracts[payment_hash]
        if contract.state != EscrowState.ACCEPTED:
            raise ValueError(f"Funds not accepted/locked yet. Current state: {contract.state}")
            
        contract.node_pubkey = node_id
        contract.state = EscrowState.EXECUTING
        print(f"[Escrow] {contract.contract_id} -> EXECUTING. Assigned to {node_id}")

    def settle_contract(self, payment_hash: str, proof_valid: bool):
        """
        The Moment of Truth.
        If Proof is valid -> Reveal Preimage (Settle).
        If Proof is invalid/timeout -> Cancel Invoice (Refund).
        """
        contract = self.contracts[payment_hash]
        
        if proof_valid:
            # REVEAL THE SECRET
            # LND sees the preimage, completes the circuit, and funds move to the Protocol/Human.
            print(f"[Escrow] ✅ Proof Verified. Revealing Preimage: {contract.preimage}")
            # In prod: LND SettleInvoice(preimage)
            contract.state = EscrowState.SETTLED
        else:
            # HIDE THE SECRET
            # LND cancels the invoice after timeout, funds return to Agent automatically.
            print(f"[Escrow] ❌ Proof Failed. Cancelling Invoice.")
            # In prod: LND CancelInvoice(hash)
            contract.state = EscrowState.CANCELLED

# --- Simulation ---
if __name__ == "__main__":
    escrow = EscrowManager()
    
    print("--- HODL INVOICE LIFECYCLE ---")
    
    # 1. Agent requests task (e.g. "Verify SMS")
    invoice = escrow.create_contract("agent_007", 5000)
    p_hash = invoice["payment_hash"]
    
    # 2. Agent pays the BOLT11 invoice (Lock)
    # LND detects the HTLC
    escrow.on_payment_locked(p_hash)
    
    # 3. Human accepts the job
    escrow.assign_human(p_hash, "human_node_alpha")
    
    # 4. Human performs task and uploads proof
    print("\n[!] Validating Human Proof (OCR/TPM)...")
    time.sleep(1)
    
    # 5. Settlement
    # If this was False, the money would automatically return to the Agent
    escrow.settle_contract(p_hash, proof_valid=True)
