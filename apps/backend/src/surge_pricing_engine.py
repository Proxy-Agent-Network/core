import asyncio
import logging

logger = logging.getLogger("PAN_SurgeEngine")

# ---------------------------------------------------------------------------
# PROXY PROTOCOL - DYNAMIC SURGE PRICING ENGINE
# "Automated SLA preservation via L402 HODL Repricing."
# 
# Triggers when Agent Utilization Ratio (AUR) > 85% or queue depth is high.
# Max Cap: 3.0x.
# 
# PAN Operational Status Matrix (OSM) - Standard Visual Identifiers:
# Tier 3 (Critical): RED (Bio/Foreign Object), PURPLE (Defleeting)
# Tier 2 (Elevated): YELLOW (Tech/Sensors), ORANGE (Calibrations)
# Tier 1 (Standard): GREEN (Power Down & Rest), BLUE (Validation), WHITE (Demo)
# ---------------------------------------------------------------------------

def decode_redis_hash(raw_hash: dict) -> dict:
    """Safely decodes Redis byte hashes into strings."""
    if not raw_hash:
        return {}
    return {
        k.decode('utf-8') if isinstance(k, bytes) else k: 
        v.decode('utf-8') if isinstance(v, bytes) else v 
        for k, v in raw_hash.items()
    }

class SurgePricingEngine:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.MAX_MULTIPLIER = 3.0
        self.TARGET_UTILIZATION = 0.75 # 75% load is nominal
        
        # OSM Tier Pricing Matrix
        self.OSM_TIER_PRICING = {
            "RED": 65.00,    # Tier 3: Bio/Foreign Object
            "PURPLE": 65.00, # Tier 3: Defleeting
            "YELLOW": 45.00, # Tier 2: Tech Fault / Sensor Occlusion
            "ORANGE": 45.00, # Tier 2: Calibrations
            "GREEN": 14.00,  # Tier 1: Power Down & Rest (PDR)
            "BLUE": 14.00,   # Tier 1: Validation
            "WHITE": 14.00   # Tier 1: Demo Vehicle
        }

    async def _calculate_network_utilization(self) -> float:
        """
        Calculates the Agent Utilization Ratio (AUR).
        AUR = (Active Missions + Pending Tasks) / Total Online Agents
        """
        try:
            # 1. Count Total Online Agents
            cursor = 0
            online_agents = 0
            while True:
                cursor, keys = await self.redis.scan(cursor=cursor, match="agent:*", count=100)
                for key in keys:
                    status = await self.redis.hget(key, "status")
                    if status and status.decode('utf-8') in ["ONLINE", "EN_ROUTE"]:
                        online_agents += 1
                if cursor == 0:
                    break

            if online_agents == 0:
                return 2.0 # Infinite demand. Force max surge if no one is online.

            # 2. Count Active Missions (Agents currently executing ORP)
            cursor = 0
            mission_count = 0
            while True:
                cursor, keys = await self.redis.scan(cursor=cursor, match="mission:active:*", count=100)
                mission_count += len(keys) # 🟢 THE FIX: Count the actual keys, not the scan batches
                if cursor == 0: break
                
            # 3. Count Pending Queue Depth
            queue_depth = await self.redis.llen("pan:dispatch:active_tasks")
            
            total_demand = mission_count + queue_depth
            
            return total_demand / online_agents
            
        except Exception as e:
            logger.error(f"⚠️ [SURGE_ENGINE] Failed to calculate utilization: {e}")
            return 0.0

    def _calculate_multiplier(self, aur: float) -> float:
        """
        Executes the exponential repricing formula:
        Multiplier = 1.0 + Max(0, (AUR - 0.75) * 10)
        Capped at MAX_MULTIPLIER (3.0x).
        """
        if aur <= self.TARGET_UTILIZATION:
            return 1.0
            
        surge = 1.0 + max(0.0, (aur - self.TARGET_UTILIZATION) * 10.0)
        return min(round(surge, 2), self.MAX_MULTIPLIER)

    async def _reprice_pending_tasks(self, new_multiplier: float):
        """
        Iterates through the active dispatch queue and aggressively updates 
        the bounty_usd field for tasks waiting for an agent.
        """
        queue_len = await self.redis.llen("pan:dispatch:active_tasks")
        if queue_len == 0 or new_multiplier <= 1.0:
            return

        tasks = await self.redis.lrange("pan:dispatch:active_tasks", 0, -1)
        
        for task_bytes in tasks:
            # 🟢 THE FIX: Standardized string decoding for keys and values
            task_id = task_bytes.decode('utf-8') if isinstance(task_bytes, bytes) else task_bytes
            
            raw_task_data = await self.redis.hgetall(f"pan:task:{task_id}")
            if not raw_task_data: continue
            
            task_data = decode_redis_hash(raw_task_data)
            
            osm_color = task_data.get("osm_color", "GREEN").upper()
            
            # Fetch the true base price (either explicitly set by the API, or derived from the OSM taxonomy)
            base_bounty_usd = float(task_data.get("base_bounty_usd", self.OSM_TIER_PRICING.get(osm_color, 14.00)))
            current_bounty = float(task_data.get("bounty_usd", base_bounty_usd))
            
            # Apply the dynamic surge multiplier against the *original base* bounty
            target_bounty = round(base_bounty_usd * new_multiplier, 2)
            
            # Only increment, never decrease a bounty that has already surged
            if target_bounty > current_bounty:
                await self.redis.hset(f"pan:task:{task_id}", "bounty_usd", target_bounty)
                logger.info(f"💸 [SURGE_ENGINE] Repriced {task_id} [{osm_color}] to ${target_bounty:.2f} ({new_multiplier}x multiplier on ${base_bounty_usd:.2f} base)")

    async def run_loop(self):
        """
        The continuous 5-second monitoring daemon.
        """
        logger.info("📈 [SURGE_ENGINE] Dynamic Pricing Daemon Online...")
        
        while True:
            try:
                # 1. Calculate Network State
                aur = await self._calculate_network_utilization()
                
                # 2. Determine Multiplier
                multiplier = self._calculate_multiplier(aur)
                
                if multiplier > 1.0:
                    logger.warning(f"🚨 [SURGE_ENGINE] NETWORK SURGE ACTIVE | AUR: {aur*100:.1f}% | Multiplier: {multiplier}x")
                    
                    # 3. Apply Surge to active queue
                    await self._reprice_pending_tasks(multiplier)
                
            except asyncio.CancelledError:
                logger.info("🛑 [SURGE_ENGINE] Shutting down gracefully.")
                raise
            except Exception as e:
                logger.error(f"⚠️ [SURGE_ENGINE] Fatal error in loop: {e}")
                
            # Sleep for 5 seconds before recalculating
            await asyncio.sleep(5.0)

# --- Standalone Execution ---
async def main():
    import redis.asyncio as redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    engine = SurgePricingEngine(redis_client)
    await engine.run_loop()

if __name__ == "__main__":
    asyncio.run(main())