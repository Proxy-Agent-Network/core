import logging
import os
import sys
import uuid
import secrets
import importlib

import redis.asyncio as redis
from fastapi import FastAPI, Request, status, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import FileSystemLoader

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
from api.reports_api import router as reports_router
from api.network_stats_api import router as network_stats_router

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

# --- Session Middleware ---
# Stage 1d-3-c: signed-cookie session for command center auth.
# Refuses to boot without a real signing key. Falls back to FLASK_SECRET_KEY
# during the parallel-period transition for one-config convenience.
session_secret = os.getenv("SESSION_SECRET_KEY") or os.getenv("FLASK_SECRET_KEY")
if not session_secret or session_secret == "fallback_local_secret":
    raise RuntimeError(
        "SESSION_SECRET_KEY (or legacy FLASK_SECRET_KEY) must be set. "
        "Refusing to boot without a real session signing key."
    )

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="pan_session",
    max_age=60 * 60,                                          # 1 hour, matches old Flask PERMANENT_SESSION_LIFETIME
    same_site="strict",                                       # matches old Flask SESSION_COOKIE_SAMESITE
    https_only=os.getenv("ENVIRONMENT") == "production",
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
# Stage 1d-3-c: command center templates live in apps/web/command_center/.
# Their parent dashboard_base.html and the 404.html live in
# apps/web/public_website/templates/. FileSystemLoader takes a list of
# directories and searches them in order, mirroring what the old Flask
# ChoiceLoader did.
PUBLIC_TEMPLATE_DIR = os.path.join(ROOT_DIR, "apps", "web", "public_website", "templates")
COMMAND_CENTER_DIR = os.path.join(ROOT_DIR, "apps", "web", "command_center")
PUBLIC_STATIC_DIR = os.path.join(ROOT_DIR, "apps", "web", "public_website", "static")

templates = Jinja2Templates(directory=PUBLIC_TEMPLATE_DIR)
templates.env.loader = FileSystemLoader([COMMAND_CENTER_DIR, PUBLIC_TEMPLATE_DIR])

def base_context(request: Request) -> dict:
    """Jinja context shared by command center templates.

    Mirrors the old Flask context_processor that injected these globals on
    every render. csrf_token is intentionally omitted because we no longer
    run global CSRF middleware; revisit if and when we add session-cookie
    POST forms beyond /login itself.
    """
    return {
        "request": request,
        "csp_nonce": secrets.token_hex(16),
        "ops_hub_token": os.environ.get("OPS_HUB_TOKEN", "dev-token-777"),
    }

# --- Static Asset Mounts ---
# /static/...      -> public_website/static/   (PAN brand CSS, logos, images)
# /command/css/... -> command_center/css/      (command center stylesheets)
# /command/js/...  -> command_center/js/       (command center JS bundles)
app.mount("/static", StaticFiles(directory=PUBLIC_STATIC_DIR), name="static")
app.mount(
    "/command/css",
    StaticFiles(directory=os.path.join(COMMAND_CENTER_DIR, "css")),
    name="command_css",
)
app.mount(
    "/command/js",
    StaticFiles(directory=os.path.join(COMMAND_CENTER_DIR, "js")),
    name="command_js",
)

# --- Router Registration ---
app.include_router(v2x_router, prefix="/api/v1", tags=["V2X Dispatch"])
app.include_router(onboarding_router, prefix="/api/v1", tags=["Agent Onboarding"])
app.include_router(telemetry_router, prefix="/api/v1", tags=["Telemetry"])
app.include_router(wallet_router, prefix="/api/v1", tags=["Wallet"])
app.include_router(agent_router, prefix="/api/v1", tags=["Agent"])
app.include_router(store_router, prefix="/api/v1", tags=["Agent Store"])
app.include_router(reports_router, prefix="/api/v1", tags=["Executive Reports"])
app.include_router(network_stats_router, prefix="/api/v1", tags=["Network Stats"])

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

# --- 404 Handler ---
# Renders a branded HTML 404 page for browser requests; returns JSON for API requests.
# Detection: paths starting with /api/ get JSON, everything else gets HTML.
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not Found", "path": request.url.path},
        )
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404,
    )

# --- API Health Check ---
@app.get("/api/v1/health")
async def health_check():
    return {"network": "Proxy Agent Network", "gateway_status": "ONLINE"}

# ============================================================================
# Stage 1d-3-c: Authentication & Command Center Pages
# ============================================================================
# All public marketing pages (/, /operations, /rates, /investors, /enlist,
# /enlist-success, /our-mission, /partners, /api-spec) are served by Netlify
# from apps/web/netlify_public/ and intentionally NOT routed here.
#
# This server (command.proxyagent.network) handles only:
#   - JSON APIs at /api/v1/*
#   - The login flow (/login, /logout)
#   - Authenticated command center pages (/command, /developers, /reports)
#   - Static assets those pages reference (/static, /command/css, /command/js)
# ============================================================================

# --- Login / Logout ---
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    ctx = base_context(request)
    ctx["error"] = error
    return templates.TemplateResponse("login.html", ctx)

@app.post("/login")
async def login_submit(request: Request, password: str = Form(...)):
    expected = os.environ.get("ADMIN_SECRET_TOKEN")
    if not expected:
        logger.error("CRITICAL: ADMIN_SECRET_TOKEN missing; login disabled.")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: admin credential not configured.",
        )
    if not password or not secrets.compare_digest(password, expected):
        return RedirectResponse(url="/login?error=invalid", status_code=status.HTTP_303_SEE_OTHER)

    # Success: clear any prior session state, mark authenticated.
    request.session.clear()
    request.session["authenticated"] = True
    return RedirectResponse(url="/command", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# --- Authenticated Command Center Pages ---
# Inline auth check is used instead of a Depends() because a redirect from a
# dependency requires extra exception-handler plumbing in FastAPI. Three
# routes is too few to justify that abstraction; revisit if the list grows.
@app.get("/command", response_class=HTMLResponse)
async def command_center_root(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", base_context(request))

@app.get("/developers", response_class=HTMLResponse)
async def developer_portal(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("developer.html", base_context(request))

@app.get("/reports", response_class=HTMLResponse)
async def reports_portal(request: Request):
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("reports.html", base_context(request))

# --- Command Center Client Config (singleton at root path) ---
# Mirrors the old Flask /pan_client_config.js route. Holds the public
# Firebase and Google Maps API keys the command center JS needs at runtime.
@app.get("/pan_client_config.js")
async def command_center_secrets():
    return FileResponse(
        os.path.join(COMMAND_CENTER_DIR, "pan_client_config.js"),
        media_type="application/javascript",
    )

# --- Dev tooling ---
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
