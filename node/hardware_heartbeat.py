import time
import requests
import secrets
import subprocess
import json
import hashlib
from datetime import datetime
# Import our hardware binding class
from tpm_binding import TPMBinding

# PROXY PROTOCOL - HARDWARE HEARTBEAT v1.4 (Reputation Guarded)
# "Trust, but verify locally. Proactive self-auditing."
# ----------------------------------------------------

class NodeHealthMonitor:
    def __init__(self, api_endpoint="https://api.proxyprotocol.com/v1", claimed_iso="US"):
        self.api_endpoint = api_endpoint
        self.claimed_iso = claimed_iso # The ISO code the operator registered with
        self.tpm = TPMBinding()
        self.is_active = True
        
        # Internal State
        self.reputation_warning_active = False
        
        if not self.tpm.check_availability():
            print("⚠️  TPM NOT DETECTED. Starting in SOFTWARE MODE (Tier 0).")
            self.has_hardware = False
        else:
            print(f"🔒 TPM 2.0 DETECTED. Claimed Jurisdiction: {self.claimed_iso}")
            self.has_hardware = True

    def _get_wifi_fingerprint(self):
        """Scans nearby WiFi Access Points for location fingerprinting."""
        try:
            cmd = ["nmcli", "-t", "-f", "BSSID,SIGNAL", "dev", "wifi", "list"]
            output = subprocess.check_output(cmd).decode('utf-8').strip()
            aps = []
            for line in output.split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        aps.append({"bssid": parts[0], "rssi": parts[1]})
            return sorted(aps, key=lambda x: int(x['rssi']), reverse=True)[:5]
        except Exception:
            return []

    def _get_network_metadata(self):
        """Captures public IP and basic Geo-metadata."""
        metadata = {"public_ip": "unknown", "latency_ms": 0, "detected_country": "unknown"}
        try:
            # 1. Get Public IP and Geo-location info (Using a public API for demo)
            ip_resp = requests.get("https://ipapi.co/json/", timeout=5)
            data = ip_resp.json()
            metadata["public_ip"] = data.get("ip")
            metadata["detected_country"] = data.get("country_code")
            
            # 2. Latency Proof
            start = time.time()
            requests.get(f"{self.api_endpoint}/status", timeout=5)
            metadata["latency_ms"] = int((time.time() - start) * 1000)
        except Exception:
            pass
        return metadata

    def _self_audit(self, telemetry):
        """
        PRE-FLIGHT CHECK:
        Compares current telemetry against claimed jurisdiction.
        Returns (is_compliant, reason)
        """
        detected_iso = telemetry['network'].get('detected_country')
        
        if detected_iso != self.claimed_iso:
            return False, f"Jurisdiction Mismatch: Claimed {self.claimed_iso} but detected {detected_iso}"
        
        # Check for sufficient WiFi entropy (Anti-VM check)
        if len(telemetry['wifi_aps']) < 1:
             return False, "Insufficient WiFi Entropy (Node appears to be virtualized)"
             
        return True, "Locality Verified"

    def pulse(self):
        """Sends an attested heartbeat with proactive reputation protection."""
        print(f"[{datetime.now().isoformat()}] 💓 Generating Pulse...")
        
        # 1. Gather Physical Telemetry
        wifi_data = self._get_wifi_fingerprint()
        net_data = self._get_network_metadata()
        
        telemetry = {
            "wifi_aps": wifi_data,
            "network": net_data
        }

        # 2. Proactive Reputation Audit
        is_compliant, reason = self._self_audit(telemetry)
        if not is_compliant:
            print(f"   [!] REPUTATION ALERT: {reason}")
            self.reputation_warning_active = True

        # 3. Construct Payload
        payload = {
            "status": "ONLINE" if is_compliant else "UNSTABLE",
            "timestamp": datetime.now().isoformat(),
            "tier": "2" if self.has_hardware else "0",
            "location_proof": telemetry,
            "local_audit": {
                "compliant": is_compliant,
                "reason": reason
            }
        }

        if self.has_hardware:
            nonce_raw = secrets.token_hex(16)
            location_hash = hashlib.sha256(json.dumps(telemetry).encode()).hexdigest()
            binding_nonce = f"{nonce_raw}:{location_hash[:16]}"
            
            # Generate Hardware Quote (PCR 0,1,7)
            attestation = self.tpm.generate_attestation_quote(binding_nonce)
            payload['attestation'] = attestation
            payload['hw_secured'] = True
            payload['binding_nonce'] = nonce_raw
        
        # 4. Transmit & Handle Slashing Response
        try:
            # response = requests.post(f"{self.api_endpoint}/nodes/heartbeat", json=payload)
            # In a real scenario, we check for PX_401 (Geofence Violation)
            # if response.status_code == 403 and "PX_401" in response.text:
            #     print("🚨 SLASH ALERT: API reported location fraud. Bond at risk.")
            print(f"   -> Compliance: {'PASSED' if is_compliant else 'SUSPICIOUS'}")
            
        except Exception as e:
            print(f"   [!] Transmission Error: {e}")

    def run(self):
        while self.is_active:
            try:
                self.pulse()
            except Exception as e:
                print(f"   [!] Pulse Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Simulate a US-based node
    monitor = NodeHealthMonitor(claimed_iso="US")
    monitor.run()
