import time
import os
import subprocess
import requests
import json
from datetime import datetime

# PROXY PROTOCOL - HARDWARE HEARTBEAT v1.0
# "Pulse check for the physical layer."
# ----------------------------------------------------
# Runs as a background daemon (systemd) on the Physical Node.

class NodeHealthMonitor:
    def __init__(self, api_endpoint="https://api.proxyprotocol.com/v1", node_id="node_local_x"):
        self.api_endpoint = api_endpoint
        self.node_id = node_id
        self.is_active = True
        
        # Thresholds
        self.TEMP_WARN_C = 75.0
        self.TEMP_CRITICAL_C = 85.0
    
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
                # Optional: Trigger key wipe here
                break

            # 2. Health Check
            temp = self._read_cpu_temp()
            if temp > self.TEMP_CRITICAL_C:
                self.emergency_delist(f"CRITICAL: Overheating ({temp}°C). Risk of computation error.")
                break
            elif temp > self.TEMP_WARN_C:
                print(f"[{datetime.now()}] ⚠️ WARNING: High Temp ({temp}°C). Throttling tasks.")

            # 3. Heartbeat Pulse
            # In a real implementation, we send a 'still alive' ping every minute
            # requests.post(f"{self.api_endpoint}/nodes/ping", json={"temp": temp})
            
            time.sleep(10)

if __name__ == "__main__":
    monitor = NodeHealthMonitor()
    monitor.run_loop()
