"""
hodl_escrow.py - Rust Bridge
----------------------------
Manages Lightning Network HODL invoices using a Rust Type-State machine.
"""
import proxy_core

class EscrowContract:
    def __init__(self):
        self._manager = proxy_core.EscrowManager()

    def create_task_contract(self, amount_sats: int) -> str:
        """
        Creates a new HODL invoice.
        Returns: The Bolt11 invoice string or Contract ID.
        """
        return self._manager.create_invoice(amount_sats)

    # Note: Future methods (settle, cancel) will be added to the Rust lib 
    # and exposed here as we expand the bindings.