import sys
import time
import requests
import platform
import json
from datetime import datetime, timezone

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

    # 2. Identity Generation (Hardware Root of Trust)
    print("🔐 Unlocking Hardware Enclave (TPM 2.0)...")
    try:
        # This will now reach down into the OS and talk to the physical silicon
        hardware_enclave = proxy_core.NodeHardware()
        
        # Mathematically bound identity
        node_id = hardware_enclave.get_fingerprint()
        
        # For now, the public key is a placeholder until we extract the actual EK bytes in Rust
        pub_key = "PENDING_TPM_EK_PUB_KEY" 
        
        print("✅ Hardware Attestation Successful.")
        print(f"   > Node Identity: {node_id}")
        time.sleep(1)
        
    except Exception as e:
        print("🚨 BOOT HALTED: Hardware Security Failure.")
        print(f"Details: {e}")
        print("This node cannot participate in the network without a valid TPM 2.0 context.")
        sys.exit(1)

    # 3. The Handshake
    print(f"📡 Attempting Handshake with Network ({MASTER_NODE_URL})...")
    payload = {
        "node_id": node_id,
        "public_key": pub_key,
        "hardware_stats": hw_stats,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        response = requests.post(MASTER_NODE_URL, json=payload)
        
        if response.status_code == 200:
            resp_data = response.json()
            print("\n✅ HANDSHAKE SUCCESSFUL!")
            print(f"   > Network Status: {resp_data.get('status', 'OK')}")
            print(f"   > Message: {resp_data.get('message', 'Connected')}")
            print("\n🚀 NODE IS NOW ACTIVE AND AWAITING TASKS...")
        else:
            print(f"\n❌ HANDSHAKE FAILED. Server returned: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("\n❌ HANDSHAKE FAILED. Could not connect to the Master Node.")
        print(f"Ensure the server is running at {MASTER_NODE_URL}")

if __name__ == "__main__":
    main()