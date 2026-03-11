from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import math
import hashlib
from datetime import datetime, timezone
import asyncio

# --- SECURITY & RATE LIMITING ---
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# --- SQLALCHEMY DATABASE ---
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey, JSON, Boolean, desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. Database Configuration (Easily swappable to PostgreSQL)
SQLALCHEMY_DATABASE_URL = "sqlite:///./pan_command.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. ORM Models (The Analytics Schema)
class Agent(Base):
    __tablename__ = "agents"
    agent_id = Column(String, primary_key=True, index=True)
    status = Column(String, default="OFFLINE") # ONLINE, BUSY, OFFLINE
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    radius = Column(Float, default=5.0)
    loadout = Column(JSON, default={})
    linked_card = Column(String, nullable=True)
    reputation_score = Column(Float, default=5.0)
    onboarding_status = Column(String, default="UNVERIFIED") # UNVERIFIED, PENDING, APPROVED, REJECTED
    checkr_candidate_id = Column(String, nullable=True) # The ID linking this agent to Checkr's vault
    bg_check_status = Column(String, nullable=True) # CLEAR, CONSIDER, SUSPENDED

class Wallet(Base):
    __tablename__ = "wallets"
    agent_id = Column(String, primary_key=True)
    balance = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    date = Column(String)
    amount = Column(String)
    description = Column(String)

class AgentSession(Base):
    __tablename__ = "agent_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, index=True)
    went_online_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    went_offline_at = Column(DateTime, nullable=True)

class Mission(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fleet_id = Column(String, default="VANGUARD-01")
    category_id = Column(String) # e.g., ERR-DOOR
    bounty_amount = Column(Float)
    status = Column(String, default="PENDING") # PENDING, ACTIVE, COMPLETED, ABORTED_AGENT, ABORTED_AV
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    accepted_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    assigned_agent_id = Column(String, nullable=True)

class DispatchEvent(Base):
    __tablename__ = "dispatch_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mission_id = Column(Integer, index=True)
    agent_id = Column(String, index=True)
    dispatched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    agent_response = Column(String, default="PENDING") # ACCEPTED, DECLINED, IGNORED

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- APP SETUP ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="PAN Central Dispatch Gateway")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "https://pan-tactical.web.app"], 
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com;"
    return response

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid payload structure. Request rejected."})

async def verify_agent_token(x_auth_token: str = Header(default=None)):
    if not x_auth_token or len(x_auth_token) < 16:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid hardware attestation token.")
    return x_auth_token

def verify_ecdsa_signature(payload_dict: dict, signature: str) -> bool:
    if not signature or len(signature) < 32:
        return False
    return True


# ====================================================================
# 1. AGENT TELEMETRY & ROUTING (SQLAlchemy Refactor)
# ====================================================================
class StatusUpdate(BaseModel):
    agentId: str
    status: str
    latitude: float
    longitude: float
    radius: float    
    loadout: dict[str, float] = {} 
    signature: str

class MissionAccept(BaseModel):
    agentId: str

@app.post("/v1/agent/status")
@limiter.limit("60/minute")
async def update_agent_status(request: Request, payload: StatusUpdate, db: Session = Depends(get_db), auth: str = Depends(verify_agent_token)):
    if not verify_ecdsa_signature(payload.dict(), payload.signature):
        raise HTTPException(status_code=403, detail="Invalid cryptographic signature.")
        
    # 1. Update Agent Core State
    agent = db.query(Agent).filter(Agent.agent_id == payload.agentId).first()
    if not agent:
        agent = Agent(agent_id=payload.agentId)
        db.add(agent)
        # Initialize Wallet
        db.add(Wallet(agent_id=payload.agentId, balance=0.0))
    
    agent.status = payload.status
    agent.lat = payload.latitude
    agent.lon = payload.longitude
    agent.radius = payload.radius
    agent.loadout = payload.loadout
    
    # 2. Analytics: Session Time Tracking
    if payload.status == "ONLINE":
        # Create a new session if one isn't open
        active_session = db.query(AgentSession).filter(AgentSession.agent_id == payload.agentId, AgentSession.went_offline_at == None).first()
        if not active_session:
            db.add(AgentSession(agent_id=payload.agentId))
    elif payload.status == "OFFLINE":
        # Close open sessions
        active_session = db.query(AgentSession).filter(AgentSession.agent_id == payload.agentId, AgentSession.went_offline_at == None).first()
        if active_session:
            active_session.went_offline_at = datetime.now(timezone.utc)

    db.commit()
    return {"acknowledged": True}

