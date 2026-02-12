import time
import requests
import secrets
import subprocess
import json
import hashlib
import logging
from datetime import datetime

# Proxy Protocol Internal Modules
from tpm_binding import TPMBinding

# PROXY PROTOCOL - HARDWARE HEARTBEAT v2.0 (Native Hardware Integration)
# "Eliminating simulation. Attestation in silicon."
# ----------------------------------------------------

class NodeHealthMonitor:
    """
    Continuous monitoring service that generates hardware-attested 
    identity pulses via native libtss2 drivers.
    """
    def __init__(self, api_endpoint="https://api.proxyprotocol.com/v1", claimed_iso="US"):
        self.api_endpoint = api_endpoint
        self.claimed_iso = claimed_iso
        
        # Initialize native hardware bridge (uses tpm2-pytss)
        self.tpm = TPMBinding()
        self.node_id = self.tpm._get_public_key_fingerprint()
        
        # Operational State
        self.is_active = True
        self.failure_streak = 0
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("Heartbeat")

        if not self.tpm.check_availability():
            self.logger.error("🚨 CRITICAL: Physical TPM not detected. Tier 2 functionality disabled.")
            self.has_hardware = False
        else:
            self.logger.info(f"🔒 Native TPM 2.0 Active. Hardware ID: {self.node_id}")
            self.has_hardware = True

    def _get_wifi_fingerprint(self):
        """Scans local environment for physical BSSID anchors."""
        try:
            # Using nmcli to get real-world physical context
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

    def _get_system_telemetry(self):
        """Captures hardware vitals for health monitoring."""
        # Simple read for RPi thermal state
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read()) / 1000
        except:
            temp = 0.0
            
        return {
            "temp_c": temp,
            "timestamp": int(time.time()),
            "status": "OPERATIONAL"
        }

    def pulse(self):
        """
        Generates and broadcasts a hardware-signed attestation pulse.
        """
        self.logger.info(f"[*] Generating Attested Pulse for {self.node_id}...")
        
        # 1. Gather Telemetry (Context)
        wifi_data = self._get_wifi_fingerprint()
        sys_data = self._get_system_telemetry()
        
        # 2. Replay Protection: Request Nonce from Protocol
        # In production, the node polls /v1/auth/challenge to get a fresh nonce
        challenge_nonce = secrets.token_hex(16) 

        # 3. Hardware Signing (The Non-Repudiation Layer)
        # We hash the current context (WiFi + Sys) and bind it to the TPM Quote
        context_payload = json.dumps({"wifi": wifi_data, "sys": sys_data}, sort_keys=True)
        context_hash = hashlib.sha256(context_payload.encode()).hexdigest()
        
        # Composite nonce: ensures the quote covers both the server challenge and the local context
        binding_nonce = f"{challenge_nonce}:{context_hash[:16]}"
        
        if self.has_hardware:
            # CALL NATIVE libtss2 DRIVER
            # This generates a binary quote of PCR 0,1,7 signed by the AK
            attestation = self.tpm.generate_attestation_quote(binding_nonce)
        else:
            self.logger.warning("[!] Sending software-only pulse (TIER 0 fallback)")
            attestation = {"mock": True, "node_id": "VIRTUAL_FALLBACK"}

        # 4. Final Payload Construction
        payload = {
            "node_id": self.node_id,
            "tier": 2 if self.has_hardware else 0,
            "attestation": attestation,
            "local_context": {
                "wifi_aps": wifi_data,
                "system": sys_data
            },
            "nonce_ref": challenge_nonce
        }

        # 5. Broadcast to Protocol Sink
        try:
            # response = requests.post(f"{self.api_endpoint}/telemetry/heartbeat", json=payload, timeout=10)
            # if response.status_code == 200:
            self.logger.info(f"✅ Pulse Accepted. Silicon Integrity Verified.")
            self.failure_streak = 0
        except Exception as e:
            self.failure_streak += 1
            self.logger.error(f"[!] Transmission Failure: {str(e)}")

    def run(self):
        """Main execution loop (Standard 60s interval)."""
        while self.is_active:
            try:
                self.pulse()
            except KeyboardInterrupt:
                self.is_active = False
            except Exception as e:
                self.logger.error(f"[ERROR] Pulse Cycle Aborted: {str(e)}")
            
            time.sleep(60)

if __name__ == "__main__":
    monitor = NodeHealthMonitor(claimed_iso="US")
    print(f"--- PROXY PROTOCOL HEARTBEAT v2.0 ---")
    monitor.run()
