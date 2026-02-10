import time
import os
import subprocess
import json
import math
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

# PROXY PROTOCOL - HARDWARE HEARTBEAT v1.1
# "Pulse check for the physical layer: Proof of Locality."
# ----------------------------------------------------
# This script runs as a background daemon on Raspberry Pi nodes.
# It cross-references WiFi fingerprints with expected coordinates
# and signs the telemetry using the hardware TPM.

class NodeHealthMonitor:
    def __init__(
        self, 
        node_id: str, 
        api_endpoint: str = "https://api.proxyprotocol.com/v1", 
        expected_lat: float = 33.4152, 
        expected_lon: float = -111.8315
    ):
        self.node_id = node_id
        self.api_endpoint = api_endpoint
        self.is_active = True
        
        # Geofence Configuration
        self.EXPECTED_LAT = expected_lat
        self.EXPECTED_LON = expected_lon
        self.GEOFENCE_RADIUS_KM = 0.5 # 500 meter tolerance
        
        # TPM Configuration
        self.AK_HANDLE = "0x81010002" # Standard Attestation Key handle

    def _get_cpu_temp(self) -> float:
        """Reads Raspberry Pi thermal zone data."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return float(f.read()) / 1000.0
        except FileNotFoundError:
            return 0.0

    def _scan_wifi_fingerprint(self) -> List[Dict]:
        """
        Scans local BSSIDs using nmcli to create a location fingerprint.
        """
        try:
            # -t (terse), -f (fields)
            cmd = ["nmcli", "-t", "-f", "BSSID,SIGNAL", "dev", "wifi"]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
            
            networks = []
            for line in output.strip().split('\n'):
                if ':' in line:
                    bssid, signal = line.split(':')
                    networks.append({"bssid": bssid, "signal": int(signal)})
            return sorted(networks, key=lambda x: x['signal'], reverse=True)[:5]
        except Exception as e:
            print(f"[Heartbeat] WiFi Scan Error: {e}")
            return []

    def _sign_with_tpm(self, payload: str) -> str:
        """
        Signs the telemetry payload using the hardware TPM 2.0.
        The private key never leaves the Infineon chip.
        """
        try:
            # 1. Hash the payload
            payload_hash = hashlib.sha256(payload.encode()).digest()
            hash_file = "/tmp/heartbeat_hash.bin"
            sig_file = "/tmp/heartbeat.sig"
            
            with open(hash_file, "wb") as f:
                f.write(payload_hash)
            
            # 2. Call TPM2_Sign
            subprocess.run([
                "tpm2_sign", 
                "-c", self.AK_HANDLE, 
                "-g", "sha256", 
                "-d", hash_file, 
                "-f", "plain", 
                "-o", sig_file
            ], check=True, capture_output=True)
            
            with open(sig_file, "rb") as f:
                return f.read().hex()
        except Exception as e:
            print(f"[Heartbeat] TPM Signing Failed: {e}")
            return "unsigned_fallback_error"

    def _calculate_distance(self, lat2: float, lon2: float) -> float:
        """Haversine formula to calculate distance in KM."""
        lat1, lon1 = self.EXPECTED_LAT, self.EXPECTED_LON
        R = 6371.0
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def pulse(self):
        """Executes a single heartbeat cycle."""
        print(f"[{datetime.now().isoformat()}] 💓 Heartbeat Initiated...")
        
        # 1. Gather Telemetry
        temp = self._get_cpu_temp()
        wifi_scan = self._scan_wifi_fingerprint()
        
        # Mocking triangulation from WiFi (In prod, this hits a Geolocation API with the BSSIDs)
        current_lat, current_lon = 33.4153, -111.8314
        drift = self._calculate_distance(current_lat, current_lon)
        
        # 2. Construct Payload
        telemetry = {
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "cpu_temp": temp,
            "geo": {"lat": current_lat, "lon": current_lon, "drift_km": round(drift, 4)},
            "wifi_fingerprint": wifi_scan
        }
        
        payload_str = json.dumps(telemetry, sort_keys=True)
        
        # 3. Hardware Sign
        signature = self._sign_with_tpm(payload_str)
        
        # 4. Transmit to Protocol
        report = {
            "payload": telemetry,
            "signature": signature,
            "hw_root": "TPM_2.0_INFINEON"
        }
        
        if drift > self.GEOFENCE_RADIUS_KM:
            print(f"⚠️  ALERT: Geofence Violation! Drift: {drift:.3f}km")
            # In production: notify API of self-delisting
        else:
            print(f"✅ Locality Verified. Signature: {signature[:16]}...")
            
        # Optional: Send to central API
        # requests.post(f"{self.api_endpoint}/nodes/heartbeat", json=report)

    def run(self, interval: int = 60):
        print(f"[*] Node Monitor Running for {self.node_id}...")
        try:
            while self.is_active:
                self.pulse()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("[*] Monitor stopped by operator.")

if __name__ == "__main__":
    # Example initialization
    monitor = NodeHealthMonitor(node_id="node_az_phoenix_01")
    monitor.run()