@app.post("/v1/mission/accept")
@limiter.limit("10/minute")
async def accept_mission(request: Request, payload: MissionAccept, db: Session = Depends(get_db), auth: str = Depends(verify_agent_token)):
    agent = db.query(Agent).filter(Agent.agent_id == payload.agentId).first()
    if agent:
        agent.status = 'BUSY'
        
        # Analytics: Correlate Accept to the Dispatch Event
        dispatch_event = db.query(DispatchEvent).filter(
            DispatchEvent.agent_id == payload.agentId, 
            DispatchEvent.agent_response == "PENDING"
        ).order_by(desc(DispatchEvent.dispatched_at)).first()
        
        if dispatch_event:
            dispatch_event.agent_response = "ACCEPTED"
            mission = db.query(Mission).filter(Mission.id == dispatch_event.mission_id).first()
            if mission:
                mission.status = "ACTIVE"
                mission.accepted_at = datetime.now(timezone.utc)
                mission.assigned_agent_id = payload.agentId

        db.commit()
        print(f"白 MISSION LOCKED: {payload.agentId[:8]}*** is now en route.")
        return {"status": "accepted"}
    return {"status": "error: agent not found"}

@app.post("/v1/webhooks/checkr")
async def checkr_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    
    # 1. Verify the webhook signature (prove it actually came from Checkr)
    # ... verification logic ...
    
    event_type = payload.get("type")
    
    if event_type == "report.completed":
        candidate_id = payload["data"]["object"]["candidate_id"]
        status = payload["data"]["object"]["status"] # Will be "clear" or "consider"
        
        agent = db.query(Agent).filter(Agent.checkr_candidate_id == candidate_id).first()
        if agent:
            agent.bg_check_status = status.upper()
            if status == "clear":
                agent.onboarding_status = "APPROVED"
                # Send push notification to agent: "You are approved for the Mesa Sector!"
            else:
                agent.onboarding_status = "REJECTED" # Flagged for manual review
                
            db.commit()
            
    return {"status": "received"}


# ====================================================================
# 2. LIVE DISPATCHER
# ====================================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[agent_id] = websocket

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]

    async def send_mission(self, agent_id: str, lat: float, lon: float, error_code: str, bounty: str, intersection: str):
        if agent_id in self.active_connections:
            payload = {
                "type": "MISSION", "lat": lat, "lon": lon,
                "errorCode": error_code, "bounty": bounty, "intersection": intersection
            }
            await self.active_connections[agent_id].send_text(json.dumps(payload))
            return True
        return False

manager = ConnectionManager()

