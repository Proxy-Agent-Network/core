from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import json
import datetime
import math
import os

app = FastAPI(title="PAN Central Dispatch Gateway")

# ====================================================================
# DATABASE INITIALIZATION (SQLITE)
# ====================================================================
DB_FILE = "pan_command.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY, 
                    status TEXT, 
                    lat REAL, 
                    lon REAL, 
                    radius REAL, 
                    loadout TEXT, 
                    linked_card TEXT
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (
                    agent_id TEXT PRIMARY KEY, 
                    balance REAL
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY, 
                    agent_id TEXT, 
                    date TEXT, 
                    amount TEXT, 
                    description TEXT
                 )''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ====================================================================
# 1. THE HARDWARE HANDSHAKE
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

@app.post("/v1/mission/accept")
async def accept_mission(payload: MissionAccept):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE agents SET status = 'BUSY' WHERE agent_id = ?", (payload.agentId,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    
    if rows_affected > 0:
        print(f"🔒 MISSION LOCKED: {payload.agentId} is now en route.")
        return {"status": "accepted"}
    return {"status": "error: agent not found"}

@app.post("/v1/agent/status")
async def update_agent_status(payload: StatusUpdate):
    print(f"📡 UPLINK: {payload.agentId} | Market Bids: {payload.loadout}")
    
    conn = get_db()
    c = conn.cursor()
    loadout_json = json.dumps(payload.loadout)
    
    c.execute('''INSERT INTO agents (agent_id, status, lat, lon, radius, loadout, linked_card) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)
                 ON CONFLICT(agent_id) DO UPDATE SET 
                 status=excluded.status, lat=excluded.lat, lon=excluded.lon, 
                 radius=excluded.radius, loadout=excluded.loadout''', 
              (payload.agentId, payload.status, payload.latitude, payload.longitude, payload.radius, loadout_json, None))
    
    c.execute("INSERT OR IGNORE INTO wallets (agent_id, balance) VALUES (?, 0.0)", (payload.agentId,))
    conn.commit()
    conn.close()
    
    return {"acknowledged": True}

# ====================================================================
# 2. LIVE DISPATCHER (WEBSOCKETS)
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
# 3. THE REVERSE AUCTION ENGINE
# ====================================================================
class WebhookPayload(BaseModel):
    lat: float
    lon: float
    errorCode: str = "ERR-702: Sensor Occlusion"
    bounty: str = "$45.00"
    intersection: str = "Main St & 1st Ave"
    required_gear: str = "clean"

@app.post("/v1/webhook/stranded")
async def trigger_stranded_av(payload: WebhookPayload):
    best_agent_id = None
    shortest_distance = float('inf')
    winning_bid = float('inf')
    
    # The Fleet Operator's absolute maximum budget
    max_budget = float(payload.bounty.replace("$", ""))

    conn = get_db()
    agents = conn.execute("SELECT * FROM agents WHERE status = 'ONLINE'").fetchall()
    conn.close()

    for agent in agents:
        agent_id = agent["agent_id"]
        loadout = json.loads(agent["loadout"]) if agent["loadout"] else {}
        
        # Check 1: Do they have the gear toggled on?
        if payload.required_gear in loadout:
            
            # Check 2: What is the Agent's minimum price?
            agent_bid = float(loadout[payload.required_gear])
            
            # Check 3: Is their bid within the Fleet Operator's budget?
            if agent_bid <= max_budget:
                
                # Check 4: Are they within driving radius?
                dist = haversine(payload.lat, payload.lon, agent["lat"], agent["lon"])
                if dist <= agent["radius"]:
                    
                    # --- DECISION MATRIX: REVERSE AUCTION ---
                    # The lowest bidder wins. If tied, the closest agent wins.
                    if agent_bid < winning_bid:
                        winning_bid = agent_bid
                        shortest_distance = dist
                        best_agent_id = agent_id
                    elif agent_bid == winning_bid and dist < shortest_distance:
                        shortest_distance = dist
                        best_agent_id = agent_id

    if best_agent_id:
        # Override the Fleet's Max Budget with the Agent's actual bid!
        final_bounty_str = f"${winning_bid:.2f}"
        print(f"🎯 MISSION MATCH: {best_agent_id} won contract! (Bid: {final_bounty_str} | Fleet Max Budget: ${max_budget:.2f})")
        
        await manager.send_mission(
            best_agent_id, payload.lat, payload.lon, payload.errorCode, final_bounty_str, payload.intersection
        )
        return {"status": f"Dispatched to {best_agent_id}", "contract_price": final_bounty_str, "distance": f"{shortest_distance:.2f}mi"}
    
    print(f"❌ DISPATCH FAILED: No agents in range, or all bids exceeded fleet budget of ${max_budget:.2f}.")
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
    amount: float

