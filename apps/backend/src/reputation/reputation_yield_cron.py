import asyncio
import logging
import os
from datetime import datetime, timezone
import redis.asyncio as redis

# --- CONFIGURATION ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
YIELD_INTERVAL_SECONDS = int(os.getenv("YIELD_INTERVAL_SECONDS", 86400))  # Default 24 hours
YIELD_RECOVERY_RATE = float(os.getenv("YIELD_RECOVERY_RATE", 0.10))       # 10% asymptotic recovery
MAX_RELIABILITY = 1.0
ACTIVITY_GATE_HOURS = 72.0

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("PAN_RepYieldCron")

async def process_yield_cycle(redis_client: redis.Redis):
    """
    Iterates over all rater_reliability scores and applies an asymptotic 
    upward yield to prevent the 'Shadowban Death Spiral'.
    """
    logger.info("🔄 Starting daily reputation yield cycle...")
    
    cursor = 0
    agents_processed = 0
    agents_recovered = 0
    
    # Batch updates in a pipeline to minimize network round-trips to Redis
    pipeline = redis_client.pipeline(transaction=False)
    batch_size = 0
    
    while True:
        # SCAN for all rater_reliability keys using an async cursor
        cursor, keys = await redis_client.scan(
            cursor=cursor, 
            match="pan:entity:*:rep:rater_reliability", 
            count=500
        )
        
        for key_b in keys:
            # Decode bytes to string
            key = key_b.decode('utf-8') if isinstance(key_b, bytes) else key_b
            
            try:
                # Extract agent_id from the key schema (pan:entity:{agent_id}:rep:rater_reliability)
                parts = key.split(":")
                if len(parts) < 5:
                    continue
                    
                agent_id = parts[2]
                
                # Fetch current reliability
                raw_rel = await redis_client.get(key)
                if not raw_rel:
                    continue
                    
                current_rel = float(raw_rel)
                agents_processed += 1
                
                # Skip agents who are already at maximum trust
                if current_rel >= MAX_RELIABILITY:
                    continue
                    
                # --- ACTIVITY GATE ---
                # Check if the agent has been active in the last 72 hours.
                # (Note: Ops must ensure pan:agent:{id}:last_active is touched on mission complete/feedback)
                last_active_raw = await redis_client.get(f"pan:agent:{agent_id}:last_active")
                if last_active_raw:
                    last_active_ts = float(last_active_raw)
                    hours_since_active = (datetime.now(timezone.utc).timestamp() - last_active_ts) / 3600.0
                    
                    if hours_since_active > ACTIVITY_GATE_HOURS:
                        logger.debug(f"Agent {agent_id} dormant ({hours_since_active:.1f}h). Skipping yield.")
                        continue
                        
                # --- YIELD MATH ---
                # Asymptotic recovery: recovers faster when score is extremely low, slows down near 1.0.
                # Formula: current + ((1.0 - current) * 0.10)
                recovery_amount = (MAX_RELIABILITY - current_rel) * YIELD_RECOVERY_RATE
                new_rel = min(MAX_RELIABILITY, current_rel + recovery_amount)
                
                # Queue the update in the pipeline
                pipeline.set(key, str(new_rel))
                batch_size += 1
                agents_recovered += 1
                
                logger.debug(f"Agent {agent_id} yield: {current_rel:.3f} -> {new_rel:.3f}")
                
                # Execute in batches of 100 to avoid memory bloat
                if batch_size >= 100:
                    await pipeline.execute()
                    batch_size = 0
                    
            except Exception as e:
                logger.error(f"⚠️ Error processing yield for key {key}: {e}")
                continue
                
        # Break the while loop when SCAN completes (cursor returns to 0)
        if cursor == 0:
            break
            
    # Flush any remaining updates in the pipeline
    if batch_size > 0:
        await pipeline.execute()
        
    logger.info(f"✅ Yield cycle complete. Processed {agents_processed} agents. Recovered {agents_recovered} active scores.")

async def main():
    logger.info("🚀 Booting PAN Reputation Yield Cron Worker...")
    logger.info(f"⚙️ Target Redis: {REDIS_URL}")
    logger.info(f"⚙️ Interval: {YIELD_INTERVAL_SECONDS} seconds")
    logger.info(f"⚙️ Recovery Rate: {YIELD_RECOVERY_RATE * 100}% of gap to {MAX_RELIABILITY}")
    logger.info(f"⚙️ Activity Gate: {ACTIVITY_GATE_HOURS} hours")
    
    # Initialize the async Redis client
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    
    try:
        # Ping to verify connection before entering the main loop
        await redis_client.ping()
        logger.info("✅ Connected to Redis successfully.")
    except Exception as e:
        logger.critical(f"❌ Failed to connect to Redis. Worker crashing: {e}")
        return

    # Main worker loop
    while True:
        try:
            await process_yield_cycle(redis_client)
        except Exception as e:
            logger.error(f"❌ Unhandled exception in yield cycle: {e}", exc_info=True)
        
        # Sleep until the next 24-hour cycle
        logger.info(f"💤 Sleeping for {YIELD_INTERVAL_SECONDS} seconds...")
        await asyncio.sleep(YIELD_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        # Start the event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown signal received. Exiting yield cron cleanly.")