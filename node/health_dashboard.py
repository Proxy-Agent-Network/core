from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import time
import os
import random
import json
from datetime import datetime
from typing import List

# PROXY PROTOCOL - NODE HEALTH DASHBOARD v1.4 (Re-Certification API Enabled)
# "On-the-fly jurisdictional agility for a mobile workforce."
# ----------------------------------------------------

app = FastAPI(title="Proxy Node Dashboard")

# --- 1. WebSocket Connection Manager ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- 2. System Monitoring & Resolution Logic ---

class SystemStats:
    def __init__(self):
        self.node_id = "node_88293_alpha_hw"
        self.start_time = datetime.now()
        self.pcr_history = [100.0] * 20
        
        # Jurisdiction State
        self.claimed_region = "US-DE"
        self.detected_region = "US-DE" # Standard state
        self.resolution_status = "LOCKED" # LOCKED, CONFLICT, TRANSITION
        
    def get_latest(self):
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        
        # Rolling PCR history
        current_integrity = 100.0 if random.random() > 0.05 else 99.98
        self.pcr_history.append(current_integrity)
        if len(self.pcr_history) > 20: self.pcr_history.pop(0)

        # Simulation: Occasionally trigger a jurisdictional mismatch
        # Represents moving the node across a geofence
        if self.resolution_status == "LOCKED" and random.random() > 0.99:
            self.detected_region = "SG-CORE"
            self.resolution_status = "CONFLICT"

        return {
            "node_id": self.node_id,
            "uptime": uptime,
            "tpm_status": "LOCKED",
            "tpm_temp": f"{random.randint(42, 48)}°C",
            "lnd_sync": "100%",
            "channel_balance": f"{1240500 + random.randint(-100, 5000):,} SATS",
            "reputation": "942/1000",
            "claimed_region": self.claimed_region,
            "detected_region": self.detected_region,
            "resolution_status": self.resolution_status,
            "lat_long": "1.3521° N, 103.8198° E" if self.detected_region == "SG-CORE" else "39.7459° N, 75.5467° W",
            "tasks_24h": random.randint(10, 25),
            "status": "ONLINE" if self.resolution_status == "LOCKED" else "SUSPENDED",
            "pcr_history": self.pcr_history
        }

    def recertify(self):
        """Resolves conflict by promoting detected region to claimed."""
        if self.resolution_status == "CONFLICT":
            self.claimed_region = self.detected_region
            self.resolution_status = "LOCKED"
            return True
        return False

stats_engine = SystemStats()

