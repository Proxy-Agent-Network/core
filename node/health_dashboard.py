from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import time
import os
import random
import hashlib
from datetime import datetime

# PROXY PROTOCOL - NODE HEALTH DASHBOARD v1.0
# "Real-time hardware visualization for the autonomous workforce."
# ----------------------------------------------------

app = FastAPI(title="Proxy Node Dashboard")

# Mocking system status (In production, this queries tpm_binding.py and LND)
class SystemStats:
    def __init__(self):
        self.node_id = "node_88293_alpha_hw"
        self.start_time = datetime.now()
        
    def get_latest(self):
        uptime = str(datetime.now() - self.start_time).split('.')[0]
        return {
            "node_id": self.node_id,
            "uptime": uptime,
            "tpm_status": "LOCKED",
            "tpm_temp": f"{random.randint(42, 48)}°C",
            "lnd_sync": "100%",
            "channel_balance": "1,240,500 SATS",
            "reputation": "942/1000",
            "region": "US-DE (Delaware Hub)",
            "lat_long": "39.7459° N, 75.5467° W",
            "tasks_24h": random.randint(10, 25),
            "status": "ONLINE"
        }

stats_engine = SystemStats()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROXY_NODE // CONTROL_PANEL</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #0D0D0D; color: #00FF41; font-family: 'Fira Code', monospace; }
        .terminal-border { border: 1px solid rgba(0, 255, 65, 0.2); }
        .bg-void { background: rgba(13, 13, 13, 0.95); }
        .glow { text-shadow: 0 0 10px rgba(0, 255, 65, 0.5); }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        .cursor { display: inline-block; width: 8px; height: 16px; background: #00FF41; animation: pulse 1s infinite; }
    </style>
</head>
<body class="p-4 md:p-8 min-h-screen">

    <!-- Header -->
    <header class="max-w-6xl mx-auto flex justify-between items-end border-b border-green-900/50 pb-6 mb-8">
        <div>
            <h1 class="text-2xl font-bold tracking-tighter glow uppercase">Proxy Node Medic <span class="text-xs opacity-50">v1.0</span></h1>
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
            <span class="text-lg font-bold text-green-500 uppercase">{{ tpm_status }}</span>
        </div>
        <div class="terminal-border p-4 bg-void">
            <span class="text-[10px] text-gray-500 uppercase block mb-1">LN Balance</span>
            <span class="text-lg font-bold text-yellow-500">{{ channel_balance }}</span>
        </div>
        <div class="terminal-border p-4 bg-void">
            <span class="text-[10px] text-gray-500 uppercase block mb-1">Uptime</span>
            <span class="text-lg font-bold text-white">{{ uptime }}</span>
        </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Physical Location & telemetry -->
        <div class="lg:col-span-2 space-y-6">
            <div class="terminal-border p-6 bg-void h-full">
                <h3 class="text-sm font-bold text-gray-400 uppercase mb-6 tracking-widest border-b border-gray-900 pb-2">Proof of Locality</h3>
                <div class="grid grid-cols-2 gap-8">
                    <div>
                        <span class="text-xs text-gray-600 block mb-2">Claimed Jurisdiction</span>
                        <p class="text-sm text-white font-bold">{{ region }}</p>
                    </div>
                    <div>
                        <span class="text-xs text-gray-600 block mb-2">GPS Coordinates (WiFi Triangulated)</span>
                        <p class="text-sm text-white mono">{{ lat_long }}</p>
                    </div>
                </div>
                
                <div class="mt-8">
                    <span class="text-xs text-gray-600 block mb-4 uppercase">Environmental Metrics</span>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center text-xs">
                            <span class="text-gray-400">TPM Chip Temperature</span>
                            <span class="text-green-500 font-bold">{{ tpm_temp }}</span>
                        </div>
                        <div class="w-full bg-gray-900 h-1.5 rounded-full overflow-hidden">
                            <div class="bg-green-500 h-full" style="width: 45%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Side: Reputation & Actions -->
        <div class="space-y-6">
            <div class="terminal-border p-6 bg-void">
                <h3 class="text-sm font-bold text-gray-400 uppercase mb-6 tracking-widest">Operator Standing</h3>
                <div class="text-center py-4">
                    <div class="text-4xl font-black text-white mb-2">{{ reputation }}</div>
                    <span class="text-[10px] text-gray-600 uppercase">Current REP Score</span>
                </div>
                <div class="mt-6 border-t border-gray-900 pt-4">
                    <div class="flex justify-between text-[10px] text-gray-500 mb-2 uppercase">
                        <span>Tasks (24h)</span>
                        <span class="text-white">{{ tasks_24h }}</span>
                    </div>
                    <div class="flex justify-between text-[10px] text-gray-500 uppercase">
                        <span>Status</span>
                        <span class="text-green-500 font-bold animate-pulse">ACTIVE</span>
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

    <!-- Live Log Terminal (Restored) -->
    <div class="max-w-6xl mx-auto mt-8">
        <div class="terminal-border bg-black p-4 h-48 overflow-y-auto text-[11px] leading-relaxed text-gray-500 mono">
            <p>[SYSTEM] Initializing Node Control Dashboard...</p>
            <p>[HARDWARE] Checking TPM 2.0 PCR Banks... OK</p>
            <p>[NETWORK] IP: 192.168.1.50 (Local Gateway)</p>
            <p>[SETTLEMENT] Listening for HODL Invoices on Lightning...</p>
            <p class="text-green-500">[*] READY_FOR_TASKS<span class="cursor"></span></p>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('clock').innerText = now.toUTCString().split(' ')[4] + ' UTC';
        }
        setInterval(updateClock, 1000);
        updateClock();
        
        // Auto-refresh the page every 30s to simulate live data
        setTimeout(() => { window.location.reload(); }, 30000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    data = stats_engine.get_latest()
    # Simple manual template replacement for the demo
    html = DASHBOARD_HTML
    for key, value in data.items():
        html = html.replace(f"{{{{ {key} }}}}", str(value))
    return html

@app.get("/api/health")
async def health_api():
    """Endpoint for programmatic fleet management tools."""
    return stats_engine.get_latest()

if __name__ == "__main__":
    # In production: python health_dashboard.py
    # Access at http://localhost:8000
    print("[*] Launching Node Health Dashboard on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
