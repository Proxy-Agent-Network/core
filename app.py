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
