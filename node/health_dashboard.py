from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import time
import os
import random
import json
from datetime import datetime
from typing import List, Dict, Optional

# PROXY PROTOCOL - NODE HEALTH DASHBOARD v1.5 (Jury Tribunal Enabled)
# "Decentralized justice for the autonomous workforce."
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

# --- 2. Jury Data Models ---

class JuryVote(BaseModel):
    case_id: str
    verdict: str # "APPROVE" or "REJECT"

# --- 3. System Monitoring & Jury Logic ---

class SystemStats:
    def __init__(self):
        self.node_id = "node_88293_alpha_hw"
        self.start_time = datetime.now()
        self.pcr_history = [100.0] * 20
        
        # Jurisdiction State
        self.claimed_region = "US-DE"
        self.detected_region = "US-DE"
        self.resolution_status = "LOCKED"
        
        # Jury State
        self.reputation = 942
        self.active_cases = [
            {
                "case_id": "dispute_9921",
                "type": "PHOTO_BLURRY",
                "instruction": "Photograph the legal notice at 123 Market St.",
                "proof_url": "ipfs://QmProof_Blurry_Sample",
                "reward_potential": "450 SATS",
                "status": "OPEN"
            }
        ]
        
    def get_latest(self):
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        
        # Rolling PCR history
        current_integrity = 100.0 if random.random() > 0.05 else 99.98
        self.pcr_history.append(current_integrity)
        if len(self.pcr_history) > 20: self.pcr_history.pop(0)

        # Conflict Simulation (Rare)
        if self.resolution_status == "LOCKED" and random.random() > 0.995:
            self.detected_region = "SG-CORE"
            self.resolution_status = "CONFLICT"

        return {
            "node_id": self.node_id,
            "uptime": uptime,
            "tpm_status": "LOCKED",
            "tpm_temp": f"{random.randint(42, 48)}°C",
            "lnd_sync": "100%",
            "channel_balance": f"{1240500 + random.randint(-100, 5000):,} SATS",
            "reputation": f"{self.reputation}/1000",
            "claimed_region": self.claimed_region,
            "detected_region": self.detected_region,
            "resolution_status": self.resolution_status,
            "lat_long": "1.3521° N, 103.8198° E" if self.detected_region == "SG-CORE" else "39.7459° N, 75.5467° W",
            "tasks_24h": random.randint(10, 25),
            "status": "ONLINE" if self.resolution_status == "LOCKED" else "SUSPENDED",
            "pcr_history": self.pcr_history,
            "cases": self.active_cases
        }

    def recertify(self):
        if self.resolution_status == "CONFLICT":
            self.claimed_region = self.detected_region
            self.resolution_status = "LOCKED"
            return True
        return False

    def submit_verdict(self, case_id: str, verdict: str):
        # Find and remove the case from local queue
        for case in self.active_cases:
            if case['case_id'] == case_id:
                case['status'] = 'VOTED'
                self.active_cases.remove(case)
                # Elite nodes gain rep/fees for voting
                self.reputation += 1 
                return True
        return False

stats_engine = SystemStats()

