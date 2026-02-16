import time
import uuid
import requests
import platform
import json
from datetime import datetime

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

def generate_identity():
    """Simulates generating a TPM Endorsement Key (EK)."""
    # In production, this comes from the TPM chip
    simulated_node_id = f"NODE-{str(uuid.uuid4())[:8].upper()}"
    simulated_pub_key = "0x7F2... (Simulated TPM Public Key)"
    return simulated_node_id, simulated_pub_key

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
    print("🔐 Unlocking Secure Enclave (Simulated)...")
    node_id, pub_key = generate_identity()
    print(f"   > Identity Generated: {node_id}")
    time.sleep(1)

    # 3. The Handshake
    print(f"📡 Attempting Handshake with Network ({MASTER_NODE_URL})...")
    payload = {
        "node_id": node_id,
        "public_key": pub_key,
        "hardware_stats": hw_stats,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        response = requests.post(MASTER_NODE_URL, json=payload)
        
        if response.status_code == 200:
            resp_data = response.json()
            print("\n✅ HANDSHAKE SUCCESSFUL!")
            print(f"   > Network Status: {resp_data['status']}")
            print(f"   > Message: {resp_data['message']}")
            print("\n🚀 NODE IS NOW ACTIVE AND AWAITING TASKS.")
        else:
            print(f"\n❌ Handshake Failed: {response.text}")
            
    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("   Is the backend server running?")

if __name__ == "__main__":
    main()