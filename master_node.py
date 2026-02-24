from flask import Flask, request, jsonify, render_template_string
import logging
import random
import time

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ==========================================
# 📊 THE PANOPTICON STATE
# ==========================================
network_state = {
    "treasury_balance": 1000000,
    "active_nodes": {},
    "ledger": []
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Panopticon: Network Dashboard</title>
    <style>
        body { font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 30px; }
        h1 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 6px; }
        .treasury { font-size: 32px; color: #3fb950; font-weight: bold; margin-top: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; border-bottom: 1px solid #30363d; text-align: left; }
        th { color: #8b949e; }
        .highlight { color: #3fb950; font-weight: bold; }
    </style>
    <script>
        // Fetch network state every 2 seconds without reloading the page
        async function fetchData() {
            const response = await fetch('/api/v1/stats');
            const data = await response.json();
            
            document.getElementById('treasury').innerText = data.treasury_balance.toLocaleString() + ' SATS';
            
            let nodesHtml = '';
            for (const [id, stats] of Object.entries(data.active_nodes)) {
                nodesHtml += `<tr><td>${id}</td><td>${stats.tasks_completed}</td><td class="highlight">${stats.total_earned} SATS</td></tr>`;
            }
            document.getElementById('nodes').innerHTML = nodesHtml;
            
            let ledgerHtml = '';
            data.ledger.forEach(tx => {
                ledgerHtml += `<tr><td>${tx.time}</td><td>${tx.node}</td><td>${tx.task}</td><td class="highlight">+${tx.amount} SATS</td></tr>`;
            });
            document.getElementById('ledger').innerHTML = ledgerHtml;
        }
        setInterval(fetchData, 2000);
        window.onload = fetchData;
    </script>
</head>
<body>
    <h1>🌐 Proxy Agent Network: Panopticon</h1>
    
    <div class="card" style="margin-bottom: 20px;">
        <h2 style="margin:0;">🏦 Master Treasury Balance</h2>
        <div class="treasury" id="treasury">Loading...</div>
    </div>

    <div class="grid">
        <div class="card">
            <h2 style="margin-top:0;">🤖 Active Hardware Nodes</h2>
            <table>
                <thead><tr><th>Hardware Identity</th><th>Tasks Finished</th><th>Sats Earned</th></tr></thead>
                <tbody id="nodes"></tbody>
            </table>
        </div>

        <div class="card">
            <h2 style="margin-top:0;">📜 Live L402 Ledger</h2>
            <table>
                <thead><tr><th>Time</th><th>Node ID</th><th>Task ID</th><th>Payout</th></tr></thead>
                <tbody id="ledger"></tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# 🌐 API ROUTES
# ==========================================
@app.route('/')
def dashboard():
    """Serves the Panopticon Web UI"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/stats', methods=['GET'])
def stats():
    """Provides real-time JSON data to the dashboard UI"""
    return jsonify(network_state)

@app.route('/api/v1/node/register', methods=['POST'])
def register_node():
    data = request.get_json()
    node_id = data.get("node_id", "")
    
    if not node_id.startswith("TPM2-EK-"):
        return jsonify({"status": "rejected"}), 403

    # Add the node to our active tracking state
    if node_id not in network_state["active_nodes"]:
        network_state["active_nodes"][node_id] = {"tasks_completed": 0, "total_earned": 0}
        
    print(f"\n[FRONT DESK] ✅ ACCEPTED: Hardware identity {node_id} verified.")
    return jsonify({"status": "connected"}), 200

@app.route('/api/v1/task/request', methods=['POST'])
def dispatch_task():
    data = request.get_json()
    node_id = data.get("node_id", "")
    task_id = f"TASK-{random.randint(1000, 9999)}"
    bounty = random.randint(10, 50) 
    
    print(f"[MANAGERS] 📋 Dispatching {task_id} to {node_id[:15]}...")
    return jsonify({"task_id": task_id, "prompt": "Analyze legal clause 4.2 for compliance.", "payout_sats": bounty}), 200

@app.route('/api/v1/task/submit', methods=['POST'])
def submit_task_and_pay():
    data = request.get_json()
    node_id = data.get("node_id")
    task_id = data.get("task_id")
    
    # Extract the requested amount from our mock Lightning invoice (e.g., lnbc41u1...)
    try:
        amount = int(data.get("invoice").split('u1')[0].replace('lnbc', ''))
    except:
        amount = 25

    # 1. Update the Treasury and Node balances
    network_state["treasury_balance"] -= amount
    if node_id in network_state["active_nodes"]:
        network_state["active_nodes"][node_id]["tasks_completed"] += 1
        network_state["active_nodes"][node_id]["total_earned"] += amount
        
    # 2. Record the transaction in the ledger (keep only the last 10)
    network_state["ledger"].insert(0, {
        "time": time.strftime("%H:%M:%S"),
        "node": node_id[:15] + "...",
        "task": task_id,
        "amount": amount
    })
    if len(network_state["ledger"]) > 10:
        network_state["ledger"].pop()

    print(f"[TREASURY] 💸 Payment Sent. (Treasury Remaining: {network_state['treasury_balance']} SATS)")
    return jsonify({"status": "paid", "preimage": "0xDEADBEEF"}), 200

if __name__ == '__main__':
    print("🌐 PROXY MASTER NODE IS ONLINE.")
    print("👀 PANOPTICON DASHBOARD AVAILABLE AT: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)