# --- 4. UI Template ---

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
        .case-card { border-left: 4px solid #333; transition: all 0.2s; }
        .case-card:hover { border-left-color: #00FF41; background: rgba(0, 255, 65, 0.02); }
    </style>
</head>
<body class="p-4 md:p-8 min-h-screen">

    <!-- Jurisdiction Conflict Alert -->
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
                <button onclick="recertifyNode()" class="bg-red-600 text-white px-6 py-2 font-black text-[10px] uppercase tracking-widest hover:bg-red-500">Re-Certify for New Region</button>
            </div>
        </div>
    </div>

    <!-- Header -->
    <header class="max-w-6xl mx-auto flex justify-between items-end border-b border-green-900/50 pb-6 mb-8">
        <div>
            <h1 class="text-2xl font-bold tracking-tighter glow uppercase">Proxy Node Medic <span class="text-xs opacity-50">v1.5</span></h1>
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
            <span class="text-[10px] text-gray-500 uppercase block mb-1 font-bold">Node ID</span>
            <span class="text-lg font-bold text-white truncate block">{{ node_id }}</span>
        </div>
        <div class="terminal-border p-4 bg-void border-l-4 border-l-green-500">
            <span class="text-[10px] text-gray-500 uppercase block mb-1 font-bold">TPM 2.0 State</span>
            <span id="stat-tpm_status" class="text-lg font-bold text-green-500 uppercase">{{ tpm_status }}</span>
        </div>
        <div class="terminal-border p-4 bg-void">
            <span class="text-[10px] text-gray-500 uppercase block mb-1 font-bold">LN Balance</span>
            <span id="stat-channel_balance" class="text-lg font-bold text-yellow-500">{{ channel_balance }}</span>
        </div>
        <div class="terminal-border p-4 bg-void">
            <span class="text-[10px] text-gray-500 uppercase block mb-1 font-bold">Reputation</span>
            <span id="stat-reputation" class="text-lg font-bold text-white">{{ reputation }}</span>
        </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="lg:col-span-2 space-y-6">
            <!-- Hardware Forensics -->
            <div class="terminal-border p-6 bg-void">
                <div class="flex justify-between items-center mb-6 border-b border-gray-900 pb-2">
                    <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest">Hardware Forensics</h3>
                    <span id="stat-resolution_status" class="text-[9px] text-green-500 mono bg-green-500/10 px-2 py-0.5 rounded">RESOLUTION_LOCKED</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <span class="text-xs text-gray-600 block mb-2 uppercase">TPM Integrity History</span>
                        <div class="chart-container">
                            <canvas id="pcrChart"></canvas>
                        </div>
                    </div>
                    <div>
                        <span class="text-xs text-gray-600 block mb-4 uppercase">Locality Evidence</span>
                        <div class="space-y-4 text-xs">
                            <div class="flex justify-between">
                                <span class="text-gray-500">Claimed:</span>
                                <span id="stat-claimed_region" class="text-white font-bold">{{ claimed_region }}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-500">Detected:</span>
                                <span id="stat-detected_region" class="text-white font-bold">{{ detected_region }}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-500">Coords:</span>
                                <span id="stat-lat_long" class="text-white mono">{{ lat_long }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Jury Tribunal Section -->
            <div class="terminal-border p-6 bg-void">
                <div class="flex justify-between items-center mb-6 border-b border-gray-900 pb-2">
                    <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest">Jury Tribunal Evidence Locker</h3>
                    <span class="text-[9px] text-yellow-500 mono bg-yellow-500/10 px-2 py-0.5 rounded">JURY ELIGIBLE (REP > 800)</span>
                </div>
                <div id="case-list" class="space-y-4">
                    <!-- Cases injected here via JS -->
                    <p class="text-xs text-gray-600 italic">Scanning network for active disputes...</p>
                </div>
            </div>
        </div>

        <div class="space-y-6">
            <!-- Node Status -->
            <div class="terminal-border p-6 bg-void">
                <h3 class="text-sm font-bold text-gray-400 uppercase mb-6 tracking-widest">Operator Standing</h3>
                <div class="flex justify-between items-center mb-4">
                    <span class="text-xs text-gray-500 uppercase">Status</span>
                    <span id="stat-status_text" class="text-green-500 font-bold animate-pulse">ACTIVE</span>
                </div>
                <div class="flex justify-between items-center mb-4">
                    <span class="text-xs text-gray-500 uppercase">Tasks (24h)</span>
                    <span id="stat-tasks_24h" class="text-white font-bold">{{ tasks_24h }}</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500 uppercase">LND Sync</span>
                    <span id="stat-lnd_sync" class="text-white font-bold">{{ lnd_sync }}</span>
                </div>
            </div>

            <!-- Environmental -->
            <div class="terminal-border p-6 bg-void">
                <h3 class="text-sm font-bold text-gray-400 uppercase mb-4 tracking-widest">Environment</h3>
                <div class="flex justify-between items-center text-xs mb-2">
                    <span class="text-gray-500">TPM Temp</span>
                    <span id="stat-tpm_temp" class="text-green-500 font-bold">{{ tpm_temp }}</span>
                </div>
                <div class="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden">
                    <div id="temp-bar" class="bg-green-500 h-full transition-all duration-500" style="width: 45%"></div>
                </div>
            </div>

            <!-- Management Actions -->
            <div class="terminal-border p-6 bg-void">
                <h3 class="text-sm font-bold text-gray-400 uppercase mb-4 tracking-widest text-center">Protocol Actions</h3>
                <div class="space-y-2">
                    <button class="w-full py-2 border border-gray-700 text-gray-400 hover:text-white hover:border-white transition-all text-[10px] uppercase font-bold">Rotate TPM Identity</button>
                    <button class="w-full py-2 border border-red-900 text-red-500 hover:bg-red-900/20 transition-all text-[10px] uppercase font-bold">Scorched Earth (Wipe)</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Live Terminal -->
    <div class="max-w-6xl mx-auto mt-8">
        <div id="terminal" class="terminal-border bg-black p-4 h-48 overflow-y-auto text-[11px] leading-relaxed text-gray-500 mono">
            <p class="text-green-500">[*] UPLINK_ESTABLISHED: Watching for network events...</p>
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
            if (terminal.children.length > 50) terminal.removeChild(terminal.firstChild);
        }

        const ctx = document.getElementById('pcrChart').getContext('2d');
        const pcrChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [{
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
                scales: { x: { display: false }, y: { min: 99.9, max: 100.1, ticks: { display: false }, grid: { color: '#111' } } }
            }
        });

        // Jury Voting Action
        async function castJuryVote(caseId, verdict) {
            addLog(`Broadcasting Jury Verdict [${verdict}] for ${caseId}...`, 'INFO');
            try {
                const res = await fetch('/api/jury/vote', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ case_id: caseId, verdict: verdict })
                });
                if (res.ok) {
                    addLog(`Consensus vote accepted. Fee reward queued.`, 'SUCCESS');
                }
            } catch (e) {
                addLog('Arbitration communication error.', 'CRITICAL');
            }
        }

        async function recertifyNode() {
            try {
                const res = await fetch('/api/recertify', { method: 'POST' });
                if (res.ok) addLog('Regional transition verified and locked.', 'SUCCESS');
            } catch (e) { addLog('Re-certification handshake failed.', 'CRITICAL'); }
        }

        function renderCases(cases) {
            const container = document.getElementById('case-list');
            if (cases.length === 0) {
                container.innerHTML = '<p class="text-xs text-gray-700 italic">No active disputes requiring arbitration.</p>';
                return;
            }
            container.innerHTML = '';
            cases.forEach(c => {
                const div = document.createElement('div');
                div.className = 'case-card bg-gray-950 p-4 rounded terminal-border';
                div.innerHTML = `
                    <div class="flex justify-between mb-4">
                        <span class="text-[10px] text-green-500 mono">${c.case_id} // ${c.type}</span>
                        <span class="text-[10px] text-yellow-500 mono font-bold">Reward: ${c.reward_potential}</span>
                    </div>
                    <p class="text-xs text-gray-300 mb-4 leading-relaxed"><span class="text-gray-600">INSTRUCTION:</span> ${c.instruction}</p>
                    <div class="grid grid-cols-2 gap-4">
                        <button onclick="castJuryVote('${c.case_id}', 'APPROVE')" class="text-[9px] font-black uppercase py-2 bg-green-500/10 border border-green-500 text-green-500 hover:bg-green-500 hover:text-black">Approve Proof</button>
                        <button onclick="castJuryVote('${c.case_id}', 'REJECT')" class="text-[9px] font-black uppercase py-2 bg-red-900/10 border border-red-500 text-red-500 hover:bg-red-500 hover:text-black">Reject Proof</button>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'log') addLog(data.message, data.level);
            else if (data.type === 'stats') {
                const stats = data.payload;
                for (const [key, value] of Object.entries(stats)) {
                    if (!['pcr_history', 'cases'].includes(key)) {
                        const el = document.getElementById(`stat-${key}`);
                        if (el) el.innerText = value;
                    }
                }
                
                const banner = document.getElementById('conflict-banner');
                if (stats.resolution_status === 'CONFLICT') {
                    banner.classList.remove('hidden');
                    document.getElementById('alert-claimed').innerText = stats.claimed_region;
                    document.getElementById('alert-detected').innerText = stats.detected_region;
                } else banner.classList.add('hidden');

                document.getElementById('temp-bar').style.width = `${(parseInt(stats.tpm_temp)/100)*100}%`;
                pcrChart.data.datasets[0].data = stats.pcr_history;
                pcrChart.update('none');
                renderCases(stats.cases);
            }
        };
    </script>
</body>
</html>
"""

# --- 5. API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    data = stats_engine.get_latest()
    html = DASHBOARD_HTML
    for key, value in data.items():
        if key not in ['pcr_history', 'cases']:
            html = html.replace(f"{{{{ {key} }}}}", str(value))
    return html

@app.post("/api/recertify")
async def recertify_endpoint():
    if stats_engine.recertify():
        return {"status": "success", "new_jurisdiction": stats_engine.claimed_region}
    raise HTTPException(status_code=400, detail="No active conflict.")

@app.post("/api/jury/vote")
async def jury_vote_endpoint(vote: JuryVote):
    """
    Handles the submission of a jury verdict.
    In prod, this signs the vote with the TPM and broadcasts to the Jury Tribunal.
    """
    if stats_engine.submit_verdict(vote.case_id, vote.verdict):
        return {"status": "accepted", "reward": "PENDING_CONSENSUS"}
    raise HTTPException(status_code=404, detail="Case not found or already closed.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            stats = stats_engine.get_latest()
            await websocket.send_json({"type": "stats", "payload": stats})
            
            # Simulated tribunal events in the logs
            if random.random() > 0.85:
                events = [
                    ("New dispute ticket detected in mempool", "INFO"),
                    ("Consensus found for case_981: APPROVE", "SUCCESS"),
                    ("Adjudication fee of 120 SATS credited", "SUCCESS"),
                    ("VRF selection active for pending Tier 3 audit", "INFO")
                ]
                msg, lvl = random.choice(events)
                await websocket.send_json({"type": "log", "message": msg, "level": lvl})
            
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("[*] Launching Adjudication-Ready Dashboard v1.5 on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
