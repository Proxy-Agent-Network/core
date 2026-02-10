import hashlib
import secrets
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional

# PROXY PROTOCOL - LEGACY SETTLEMENT REFERENCE (v0.9)
# ----------------------------------------------------
# TARGET AUDIENCE: Rust Migration Team
# PURPOSE: This file documents the business logic for HODL Invoices.
#          Port this state machine to the Rust 'State Actor'.

class InvoiceState(Enum):
    CREATED = "CREATED"         # Invoice generated, waiting for payer
    ACCEPTED = "ACCEPTED"       # HTLC locked by LND (The "HODL" state)
    SETTLED = "SETTLED"         # Preimage revealed, funds claimed
    CANCELLED = "CANCELLED"     # Timed out or manually cancelled

@dataclass
class HodlInvoice:
    r_hash: str                 # The Payment Hash (Lock)
    preimage: str               # The Preimage (Key) - KEEP SECRET
    amount_sats: int
    expiry_height: int          # Block height for CLTV expiry
    state: InvoiceState = InvoiceState.CREATED
    creation_time: float = 0.0

class HodlInvoiceManager:
    def __init__(self):
        # In-Memory Store (RUST-TODO: Port to sled or redb for persistence)
        self.invoices: Dict[str, HodlInvoice] = {}
        
    def create_invoice(self, amount_sats: int, cltv_delta: int = 144) -> Dict:
        """
        Generates a new HODL invoice.
        RUST-TODO: Use LDK's `ChannelManager` to generate the payment hash.
        """
        # 1. Generate Preimage (32 bytes)
        preimage = secrets.token_bytes(32)
        
        # 2. Hash it (SHA256)
        r_hash = hashlib.sha256(preimage).digest()
        r_hash_hex = r_hash.hex()
        
        # 3. Store State
        invoice = HodlInvoice(
            r_hash=r_hash_hex,
            preimage=preimage.hex(),
            amount_sats=amount_sats,
            expiry_height=cltv_delta, # Relative height for now
            creation_time=time.time()
        )
        self.invoices[r_hash_hex] = invoice
        
        print(f"[Legacy] Invoice Created: {r_hash_hex[:8]}... (Amt: {amount_sats})")
        
        return {
            "payment_hash": r_hash_hex,
            "payment_preimage": preimage.hex(), # Only for internal use!
            # Mock BOLT11
            "payment_request": f"lnbc{amount_sats}n1...{r_hash_hex[:6]}..."
        }

    def on_htlc_intercept(self, r_hash_hex: str):
        """
        Callback when LND receives the HTLC but hasn't settled it yet.
        This is the critical "HODL" moment.
        """
        if r_hash_hex not in self.invoices:
            print(f"[Legacy] Error: Unknown HTLC {r_hash_hex}")
            return False

        invoice = self.invoices[r_hash_hex]
        
        # State Transition: CREATED -> ACCEPTED
        if invoice.state == InvoiceState.CREATED:
            invoice.state = InvoiceState.ACCEPTED
            print(f"[Legacy] HTLC Locked for {r_hash_hex[:8]}... Funds Secured.")
            return True
            
        return False

    def settle_invoice(self, r_hash_hex: str):
        """
        Release the funds by revealing the preimage to LND.
        RUST-TODO: This must be atomic to prevent race conditions during settlement.
        """
        if r_hash_hex not in self.invoices:
            raise ValueError("Invoice not found")
            
        invoice = self.invoices[r_hash_hex]
        
        if invoice.state != InvoiceState.ACCEPTED:
            raise ValueError(f"Cannot settle invoice in state {invoice.state}")
            
        # State Transition: ACCEPTED -> SETTLED
        invoice.state = InvoiceState.SETTLED
        print(f"[Legacy] SETTLE ACTION: Revealing Preimage {invoice.preimage[:8]}...")
        # In prod: lnd.settle_invoice(preimage)

    def cancel_invoice(self, r_hash_hex: str):
        """
        Refund the agent by cancelling the HTLC.
        """
        if r_hash_hex not in self.invoices:
            raise ValueError("Invoice not found")

        invoice = self.invoices[r_hash_hex]
        
        # State Transition: ACCEPTED -> CANCELLED
        invoice.state = InvoiceState.CANCELLED
        print(f"[Legacy] CANCEL ACTION: Rejecting HTLC for {r_hash_hex[:8]}...")
        # In prod: lnd.cancel_invoice(payment_hash)

# --- Rust Team Context ---
if __name__ == "__main__":
    manager = HodlInvoiceManager()
    
    print("--- STARTING LEGACY FLOW ---")
    
    # 1. Create
    inv = manager.create_invoice(10000)
    p_hash = inv['payment_hash']
    
    # 2. Lock (Agent Pays)
    # Simulate LND interceptor firing
    manager.on_htlc_intercept(p_hash)
    
    # 3. Settle (Human Finishes Task)
    # Verify pre-image release
    manager.settle_invoice(p_hash)
    
    print("--- FLOW COMPLETE ---")
