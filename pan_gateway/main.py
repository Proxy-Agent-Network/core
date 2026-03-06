from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json

app = FastAPI(title="PAN Central Dispatch Gateway")

# --- IN-MEMORY TACTICAL DATABASE ---
agent_database = {}

# --- 1. THE HARDWARE HANDSHAKE ---
class StatusUpdate(BaseModel):
    agentId: str
    status: str
    latitude: float
    longitude: float
    radius: float    
    loadout: list[str] = []
    signature: str

# --- THE MISSION CLAIM ENDPOINT ---
class MissionAccept(BaseModel):
    agentId: str

@app.post("/v1/mission/accept")
async def accept_mission(payload: MissionAccept):
    if payload.agentId in agent_database:
        agent_database[payload.agentId]["status"] = "BUSY"
        print(f"🔒 MISSION LOCKED: {payload.agentId} is now en route.")
        return {"status": "accepted"}
    return {"status": "error: agent not found"}

@app.post("/v1/agent/status")
async def update_agent_status(payload: StatusUpdate):
    print(f"📡 UPLINK: {payload.agentId} | Loadout: {payload.loadout}")
    
    agent_database[payload.agentId] = {
        "status": payload.status,
        "lat": payload.latitude,
        "lon": payload.longitude,
        "radius": payload.radius,
        "loadout": payload.loadout # <-- STORE IT
    }
    return {"acknowledged": True}

# --- 2. LIVE DISPATCHER (WebSockets) ---
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
                "type": "MISSION", 
                "lat": lat, 
                "lon": lon,
                "errorCode": error_code,
                "bounty": bounty,
                "intersection": intersection
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

import math

# --- Helper: Calculate Distance in Miles ---
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- 3. UDS WEBHOOK RECEIVER ---
class WebhookPayload(BaseModel):
    lat: float
    lon: float
    errorCode: str = "ERR-702: Sensor Occlusion"
    bounty: str = "$45.00"
    intersection: str = "Main St & 1st Ave"
    required_gear: str = "clean" # <-- NEW: What does this job require?

@app.post("/v1/webhook/stranded")
async def trigger_stranded_av(payload: WebhookPayload):
    best_agent_id = None
    shortest_distance = float('inf')

    # THE DISPATCH SCANNER
    for agent_id, info in agent_database.items():
        if info["status"] == "ONLINE":
            # Check 1: Does the agent have the required gear toggled ON?
            if payload.required_gear in info.get("loadout", []):
                
                # Check 2: Is the stranded AV inside the agent's Service Radius?
                dist = haversine(payload.lat, payload.lon, info["lat"], info["lon"])
                if dist <= info["radius"]:
                    
                    # Check 3: Is this the closest agent we've found so far?
                    if dist < shortest_distance:
                        shortest_distance = dist
                        best_agent_id = agent_id

    # DECISION MATRIX
    if best_agent_id:
        print(f"🎯 MISSION MATCH: Routing to {best_agent_id} (Distance: {shortest_distance:.2f}mi)")
        success = await manager.send_mission(
            best_agent_id, payload.lat, payload.lon, payload.errorCode, payload.bounty, payload.intersection
        )
        return {"status": f"Dispatched to {best_agent_id}", "distance": f"{shortest_distance:.2f}mi"}
    
    print(f"❌ DISPATCH FAILED: No qualified agents in range for '{payload.required_gear}'.")
    return {"status": "Failed: No qualified agents in range"}

# --- 4. CENTRAL COMMAND DASHBOARD ---
@app.get("/v1/agents")
async def get_active_agents():
    return agent_database

@app.get("/dashboard")
async def get_dashboard():
    """Serves the live tactical web interface with an opacity-capped heatmap."""
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

            // Green for available, Cyan for en-route
            var onlineIcon = L.divIcon({ className: 'custom-div-icon', html: "<div style='background-color:#4CAF50; height:15px; width:15px; border-radius:50%; border:2px solid white;'></div>", iconSize: [15, 15], iconAnchor: [7, 7] });
            var busyIcon = L.divIcon({ className: 'custom-div-icon', html: "<div style='background-color:#00BCD4; height:15px; width:15px; border-radius:50%; border:2px solid white; box-shadow: 0 0 10px #00BCD4;'></div>", iconSize: [15, 15], iconAnchor: [7, 7] });

            setInterval(async () => {
                const response = await fetch('/v1/agents');
                const data = await response.json();
                
                for (const [agentId, info] of Object.entries(data)) {
                    var radiusInMeters = info.radius * 1609.34; 
                    var loadoutHtml = (info.loadout && info.loadout.length > 0) 
                        ? info.loadout.map(item => `<span style="background:#333;color:#4CAF50;padding:2px 6px;border-radius:4px;font-size:10px;margin-right:4px;display:inline-block;margin-bottom:4px;">${item.toUpperCase()}</span>`).join('') 
                        : '<span style="color:red;font-size:10px;">NO GEAR FITTED</span>';
                        
                    var popupContent = `<b>${agentId}</b><br>Status: ${info.status}<br><div style="margin-top:6px;">${loadoutHtml}</div>`;

                    if (info.status === 'ONLINE' || info.status === 'BUSY') {
                        // 1. Draw or Update the Marker
                        var currentIcon = info.status === 'ONLINE' ? onlineIcon : busyIcon;
                        
                        if (markers[agentId]) {
                            markers[agentId].setLatLng([info.lat, info.lon]);
                            markers[agentId].setIcon(currentIcon);
                            markers[agentId].setPopupContent(popupContent);
                        } else {
                            markers[agentId] = L.marker([info.lat, info.lon], {icon: currentIcon}).bindPopup(popupContent).addTo(map);
                        }

                        // 2. Handle the Service Radius Ring (Only show if ONLINE)
                        if (info.status === 'ONLINE') {
                            if (circles[agentId]) {
                                circles[agentId].setLatLng([info.lat, info.lon]);
                                circles[agentId].setRadius(radiusInMeters);
                            } else {
                                circles[agentId] = L.circle([info.lat, info.lon], {pane: 'heatmapPane', color: 'transparent', fillColor: '#F44336', fillOpacity: 0.2, radius: radiusInMeters}).addTo(map);
                            }
                        } else if (info.status === 'BUSY' && circles[agentId]) {
                            // If they are busy, they are off the market. Remove their red ring!
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