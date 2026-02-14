import base64
import json
import sqlite3
from datetime import datetime
import os

class ProxyRegistryVerifier:
    def __init__(self, db_path="registry.db"):
        self.db_path = db_path
        self._bootstrap_db()

    def _bootstrap_db(self):
        """Initializes the SQLite database and creates the nodes table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    hardware_id TEXT UNIQUE,
                    enrolled_at TEXT,
                    status TEXT,
                    ak_public TEXT
                )
            ''')
            conn.commit()

    def verify_enrollment(self, payload):
        """
        Validates the hardware proof and saves the node to the persistent database.
        """
        manifest = payload.get("hardware_manifest")
        ek_pub = manifest.get("ek_public")
        ak_pub = manifest.get("ak_public")
        quote = manifest.get("pcr_quote")

        # 1. Cryptographic Quote Verification (Placeholder for hardware handshake)
        # In a real TPM handshake, we verify the signature against the ak_public.
        is_signature_valid = self._mock_crypto_verify(
            quote['message'], 
            quote['signature'], 
            ak_pub
        )

        if not is_signature_valid:
            return {"status": "REJECTED", "reason": "HARDWARE_SIGNATURE_MISMATCH"}

        # 2. Check if this Hardware ID (EK) is already registered
        # This prevents the same physical board from claiming multiple Node IDs.
        existing_node = self._get_node_by_hardware_id(ek_pub)
        if existing_node:
            return {
                "status": "SUCCESS", 
                "node_id": existing_node[0], 
                "message": "Node already enrolled. Returning existing ID.",
                "manifest": {
                    "node_id": existing_node[0],
                    "enrolled_at": existing_node[1],
                    "status": existing_node[2]
                }
            }

        # 3. Successful New Enrollment
        new_id = f"NODE-{base64.b16encode(os.urandom(4)).decode()}"
        enrolled_at = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO nodes (node_id, hardware_id, enrolled_at, status, ak_public) VALUES (?, ?, ?, ?, ?)",
                (new_id, ek_pub, enrolled_at, "VERIFIED", ak_pub)
            )
            conn.commit()
        
        print(f"[+] Node {new_id} persisted to Registry DB.")
        return {
            "status": "SUCCESS", 
            "node_id": new_id, 
            "manifest": {
                "node_id": new_id,
                "enrolled_at": enrolled_at,
                "status": "VERIFIED"
            }
        }

    def _get_node_by_hardware_id(self, hardware_id):
        """Looks up a node by its unique TPM Endorsement Key."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT node_id, enrolled_at, status FROM nodes WHERE hardware_id = ?", (hardware_id,))
            return cursor.fetchone()

    def _mock_crypto_verify(self, message, signature, pub_key):
        return True # Defaulting to True for sandbox testing

if __name__ == "__main__":
    # Test simulation
    verifier = ProxyRegistryVerifier()
    test_payload = {
        "hardware_manifest": {
            "ek_public": "TEST_HW_ID_12345",
            "ak_public": "TEST_AK_PUB_BLOB",
            "pcr_quote": {"message": "...", "signature": "..."},
            "nonce": "TEST_NONCE"
        }
    }
    result = verifier.verify_enrollment(test_payload)
    print(json.dumps(result, indent=4))
