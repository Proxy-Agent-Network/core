import time
import hmac
import hashlib
import requests
import random

# ==========================================
# 🛡️ HARDWARE IDENTITY (Zero-Trust)
# ==========================================
# In production, this seed never leaves the physical TPM 2.0 chip.
HARDWARE_SEED = b"simulated_hardware_seed_0x99"
MY_NODE_ID = f"TPM2-EK-DEV-BYPASS-{random.randint(1000,9999)}"
MASTER_NODE_URL = "http://127.0.0.1:5001"

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
    print(f"[*] Booting Autonomous Node: {MY_NODE_ID}")
    
    # The register endpoint currently expects the signature in the JSON body 
    # based on our master_node.py architecture.
    timestamp = str(int(time.time()))
    payload = f"{MY_NODE_ID}:{timestamp}".encode('utf-8')
    signature = hmac.new(HARDWARE_SEED, payload, hashlib.sha256).hexdigest()
    
    res = requests.post(f"{MASTER_NODE_URL}/api/v1/node/register", json={
        "node_id": MY_NODE_ID,
        "timestamp": timestamp,
        "signature": signature
    })
    
    if res.status_code == 200:
        print("[+] Successfully registered with the Zero-Trust Network.")
        return True
    else:
        print(f"[-] Registration failed: {res.text}")
        return False

def hunt_for_bounties():
    """The main economic loop: Request task, do work, submit invoice."""
    while True:
        try:
            print("\n[*] Pinging Master Node for available tasks...")
            
            # 1. Request a Task (Using our secure headers)
            res = requests.post(f"{MASTER_NODE_URL}/api/v1/task/request", headers=get_secure_headers(), json={"node_id": MY_NODE_ID})
            
            if res.status_code == 200:
                task_data = res.json()
                task_id = task_data['task_id']
                bounty = task_data['payout_sats']
                
                print(f"[+] Task {task_id} acquired! Bounty: {bounty} SATS")
                print(f"[*] Simulating AI cognitive work for 3 seconds...")
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