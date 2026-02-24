from flask import Flask, request, jsonify, render_template_string
import logging
import random
import time
import hmac
import hashlib

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ==========================================
# 📊 THE PANOPTICON STATE
# ==========================================
network_state = {
    "treasury_balance": 1000000,
    "active_nodes": {},
    "ledger": [],
    "completed_tasks": set()
}

# ==========================================
# ⚡ LND GATEWAY (Simulated L402 Settlement)
# ==========================================
class LightningGateway:
    @staticmethod
    def pay_invoice(invoice_string: str):
        """
        Simulates passing the invoice to a local Bitcoin Lightning Node.
        In production: response = lnd_client.pay_invoice(invoice_string)
        """
        if not invoice_string.startswith("lnbc"):
            raise ValueError("Invalid Lightning Invoice format.")
            
        try:
            # Extract the amount for our internal ledger simulation
            amount_str = invoice_string.split('u1')[0].replace('lnbc', '')
            amount = int(amount_str)
            
            # Extract the payment hash from the invoice (the mock part after 'u1')
            payment_hash = invoice_string.split('u1')[1]
            
            # Simulate the cryptographic Preimage returned by the Lightning Network
            # In L402, the hash of the Preimage MUST equal the payment_hash.
            simulated_preimage = f"PREIMAGE_FOR_{payment_hash}"
            
            return amount, simulated_preimage
        except Exception:
            raise ValueError("Invoice decoding failed.")

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
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No payload"}), 400

    node_id = data.get("node_id", "")
    timestamp = data.get("timestamp", "")
    signature = data.get("signature", "")
    
    # 1. The basic prefix check
    if not node_id.startswith("TPM2-EK-"):
        return jsonify({"status": "rejected", "message": "Hardware root of trust missing."}), 403

    # ==========================================
    # 🛑 THE ZERO-TRUST BOUNDARY (ATTESTATION)
    # ==========================================
    # In production, the Master Node verifies the signature against the TPM's Public Key.
    # Here, we simulate it with a shared cryptographic seed.
    tpm_seed = b"simulated_hardware_seed_0x99"
    expected_sig = hmac.new(tpm_seed, f"{node_id}:{timestamp}".encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(str(signature), expected_sig):
        print(f"\n[FRONT DESK] 🚨 REJECTED: Cryptographic signature invalid for {node_id}")
        return jsonify({"status": "rejected", "message": "Hardware attestation failed. Spoofing detected."}), 403

    # Add the node to our active tracking state
    if node_id not in network_state["active_nodes"]:
        network_state["active_nodes"][node_id] = {"tasks_completed": 0, "total_earned": 0}
        
    print(f"\n[FRONT DESK] ✅ ACCEPTED: Hardware identity and signature verified for {node_id[:20]}...")
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
    # Fixed: Simply call request.get_json()
    data = request.get_json(force=True, silent=True) 
    
    if not data:
         return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400
         
    node_id = data.get("node_id")
    task_id = data.get("task_id")
    
    # ==========================================
    # 🛑 THE ZERO-TRUST BOUNDARY (ANTI-REPLAY)
    # ==========================================
    if task_id in network_state["completed_tasks"]:
        print(f"[SECURITY] 🚨 REPLAY ATTACK BLOCKED! Node {node_id[:15]} attempted double-spend on {task_id}.")
        return jsonify({
            "status": "rejected",
            "message": "Idempotency collision. Task already settled."
        }), 409
        
    # Mark the task as settled so it can never be paid again
    network_state["completed_tasks"].add(task_id)
    
    invoice = data.get("invoice", "")

    # ==========================================
    # 🛑 THE ZERO-TRUST BOUNDARY (L402 SETTLEMENT)
    # ==========================================
    try:
        # We NO LONGER trust the invoice. We force the LND gateway to settle it.
        amount, preimage = LightningGateway.pay_invoice(invoice)
    except ValueError as e:
        print(f"[TREASURY] 🚨 FRAUD DETECTED: Invalid L402 invoice from {node_id[:15]}")
        # We must remove the task from completed_tasks so the node can try again legitimately
        network_state["completed_tasks"].remove(task_id) 
        return jsonify({"status": "rejected", "message": str(e)}), 402

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
    
    # Return the cryptographic preimage as proof of payment
    return jsonify({"status": "paid", "preimage": preimage}), 200

if __name__ == '__main__':
    print("🌐 PROXY MASTER NODE IS ONLINE.")
    print("👀 PANOPTICON DASHBOARD AVAILABLE AT: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)