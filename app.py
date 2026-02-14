from flask import Flask, request, jsonify
from verifier import ProxyRegistryVerifier
import uuid

app = Flask(__name__)
verifier = ProxyRegistryVerifier()

# In-memory store for nonces (In prod, use Redis)
issued_nonces = {}

@app.route('/api/v1/auth/challenge', methods=['GET'])
def get_challenge():
    """
    Step 1: Node requests a nonce to sign.
    """
    nonce = uuid.uuid4().hex
    # Store nonce with a timestamp (logic for expiration can be added)
    issued_nonces[nonce] = True 
    return jsonify({"nonce": nonce, "ttl": 300})

@app.route('/api/v1/nodes/enroll', methods=['POST'])
def enroll_node():
    """
    Step 2: Node submits the TPM quote and hardware manifest.
    """
    payload = request.json
    if not payload:
        return jsonify({"error": "Missing payload"}), 400

    # Validate that the nonce was actually issued by us
    nonce = payload.get("hardware_manifest", {}).get("nonce")
    if nonce not in issued_nonces:
        return jsonify({"error": "Invalid or expired nonce"}), 403

    # Run the verification logic we wrote in verifier.py
    registration_result = verifier.verify_enrollment(payload)

    if registration_result["status"] == "SUCCESS":
        # Remove used nonce to prevent replay attacks
        del issued_nonces[nonce]
        return jsonify(registration_result), 201
    else:
        return jsonify(registration_result), 401

if __name__ == '__main__':
    # Running on 0.0.0.0 makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)

# Add this to core/app.py

@app.route('/api/v1/tasks/post', methods=['POST'])
def post_task():
    """
    Endpoint for Autonomous Agents to post a new 'Bid' for physical execution.
    """
    data = request.json
    # In prod, we would verify the Agent's signature and Lightning Balance here
    
    new_task = {
        "task_id": f"TASK-{uuid.uuid4().hex[:8].upper()}",
        "status": "OPEN",
        "bid_sats": data.get("bid_sats"),
        "type": data.get("type"),
        "required_tier": data.get("tier", 1),
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Save to database (Next step: Update schema)
    # save_task_to_db(new_task)
    
    print(f"[!] New Bid Received: {new_task['task_id']} for {new_task['bid_sats']} Sats")
    return jsonify(new_task), 201
