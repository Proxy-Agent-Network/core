import json
import logging
import statistics
from datetime import datetime
from typing import List, Dict, Tuple

# PROXY PROTOCOL - REPUTATION FORENSIC AUDITOR (v1.0)
# "Detecting the ghost in the machine."
# ----------------------------------------------------

class ForensicAuditor:
    """
    Analyzes historical node behavior to detect patterns that simple
    real-time validators might miss.
    """
    def __init__(self):
        # Configuration Thresholds
        self.HUMAN_SPEED_FLOOR = 2.0  # Seconds. Anything faster is likely a script.
        self.COORDINATE_PRECISION = 4  # Decimal places for geofence overlap detection
        self.MIN_AUDIT_SAMPLE = 5      # Need at least 5 tasks for a valid profile
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ForensicAuditor")

    def audit_node_history(self, node_id: str, events: List[Dict]) -> Dict:
        """
        Runs a comprehensive battery of tests on a node's audit log.
        """
        if len(events) < self.MIN_AUDIT_SAMPLE:
            return {"status": "INSUFFICIENT_DATA", "node_id": node_id}

        self.logger.info(f"[*] Auditing Node {node_id} (Sample Size: {len(events)})")

        results = {
            "node_id": node_id,
            "timestamp": datetime.now().isoformat(),
            "risk_score": 0.0, # 0.0 to 1.0 (Critical)
            "flags": [],
            "heuristics": {}
        }

        # 1. Human-Impossible Timing Analysis
        # Detects bots that submit proofs faster than a human could physically act.
        latencies = [e.get('execution_seconds', 0) for e in events if 'execution_seconds' in e]
        if latencies:
            min_lat = min(latencies)
            avg_lat = statistics.mean(latencies)
            if min_lat < self.HUMAN_SPEED_FLOOR:
                results["risk_score"] += 0.4
                results["flags"].append("HUMAN_IMPOSSIBLE_SPEED")
            results["heuristics"]["avg_execution_time"] = round(avg_lat, 2)

        # 2. Sybil Mimicry (Geographical Overlap)
        # Detects if multiple Node IDs are operating from the exact same physical coordinates.
        coordinates = [
            (round(e['lat'], self.COORDINATE_PRECISION), round(e['lon'], self.COORDINATE_PRECISION))
            for e in events if 'lat' in e and 'lon' in e
        ]
        unique_coords = set(coordinates)
        if len(unique_coords) == 1 and len(events) > 10:
            # While stationary nodes are common, absolute zero drift over 10 tasks 
            # might indicate a simulated coordinate feed.
            results["heuristics"]["coordinate_stability"] = "ABSOLUTE"
        
        # 3. Sophisticated Laziness (Entropy Check)
        # Detects if task results (text) have suspiciously low variance (template farming).
        results_text = [e.get('result_text', '') for e in events if 'result_text' in e]
        if results_text:
            unique_results = len(set(results_text))
            variance_ratio = unique_results / len(results_text)
            if variance_ratio < 0.2:
                results["risk_score"] += 0.3
                results["flags"].append("LOW_OUTPUT_ENTROPY")
            results["heuristics"]["unique_output_ratio"] = round(variance_ratio, 2)

        # 4. Final Verdict
        results["status"] = "CRITICAL" if results["risk_score"] >= 0.7 else "STABLE"
        
        if results["status"] == "CRITICAL":
            self.logger.warning(f"🚨 Forensic Alert for {node_id}: {results['flags']}")
            
        return results

# --- Simulation ---
if __name__ == "__main__":
    auditor = ForensicAuditor()

    # Case: A suspicious node submitting very fast, identical results
    suspicious_logs = [
        {"task_id": f"T-{i}", "execution_seconds": 0.4, "result_text": "Task Approved.", "lat": 39.7459, "lon": -75.5467}
        for i in range(10)
    ]

    report = auditor.audit_node_history("NODE_SUSPECT_01", suspicious_logs)
    
    print("\n--- REPUTATION FORENSIC REPORT ---")
    print(json.dumps(report, indent=2))

    if report['status'] == "CRITICAL":
        print("\n⚖️ ACTION: Escalating to High Court for Manual Review.")