@app.post("/v1/mission/complete")
async def complete_mission(req: MissionCompleteRequest):
    conn = get_db()
    c = conn.cursor()
    
    c.execute("UPDATE wallets SET balance = balance + ? WHERE agent_id = ?", (req.netPayout, req.agentId))
    
    timestamp = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
    txn_id = f"TXN-{int(datetime.datetime.now().timestamp())}"
    c.execute("INSERT INTO transactions (id, agent_id, date, amount, description) VALUES (?, ?, ?, ?, ?)",
              (txn_id, req.agentId, timestamp, f"+${req.netPayout:.2f}", "L402 Escrow Release - On-Scene Repair"))
    
    c.execute("UPDATE agents SET status = 'ONLINE' WHERE agent_id = ?", (req.agentId,))
    
    c.execute("SELECT balance FROM wallets WHERE agent_id = ?", (req.agentId,))
    new_balance = c.fetchone()["balance"]
    
    conn.commit()
    conn.close()
    
    print(f"💰 ESCROW UNLOCKED: ${req.netPayout:.2f} routed to {req.agentId}.")
    return {"status": "success", "newBalance": new_balance}

@app.post("/v1/wallet/link_card")
async def link_card(req: LinkCardRequest):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE agents SET linked_card = ? WHERE agent_id = ?", (req.cardNumber, req.agentId))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/v1/wallet/withdraw")
async def withdraw_funds(req: WithdrawRequest):
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT balance FROM wallets WHERE agent_id = ?", (req.agentId,))
    row = c.fetchone()
    if not row or row["balance"] < req.amount:
        conn.close()
        return {"status": "error", "message": "Insufficient funds"}
        
    new_balance = row["balance"] - req.amount
    c.execute("UPDATE wallets SET balance = ? WHERE agent_id = ?", (new_balance, req.agentId))
    
    timestamp = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
    txn_id = f"WD-{int(datetime.datetime.now().timestamp())}"
    c.execute("INSERT INTO transactions (id, agent_id, date, amount, description) VALUES (?, ?, ?, ?, ?)",
              (txn_id, req.agentId, timestamp, f"-${req.amount:.2f}", "ACH Transfer to Linked Card"))
    
    conn.commit()
    conn.close()
    return {"status": "success", "newBalance": new_balance}

@app.get("/v1/agent/{agent_id}/wallet")
async def get_wallet(agent_id: str):
    conn = get_db()
    
    wallet_row = conn.execute("SELECT balance FROM wallets WHERE agent_id = ?", (agent_id,)).fetchone()
    balance = wallet_row["balance"] if wallet_row else 0.0
    
    agent_row = conn.execute("SELECT linked_card FROM agents WHERE agent_id = ?", (agent_id,)).fetchone()
    linked_card = agent_row["linked_card"] if agent_row else None
    
    tx_rows = conn.execute("SELECT * FROM transactions WHERE agent_id = ? ORDER BY id DESC", (agent_id,)).fetchall()
    history = [{"id": r["id"], "date": r["date"], "amount": r["amount"], "description": r["description"]} for r in tx_rows]
    
    conn.close()
    return {"balance": balance, "linkedCard": linked_card, "history": history}

# ====================================================================
# 5. CENTRAL COMMAND DASHBOARD
# ====================================================================
@app.get("/v1/agents")
async def get_active_agents():
    conn = get_db()
    agents = conn.execute("SELECT * FROM agents").fetchall()
    conn.close()
    
    result = {}
    for a in agents:
        result[a["agent_id"]] = {
            "status": a["status"],
            "lat": a["lat"],
            "lon": a["lon"],
            "radius": a["radius"],
            "loadout": json.loads(a["loadout"]) if a["loadout"] else {}
        }
    return result

@app.get("/dashboard")
async def get_dashboard():
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
        <div id="header">🟢 PAN COMMAND: GLOBAL OVERWATCH</div>
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