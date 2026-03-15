import logging
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# PROXY PROTOCOL - REGIONAL TRAFFIC CONTROLLER (v1.0)
# "Ensuring 99% SLA availability via automated path failover."
# ----------------------------------------------------

class RegionalTrafficController:
    """
    Monitors regional hub latency and dynamically adjusts task distribution 
    to bypass degraded infrastructure.
    """
    def __init__(self):
        # Configuration Thresholds
        self.LATENCY_DEGRADED_THRESHOLD_MS = 1000  # P50 > 1s = Degraded
        self.LATENCY_CRITICAL_THRESHOLD_MS = 2500  # P50 > 2.5s = Critical/Shutdown
        
        # Routing Weights (Defaults)
        self.hub_states: Dict[str, Dict] = {
            "US_EAST": {"status": "OPTIMAL", "weight": 1.0, "latency": 20},
            "US_WEST": {"status": "OPTIMAL", "weight": 1.0, "latency": 80},
            "EU_WEST": {"status": "OPTIMAL", "weight": 1.0, "latency": 140},
            "ASIA_SE": {"status": "OPTIMAL", "weight": 1.0, "latency": 260}
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TrafficController")

    def update_hub_telemetry(self, performance_report: Dict[str, Dict]):
        """
        Ingests data from core/ops/performance_profiler.py.
        Analyzes P50 drift and updates regional health states.
        """
        self.logger.info("[*] Syncing regional hub telemetry...")
        
        for hub_id, stats in performance_report.items():
            if hub_id not in self.hub_states:
                continue

            p50 = stats.get("avg_ms", 0)
            self.hub_states[hub_id]["latency"] = p50

            # 1. Evaluate State
            if p50 >= self.LATENCY_CRITICAL_THRESHOLD_MS:
                self.hub_states[hub_id]["status"] = "CRITICAL"
                self.hub_states[hub_id]["weight"] = 0.0  # Full Traffic Drain
                self.logger.error(f"🚨 HUB {hub_id} CRITICAL: Draining all traffic (Latency: {p50}ms)")
            elif p50 >= self.LATENCY_DEGRADED_THRESHOLD_MS:
                self.hub_states[hub_id]["status"] = "DEGRADED"
                self.hub_states[hub_id]["weight"] = 0.2  # 80% Traffic Reduction
                self.logger.warning(f"⚠️ HUB {hub_id} DEGRADED: Reducing traffic load (Latency: {p50}ms)")
            else:
                self.hub_states[hub_id]["status"] = "OPTIMAL"
                self.hub_states[hub_id]["weight"] = 1.0
                
        self._log_routing_table()

    def get_optimized_route(self, preferred_hub: str) -> str:
        """
        Given an Agent's preferred hub, return the best available hub.
        Implements the 'Next-Best-Path' failover logic.
        """
        # If preferred hub is healthy, use it
        if self.hub_states.get(preferred_hub, {}).get("status") == "OPTIMAL":
            return preferred_hub
        
        # Failover logic: Find the lowest latency hub that is currently OPTIMAL
        optimal_hubs = [
            (h_id, h["latency"]) for h_id, h in self.hub_states.items() 
            if h["status"] == "OPTIMAL"
        ]
        
        if not optimal_hubs:
            self.logger.critical("🚨 SYSTEMIC BROWNOUT: No hubs reporting OPTIMAL status.")
            return preferred_hub # Fallback to original; better than nothing

        # Sort by latency and return the fastest available hub
        optimal_hubs.sort(key=lambda x: x[1])
        failover_hub = optimal_hubs[0][0]
        
        self.logger.info(f"[*] FAILOVER: Rerouting {preferred_hub} -> {failover_hub}")
        return failover_hub

    def _log_routing_table(self):
        """Internal diagnostic print."""
        table = []
        for hub, data in self.hub_states.items():
            table.append(f"{hub}: {data['status']} ({data['weight']}x)")
        self.logger.info(f"[*] Active Routing Table: {' | '.join(table)}")

# --- Operational Simulation ---
if __name__ == "__main__":
    controller = RegionalTrafficController()
    
    print("--- PROTOCOL REGIONAL TRAFFIC SIMULATION ---")
    
    # 1. Scenario: Standard healthy state
    print("[*] State: Normal operations.")
    controller._log_routing_table()

    # 2. Scenario: Asia-SG Latency Spike (from PerformanceProfiler data)
    print("\n[!] Event: Asia-SG hub suffering congestion spike...")
    mock_report = {
        "ASIA_SE": {"avg_ms": 1240, "load_factor": "HIGH"},
        "EU_WEST": {"avg_ms": 142, "load_factor": "NORMAL"},
        "US_EAST": {"avg_ms": 18, "load_factor": "NORMAL"},
        "US_WEST": {"avg_ms": 84, "load_factor": "NORMAL"}
    }
    
    controller.update_hub_telemetry(mock_report)

    # 3. Scenario: Agent attempts to route via Asia-SG
    print("\n[?] Request: Agent targeting Asia-SG hub...")
    final_hub = controller.get_optimized_route("ASIA_SE")
    print(f"    -> Result: Rerouted to {final_hub} for SLA preservation.")

    # 4. Scenario: ASIA-SG recovery
    print("\n[*] Event: Asia-SG hub latency normalized.")
    recovery_report = {
        "ASIA_SE": {"avg_ms": 260, "load_factor": "NORMAL"}
    }
    controller.update_hub_telemetry(recovery_report)
