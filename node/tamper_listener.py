import time
import subprocess
import signal
import sys
import os

# PROXY PROTOCOL - PHYSICAL TAMPER LISTENER (v1.0)
# "The hardware watchdog for the Scorched Earth protocol."
# ----------------------------------------------------

try:
    import RPi.GPIO as GPIO
except ImportError:
    # Fallback for development/non-Pi environments
    GPIO = None

class TamperListener:
    """
    Monitors a physical GPIO pin connected to a chassis intrusion switch.
    If the circuit is broken (chassis opened), it triggers the 
    irreversible 'tamper_response.sh' script.
    """
    
    def __init__(self, pin=26, response_script="/app/core/scripts/tamper_response.sh"):
        """
        Args:
            pin: The BCM GPIO pin number (Default 26 / Physical 37).
            response_script: Path to the 'Scorched Earth' bash execution.
        """
        self.TAMPER_PIN = pin
        self.RESPONSE_SCRIPT = response_script
        self.is_monitoring = True
        
        if GPIO is None:
            print("[!] GPIO library not detected. Running in SIMULATION MODE.")
        else:
            self._setup_gpio()

    def _setup_gpio(self):
        """
        Configures the GPIO pin with an internal pull-up resistor.
        
        CIRCUIT DESIGN:
        - Switch connects the pin to GROUND when the chassis is CLOSED (Pin = 0/LOW).
        - If the case is OPENED, the circuit breaks.
        - The Pull-Up resistor forces the pin to 3.3V (Pin = 1/HIGH).
        """
        GPIO.setmode(GPIO.BCM)
        # Pull-up forces the default state to HIGH (1)
        GPIO.setup(self.TAMPER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Detection on RISING edge (Transition from Ground to 3.3V)
        GPIO.add_event_detect(
            self.TAMPER_PIN, 
            GPIO.RISING, 
            callback=self.trigger_scorched_earth, 
            bouncetime=200 # Debounce to prevent false positives from vibration
        )
        print(f"[*] Hardware Watchdog Active: Monitoring GPIO {self.TAMPER_PIN}...")

    def trigger_scorched_earth(self, channel=None):
        """
        The point of no return. Triggers hardware wipe and process kill.
        """
        print("\n" + "!"*45)
        print("🚨 CRITICAL: PHYSICAL CHASSIS INTRUSION DETECTED!")
        print("🚨 INITIATING SCORCHED EARTH PROTOCOL...")
        print("!"*45 + "\n")
        
        # 1. Immediate local log entry
        with open("/var/log/proxy_tamper.log", "a") as f:
            f.write(f"[{time.ctime()}] INTRUSION INTERRUPT ON GPIO {self.TAMPER_PIN}\n")

        # 2. Execute the Scrubber
        # This script (previously defined in the Canvas) wipes TPM and shreds secrets.
        try:
            if os.path.exists(self.RESPONSE_SCRIPT):
                # Using Popen so the script continues to run even if this process is killed
                subprocess.Popen(["/bin/bash", self.RESPONSE_SCRIPT])
            else:
                print(f"[ERROR] Logic Failure: {self.RESPONSE_SCRIPT} not found.")
                # EMERGENCY FALLBACK: Just kill the sensitive daemon processes
                subprocess.run(["pkill", "-9", "-f", "node_daemon.py"])
        except Exception as e:
            print(f"[CRITICAL] OS-Level failure during tamper response: {e}")
            sys.exit(1)

    def run(self):
        """Main loop to keep the listener process in the background."""
        try:
            while self.is_monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        print("\n[*] Deactivating Hardware Watchdog...")
        self.is_monitoring = False
        if GPIO:
            GPIO.cleanup()

if __name__ == "__main__":
    # Check for root privileges (Required for GPIO/Wiping)
    if os.geteuid() != 0 and GPIO is not None:
        print("❌ PERMISSION DENIED: Tamper listener must run as root.")
        sys.exit(1)
        
    listener = TamperListener()
    
    # Feature for remote security testing
    if len(sys.argv) > 1 and sys.argv[1] == "--simulate-intrusion":
        listener.trigger_scorched_earth()
    else:
        listener.run()
