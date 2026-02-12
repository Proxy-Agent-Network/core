import hashlib
import secrets
import time
import json

# PROXY PROTOCOL - HELLO WORLD (SMS VERIFICATION)
# "The lifecycle of a single task from Request to Settlement."
# ----------------------------------------------------

class MockProxyNetwork:
    """
    Simulates the Protocol Backend + Lightning Network state machine.
    """
    def __init__(self):
        self.mempool = {}
        self.invoices = {}
        
    def request_task(self, task_type, payload, bid_sats):
        task_id = f"task_{secrets.token_hex(4)}"
        print(f"\n[Network] 🟢 New Request Received: {task_type}")
        print(f"          -> Payload: {json.dumps(payload)}")
        print(f"          -> Bid: {bid_sats} sats")
        
        # Generate HODL Invoice Data
        preimage = secrets.token_bytes(32)
        payment_hash = hashlib.sha256(preimage).hexdigest()
        
        invoice = {
            "payment_hash": payment_hash,
            "preimage": preimage.hex(), # Secret key held by protocol
            "amount": bid_sats,
            "state": "OPEN"
        }
        self.invoices[payment_hash] = invoice
        self.mempool[task_id] = {"status": "AWAITING_PAYMENT", "invoice": payment_hash}
        
        return {
            "task_id": task_id,
            # Simulating a BOLT11 string
            "invoice": f"lnbc{bid_sats}n1...{payment_hash[:6]}..."
        }

    def simulate_payment_lock(self, task_id):
        """
        Simulates the Lightning Network accepting the HTLC.
        Funds are now locked; Agent cannot spend them, Node cannot claim them yet.
        """
        task = self.mempool[task_id]
        invoice = self.invoices[task['invoice']]
        invoice['state'] = "LOCKED"
        task['status'] = "MATCHING"
        print(f"[Network] 🔒 Lightning Funds Locked (HODL Invoice). Dispatching to Humans...")

    def simulate_human_work(self, task_id):
        """
        Simulates a human node receiving the alert and acting.
        """
        print(f"[Network] 👤 Human Node 'node_alice' accepted task.")
        time.sleep(1) # Simulate real-world latency
        print(f"[Network] 📱 Human received SMS code on device.")
        
        # Human enters the code into their app
        return "849201"

    def settle(self, task_id, proof):
        """
        Validates proof and reveals the preimage to settle the funds.
        """
        print(f"[Network] ✅ Proof Verified: Code '{proof}' matches expected format.")
        
        task = self.mempool[task_id]
        invoice = self.invoices[task['invoice']]
        
        # THE SETTLEMENT MOMENT
        # Protocol reveals the preimage to the Lightning Network
        invoice['state'] = "SETTLED"
        task['status'] = "COMPLETED"
        
        print(f"[Network] 💸 Preimage Revealed: {invoice['preimage'][:16]}...")
        print(f"[Network] 💰 Payment finalized. {invoice['amount']} sats moved to 'node_alice'.")

def main():
    network = MockProxyNetwork()
    
    print("=== PROXY PROTOCOL HELLO WORLD ===")
    
    # 1. Agent: Wants to verify a Twitter account
    print("--- STEP 1: AGENT REQUEST ---")
    task_req = network.request_task(
        task_type="verify_sms_otp", 
        payload={"service": "Twitter", "country": "US"}, 
        bid_sats=1500
    )
    task_id = task_req['task_id']
    
    # 2. Agent: Pays the Invoice via LND
    print("\n--- STEP 2: ESCROW LOCK ---")
    network.simulate_payment_lock(task_id)
    
    # 3. Human: Does the work
    print("\n--- STEP 3: PHYSICAL EXECUTION ---")
    sms_code = network.simulate_human_work(task_id)
    
    # 4. Protocol: Settles
    print("\n--- STEP 4: SETTLEMENT ---")
    network.settle(task_id, sms_code)
    
    print("\n[Agent] Mission Complete. Twitter Account Verified.")

if __name__ == "__main__":
    main()
