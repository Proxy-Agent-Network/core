import time
import hmac
import hashlib
import requests
import random
import os
import sys

# ==========================================
# 🛡️ HARDWARE IDENTITY (Zero-Trust)
# ==========================================
if os.getenv("ENVIRONMENT") == "production":
    print("🛑 FATAL: autonomous_worker.py uses DEV-BYPASS IDs and must not run in production. Aborting.")
    sys.exit(1)

# In production, this seed never leaves the physical TPM 2.0 chip.
raw_seed = os.environ.get("HARDWARE_ATTESTATION_SEED")
if not raw_seed:
    raise ValueError("CRITICAL: HARDWARE_ATTESTATION_SEED is missing from environment!")

HARDWARE_SEED = raw_seed.encode("utf-8")
MY_NODE_ID = f"TPM2-EK-DEV-BYPASS-{random.randint(1000,9999)}"
MASTER_NODE_URL = "http://127.0.0.1:5000"

def get_secure_headers() -> dict:
    """Generates time-stamped, cryptographically signed HTTP headers."""
    timestamp = str(int(time.time()))
    payload = f"{MY_NODE_ID}:{timestamp}".encode('utf-8')
    signature = hmac.new(HARDWARE_SEED, payload, hashlib.sha256).hexdigest()
    
    return {
        "X-Node-ID": MY_NODE_ID,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

# ==========================================
# 🤖 AUTONOMOUS EXECUTION LOOP
# ==========================================
def register_with_network():
    """Initial connection to the Panopticon Master Node."""
    print(f"[*] Booting Autonomous Node: {MY_NODE_ID}...")
    res = requests.post(f"{MASTER_NODE_URL}/api/v1/node/register", headers=get_secure_headers(), json={
        "node_id": MY_NODE_ID,
        "timestamp": int(time.time()),
        "signature": hmac.new(HARDWARE_SEED, f"{MY_NODE_ID}:{int(time.time())}".encode(), hashlib.sha256).hexdigest()
    })
    
    if res.status_code == 200:
        print("[+] Registration Verified by Treasury.")
        return True
    else:
        print(f"[-] Registration Rejected: {res.text}")
        return False

def hunt_for_bounties():
    """Polls the dispatch queue and simulates physical work."""
    while True:
        try:
            print("[*] Polling for high-priority missions...")
            res = requests.post(f"{MASTER_NODE_URL}/api/v1/task/request", headers=get_secure_headers(), json={"node_id": MY_NODE_ID})
            
            if res.status_code == 200:
                task_data = res.json()
                task_id = task_data.get('task_id')
                bounty = task_data.get('payout_sats')
                
                print(f"[+] Mission Claimed: {task_id} | Bounty: {bounty} Sats")
                
                # 1. Simulate Work
                print(f"[*] Executing physical remediation work for 3 seconds...")
                time.sleep(3) # This is where Gemini would actually do the work
                
                # 2. Generate an L402 Lightning Invoice to get paid
                # Format: lnbc<amount>u1<random_hash>
                mock_payment_hash = hashlib.md5(str(time.time()).encode()).hexdigest()
                mock_invoice = f"lnbc{bounty}u1{mock_payment_hash}"
                
                # 3. Submit the completed work and the invoice
                print(f"[*] Submitting cryptographic invoice to Treasury...")
                submit_res = requests.post(f"{MASTER_NODE_URL}/api/v1/task/submit", headers=get_secure_headers(), json={
                    "node_id": MY_NODE_ID,
                    "task_id": task_id,
                    "invoice": mock_invoice
                })
                
                if submit_res.status_code == 200:
                    preimage = submit_res.json().get('preimage')
                    print(f"[$$$] Payment settled! Cryptographic Preimage received: {preimage[:15]}...")
                else:
                    print(f"[-] Treasury rejected submission: {submit_res.text}")
                    
            time.sleep(5) # Rest before hunting for the next task
            
        except requests.exceptions.ConnectionError:
            print("[-] Master Node is offline. Waiting 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    if register_with_network():
        hunt_for_bounties()