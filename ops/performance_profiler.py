import time
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

# PROXY PROTOCOL - PERFORMANCE PROFILER (v1.0)
# "Optimizing network throughput through high-fidelity telemetry."
# ----------------------------------------------------

@dataclass
class ExecutionMetric:
    task_id: str
    node_id: str
    region: str
    latency_sec: float
    timestamp: float

class PerformanceProfiler:
    """
    Analyzes systemic task performance to drive market pricing
    and identify regional routing bottlenecks.
    """
    def __init__(self):
        # Configuration
        self.WINDOW_SIZE_SEC = 3600  # 1-hour sliding window for TPS
        self.MAX_SAMPLES = 5000      # Cap in-memory history
        
        # In-memory history
        self.history: List[ExecutionMetric] = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("PerfProfiler")

    def record_execution(self, task_id: str, node_id: str, region: str, duration: float):
        """
        Ingests a completed task metric.
        """
        metric = ExecutionMetric(
            task_id=task_id,
            node_id=node_id,
            region=region,
            latency_sec=duration,
            timestamp=time.time()
        )
        
        self.history.append(metric)
        
        # Maintain window and sample cap
        self._prune_history()
        
        if len(self.history) % 100 == 0:
            self.logger.info(f"[*] Aggregated {len(self.history)} performance samples.")

    def _prune_history(self):
        """Removes metrics older than the sliding window."""
        cutoff = time.time() - self.WINDOW_SIZE_SEC
        self.history = [m for m in self.history if m.timestamp > cutoff]
        if len(self.history) > self.MAX_SAMPLES:
            self.history = self.history[-self.MAX_SAMPLES:]

    def calculate_systemic_vitals(self) -> Dict:
        """
        Computes TPS and latency percentiles.
        """
        if not self.history:
            return {"tps": 0.0, "p50_ms": 0, "p99_ms": 0}

        # 1. Transactions Per Second (TPS)
        # Count tasks in the last 60 seconds
        now = time.time()
        recent_count = len([m for m in self.history if m.timestamp > (now - 60)])
        tps = round(recent_count / 60.0, 2)

        # 2. Latency Percentiles (ms)
        latencies = [m.latency_sec * 1000 for m in self.history]
        p50 = int(statistics.median(latencies))
        
        # P99 Calculation
        sorted_lats = sorted(latencies)
        idx_p99 = int(len(sorted_lats) * 0.99)
        p99 = int(sorted_lats[min(idx_p99, len(sorted_lats)-1)])

        return {
            "tps": tps,
            "p50_ms": p50,
            "p99_ms": p99,
            "sample_count": len(self.history)
        }

    def get_congestion_multiplier(self) -> float:
        """
        Dynamic multiplier logic based on latency drift.
        Standard P50 baseline for Tier 1: 300ms (Network overhead only).
        """
        vitals = self.calculate_systemic_vitals()
        p50 = vitals["p50_ms"]
        
        # Base logic: If P50 latency exceeds 1s, start scaling price
        if p50 <= 500:
            return 1.0
        
        # Exponential scale: 1.0 + ((Latency - 500) / 1000)^2
        # Example: 1500ms P50 -> 1.0 + (1000/1000)^2 = 2.0x Multiplier
        drift = (p50 - 500) / 1000
        multiplier = 1.0 + (drift ** 2)
        
        return round(min(multiplier, 5.0), 2) # Cap at 5x for latency-based surge

    def generate_regional_report(self) -> Dict[str, Dict]:
        """
        Identifies which regional hubs are under-performing.
        """
        regional_stats = {}
        for m in self.history:
            if m.region not in regional_stats:
                regional_stats[m.region] = []
            regional_stats[m.region].append(m.latency_sec * 1000)

        report = {}
        for region, lats in regional_stats.items():
            avg = statistics.mean(lats)
            report[region] = {
                "avg_ms": int(avg),
                "load_factor": "HIGH" if avg > 1000 else "NORMAL"
            }
            
        return report

# --- Operational Simulation ---
if __name__ == "__main__":
    profiler = PerformanceProfiler()
    
    print("--- PROTOCOL PERFORMANCE AUDIT ---")
    
    # 1. Simulate Normal Traffic
    print("[*] Simulating 500 nominal task completions...")
    for i in range(500):
        # Average 250ms duration (excluding physical execution)
        profiler.record_execution(f"T-{i}", "NODE_X", "US_EAST", 0.25 + (i % 10 / 100))

    vitals = profiler.calculate_systemic_vitals()
    print(f"    -> System TPS: {vitals['tps']}")
    print(f"    -> P50 Latency: {vitals['p50_ms']}ms")
    print(f"    -> Multiplier: {profiler.get_congestion_multiplier()}x")

    # 2. Simulate Latency Spike (Saturation)
    print("\n[!] Simulating network saturation spike...")
    for i in range(100):
        # Latency jumps to 1.8 seconds
        profiler.record_execution(f"T-SPIKE-{i}", "NODE_Y", "ASIA_SE", 1.8)

    new_vitals = profiler.calculate_systemic_vitals()
    multiplier = profiler.get_congestion_multiplier()
    
    print(f"    -> New P50:    {new_vitals['p50_ms']}ms")
    print(f"    -> New Surge:  {multiplier}x")
    
    # 3. Regional Breakdown
    print("\n[*] Regional Impact Analysis:")
    print(json.dumps(profiler.generate_regional_report(), indent=2))
