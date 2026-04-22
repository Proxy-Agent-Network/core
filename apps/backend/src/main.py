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

# 🛡️ ISSUE 2 FIX: Hard imports for core Android dependencies. Fail fast if these are broken.
from api.telemetry_socket import router as telemetry_router
from api.wallet_api import router as wallet_router
from api.agent_api import router as agent_router

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

# 🛡️ THE FIX: Bulletproof Mock Redis Client for Local Dev (Now Gated)
# Note: @app.on_event is deprecated in newer FastAPI versions (Issue 3). 
# Slated for migration to lifespan context managers in a future architectural pass.
@app.on_event("startup")
async def startup_event():
    if os.getenv("ENVIRONMENT") != "production" and os.getenv("USE_MOCK_REDIS") == "1":
        class MockRedis:
            def __init__(self): 
                self.cache = {}
                self.hashes = {}
                
            async def get(self, key): return self.cache.get(key)
            async def set(self, key, value, *args, **kwargs): return True
            async def setex(self, key, time, value): return True
            async def delete(self, *keys): return True
            
            async def exists(self, key):
                # 🟢 DEV BYPASS: Never block re-registration so you can test multiple times
                if key.endswith(":pubkey"): return False 
                return True
                
            async def hset(self, name, key=None, value=None, mapping=None): return 1
                
            async def hgetall(self, name):
                # 🟢 BULLETPROOF DEV BYPASS: Accept ANY agent ID Firebase sends
                if name.startswith("pan:agent:"):
                    return {
                        "callsign": "DEV-TESTER",
                        "status": "VERIFIED_AWAITING_HARDWARE",
                        "email": "dev@proxyagent.network",
                        "vehicle_class": "TACTICAL"
                    }
                return {}
                
            async def hincrby(self, name, key, amount=1): return 1
                
        app.state.redis_client = MockRedis()
        logger.info("🛡️ Injected BULLETPROOF Mock Redis Client into app.state.")
    else:
        # 🟢 Fail-closed: Default to a real Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        app.state.redis_client = redis.from_url(redis_url)
        logger.info("🟢 Real Redis client connected and injected into app.state.")

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

# 🛡️ ISSUE 2 FIX: Required routers are now firmly registered
app.include_router(telemetry_router, prefix="/api/v1", tags=["Telemetry"])
app.include_router(wallet_router, prefix="/api/v1", tags=["Wallet"])
app.include_router(agent_router, prefix="/api/v1", tags=["Agent"])

def load_optional_router(module_name, prefix, tags):
    """Dynamically loads non-critical routers. Core systems should use hard imports."""
    try:
        mod = importlib.import_module(module_name)
        app.include_router(mod.router, prefix=prefix, tags=tags)
        logger.info(f"Loaded optional router: {module_name}")
    except ImportError:
        # 🛡️ ISSUE 1 FIX: Accurate logging reflecting the removal of the fallback mock
        logger.warning(f"Missing router module: {module_name}. Endpoints will 404.")

# [C2 FIX: Removed the /api/v1/{path:path} fallback mock to ensure routing bugs fail loudly with a 404]

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

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting up Tactical Gateway via Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)