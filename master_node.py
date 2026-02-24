from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ==========================================
# 🏦 THE TREASURY (Simulated)
# ==========================================
# In production, this is a real LND node channel balance
treasury_balance_sats = 1000000 

@app.route('/api/v1/node/register', methods=['POST'])
def register_node():
    data = request.get_json()
    node_id = data.get("node_id", "")
    
    if not node_id.startswith("TPM2-EK-"):
        return jsonify({"status": "rejected", "message": "Hardware root of trust missing."}), 403

    print(f"\n[FRONT DESK] ✅ ACCEPTED: Hardware identity {node_id} verified.")
    return jsonify({"status": "connected", "message": "Welcome to the Proxy Agent Network."}), 200

@app.route('/api/v1/task/request', methods=['POST'])
def dispatch_task():
    """Layer 4 Managers dispatching work to the hardware node."""
    data = request.get_json()
    node_id = data.get("node_id", "")

    # Generate a random task and bounty
    task_id = f"TASK-{random.randint(1000, 9999)}"
    bounty = random.randint(10, 50) # SATS

    print(f"[MANAGERS] 📋 Dispatching {task_id} to {node_id[:15]}... (Bounty: {bounty} SATS)")

    return jsonify({
        "task_id": task_id,
        "prompt": "Analyze legal clause 4.2 for compliance.",
        "payout_sats": bounty
    }), 200

@app.route('/api/v1/task/submit', methods=['POST'])
def submit_task_and_pay():
    """The atomic swap: Node provides the answer and an invoice. We pay it."""
    global treasury_balance_sats
    data = request.get_json()
    
    node_id = data.get("node_id")
    invoice = data.get("invoice")
    
    print(f"[TREASURY] 💸 Routing Lightning Payment for invoice: {invoice[:15]}...")
    
    # Simulate the LND payment channel settling
    treasury_balance_sats -= 25 # Simulated average deduction
    print(f"[TREASURY] ✅ Payment Sent. (Treasury Remaining: {treasury_balance_sats} SATS)")

    # In L402, paying the invoice reveals the cryptographic Preimage
    return jsonify({
        "status": "paid",
        "preimage": "0xDEADBEEF_SIMULATED_PREIMAGE"
    }), 200

if __name__ == '__main__':
    print("🌐 PROXY MASTER NODE (FRONT DESK & TREASURY) IS ONLINE.")
    print("Listening on http://127.0.0.1:5000...")
    app.run(host='127.0.0.1', port=5000)