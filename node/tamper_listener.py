import time
import subprocess
import signal
import sys
import os
import cv2
import numpy as np
import hashlib
from typing import List, Dict, Optional

# PROXY PROTOCOL - TAMPER LISTENER v1.1 (Hardware + Evidence Integrity)
# "Defending the silicon and the proof."
# ----------------------------------------------------

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

class TamperListener:
    """
    Enhanced watchdog that monitors physical chassis intrusion AND 
    performs perceptual hashing on incoming evidence to detect fraud.
    """
    
    def __init__(self, pin=26, response_script="/app/core/scripts/tamper_response.sh"):
        self.TAMPER_PIN = pin
        self.RESPONSE_SCRIPT = response_script
        self.is_monitoring = True
        
        # Local cache of previously used proof hashes to prevent reuse
        # Format: { "hash": timestamp }
        self.evidence_history_cache: Dict[str, float] = {}
        
        if GPIO is None:
            print("[!] GPIO library not detected. Running hardware monitoring in SIMULATION.")
        else:
            self._setup_gpio()

    # --- 1. HARDWARE INTEGRITY (Physical Tamper) ---

    def _setup_gpio(self):
        """Configures physical intrusion detection circuit."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TAMPER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.TAMPER_PIN, 
            GPIO.RISING, 
            callback=self.trigger_scorched_earth, 
            bouncetime=200
        )
        print(f"[*] Hardware Watchdog Active: Monitoring GPIO {self.TAMPER_PIN}")

    def trigger_scorched_earth(self, channel=None):
        """Irreversible hardware wipe and process termination."""
        print("\n🚨 CRITICAL: CHASSIS INTRUSION DETECTED! INITIATING WIPE.")
        try:
            if os.path.exists(self.RESPONSE_SCRIPT):
                subprocess.Popen(["/bin/bash", self.RESPONSE_SCRIPT])
            else:
                subprocess.run(["pkill", "-9", "-f", "node_daemon.py"])
        except Exception:
            sys.exit(1)

    # --- 2. EVIDENCE INTEGRITY (Perceptual Hashing) ---

    def compute_perceptual_hash(self, image_path: str) -> Optional[str]:
        """
        Calculates a Difference Hash (dHash) for the image.
        dHash is resistant to resizing, brightness shifts, and format changes.
        """
        try:
            image = cv2.imread(image_path)
            if image is None: return None
            
            # 1. Grayscale and resize to 9x8 for dHash
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
            
            # 2. Compute differences between adjacent pixels
            diff = resized[:, 1:] > resized[:, :-1]
            
            # 3. Convert boolean array to hex string
            return hashlib.md5(diff.tobytes()).hexdigest()
        except Exception as e:
            print(f"[Tamper] Hash calculation failed: {e}")
            return None

    def audit_evidence_integrity(self, image_path: str) -> Dict:
        """
        Pre-filter check for task evidence.
        Detects if this image has been used before (Fraud Replay).
        """
        p_hash = self.compute_perceptual_hash(image_path)
        if not p_hash:
            return {"status": "ERROR", "reason": "UNREADABLE_IMAGE"}

        # Check for reuse
        if p_hash in self.evidence_history_cache:
            print(f"🚨 TAMPER ALERT: Perceptual match detected for {image_path}. Probable fraud.")
            return {
                "status": "TAMPERED", 
                "reason": "REUSED_EVIDENCE_DETECTED",
                "original_seen": self.evidence_history_cache[p_hash]
            }

        # Record for future comparison
        self.evidence_history_cache[p_hash] = time.time()
        
        return {
            "status": "VALID", 
            "p_hash": p_hash,
            "msg": "Evidence unique. Proceeding to OCR validation."
        }

    def run(self):
        """Main background loop."""
        try:
            while self.is_monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        self.is_monitoring = False
        if GPIO: GPIO.cleanup()

# --- Operational Simulation ---
if __name__ == "__main__":
    listener = TamperListener()
    
    print("--- PROTOCOL EVIDENCE INTEGRITY TEST ---")
    
    # 1. Create a mock image
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.putText(dummy_img, "VALID PROOF", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.imwrite("proof_alpha.jpg", dummy_img)

    # 2. First submission (Should be VALID)
    print("[*] Node submitting first proof...")
    audit_1 = listener.audit_evidence_integrity("proof_alpha.jpg")
    print(f"    -> Result: {audit_1['status']}")

    # 3. Second submission of the same visual content (Should be TAMPERED)
    # Even if saved as a different file or resized, dHash will catch it.
    print("\n[*] Attacker submitting duplicate visual proof...")
    audit_2 = listener.audit_evidence_integrity("proof_alpha.jpg")
    print(f"    -> Result: {audit_2['status']} (Reason: {audit_2.get('reason')})")

    if audit_2['status'] == "TAMPERED":
        print("✅ FRAUD BLOCKED: Pre-broadcasting filter successful.")
