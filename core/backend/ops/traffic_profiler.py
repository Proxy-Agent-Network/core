import time
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from datetime import datetime

# PROXY PROTOCOL - TRAFFIC PROFILER API (v1.0)
# "Identifying hotspots to optimize Proxy Sentry deployment."
# ----------------------------------------------------

@dataclass
class TaskIntentPacket:
    task_id: str
    target_region: str
    lat: float
    lon: float
    timestamp: float
    bid_sats: int

class TrafficProfiler:
    """
    Analyzes spatial distribution of task intents to identify 
    unmet demand and suggest infrastructure scaling.
    """
    def __init__(self):
        self.WINDOW_SIZE_SEC = 86400  # 24-hour analysis window
        self.SCALING_THRESHOLD = 5000 # Tasks per day in a 10km radius triggers scaling
        
        # In-memory history stores
        # Format: { "region_code": [TaskIntentPacket] }
        self.intent_history: Dict[str, List[TaskIntentPacket]] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TrafficProfiler")

    def record_intent(self, task_id: str, region: str, lat: float, lon: float, bid: int):
        """
        Ingests a new task intent for hotspot analysis.
        This represents an Agent looking for a Human, regardless of whether a match occurred.
        """
        packet = TaskIntentPacket(
            task_id=task_id,
            target_region=region,
            lat=lat,
            lon=lon,
            timestamp=time.time(),
            bid_sats=bid
        )
        
        if region not in self.intent_history:
            self.intent_history[region] = []
            
        self.intent_history[region].append(packet)
        self._prune_history(region)

    def _prune_history(self, region: str):
        """Removes data older than the sliding window to prevent memory bloat."""
        cutoff = time.time() - self.WINDOW_SIZE_SEC
        self.intent_history[region] = [p for p in self.intent_history[region] if p.timestamp > cutoff]
        if not self.intent_history[region]:
            del self.intent_history[region]

    def identify_hotspots(self) -> List[Dict]:
        """
        Groups intents geographically to find high-density pockets.
        Detects where the "Network Pull" is strongest.
        """
        hotspots = []
        for region, packets in self.intent_history.items():
            if len(packets) < 10: continue # Ignore low-traffic outliers
            
            # Calculate metrics for the region
            total_volume = len(packets)
            avg_bid = statistics.mean([p.bid_sats for p in packets])
            
            # Regional density check
            if total_volume > 100: 
                hotspots.append({
                    "region": region,
                    "intent_count": total_volume,
                    "avg_bid_sats": int(avg_bid),
                    "density_rating": "CRITICAL" if total_volume > 1000 else "ELEVATED",
                    "status": "SCALING_RECOMMENDED" if total_volume > (self.SCALING_THRESHOLD / 10) else "STABLE"
                })
                
        return sorted(hotspots, key=lambda x: x['intent_count'], reverse=True)

    def generate_sentry_recommendation(self) -> Dict:
        """
        Specific output for the Proxy Foundation to prioritize hardware production and shipments.
        """
        hotspots = self.identify_hotspots()
        if not hotspots:
            return {"recommendation": "Fleet Static", "priority": "LOW", "msg": "Current capacity meets demand."}

        primary = hotspots[0]
        return {
            "primary_target": primary['region'],
            "intent_saturation": f"{primary['intent_count']} packets/24h",
            "priority": "HIGH" if primary['density_rating'] == "CRITICAL" else "MEDIUM",
            "recommended_action": f"Provision 5+ Proxy Sentry (Tier 2) units to {primary['region']} region immediately."
        }

# --- Operational Simulation ---
if __name__ == "__main__":
    profiler = TrafficProfiler()
    
    print("--- PROTOCOL TRAFFIC HOTSPOT AUDIT ---")
    
    # 1. Simulate Standard baseline traffic
    regions = ["US_EAST", "EU_WEST", "US_WEST"]
    for r in regions:
        for i in range(50):
            profiler.record_intent(f"T-{r}-{i}", r, 40.0, -70.0, 1500)

    # 2. Simulate a Massive Surge in a specific jurisdiction (Tokyo, Japan)
    # This represents a new enterprise agent launching in Asia
    print("[*] Simulating viral task surge in Tokyo (JP_EAST)...")
    for i in range(800):
        profiler.record_intent(f"T-JP-{i}", "JP_EAST", 35.6, 139.6, 2500)

    # 3. Analyze Hotspots
    spots = profiler.identify_hotspots()
    for spot in spots:
        print(f"\n[Region: {spot['region']}]")
        print(f"    -> Intent Count: {spot['intent_count']}")
        print(f"    -> Avg Bid:      {spot['avg_bid_sats']} sats")
        print(f"    -> Rating:       {spot['density_rating']}")

    # 4. Get Hardware Scaling Recommendation
    rec = profiler.generate_sentry_recommendation()
    print("\n--- INFRASTRUCTURE SCALING RECOMMENDATION ---")
    print(f"Target Cluster: {rec['primary_target']}")
    print(f"Action:         {rec['recommended_action']}")
    print(f"Priority Level: {rec['priority']}")
