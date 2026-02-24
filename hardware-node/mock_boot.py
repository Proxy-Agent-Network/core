import os
import sys
import time
import requests
import platform
import json
import hmac
import hashlib
from datetime import datetime, timezone
from node_wallet import LightningWallet
from agent_engine import AgentEngine

# Import our compiled Rust hardware enclave library
try:
    import proxy_core
except ImportError:
    print("❌ ERROR: Could not import proxy_core. Did you run 'maturin develop'?")
    sys.exit(1)

# Configuration
MASTER_NODE_URL = "http://127.0.0.1:5000/api/v1/node/register"

def get_hardware_fingerprint():
    """Generates a 'fingerprint' based on your actual machine specs."""
    return {
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_cores": 8,  # Simulated for consistency
        "ram_gb": 16     # Simulated
    }

def main():
    print("🔌 INITIATING PROXY NODE BOOT SEQUENCE...")
    time.sleep(1)
    
    # 1. Hardware Discovery
    print("🔍 Scanning Local Hardware...")
    hw_stats = get_hardware_fingerprint()
    print(f"   > CPU: {hw_stats['processor']}")
    print(f"   > OS:  {hw_stats['os']} {hw_stats['release']}")
    time.sleep(1)

    # 2. Identity Generation
    print("🔐 Unlocking Hardware Enclave (TPM 2.0)...")
    try:
        hardware_enclave = proxy_core.NodeHardware()
        node_id = hardware_enclave.get_fingerprint()
        
        # --> DEV HACK: Append the terminal Process ID to simulate multiple physical machines
        node_id = f"{node_id}-{os.getpid()}"
        
        pub_key = "PENDING_TPM_EK_PUB_KEY" 
        print("✅ Hardware Attestation Successful.")
        
    except Exception as e:
        print("🚨 BOOT HALTED: Hardware Security Failure.")
        sys.exit(1)

    # 2.5 Initialize Economic & Cognitive Layers
    print("⚡ Spinning up L402 Lightning Wallet...")
    wallet = LightningWallet(node_id)
    time.sleep(1)

    print("🧠 Booting Cognitive Engine...")
    brain = AgentEngine()
    time.sleep(1)

    # 3. The Handshake
    print(f"📡 Attempting Handshake with Network (http://127.0.0.1:5000/api/v1/node/register)...")
    
    # Generate a fresh timestamp
    iso_timestamp = datetime.now(timezone.utc).isoformat()
    
    # 🛑 The Node mathematically signs its identity using its simulated TPM private key
    tpm_seed = b"simulated_hardware_seed_0x99" 
    payload_signature = hmac.new(tpm_seed, f"{node_id}:{iso_timestamp}".encode(), hashlib.sha256).hexdigest()

    payload = {
        "node_id": node_id,
        "public_key": pub_key,
        "hardware_stats": hw_stats,
        "timestamp": iso_timestamp,
        "signature": payload_signature # <-- The Cryptographic Proof
    }

    try:
        response = requests.post("http://127.0.0.1:5000/api/v1/node/register", json=payload)
        if response.status_code == 200:
            print("\n✅ HANDSHAKE SUCCESSFUL!")
            print("\n🚀 NODE IS NOW ACTIVE. ENTERING TASK LOOP...")
        else:
            print(f"\n❌ HANDSHAKE FAILED. Server returned: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ HANDSHAKE FAILED. Could not connect to the Master Node.")
        sys.exit(1)

    # ==========================================
    # 🔄 4. THE PROOF OF WORK LOOP
    # ==========================================
    while True:
        time.sleep(3) # Poll the network every 3 seconds
        
        try:
            # A. Ask the Front Desk for a task
            req_resp = requests.post("http://127.0.0.1:5000/api/v1/task/request", json={"node_id": node_id})
            
            if req_resp.status_code == 200:
                task = req_resp.json()
                print(f"\n[NODE] 📥 Received Task: {task['task_id']} | Bounty: {task['payout_sats']} SATS")
                print(f"       > Prompt: '{task['prompt']}'")
                
                # B. Execute the AI inference work
                print(f"[NODE] 🧠 Routing task to Cognitive Engine...")
                ai_answer = brain.process_task(task['prompt'])
                
                # C. Generate the Lightning Invoice
                invoice, p_hash = wallet.generate_invoice(task['payout_sats'])
                
                # D. Submit the REAL answer AND the invoice
                submit_payload = {
                    "node_id": node_id,
                    "task_id": task['task_id'],
                    "result": ai_answer, # <-- Dynamically generated AI output
                    "invoice": invoice
                }
                pay_resp = requests.post("http://127.0.0.1:5000/api/v1/task/submit", json=submit_payload)
                
                # E. Settle the funds
                if pay_resp.status_code == 200:
                    print(f"[NODE] ✅ Cryptographic Preimage verified by Network!")
                    wallet.receive_payment(task['payout_sats'])
                    
        except requests.exceptions.ConnectionError:
            print("🚨 Connection to Master Node lost. Retrying...")
            time.sleep(5)

if __name__ == "__main__":
    main()