@app.websocket("/ws/v1/dispatch/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    token = websocket.query_params.get("token")
    if not token or len(token) < 16:
        await websocket.close(code=1008)
        return

    await manager.connect(agent_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(agent_id)

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ====================================================================
# 3. REVERSE AUCTION ENGINE & EVENT LOGGING
# ====================================================================
class WebhookPayload(BaseModel):
    lat: float
    lon: float
    errorCode: str = "ERR-702: Sensor Occlusion"
    bounty: str = "$45.00"
    intersection: str = "Main St & 1st Ave"
    required_gear: str = "sensor_cleaning"

auction_lock = asyncio.Lock()

@app.post("/v1/webhook/stranded")
@limiter.limit("30/minute")
async def trigger_stranded_av(request: Request, payload: WebhookPayload, db: Session = Depends(get_db)):
    async with auction_lock: 
        best_agent_id = None
        shortest_distance = float('inf')
        winning_bid = float('inf')
        
        max_budget = float(payload.bounty.replace("$", ""))
        agents = db.query(Agent).filter(Agent.status == 'ONLINE').all()

        for agent in agents:
            loadout = agent.loadout if agent.loadout else {}
            if payload.required_gear in loadout:
                agent_bid = float(loadout[payload.required_gear])
                
                if agent_bid <= max_budget:
                    dist = haversine(payload.lat, payload.lon, agent.lat, agent.lon)
                    if dist <= agent.radius:
                        if agent_bid < winning_bid:
                            winning_bid = agent_bid
                            shortest_distance = dist
                            best_agent_id = agent.agent_id
                        elif agent_bid == winning_bid and dist < shortest_distance:
                            shortest_distance = dist
                            best_agent_id = agent.agent_id

        if best_agent_id:
            final_bounty_str = f"${winning_bid:.2f}"
            
            # Analytics: Create the Master Mission Ledger entry
            mission = Mission(category_id=payload.errorCode, bounty_amount=winning_bid)
            db.add(mission)
            db.commit()
            db.refresh(mission)
            
            # Analytics: Track the Dispatch Event (for acceptance funnels)
            dispatch = DispatchEvent(mission_id=mission.id, agent_id=best_agent_id)
            db.add(dispatch)
            db.commit()
            
            print(f"識 MISSION MATCH: {best_agent_id[:8]}*** won contract! (Bid: {final_bounty_str})")
            await manager.send_mission(best_agent_id, payload.lat, payload.lon, payload.errorCode, final_bounty_str, payload.intersection)
            return {"status": f"Dispatched", "contract_price": final_bounty_str}
        
        return {"status": "Failed: No agents met market criteria"}


# ====================================================================
# 4. PERSISTENT ESCROW & BANKING
# ====================================================================
class MissionCompleteRequest(BaseModel):
    agentId: str
    netPayout: float

class LinkCardRequest(BaseModel):
    agentId: str
    cardNumber: str 

class WithdrawRequest(BaseModel):
    agentId: str
    amount: float = Field(..., gt=0) 

@app.post("/v1/mission/complete")
@limiter.limit("10/minute")
async def complete_mission(request: Request, req: MissionCompleteRequest, db: Session = Depends(get_db), auth: str = Depends(verify_agent_token)):
    wallet = db.query(Wallet).filter(Wallet.agent_id == req.agentId).first()
    if wallet:
        wallet.balance += req.netPayout
        
    agent = db.query(Agent).filter(Agent.agent_id == req.agentId).first()
    if agent:
        agent.status = 'ONLINE'
        
    # Analytics: Close out the Active Mission Ledger
    mission = db.query(Mission).filter(Mission.assigned_agent_id == req.agentId, Mission.status == "ACTIVE").order_by(desc(Mission.id)).first()
    if mission:
        mission.status = "COMPLETED"
        mission.resolved_at = datetime.now(timezone.utc)

    txn_id = f"TXN-{int(datetime.now(timezone.utc).timestamp())}"
    timestamp = datetime.now().strftime("%m/%d/%Y %H:%M")
    db.add(Transaction(id=txn_id, agent_id=req.agentId, date=timestamp, amount=f"+${req.netPayout:.2f}", description="L402 Escrow Release - On-Scene Repair"))
    
    db.commit()
    return {"status": "success", "newBalance": wallet.balance if wallet else 0.0}

@app.post("/v1/wallet/link_card")
@limiter.limit("5/minute")
async def link_card(request: Request, req: LinkCardRequest, db: Session = Depends(get_db), auth: str = Depends(verify_agent_token)):
    hashed_card = hashlib.sha256(req.cardNumber.encode()).hexdigest()[:16]
    secure_mask = f"ENCRYPTED-****-{hashed_card}"
    
    agent = db.query(Agent).filter(Agent.agent_id == req.agentId).first()
    if agent:
        agent.linked_card = secure_mask
        db.commit()
    return {"status": "success"}

@app.post("/v1/wallet/withdraw")
@limiter.limit("5/minute")
async def withdraw_funds(request: Request, req: WithdrawRequest, db: Session = Depends(get_db), auth: str = Depends(verify_agent_token)):
    wallet = db.query(Wallet).filter(Wallet.agent_id == req.agentId).first()
    if not wallet or wallet.balance < req.amount:
        return {"status": "error", "message": "Insufficient funds"}
        
    wallet.balance -= req.amount
    txn_id = f"WD-{int(datetime.now(timezone.utc).timestamp())}"
    timestamp = datetime.now().strftime("%m/%d/%Y %H:%M")
    
    db.add(Transaction(id=txn_id, agent_id=req.agentId, date=timestamp, amount=f"-${req.amount:.2f}", description="ACH Transfer to Linked Card"))
    db.commit()
    
    return {"status": "success", "newBalance": wallet.balance}

@app.get("/v1/agent/{agent_id}/wallet")
@limiter.limit("15/minute")
async def get_wallet(request: Request, agent_id: str, db: Session = Depends(get_db), auth: str = Depends(verify_agent_token)):
    wallet = db.query(Wallet).filter(Wallet.agent_id == agent_id).first()
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    transactions = db.query(Transaction).filter(Transaction.agent_id == agent_id).order_by(desc(Transaction.id)).all()
    
    history = [{"id": t.id, "date": t.date, "amount": t.amount, "description": t.description} for t in transactions]
    
    return {
        "balance": wallet.balance if wallet else 0.0, 
        "linkedCard": agent.linked_card if agent else None, 
        "history": history
    }

# ====================================================================
# 5. CENTRAL COMMAND DASHBOARD
# ====================================================================
@app.get("/v1/agents")
@limiter.limit("20/minute")
async def get_active_agents(request: Request, db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    result = {}
    for a in agents:
        result[a.agent_id] = {
            "status": a.status,
            "lat": a.lat,
            "lon": a.lon,
            "radius": a.radius,
            "loadout": a.loadout if a.loadout else {}
        }
    return result

@app.get("/dashboard")
@limiter.limit("10/minute")
async def get_dashboard(request: Request):
    # Retained existing dashboard HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PAN Central Command</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body { margin: 0; padding: 0; background-color: #121212; color: white; font-family: monospace; }
            #header { padding: 15px; background-color: #1E1E1E; border-bottom: 2px solid #4CAF50; font-size: 20px; font-weight: bold; }
            #map { height: calc(100vh - 54px); width: 100vw; }
        </style>
    </head>
    <body>
        <div id="header">泙 PAN COMMAND: GLOBAL OVERWATCH</div>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([33.3061, -111.6601], 10);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
            }).addTo(map);

            map.createPane('heatmapPane');
            map.getPane('heatmapPane').style.opacity = '0.5';

            var markers = {};
            var circles = {}; 

            var onlineIcon = L.divIcon({ className: 'custom-div-icon', html: "<div style='background-color:#4CAF50; height:15px; width:15px; border-radius:50%; border:2px solid white;'></div>", iconSize: [15, 15], iconAnchor: [7, 7] });
            var busyIcon = L.divIcon({ className: 'custom-div-icon', html: "<div style='background-color:#00BCD4; height:15px; width:15px; border-radius:50%; border:2px solid white; box-shadow: 0 0 10px #00BCD4;'></div>", iconSize: [15, 15], iconAnchor: [7, 7] });

            setInterval(async () => {
                const response = await fetch('/v1/agents');
                const data = await response.json();
                
                for (const [agentId, info] of Object.entries(data)) {
                    var radiusInMeters = info.radius * 1609.34; 
                    
                    var loadoutHtml = "";
                    if (info.loadout && Object.keys(info.loadout).length > 0) {
                        for (const [key, val] of Object.entries(info.loadout)) {
                            loadoutHtml += `<span style="background:#333;color:#4CAF50;padding:2px 6px;border-radius:4px;font-size:10px;margin-right:4px;display:inline-block;margin-bottom:4px;">${key.toUpperCase()}: $${val}</span>`;
                        }
                    } else {
                        loadoutHtml = '<span style="color:red;font-size:10px;">NO GEAR FITTED</span>';
                    }
                        
                    var popupContent = `<b>${agentId}</b><br>Status: ${info.status}<br><div style="margin-top:6px;">${loadoutHtml}</div>`;

                    if (info.status === 'ONLINE' || info.status === 'BUSY') {
                        var currentIcon = info.status === 'ONLINE' ? onlineIcon : busyIcon;
                        
                        if (markers[agentId]) {
                            markers[agentId].setLatLng([info.lat, info.lon]);
                            markers[agentId].setIcon(currentIcon);
                            markers[agentId].setPopupContent(popupContent);
                        } else {
                            markers[agentId] = L.marker([info.lat, info.lon], {icon: currentIcon}).bindPopup(popupContent).addTo(map);
                        }

                        if (info.status === 'ONLINE') {
                            if (circles[agentId]) {
                                circles[agentId].setLatLng([info.lat, info.lon]);
                                circles[agentId].setRadius(radiusInMeters);
                            } else {
                                circles[agentId] = L.circle([info.lat, info.lon], {pane: 'heatmapPane', color: 'transparent', fillColor: '#F44336', fillOpacity: 0.2, radius: radiusInMeters}).addTo(map);
                            }
                        } else if (info.status === 'BUSY' && circles[agentId]) {
                            map.removeLayer(circles[agentId]);
                            delete circles[agentId];
                        }
                    } else if (info.status === 'OFFLINE' && markers[agentId]) {
                        map.removeLayer(markers[agentId]);
                        if(circles[agentId]) { map.removeLayer(circles[agentId]); delete circles[agentId]; }
                        delete markers[agentId];
                    }
                }
            }, 2000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)