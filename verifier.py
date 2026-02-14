import base64
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VerifiedNode:
    node_id: str
    hardware_id: str
    enrolled_at: str
    status: str

class ProxyRegistryVerifier:
    def __init__(self):
        # In prod, this would be a database (SQLite or PostgreSQL)
        self.registry = {}
        self.issued_nonces = set()

    def verify_enrollment(self, payload):
        """
        Validates the hardware proof from the node script.
        """
        node_id_candidate = payload.get("node_id")
        manifest = payload.get("hardware_manifest")
        
        # 1. Nonce Integrity Check
        # Prevents an attacker from reusing a valid old signature
        nonce = manifest.get("nonce")
        # if nonce not in self.issued_nonces:
        #    return {"status": "REJECTED", "reason": "INVALID_OR_EXPIRED_NONCE"}

        # 2. Cryptographic Quote Verification
        # In a real TPM handshake, we use OpenSSL to verify the signature blob
        # against the AK public key.
        quote = manifest.get("pcr_quote")
        is_signature_valid = self._mock_crypto_verify(
            quote['message'], 
            quote['signature'], 
            manifest['ak_public']
        )

        if not is_signature_valid:
            return {"status": "REJECTED", "reason": "HARDWARE_SIGNATURE_MISMATCH"}

        # 3. Successful Enrollment
        new_id = f"NODE-{base64.b16encode(datetime.now().strftime('%f').encode()).decode()[:8]}"
        
        node_data = VerifiedNode(
            node_id=new_id,
            hardware_id=manifest['ek_public'], # Using EK as unique HW fingerprint
            enrolled_at=datetime.utcnow().isoformat(),
            status="VERIFIED"
        )

        self.registry[new_id] = node_data
        
        print(f"[+] Node {new_id} added to the Satoshi Standard Registry.")
        return {"status": "SUCCESS", "node_id": new_id, "manifest": vars(node_data)}

    def _mock_crypto_verify(self, message, signature, pub_key):
        """
        Placeholder for the actual RSA-PSS verification logic.
        Once hardware arrives, we replace this with the 'tpm2_checkquote' wrapper.
        """
        return True # Defaulting to True for sandbox testing

if __name__ == "__main__":
    # Test simulation
    verifier = ProxyRegistryVerifier()
    
    # Mock payload coming from the client enroll.py
    test_payload = {
        "node_id": "PENDING",
        "hardware_manifest": {
            "ek_public": "INF_TPM_EK_BLOB_882",
            "ak_public": "INF_TPM_AK_BLOB_004",
            "pcr_quote": {"message": "...", "signature": "..."},
            "nonce": "TEST_NONCE_123"
        }
    }
    
    result = verifier.verify_enrollment(test_payload)
    print(json.dumps(result, indent=4))
