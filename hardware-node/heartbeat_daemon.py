import requests
import time
import json
import hashlib
import hmac
import platform

# CONFIGURATION
SERVER_URL = "http://localhost:5000/api/register"
NODE_ID = "NODE_79F9F798" # Your Real Hardware ID
SECRET_KEY = b"PROXY_NETWORK_ROOT_V1_SECURE"

def generate_signed_heartbeat():
    """Generates a signed telemetry packet."""
    timestamp = str(int(time.time()))
    # Simple telemetry: System load and platform info
    telemetry = {
        "status": "ONLINE",
        "cpu_arch": platform.machine(),
        "load": "LOW" 
    }
    
    # Create signature to prevent spoofing
    msg = f"{NODE_ID}:{timestamp}".encode()
    signature = hmac.new(SECRET_KEY, msg, hashlib.sha256).hexdigest()
    
    return {
        "node_id": NODE_ID,
        "timestamp": timestamp,
        "signature": signature,
        "telemetry": telemetry
    }

def start_heartbeat():
    print(f"--- HEARTBEAT DAEMON STARTED [{NODE_ID}] ---")
    while True:
        try:
            payload = generate_signed_heartbeat()
            response = requests.post(SERVER_URL, json=payload)
            
            if response.status_code == 200:
                print(f"[{time.strftime('%H:%M:%S')}] Heartbeat synced. Status: 200 OK")
            else:
                print(f"[!] Sync failed: {response.status_code}")
                
        except Exception as e:
            print(f"[!] Network Error: {e}")
            
        # Wait 60 seconds for the next pulse
        time.sleep(60)

if __name__ == "__main__":
    start_heartbeat()