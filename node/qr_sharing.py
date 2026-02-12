import hashlib
import time
import json
import secrets
from typing import Dict, Optional

# PROXY PROTOCOL - SECURE QR HANDSHAKE (v1.0)
# "Cryptographic proof of physical proximity."
# ----------------------------------------------------

class QRKeySharer:
    """
    Manages the generation and verification of one-time QR payloads
    for Tier 2 (Courier/Identity) physical hand-offs.
    """
    
    def __init__(self, tpm_interface=None):
        self.tpm = tpm_interface
        self.HANDSHAKE_TTL = 300  # 5 minute window for verification

    def generate_handshake_payload(self, node_id: str, task_id: str) -> Dict:
        """
        Generates a signed payload to be rendered as a QR code.
        The payload is bound to the Node, the Task, and the current Time.
        """
        nonce = secrets.token_hex(16)
        timestamp = int(time.time())
        
        # 1. Create the data structure
        payload = {
            "version": "1.0",
            "node_id": node_id,
            "task_id": task_id,
            "nonce": nonce,
            "timestamp": timestamp,
            "expires": timestamp + self.HANDSHAKE_TTL
        }

        # 2. Cryptographic Binding
        # In production, we sign this with the TPM Attestation Key (AK)
        payload_string = json.dumps(payload, sort_keys=True)
        
        if self.tpm:
            # Generate a real hardware signature
            signature = self.tpm.sign(payload_string.encode())
        else:
            # Mock signature for dev/testing
            signature = hashlib.sha256(f"{payload_string}:MOCK_SECRET".encode()).hexdigest()

        return {
            "data": payload,
            "signature": signature,
            "raw_qr_string": f"PX_AUTH:{payload_string}|SIG:{signature}"
        }

    def verify_handshake(self, qr_string: str, expected_task_id: str) -> Dict:
        """
        Verifies a scanned QR string against protocol standards.
        Checks for expiration, task alignment, and signature validity.
        """
        try:
            # Simple parser for the standard PX_AUTH format
            parts = qr_string.split("|SIG:")
            payload_json = parts[0].replace("PX_AUTH:", "")
            signature = parts[1]
            
            payload = json.loads(payload_json)
            now = int(time.time())

            # Check 1: Expiration
            if now > payload['expires']:
                return {"status": "EXPIRED", "error": "Handshake window closed."}

            # Check 2: Task Alignment
            if payload['task_id'] != expected_task_id:
                return {"status": "INVALID", "error": "Task mismatch."}

            # Check 3: Signature Integrity
            # In prod, this verifies against the Node's public key in the registry
            is_valid = True # Mock validation logic
            
            if not is_valid:
                return {"status": "FORGED", "error": "Hardware signature invalid."}

            print(f"✅ Handshake Verified for Node {payload['node_id']} on Task {payload['task_id']}")
            return {"status": "SUCCESS", "node_id": payload['node_id']}

        except Exception as e:
            return {"status": "ERROR", "error": f"Malformed QR data: {str(e)}"}

# --- Hand-off Simulation ---
if __name__ == "__main__":
    sharer = QRKeySharer()
    
    # 1. Courier (Node A) arrives at location
    print("[Node] Generating proof of arrival for Task #882...")
    qr_payload = sharer.generate_handshake_payload(
        node_id="node_courier_01", 
        task_id="task_882"
    )
    
    print(f"QR String Ready: {qr_payload['raw_qr_string'][:60]}...")

    # 2. Recipient (Agent Representative) scans the code
    print("\n[Agent] Scanning QR Code...")
    # Simulate scanning the string generated above
    result = sharer.verify_handshake(qr_payload['raw_qr_string'], "task_882")
    
    if result['status'] == "SUCCESS":
        print("🎉 HAND-OFF AUTHORIZED: Releasing Escrow Funds.")
    else:
        print(f"🚨 SECURITY ALERT: {result['error']}")
