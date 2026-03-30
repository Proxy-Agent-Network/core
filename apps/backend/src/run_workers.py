import asyncio
import logging
import os
import sys
import redis.asyncio as redis

# Setup central logging for the supervisor
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PAN_Supervisor")

# ---------------------------------------------------------------------------
# WORKER IMPORTS
# ---------------------------------------------------------------------------
from matching_engine import run_matching_engine
from core.economics.surge_pricing_engine import SurgePricingEngine

# Note: Depending on how watchdog_worker.py is currently structured, 
# you may need to wrap its main loop in an async def run_watchdog(redis_client):
try:
    from watchdog_worker import run_watchdog
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("⚠️ Could not import run_watchdog from watchdog_worker.py.")
    logger.warning("Ensure it exposes an async function to be managed by the supervisor.")

# ---------------------------------------------------------------------------
# SUPERVISOR DAEMON
# ---------------------------------------------------------------------------
async def main():
    logger.info("🚀 PAN Tactical Worker Supervisor Starting...")
    
    # 1. Initialize Shared Redis Connection Pool
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    try:
        redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
        await redis_client.ping()
        logger.info(f"✅ Connected to Redis at {redis_host}:{redis_port}")
    except Exception as e:
        logger.critical(f"🛑 FATAL: Failed to connect to Redis: {e}")
        sys.exit(1)

    # 2. Initialize Engine Classes
    surge_engine = SurgePricingEngine(redis_client)

    # 3. Create Concurrent Tasks
    logger.info("⚙️ Dispatching background workers...")
    tasks = [
        asyncio.create_task(run_matching_engine(redis_client), name="MatchingEngine"),
        asyncio.create_task(surge_engine.run_loop(), name="SurgeEngine")
    ]
    
    if WATCHDOG_AVAILABLE:
        tasks.append(asyncio.create_task(run_watchdog(redis_client), name="SLAWatchdog"))

    logger.info(f"✅ Successfully launched {len(tasks)} background daemons.")

    # 4. Await and supervise (these run infinitely unless there's a fatal crash)
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("🛑 Supervisor received shutdown signal. Cancelling workers...")
        for task in tasks:
            task.cancel()
        
        # Wait for tasks to gracefully exit
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("🛑 All workers shut down gracefully.")
    except Exception as e:
        logger.critical(f"🛑 FATAL: A worker crashed the supervisor loop: {e}", exc_info=True)
    finally:
        await redis_client.aclose()

if __name__ == "__main__":
    try:
        # Run the asyncio event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Supervisor killed by user (SIGINT).")