# --- 3. UI Template ---

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROXY_NODE // CONTROL_PANEL</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #0D0D0D; color: #00FF41; font-family: 'Fira Code', monospace; }
        .terminal-border { border: 1px solid rgba(0, 255, 65, 0.2); }
        .bg-void { background: rgba(13, 13, 13, 0.95); }
        .glow { text-shadow: 0 0 10px rgba(0, 255, 65, 0.5); }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        .cursor { display: inline-block; width: 8px; height: 16px; background: #00FF41; animation: pulse 1s infinite; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #1a1a1a; }
        .chart-container { position: relative; height: 180px; width: 100%; }
        .alert-bar { border: 1px solid #FF3333; background: rgba(255, 51, 51, 0.1); }
    </style>
</head>
<body class="p-4 md:p-8 min-h-screen">

    <!-- Jurisdiction Conflict Alert (Dynamic) -->
    <div id="conflict-banner" class="max-w-6xl mx-auto mb-8 hidden">
        <div class="alert-bar p-6 rounded-lg flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="flex items-center gap-6">
                <span class="text-4xl animate-pulse">⚖️</span>
                <div>
                    <h2 class="text-red-500 font-black uppercase tracking-tighter text-lg">Jurisdiction Conflict Detected</h2>
                    <p class="text-xs text-gray-400">Node claimed <span id="alert-claimed" class="text-white font-bold">---</span> but telemetry detects <span id="alert-detected" class="text-white font-bold">---</span>.</p>
                </div>
            </div>
            <div class="flex gap-4">
                <button onclick="recertifyNode()" class="bg-red-600 text-white px-6 py-2 font-black text-[10px] uppercase tracking-widest hover:bg-red-500 transition-all">Re-Certify for New Region</button>
                <button class="border border-gray-700 text-gray-500 px-6 py-2 font-black text-[10px] uppercase tracking-widest hover:text-white">Ignore (SLA Penalty)</button>
            </div>
        </div>
    </div>

    <!-- Header -->
    <header class="max-w-6xl mx-auto flex justify-between items-end border-b border-green-900/50 pb-6 mb-8">
        <div>
            <h1 class="text-2xl font-bold tracking-tighter glow uppercase">Proxy Node Medic <span class="text-xs opacity-50">v1.4</span></h1>
            <p class="text-xs text-gray-500 mt-1">NODE_ID: <span class="text-green-500">{{ node_id }}</span></p>
        </div>
        <div class="text-right">
            <span class="text-[10px] text-gray-600 uppercase block">System Time</span>
            <span id="clock" class="text-sm font-bold text-white">00:00:00 UTC</span>
        </div>
    </header>

    <!-- KPI Grid -->
    <div class="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="terminal-border p-4 bg-void">
            <span class="text-[10px] text-gray-500 uppercase block mb-1">Hardware ID</span>
            <span class="text-lg font-bold text-white truncate block">{{ node_id }}</span>
        </div>
        <div class="terminal-border p-4 bg-void border-l-4 border-l-green-500">
            <span class="text-[10px] text-gray-500 uppercase block mb-1">TPM 2.0 State</span>
            <span id="stat-tpm_status" class="text-lg font-bold text-green-500 uppercase">{{ tpm_status }}</span>
        </div>
        <div class="terminal-border p-4 bg-void">
            <span class="text-[10px] text-gray-500 uppercase block mb-1">LN Balance</span>
            <span id="stat-channel_balance" class="text-lg font-bold text-yellow-500">{{ channel_balance }}</span>
        </div>
        <div class="terminal-border p-4 bg-void">
            <span class="text-[10px] text-gray-500 uppercase block mb-1">Uptime</span>
            <span id="stat-uptime" class="text-lg font-bold text-white">{{ uptime }}</span>
        </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="lg:col-span-2 space-y-6">
            <!-- Locality & Forensics -->
            <div class="terminal-border p-6 bg-void h-full">
                <div class="flex justify-between items-center mb-6 border-b border-gray-900 pb-2">
                    <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest">Jurisdiction Selection Map</h3>
                    <div class="flex gap-2">
                        <span id="stat-resolution_status" class="text-[9px] text-green-500 mono bg-green-500/10 px-2 py-0.5 rounded">RESOLUTION_LOCKED</span>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div>
                        <span class="text-xs text-gray-600 block mb-2 uppercase">TPM Integrity History</span>
                        <div class="chart-container">
                            <canvas id="pcrChart"></canvas>
                        </div>
                    </div>
                    <div>
                        <span class="text-xs text-gray-600 block mb-4 uppercase">Locality Evidence</span>
                        <div class="space-y-4">
                            <div class="flex justify-between items-start">
                                <div>
                                    <span class="text-[10px] text-gray-500 block mb-1">Claimed Hub</span>
                                    <p id="stat-claimed_region" class="text-xs text-white font-bold">{{ claimed_region }}</p>
                                </div>
                                <div class="text-right">
                                    <span class="text-[10px] text-gray-500 block mb-1">Detected Geo</span>
                                    <p id="stat-detected_region" class="text-xs text-white font-bold">{{ detected_region }}</p>
                                </div>
                            </div>
                            <div>
                                <span class="text-[10px] text-gray-500 block mb-1">Coordinates</span>
                                <p id="stat-lat_long" class="text-xs text-white mono">{{ lat_long }}</p>
                            </div>
                            <div class="pt-2">
                                <span class="text-[10px] text-gray-500 block mb-2 uppercase">Env: TPM Temp</span>
                                <div class="flex justify-between items-center text-xs mb-1">
                                    <span id="stat-tpm_temp" class="text-green-500 font-bold">{{ tpm_temp }}</span>
                                </div>
                                <div class="w-full bg-gray-900 h-1 rounded-full overflow-hidden">
                                    <div id="temp-bar" class="bg-green-500 h-full transition-all duration-500" style="width: 45%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="space-y-6">
            <div class="terminal-border p-6 bg-void">
                <h3 class="text-sm font-bold text-gray-400 uppercase mb-6 tracking-widest">Operator Standing</h3>
                <div class="text-center py-4">
                    <div id="stat-reputation" class="text-4xl font-black text-white mb-2">{{ reputation }}</div>
                    <span class="text-[10px] text-gray-600 uppercase">Current REP Score</span>
                </div>
                <div class="mt-6 border-t border-gray-900 pt-4">
                    <div class="flex justify-between text-[10px] text-gray-500 mb-2 uppercase">
                        <span>Tasks (24h)</span>
                        <span id="stat-tasks_24h" class="text-white">{{ tasks_24h }}</span>
                    </div>
                    <div class="flex justify-between text-[10px] text-gray-500 uppercase">
                        <span>Status</span>
                        <span id="stat-status_text" class="text-green-500 font-bold animate-pulse">ACTIVE</span>
                    </div>
                </div>
            </div>

            <div class="terminal-border p-6 bg-void">
                <h3 class="text-sm font-bold text-gray-400 uppercase mb-4 tracking-widest">Management</h3>
                <div class="space-y-2">
                    <button class="w-full py-2 border border-gray-700 text-gray-400 hover:text-white hover:border-white transition-all text-[10px] uppercase font-bold">Download Logs</button>
                    <button class="w-full py-2 border border-red-900 text-red-500 hover:bg-red-900/20 transition-all text-[10px] uppercase font-bold">Scorched Earth (Wipe)</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Live Log Terminal -->
    <div class="max-w-6xl mx-auto mt-8">
        <div id="terminal" class="terminal-border bg-black p-4 h-48 overflow-y-auto text-[11px] leading-relaxed text-gray-500 mono">
            <p class="text-green-500">[*] UPLINK_ESTABLISHED: Watching for jurisdictional shifts...</p>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toUTCString().split(' ')[4] + ' UTC';
        }
        setInterval(updateClock, 1000);
        updateClock();

        const terminal = document.getElementById('terminal');
        function addLog(message, level = 'INFO') {
            const p = document.createElement('p');
            const time = new Date().toISOString().split('T')[1].split('.')[0];
            let colorClass = 'text-gray-500';
            if (level === 'SUCCESS') colorClass = 'text-green-400';
            if (level === 'WARN') colorClass = 'text-yellow-500';
            if (level === 'CRITICAL') colorClass = 'text-red-500';
            
            p.innerHTML = `<span class="text-gray-700">[${time}]</span> <span class="${colorClass}">[${level}] ${message}</span>`;
            terminal.appendChild(p);
            terminal.scrollTop = terminal.scrollHeight;
            if (terminal.children.length > 100) terminal.removeChild(terminal.firstChild);
        }

        const ctx = document.getElementById('pcrChart').getContext('2d');
        const pcrChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [{
                    label: 'Integrity %',
                    data: Array(20).fill(100),
                    borderColor: '#00FF41',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(0, 255, 65, 0.05)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { 
                        min: 99.9, 
                        max: 100.1, 
                        ticks: { color: '#333', font: { size: 8 } },
                        grid: { color: '#111' }
                    }
                }
            }
        });

        // 4. Re-Certification Action
        async function recertifyNode() {
            addLog('INFO', 'Initiating Jurisdiction Re-Certification Ceremony...');
            try {
                const res = await fetch('/api/recertify', { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    addLog('SUCCESS', `Regional transition complete. Hub promoted to ${data.new_jurisdiction}.`);
                } else {
                    const err = await res.json();
                    addLog('CRITICAL', `Re-Certification Failed: ${err.detail}`);
                }
            } catch (e) {
                addLog('CRITICAL', 'Network Communication Error during resolution.');
            }
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'log') {
                addLog(data.message, data.level);
            } else if (data.type === 'stats') {
                const stats = data.payload;
                for (const [key, value] of Object.entries(stats)) {
                    if (key !== 'pcr_history') {
                        const el = document.getElementById(`stat-${key}`);
                        if (el) el.innerText = value;
                    }
                }
                
                // Conflict Resolver logic
                const banner = document.getElementById('conflict-banner');
                if (stats.resolution_status === 'CONFLICT') {
                    banner.classList.remove('hidden');
                    document.getElementById('alert-claimed').innerText = stats.claimed_region;
                    document.getElementById('alert-detected').innerText = stats.detected_region;
                    document.getElementById('stat-status_text').className = "text-red-500 font-bold animate-pulse";
                    document.getElementById('stat-status_text').innerText = "CONFLICT";
                    document.getElementById('stat-resolution_status').className = "text-[9px] text-red-500 mono bg-red-500/10 px-2 py-0.5 rounded";
                    document.getElementById('stat-resolution_status').innerText = "JURISDICTION_CONFLICT";
                } else {
                    banner.classList.add('hidden');
                    // Reset UI to Healthy State
                    document.getElementById('stat-status_text').className = "text-green-500 font-bold animate-pulse";
                    document.getElementById('stat-status_text').innerText = "ACTIVE";
                    document.getElementById('stat-resolution_status').className = "text-[9px] text-green-500 mono bg-green-500/10 px-2 py-0.5 rounded";
                    document.getElementById('stat-resolution_status').innerText = "RESOLUTION_LOCKED";
                }

                const temp = parseInt(stats.tpm_temp);
                document.getElementById('temp-bar').style.width = `${(temp/100)*100}%`;
                pcrChart.data.datasets[0].data = stats.pcr_history;
                pcrChart.update('none');
            }
        };

        ws.onclose = () => {
            addLog('WebSocket connection lost. Reconnecting...', 'WARN');
            setTimeout(() => window.location.reload(), 5000);
        };
    </script>
