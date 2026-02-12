import asyncio
import logging
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# PROXY PROTOCOL - ANOMALY DETECTION ENGINE (v1.0)
# "Defending against coordinated Sybil clusters."
# ----------------------------------------------------

class AnomalyDetectionEngine:
    """
    Analyzes live telemetry and task outcomes to identify non-random 
    failure spikes (Sybil Pulsing) that indicate coordinated sabotage.
    """
    def __init__(self):
        # Configuration Thresholds
        self.WINDOW_SIZE_SEC = 300       # 5-minute analysis window
        self.CLUSTER_FAILURE_THRESHOLD = 0.25 # 25% failure in a cluster is an anomaly
        self.IP_PREFIX_MATCH = 24        # Group by /24 subnet (standard ISP grouping)
        
        # In-memory history stores
        # Format: { "node_id": [{"timestamp": float, "outcome": bool, "ip": str}] }
        self.event_window: Dict[str, List[Dict]] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("AnomalyDetection")

    def record_task_outcome(self, node_id: str, success: bool, metadata: Dict):
        """
        Ingests a task result for windowed analysis.
        metadata: {"ip": "1.2.3.4", "region": "US_EAST"}
        """
        now = time.time()
        if node_id not in self.event_window:
            self.event_window[node_id] = []
            
        self.event_window[node_id].append({
            "timestamp": now,
            "outcome": success,
            "ip": metadata.get("ip", "0.0.0.0"),
            "region": metadata.get("region", "UNKNOWN")
        })
        
        self._prune_window(now)

    def _prune_window(self, current_time: float):
        """Removes events older than the WINDOW_SIZE."""
        cutoff = current_time - self.WINDOW_SIZE_SEC
        for node_id in list(self.event_window.keys()):
            self.event_window[node_id] = [
                e for e in self.event_window[node_id] if e['timestamp'] > cutoff
            ]
            if not self.event_window[node_id]:
                del self.event_window[node_id]

    def analyze_sybil_clusters(self) -> List[Dict]:
        """
        Groups nodes by subnet and region to identify coordinated failure pulses.
        """
        subnets: Dict[str, Dict] = {}
        
        for node_id, events in self.event_window.items():
            for e in events:
                # Grouping by first 3 octets (/24)
                prefix = ".".join(e['ip'].split(".")[:3])
                if prefix not in subnets:
                    subnets[prefix] = {"total": 0, "failures": 0, "nodes": set()}
                
                subnets[prefix]["total"] += 1
                subnets[prefix]["nodes"].add(node_id)
                if not e['outcome']:
                    subnets[prefix]["failures"] += 1

        anomalies = []
        for prefix, stats in subnets.items():
            failure_rate = stats["failures"] / stats["total"] if stats["total"] > 0 else 0
            
            # Logic: If multiple nodes in the same subnet fail at high rates simultaneously
            if len(stats["nodes"]) > 3 and failure_rate >= self.CLUSTER_FAILURE_THRESHOLD:
                anomaly_report = {
                    "type": "SYBIL_PULSING_DETECTED",
                    "subnet": f"{prefix}.0/24",
                    "node_count": len(stats["nodes"]),
                    "failure_rate": f"{failure_rate:.1%}",
                    "severity": "CRITICAL" if failure_rate > 0.5 else "ELEVATED",
                    "timestamp": datetime.now().isoformat()
                }
                anomalies.append(anomaly_report)
                self.logger.warning(f"🚨 ANOMALY: Subnet {prefix} is pulsing! Fail Rate: {failure_rate:.1%}")

        return anomalies

    async def detect_pcr_drift_correlation(self, drift_events: List[Dict]) -> bool:
        """
        Correlates hardware attestation failures with task outcomes.
        Returns True if a coordinated firmware exploit is suspected.
        """
        # If > 5 unique nodes report PCR drift within 1 minute, it's a systemic SEV-1
        unique_nodes = set([d['node_id'] for d in drift_events])
        if len(unique_nodes) >= 5:
            self.logger.critical("🚨 SYSTEMIC PCR DRIFT DETECTED. COHORT COMPROMISE SUSPECTED.")
            return True
        return False

# --- Master Orchestrator Integration Simulation ---
async def main():
    detector = AnomalyDetectionEngine()
    
    print("--- PROTOCOL ANOMALY DETECTION TEST ---")
    
    # 1. Simulate a Sybil Cluster on Subnet 192.168.42.X
    print("[*] Simulating coordinated task failures on subnet 192.168.42.0/24...")
    for i in range(10):
        node_id = f"NODE_SUSPECT_{i}"
        # Coordinated failure
        detector.record_task_outcome(node_id, success=False, metadata={"ip": f"192.168.42.{10+i}"})

    # 2. Simulate honest traffic elsewhere
    for i in range(20):
        detector.record_task_outcome(f"NODE_HONEST_{i}", success=True, metadata={"ip": f"10.0.1.{i}"})

    # 3. Run Analysis
    reports = detector.analyze_sybil_clusters()
    
    if reports:
        print("\n[!] DETECTED ANOMALIES:")
        for r in reports:
            print(f"    - {r['type']} | Cluster: {r['subnet']} | Fail Rate: {r['failure_rate']}")
    else:
        print("\n✅ Network state stable.")

if __name__ == "__main__":
    asyncio.run(main())
