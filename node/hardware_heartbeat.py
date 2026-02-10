import os
import platform
import time
import json
import uuid
from datetime import datetime

# --- CONFIGURATION ---
# On Windows, we'll save the log to the current folder instead of /var/log/
LOG_FILE = "proxy_heartbeat.log" if platform.system() == "Windows" else "/var/log/proxy_heartbeat.log"

def get_node_identity():
    """
    On a Pi, this would talk to the TPM chip. 
    On Windows, we'll use a unique ID based on your computer.
    """
    if platform.system() == "Windows":
        return f"SIM-WIN-{uuid.getnode()}"
    return "HARDWARE-TPM-PROD-001"

def get_location_mock():
    """
    Simulates GPS/WiFi triangulation.
    """
    return {"lat": 51.5074, "lng": -0.1278, "city": "London", "iso": "GB"}

def pulse():
    identity = get_node_identity()
    location = get_location_mock()
    
    heartbeat_payload = {
        "timestamp": datetime.now().isoformat(),
        "node_id": identity,
        "location": location,
        "status": "ACTIVE",
        "mock_mode": platform.system() == "Windows"
    }

    # In a real scenario, this would be signed by the TPM
    signature = f"sig_mock_{uuid.uuid4().hex[:8]}"
    heartbeat_payload["signature_proof"] = signature

    log_entry = json.dumps(heartbeat_payload)
    
    # Append to the log file
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Heartbeat Sent: {signature}")

if __name__ == "__main__":
    print(f"Proxy Heartbeat Initialized on {platform.system()}")
    print(f"Logging to: {os.path.abspath(LOG_FILE)}")
    
    try:
        while True:
            pulse()
            time.sleep(10) # Pulse every 10 seconds
    except KeyboardInterrupt:
        print("\nHeartbeat stopped by user.")
