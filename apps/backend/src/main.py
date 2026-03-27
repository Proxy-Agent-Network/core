import os
import secrets
from dotenv import load_dotenv

load_dotenv()

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import redis.asyncio as redis

# 1. Import our newly hardened async routers
from api.wallet_api import router as wallet_router
from api.v2x_bounty_api import router as v2x_router
from api.telemetry_socket import router as telemetry_router
from ops.logistics_webhook_api import router as logistics_router
from api.onboarding_api import router as onboarding_router

# 🛠️ NEW: Import the background workers
from matching_engine import run_matching_engine
from ops.sla_monitor import run_sla_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Panopticon_Master")

# --- LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Initiating Panopticon Boot Sequence...")
    
    redis_host = os.environ.get("REDIS_HOST")
    if not redis_host:
        raise RuntimeError("FATAL: REDIS_HOST environment variable is not set.")
    
    redis_port = int(os.environ.get("REDIS_PORT", 6379))
        
    app.state.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    
    try:
        await app.state.redis_client.ping()
        logger.info(f"🔌 Redis connection verified at {redis_host}:{redis_port}")
    except redis.ConnectionError as e:
        logger.critical(f"🛑 FATAL: Cannot connect to Redis at {redis_host}:{redis_port}: {e}")
        raise RuntimeError(f"Redis initialization failed: {e}")

    engine_task = asyncio.create_task(
        run_matching_engine(app.state.redis_client),
        name="matching_engine"
    )
    app.state.matching_engine_task = engine_task

    # 🟢 NEW: Spin up the 12-Minute SLA Enforcer
    sla_task = asyncio.create_task(
        run_sla_monitor(app.state.redis_client),
        name="sla_monitor"
    )
    app.state.sla_monitor_task = sla_task

    yield # --- SYSTEM IS LIVE ---
    
    # --- SHUTDOWN SEQUENCE ---
    logger.info("🛑 Initiating Graceful Shutdown...")
    
    # Clean up the workers on shutdown
    engine_task.cancel()
    sla_task.cancel()
    await asyncio.gather(engine_task, sla_task, return_exceptions=True)
    
    await app.state.redis_client.aclose()


# --- CORE FASTAPI APPLICATION ---
app = FastAPI(
    title="Proxy Agent Network (PAN) - Sector 1 Engine",
    description="The Last-Mile Physical Redundancy Protocol for Autonomous Fleets.",
    version="2.0.0",
    lifespan=lifespan
)

# --- MOUNT ASYNC ROUTERS (V2 Architecture) ---
# Note: Onboarding router is mounted with /api/v1 to match the V2X/Wallet patterns.
app.include_router(v2x_router, prefix="/api")
app.include_router(telemetry_router, prefix="/api") 
app.include_router(wallet_router, prefix="/api")
app.include_router(logistics_router, prefix="/logistics")
app.include_router(onboarding_router, prefix="/api/v1")

# --- FASTAPI NATIVE TEMPLATING ---
logger.info("🔗 Initializing Native UI Template Engine...")

# 1. Resolve exact absolute paths based on your workspace
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # C:\Coding\proxy\apps\backend\src
PUBLIC_WEBSITE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../web/public_website"))
WEB_DIR = os.path.join(PUBLIC_WEBSITE_DIR, "templates")

# Fail fast if templates are missing
if not os.path.exists(WEB_DIR):
    logger.error(f"🛑 CRITICAL: Could not find templates directory at {WEB_DIR}!")
    raise RuntimeError(f"FATAL: Web templates directory not found at {WEB_DIR}")

logger.info(f"✅ Found web templates directory at: {WEB_DIR}")
templates = Jinja2Templates(directory=WEB_DIR)

# 2. Mount Static Files (CSS, JS, Images)
# Mounts the root public_website folder so /css, /images, etc. all resolve natively
if os.path.exists(PUBLIC_WEBSITE_DIR):
    app.mount("/static", StaticFiles(directory=PUBLIC_WEBSITE_DIR), name="static")
    logger.info(f"✅ Mounted static directory from: {PUBLIC_WEBSITE_DIR}")
else:
    logger.warning(f"⚠️ Static directory not found at {PUBLIC_WEBSITE_DIR}. Assets may fail to load.")

# 3. UI Routes
@app.get("/enlist", response_class=HTMLResponse)
async def view_enlist_portal(request: Request):
    """Renders the Vanguard 50 Onboarding Portal"""
    return templates.TemplateResponse(
        request=request,
        name="enlist.html",
        context={
            "request": request, 
            # 🟢 Generate a unique, cryptographically secure CSRF token per render
            "csrf_token": secrets.token_hex(32)
        }
    )

@app.get("/enlist-success", response_class=HTMLResponse)
async def view_enlist_success(request: Request):
    """Renders the Enlistment Success & Referral Page"""
    return templates.TemplateResponse(
        request=request,
        name="enlist_success.html",
        context={"request": request}
    )

@app.get("/", response_class=RedirectResponse)
async def view_home():
    """Redirects the root URL to the enlistment portal"""
    return RedirectResponse(url="/enlist")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)