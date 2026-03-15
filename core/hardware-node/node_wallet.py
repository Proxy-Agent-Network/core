import time
import hashlib
import os

class LightningWallet:
    def __init__(self, node_id):
        self.node_id = node_id
        self.balance_sats = 0
        print(f"[WALLET] ⚡ Initializing Lightning Wallet for {self.node_id}")

    def generate_invoice(self, amount_sats, memo="Inference Task Payout"):
        """
        In production, this talks via gRPC to a local LND (Lightning Network Daemon) node.
        For our transition phase, we generate a cryptographically secure mock invoice.
        """
        print(f"[WALLET] 🧾 Generating L402 Invoice for {amount_sats} SATS...")
        
        # Create a deterministic but unique hash for this specific invoice
        raw_data = f"{self.node_id}-{time.time()}-{amount_sats}-{os.urandom(4)}".encode()
        payment_hash = hashlib.sha256(raw_data).hexdigest()
        
        # Standard Lightning invoice prefix (lnbc) + mock data
        mock_invoice = f"lnbc{amount_sats}u1{payment_hash[:40]}"
        
        return mock_invoice, payment_hash

    def receive_payment(self, amount_sats):
        """Simulates the cryptographic settlement of an invoice."""
        self.balance_sats += amount_sats
        print(f"[WALLET] 💰 PAYMENT RECEIVED: +{amount_sats} SATS. (New Balance: {self.balance_sats} SATS)")

if __name__ == "__main__":
    # Local testing execution
    test_wallet = LightningWallet("TPM2-EK-DEV-TEST")
    invoice, p_hash = test_wallet.generate_invoice(50)
    print(f"Generated Invoice: {invoice}")