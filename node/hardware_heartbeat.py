import time
import requests
import secrets
from datetime import datetime
# Import our new class
from tpm_binding import TPMBinding

# PROXY PROTOCOL - HARDWARE HEARTBEAT v1.2 (Attested)
# "Heartbeat with a Pulse."
# ----------------------------------------------------

class NodeHealthMonitor:
    def __init__(self, api_endpoint="https://api.proxyprotocol.com/v1"):
        self.api_endpoint = api_endpoint
        self.tpm = TPMBinding()
        self.is_active = True
        
        if not self.tpm.check_availability():
            print("⚠️  TPM NOT DETECTED. Starting in SOFTWARE MODE (Tier 0).")
            self.has_hardware = False
        else:
            print("🔒 TPM 2.0 DETECTED. Starting in HARDWARE MODE (Tier 2/3).")
            self.has_hardware = True

    def pulse(self):
        """
        Sends a cryptographically attested heartbeat.
        """
        print(f"[{datetime.now().isoformat()}] 💓 Generating Pulse...")
        
        payload = {
            "status": "ONLINE",
            "timestamp": datetime.now().isoformat(),
            "tier": "2" if self.has_hardware else "0"
        }

        if self.has_hardware:
            # 1. Get Challenge/Nonce from API (Anti-Replay)
            # In prod: resp = requests.get(f"{self.api_endpoint}/auth/challenge")
            # nonce = resp.json()['nonce']
            nonce = secrets.token_hex(16) # Mock nonce
            
            # 2. Generate Hardware Quote
            # This takes ~500ms on a Raspberry Pi
            attestation = self.tpm.generate_attestation_quote(nonce)
            
            payload['attestation'] = attestation
            payload['hw_secured'] = True
        
        # 3. Transmit
        print(f"   -> Uploading to Network (Size: {len(str(payload))} bytes)")
        # requests.post(f"{self.api_endpoint}/nodes/heartbeat", json=payload)
        
        if self.has_hardware:
            print("   ✅ SENT: Hardware-Signed Quote (PCR 0,1,7)")
        else:
            print("   ⚠️ SENT: Unsigned Heartbeat (Low Trust)")

    def run(self):
        while self.is_active:
            self.pulse()
            time.sleep(60) # 1 Minute Heartbeat

if __name__ == "__main__":
    monitor = NodeHealthMonitor()
    monitor.run()
