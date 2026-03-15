import os
import shutil
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List

# PROXY PROTOCOL - EVIDENCE PURGE UTILITY (v1.0)
# "Treating data as toxic waste."
# ----------------------------------------------------

class EvidencePurgeUtility:
    """
    Cron-compatible service that wipes evidence shards from the filesystem
    once the 24-hour legal retention window has closed.
    """
    def __init__(self, 
                 locker_path: str = "/app/data/evidence_locker/", 
                 verdict_path: str = "/app/data/verdicts/"):
        self.locker_path = locker_path
        self.verdict_path = verdict_path
        self.retention_hours = 24
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("EvidencePurge")

    def run_purge_sweep(self):
        """
        Iterates through the Evidence Locker and destroys shards for closed cases.
        """
        self.logger.info(f"[*] Starting Evidence Purge sweep (Retention: {self.retention_hours}h)...")
        
        # 1. Identify all cases currently in the locker
        if not os.path.exists(self.locker_path):
            self.logger.info("[!] Locker path not found. Nothing to purge.")
            return

        active_cases = [d for d in os.listdir(self.locker_path) if os.path.isdir(os.path.join(self.locker_path, d))]
        
        purged_count = 0
        for case_id in active_cases:
            if self._should_purge_case(case_id):
                self._execute_scorched_earth(case_id)
                purged_count += 1

        self.logger.info(f"[✓] Sweep complete. Purged {purged_count} cases.")

    def _should_purge_case(self, case_id: str) -> bool:
        """
        Checks if a case is finalized and the window has passed.
        """
        # Look for the finalized verdict manifest
        verdict_file = os.path.join(self.verdict_path, f"verdict_{case_id}.json")
        
        if not os.path.exists(verdict_file):
            # Case might still be open; skip to be safe.
            return False

        try:
            with open(verdict_file, 'r') as f:
                verdict_data = json.load(f)
                
            published_at_str = verdict_data.get('published_at')
            if not published_at_str:
                return False

            published_at = datetime.fromisoformat(published_at_str)
            cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
            
            # Return true only if the verdict is older than 24 hours
            return published_at < cutoff_time
            
        except Exception as e:
            self.logger.error(f"[!] Error parsing verdict for {case_id}: {str(e)}")
            return False

    def _execute_scorched_earth(self, case_id: str):
        """
        Irreversibly deletes the case directory.
        """
        case_dir = os.path.join(self.locker_path, case_id)
        try:
            # Overwrite directory contents before deletion if high security is required
            # shutil.rmtree is the standard implementation
            shutil.rmtree(case_dir)
            self.logger.info(f"[X] Case {case_id} shards destroyed.")
        except Exception as e:
            self.logger.error(f"[!] Failed to destroy {case_id}: {str(e)}")

# --- Production Simulation ---
if __name__ == "__main__":
    # Mocking the filesystem for demonstration
    # In a real environment, this script is run by a systemd timer.
    
    purge_tool = EvidencePurgeUtility()
    
    print("--- HIGH COURT PRIVACY ENFORCEMENT ---")
    print(f"[*] Time: {datetime.now().isoformat()}")
    
    # Run the sweep
    purge_tool.run_purge_sweep()
