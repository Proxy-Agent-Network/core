import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
# 🛠️ THE FIX: Commented out the legacy Flask middleware
# from fastapi.middleware.wsgi import WSGIMiddleware
import redis.asyncio as redis

# 1. Import our newly hardened async routers
from api.v2x_bounty_api import router as v2x_router
from api.telemetry_socket import router as telemetry_router # 🛠️ THE FIX: Wired up the WebSocket!
from ops.logistics_webhook_api import router as logistics_router

# 2. Import the legacy Flask monolith
# 🛠️ THE FIX: Commented out the missing Flask app import
# from app import app as flask_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Panopticon_Master")

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Initiating Panopticon Boot Sequence...")
    
    # 🛠️ THE FIX: Explicit environment requirement, no silent fallbacks.
    redis_host = os.environ.get("REDIS_HOST")
    if not redis_host:
        raise RuntimeError("FATAL: REDIS_HOST environment variable is not set.")
        
    app.state.redis_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    
    try:
        await app.state.redis_client.ping()
        logger.info(f"🔌 Redis connection verified at {redis_host}")
    except redis.ConnectionError as e:
        logger.critical(f"🛑 FATAL: Cannot connect to Redis at {redis_host}: {e}")
        raise RuntimeError(f"Redis initialization failed: {e}")

    yield # --- SYSTEM IS LIVE ---
    
    # --- SHUTDOWN SEQUENCE ---
    logger.info("🛑 Initiating Graceful Shutdown...")
    await app.state.redis_client.aclose()


# --- CORE FASTAPI APPLICATION ---
app = FastAPI(
    title="Proxy Agent Network (PAN) - Sector 1 Engine",
    description="The Last-Mile Physical Redundancy Protocol for Autonomous Fleets.",
    version="2.0.0",
    lifespan=lifespan
)

# --- MOUNT ASYNC ROUTERS (V2 Architecture) ---
app.include_router(v2x_router, prefix="/api")
app.include_router(telemetry_router, prefix="/api") # 🛠️ THE FIX: Mounted the WebSocket router
app.include_router(logistics_router, prefix="/logistics") 

# --- MOUNT LEGACY FLASK APP (The Strangler Fig) ---
# 🛑 WARNING: Do not move this! The Flask catch-all WSGI middleware MUST be mounted 
# LAST. If placed above the FastAPI routers, it will intercept and swallow all traffic.

# 🛠️ THE FIX: Commented out the Flask mount command
# logger.info("🔗 Wrapping legacy Flask monolith in WSGI Middleware...")
# app.mount("/", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)