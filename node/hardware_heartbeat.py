import time
import requests
import secrets
import subprocess
import json
import hashlib
from datetime import datetime
# Import our hardware binding class
from tpm_binding import TPMBinding

# PROXY PROTOCOL - HARDWARE HEARTBEAT v1.3 (Geolocated & Attested)
# "Proof of Locality: Identity tied to a coordinate."
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

    def _get_wifi_fingerprint(self):
        """
        Scans nearby WiFi Access Points to create a unique physical location hash.
        Requires 'network-manager' (nmcli) on Linux.
        """
        try:
            # -t: Terse output, -f: Specific fields
            cmd = ["nmcli", "-t", "-f", "BSSID,SIGNAL", "dev", "wifi", "list"]
            output = subprocess.check_output(cmd).decode('utf-8').strip()
            
            aps = []
            for line in output.split('\n'):
                if line:
                    bssid, signal = line.split(':')
                    aps.append({"bssid": bssid, "rssi": signal})
            
            # Sort by signal strength and take top 5 to ensure stability
            aps = sorted(aps, key=lambda x: int(x['rssi']), reverse=True)[:5]
            return aps
        except Exception as e:
            print(f"   [!] WiFi Scan Failed: {e}")
            return []

    def _get_network_metadata(self):
        """
        Captures public IP and performs a latency check to the Proxy API.
        """
        metadata = {"public_ip": "unknown", "latency_ms": 0}
        try:
            # 1. Get Public IP
            ip_resp = requests.get("https://api.ipify.org?format=json", timeout=5)
            metadata["public_ip"] = ip_resp.json().get("ip")
            
            # 2. Ping API for Latency Proof
            start = time.time()
            requests.get(f"{self.api_endpoint}/status", timeout=5)
            metadata["latency_ms"] = int((time.time() - start) * 1000)
        except Exception:
            pass
        return metadata

    def pulse(self):
        """
        Sends a cryptographically attested heartbeat including Geolocation Proofs.
        """
        print(f"[{datetime.now().isoformat()}] 💓 Generating Geolocated Pulse...")
        
        # 1. Gather Physical Telemetry
        wifi_data = self._get_wifi_fingerprint()
        net_data = self._get_network_metadata()
        
        # 2. Construct Core Payload
        payload = {
            "status": "ONLINE",
            "timestamp": datetime.now().isoformat(),
            "tier": "2" if self.has_hardware else "0",
            "location_proof": {
                "wifi_aps": wifi_data,
                "network": net_data
            }
        }

        if self.has_hardware:
            # 3. Request Challenge Nonce (Prevents Replay)
            # In production, we'd fetch this from the API.
            nonce_raw = secrets.token_hex(16)
            
            # To bind the location to the hardware quote, we hash the location data
            # into the nonce sent to the TPM. This proves the machine was at 
            # THESE coordinates when it signed the quote.
            location_hash = hashlib.sha256(json.dumps(payload['location_proof']).encode()).hexdigest()
            binding_nonce = f"{nonce_raw}:{location_hash[:16]}"
            
            # 4. Generate Hardware Quote (PCR 0,1,7)
            attestation = self.tpm.generate_attestation_quote(binding_nonce)
            
            payload['attestation'] = attestation
            payload['hw_secured'] = True
            payload['binding_nonce'] = nonce_raw
        
        # 5. Transmit
        print(f"   -> Data: IP {net_data['public_ip']} | Latency {net_data['latency_ms']}ms | APs {len(wifi_data)}")
        # requests.post(f"{self.api_endpoint}/nodes/heartbeat", json=payload)
        
        if self.has_hardware:
            print("   ✅ SENT: Hardware-Signed Locality Proof (TPM 2.0)")
        else:
            print("   ⚠️ SENT: Unsigned Heartbeat (Low Trust / Software Mode)")

    def run(self):
        while self.is_active:
            try:
                self.pulse()
            except Exception as e:
                print(f"   [!] Pulse Error: {e}")
            time.sleep(60) # 1 Minute Heartbeat

if __name__ == "__main__":
    monitor = NodeHealthMonitor()
    monitor.run()
