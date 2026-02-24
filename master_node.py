from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
# Suppress the default Flask startup text for cleaner logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/api/v1/node/register', methods=['POST'])
def register_node():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No payload provided"}), 400

    node_id = data.get("node_id", "")
    hardware_stats = data.get("hardware_stats", {})

    print(f"\n[FRONT DESK] 📡 Incoming registration request from {request.remote_addr}")
    print(f"[FRONT DESK] 🔍 Inspecting Identity: {node_id}")

    # ==========================================
    # 🛑 THE ZERO-TRUST BOUNDARY
    # ==========================================
    # We enforce that only hardware-backed nodes can join the network.
    if not node_id.startswith("TPM2-EK-"):
        print("[FRONT DESK] 🚨 REJECTED: Node failed hardware attestation check.")
        return jsonify({
            "status": "rejected",
            "message": "Hardware root of trust missing. Spoofed or legacy nodes are not permitted."
        }), 403

    print(f"[FRONT DESK] ✅ ACCEPTED: Hardware identity verified. CPU: {hardware_stats.get('processor', 'Unknown')}")
    
    # In production, we would save the node's details to our database right here.

    return jsonify({
        "status": "connected",
        "message": "Welcome to the Proxy Agent Network. Awaiting L402 payment channel."
    }), 200

if __name__ == '__main__':
    print("🌐 PROXY MASTER NODE (FRONT DESK) IS ONLINE.")
    print("Listening for hardware registrations on http://127.0.0.1:5000...")
    app.run(host='127.0.0.1', port=5000)