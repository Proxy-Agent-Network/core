import uuid
import logging
import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from v2x_bounty_api import router as v2x_router
from onboarding_api import router as onboarding_router

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
    allow_methods=["GET", "POST", "OPTIONS"], # Restrict allowed methods
    allow_headers=["Authorization", "Content-Type", "X-Node-ID", "X-Timestamp", "X-Signature"],
)

# --- Templates ---
# Ensure your templates directory is correctly mapped here
templates = Jinja2Templates(directory="apps/web/public_website/templates")

# --- Router Registration ---
app.include_router(v2x_router, prefix="/api", tags=["V2X Dispatch"])
app.include_router(onboarding_router, prefix="/api", tags=["Agent Onboarding"])

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = str(uuid.uuid4())
    # Log the full trace securely on the server with the ID
    logger.error(f"Unhandled Exception on {request.url} [Correlation ID: {correlation_id}]: {exc}")
    
    # PHASE 4 FIX: Return sanitized response with Correlation ID
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal operational error occurred.",
            "correlation_id": correlation_id
        },
    )

# --- Root/Health Check ---
@app.get("/")
async def root_health_check():
    return {
        "network": "Proxy Agent Network",
        "gateway_status": "ONLINE",
        "v2x_dispatch": "ACTIVE",
        "compliance_mode": "SB-1417-STRICT"
    }

# --- Frontend HTML Routes ---
@app.get("/enlist", response_class=HTMLResponse)
async def enlist_page(request: Request):
    """Serves the Vanguard 50 onboarding wizard (Checkr/Stripe flow)."""
    return templates.TemplateResponse("enlist.html", {"request": request})

@app.get("/enlist-success", response_class=HTMLResponse)
async def enlist_success(request: Request):
    """Serves the success landing page after background check initiation."""
    return templates.TemplateResponse("enlist_success.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    # Standard entry point for local debugging. 
    # In production, use `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`
    logger.info("Starting up Tactical Gateway via Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)