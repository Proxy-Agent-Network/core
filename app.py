from flask import Flask, request, jsonify
from verifier import ProxyRegistryVerifier
import uuid
from datetime import datetime

app = Flask(__name__)
# This assumes verifier.py is in the same folder
verifier = ProxyRegistryVerifier()

issued_nonces = {}

@app.route('/api/v1/auth/challenge', methods=['GET'])
def get_challenge():
    nonce = uuid.uuid4().hex
    issued_nonces[nonce] = True 
    return jsonify({"nonce": nonce, "ttl": 300})

@app.route('/api/v1/nodes/enroll', methods=['POST'])
def enroll_node():
    payload = request.json
    nonce = payload.get("hardware_manifest", {}).get("nonce")
    if nonce not in issued_nonces:
        return jsonify({"error": "Invalid or expired nonce"}), 403
    result = verifier.verify_enrollment(payload)
    return jsonify(result)

# --- THE CRITICAL ROUTE ---
@app.route('/api/v1/tasks/post', methods=['POST'])
def post_task():
    data = request.json
    agent_id = data.get("agent_id", "UNKNOWN_AGENT")
    task_type = data.get("type", "GENERAL")
    bid_sats = data.get("bid_sats", 0)

    # This calls the create_task function in your verifier.py
    task_id = verifier.create_task(agent_id, task_type, bid_sats)
    
    print(f"[*] Task Created: {task_id} for {agent_id}")
    return jsonify({
        "status": "SUCCESS",
        "task_id": task_id,
        "message": "Task posted to Order Book"
    }), 201

if __name__ == '__main__':
    # host 0.0.0.0 lets your Raspberry Pi find this later
    app.run(host='0.0.0.0', port=5000, debug=True)
