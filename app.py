from flask import Flask, request, jsonify
from verifier import ProxyRegistryVerifier
import uuid
from datetime import datetime

app = Flask(__name__)
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
        return jsonify({"error": "Invalid nonce"}), 403
    
    result = verifier.verify_enrollment(payload)
    if result["status"] == "SUCCESS":
        del issued_nonces[nonce]
    return jsonify(result)

# --- ADD THIS NEW SECTION BELOW ---

@app.route('/api/v1/tasks/post', methods=['POST'])
def post_task():
    """Endpoint for Agents to post a new Bid."""
    data = request.json
    agent_id = data.get("agent_id", "UNKNOWN_AGENT")
    task_type = data.get("type", "GENERAL")
    bid_sats = data.get("bid_sats", 0)

    # Use the verifier to save the task to the database
    task_id = verifier.create_task(agent_id, task_type, bid_sats)
    
    return jsonify({
        "status": "SUCCESS",
        "task_id": task_id,
        "message": "Task posted to Order Book"
    }), 201

# ----------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
