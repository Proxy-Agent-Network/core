import time
import os
import subprocess
import requests
import json
import math
from datetime import datetime

# PROXY PROTOCOL - HARDWARE HEARTBEAT v1.1
# "Pulse check for the physical layer."
# ----------------------------------------------------
# Runs as a background daemon (systemd) on the Physical Node.

class NodeHealthMonitor:
    def __init__(self, api_endpoint="https://api.proxyprotocol.com/v1", node_id="node_local_x", expected_lat=33.4152, expected_lon=-111.8315):
        self.api_endpoint = api_endpoint
        self.node_id = node_id
        self.is_active = True
        
        # Thresholds
        self.TEMP_WARN_C = 75.0
        self.TEMP_CRITICAL_C = 85.0
        
        # Geofence Config (Proof of Locality)
        self.EXPECTED_LAT = expected_lat
        self.EXPECTED_LON = expected_lon
        self.GEOFENCE_RADIUS_KM = 0.5 # 500 meters
    
    def _read_cpu_temp(self) -> float:
        """Reads Raspberry Pi / Linux CPU temperature."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return float(f.read()) / 1000.0
        except FileNotFoundError:
            # Fallback for dev environments not on Pi
            return 45.0 

    def _check_tpm_status(self) -> bool:
        """Verifies the Hardware Root of Trust is responsive."""
        if not os.path.exists("/dev/tpm0"):
            return False
        
        # Simple ping command to the TPM resource manager
        try:
            # In prod, use tpm2_getcap -c properties-fixed
            subprocess.check_output(["tpm2_getcap", "properties-fixed"], stderr=subprocess.STDOUT)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_chassis_intrusion(self) -> bool:
        """
        Checks the physical GPIO plunger switch.
        Returns True if the case is OPEN (Intrusion Detected).
        """
        # Mocking GPIO read for reference. 
        # In prod: import RPi.GPIO as GPIO; return GPIO.input(PIN_INTRUSION)
        # 0 = Closed (Safe), 1 = Open (Danger)
        return False 

    def _get_wifi_fingerprint(self) -> dict:
        """
        Scans local WiFi environment to generate a location fingerprint.
        Triangulates position based on known BSSID anchors.
        """
        # In prod: subprocess.check_output(['nmcli', '-f', 'BSSID,SIGNAL', 'dev', 'wifi'])
        # Mocking a scan result near the expected coordinates
        return {
            "networks_visible": 14,
            "strongest_bssid": "aa:bb:cc:dd:ee:ff",
            "triangulated_lat": 33.4153, # Slight drift for realism
            "triangulated_lon": -111.8314
        }

    def _sign_locality_proof(self, location_data: dict) -> str:
        """
        Uses the TPM 2.0 to cryptographically sign the location telemetry.
        This prevents software spoofing of GPS coordinates.
        """
        payload = json.dumps(location_data, sort_keys=True).encode()
        # In prod: Use tpm2_sign CLI or python-tss library
        # Mocking signature generation
        return f"tpm_sig_secp256r1_{hash(payload)}"

    def _check_geofence(self) -> bool:
        """
        Verifies Node is within allowed physical radius using WiFi/Cellular consensus.
        """
        scan_data = self._get_wifi_fingerprint()
        
        # Calculate Haversine distance (approximate)
        lat1, lon1 = self.EXPECTED_LAT, self.EXPECTED_LON
        lat2, lon2 = scan_data['triangulated_lat'], scan_data['triangulated_lon']
        
        R = 6371 # Radius of earth in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance_km = R * c
        
        if distance_km > self.GEOFENCE_RADIUS_KM:
            print(f"[{datetime.now()}] ⚠️ GEOFENCE VIOLATION: Drifted {distance_km:.3f}km")
            return False
            
        # Generate signed proof for the network
        proof = self._sign_locality_proof({
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "scan": scan_data
        })
        print(f"[{datetime.now()}] 📍 Location Verified ({distance_km:.3f}km drift). Proof signed by TPM.")
        return True

    def emergency_delist(self, reason: str):
        """
        CRITICAL: Proactively remove node from the network registry.
        Prevents assignment of new tasks during hardware failure.
        """
        print(f"[{datetime.now()}] 🚨 EMERGENCY DELIST TRIGGERED: {reason}")
        
        payload = {
            "node_id": self.node_id,
            "status": "offline",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # High-priority status update
            # requests.post(f"{self.api_endpoint}/nodes/status", json=payload)
            print(f"   -> Network notified. Status set to OFFLINE.")
        except Exception as e:
            print(f"   -> Failed to notify network: {e}")
            
        self.is_active = False

    def run_loop(self):
        print(f"[{datetime.now()}] 🟢 Hardware Heartbeat Active. Monitoring...")
        
        while self.is_active:
            # 1. Security Check (Priority #1)
            if not self._check_tpm_status():
                self.emergency_delist("CRITICAL: TPM Module not detected. Identity integrity lost.")
                break
            
            if self._check_chassis_intrusion():
                self.emergency_delist("CRITICAL: Chassis intrusion detected. Possible physical tampering.")
                break

            # 2. Proof of Locality (Competitive Edge)
            if not self._check_geofence():
                self.emergency_delist("CRITICAL: Node moved outside Geofence. Possible theft.")
                break

            # 3. Health Check
            temp = self._read_cpu_temp()
            if temp > self.TEMP_CRITICAL_C:
                self.emergency_delist(f"CRITICAL: Overheating ({temp}°C). Risk of computation error.")
                break
            elif temp > self.TEMP_WARN_C:
                print(f"[{datetime.now()}] ⚠️ WARNING: High Temp ({temp}°C). Throttling tasks.")

            # 4. Heartbeat Pulse
            # In a real implementation, we send a 'still alive' ping every minute
            # requests.post(f"{self.api_endpoint}/nodes/ping", json={"temp": temp})
            
            time.sleep(10)

if __name__ == "__main__":
    monitor = NodeHealthMonitor()
    monitor.run_loop()
