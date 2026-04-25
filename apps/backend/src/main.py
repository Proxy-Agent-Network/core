import logging
import os
import sys
import uuid
import importlib
import redis.asyncio as redis
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

# --- 1. INJECT MONOREPO PATHS ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, os.path.join(ROOT_DIR, "apps", "backend", "src"))

# Route the imports through the 'api' directory module
from api.v2x_bounty_api import router as v2x_router
from api.onboarding_api import router as onboarding_router
from api.telemetry_socket import router as telemetry_router
from api.wallet_api import router as wallet_router
from api.agent_api import router as agent_router
from api.store_api import router as store_router

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Gateway")

# --- App Initialization ---
app = FastAPI(
    title="Proxy Agent Network - Operational Gateway",
    description="High-Speed Mission Dispatch & Telemetry API",
    version="2.0.0"
)

@app.on_event("startup")
async def startup_event():
    # 🟢 THE FIX: Default to a real Redis connection
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    client = redis.from_url(redis_url)
    app.state.redis_client = client
    logger.info("🟢 Real Redis client connected and injected into app.state.")
    
    # 🟢 THE FIX: Seed the dev agent directly into Real Redis!
    # This bypasses Firebase onboarding but utilizes Real Redis for Pub/Sub WebSocket dispatch.
    if os.getenv("ENVIRONMENT") != "production":
        await client.hset("pan:agent:DEV_AGENT_01", mapping={
            "callsign": "DEV-TESTER",
            "status": "VERIFIED_AWAITING_HARDWARE",
            "email": "dev@proxyagent.network",
            "vehicle_class": "TACTICAL"
        })
        logger.info("🛡️ Seeded DEV_AGENT_01 into Real Redis for full end-to-end testing.")

# 🛡️ PHASE 3 FIX: Strict CORS Origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://command.proxyagent.network").split(",")
if os.getenv("ENVIRONMENT") != "production":
    allowed_origins.extend([
        "http://localhost:5000", 
        "http://127.0.0.1:5000", 
        "http://localhost:3000", 
        "http://localhost", 
        "https://pan-tactical.local"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# --- Templates ---
TEMPLATE_DIR = os.path.join(ROOT_DIR, "apps", "web", "public_website", "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# --- Router Registration ---
app.include_router(v2x_router, prefix="/api/v1", tags=["V2X Dispatch"])
app.include_router(onboarding_router, prefix="/api/v1", tags=["Agent Onboarding"])
app.include_router(telemetry_router, prefix="/api/v1", tags=["Telemetry"])
app.include_router(wallet_router, prefix="/api/v1", tags=["Wallet"])
app.include_router(agent_router, prefix="/api/v1", tags=["Agent"])
app.include_router(store_router, prefix="/api/v1", tags=["Agent Store"])

def load_optional_router(module_name, prefix, tags):
    """Dynamically loads non-critical routers. Core systems should use hard imports."""
    try:
        mod = importlib.import_module(module_name)
        app.include_router(mod.router, prefix=prefix, tags=tags)
        logger.info(f"Loaded optional router: {module_name}")
    except ImportError:
        logger.warning(f"Missing router module: {module_name}. Endpoints will 404.")

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = str(uuid.uuid4())
    logger.error(f"Unhandled Exception on {request.url} [Correlation ID: {correlation_id}]: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal operational error occurred.", "correlation_id": correlation_id},
    )

# --- Root/Health Check ---
@app.get("/")
async def root_health_check():
    return {"network": "Proxy Agent Network", "gateway_status": "ONLINE"}

@app.get("/enlist", response_class=HTMLResponse)
async def enlist_page(request: Request):
    return templates.TemplateResponse("enlist.html", {"request": request})

@app.get("/enlist-success", response_class=HTMLResponse)
async def enlist_success(request: Request):
    return templates.TemplateResponse("enlist_success.html", {"request": request})

@app.post("/api/v1/dev/override-hardware")
async def override_hardware(request: Request):
    client = request.app.state.redis_client
    
    # 🟢 THE FIX: Explicitly target the exact pubkey string! Wildcards can fail in async Redis.
    await client.delete("pan:agent:DEV_AGENT_01:pubkey")
    
    # Re-seed the clean agent profile
    await client.hset("pan:agent:DEV_AGENT_01", mapping={
        "callsign": "DEV-TESTER",
        "status": "VERIFIED_AWAITING_HARDWARE",
        "email": "dev@proxyagent.network",
        "vehicle_class": "TACTICAL"
    })
    return {"status": "success", "message": "Old hardware lock obliterated."}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting up Tactical Gateway via Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)