</body>
</html>
"""

# --- 4. API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    data = stats_engine.get_latest()
    html = DASHBOARD_HTML
    for key, value in data.items():
        if key != 'pcr_history':
            html = html.replace(f"{{{{ {key} }}}}", str(value))
    return html

@app.post("/api/recertify")
async def recertify_endpoint():
    """
    POST endpoint to trigger regional re-certification.
    Validates physical telemetry and promotes detected region to claimed status.
    """
    success = stats_engine.recertify()
    if success:
        return {"status": "success", "new_jurisdiction": stats_engine.claimed_region}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No jurisdiction conflict active for this node.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            stats = stats_engine.get_latest()
            await websocket.send_json({"type": "stats", "payload": stats})
            
            # Simulate occasional forensic logs including conflict awareness
            if random.random() > 0.8:
                log_msgs = [
                    ("WiFi Entropy Shift detected (Roaming active)", "WARN"),
                    ("New IP Jurisdiction: Singapore (ASN 173)", "INFO"),
                    ("Legal Bridge: Matching SG-ETA-2010 templates", "SUCCESS"),
                    ("Conflict Resolver: Awaiting operator confirmation", "WARN"),
                    ("PCR 7 Secure Boot: Hub state verification passed", "SUCCESS")
                ]
                msg, level = random.choice(log_msgs)
                await websocket.send_json({"type": "log", "message": msg, "level": level})
            
            await asyncio.sleep(3)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS Error: {e}")
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_api():
    return stats_engine.get_latest()

if __name__ == "__main__":
    print("[*] Launching Jurisdiction-Aware Dashboard v1.4 on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
