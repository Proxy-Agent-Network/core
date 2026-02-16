import time
import json
import socket
import hashlib

# Protocol Configuration
PROTOCOL_VERSION = "v1.6.0"
DISCOVERY_URL = "https://node-gate.proxyagent.network/heartbeat"

class ProxyNode:
    def __init__(self):
        self.node_id = self._generate_hardware_id()
        self.status = "ACTIVE"
        
    def _generate_hardware_id(self):
        """
        Generates a unique ID. 
        FUTURE: Replace with physical TPM 2.0 Attestation Key (AK)
        """
        cpu_serial = "0000000000000000"
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Serial'):
                        cpu_serial = line.split(':')[1].strip()
        except:
            cpu_serial = socket.gethostname()
        return hashlib.sha256(cpu_serial.encode()).hexdigest()[:16]

    def emit_heartbeat(self):
        payload = {
            "node_id": self.node_id,
            "version": PROTOCOL_VERSION,
            "timestamp": time.time(),
            "status": self.status,
            "hardware_metrics": {
                "load": 0.45, # Placeholder for real sys metrics
                "tpm_status": "SIMULATED" # Change to 'VERIFIED' for physical
            }
        }
        # In production, this would be a POST request to DISCOVERY_URL
        print(f"💓 Heartbeat Sent: {json.dumps(payload)}")

if __name__ == "__main__":
    node = ProxyNode()
    print(f"Proxy Node {node.node_id} Initialized...")
    while True:
        node.emit_heartbeat()
        time.sleep(60) # Broadcast every minute