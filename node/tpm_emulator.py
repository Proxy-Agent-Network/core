import os
import json
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# PROXY PROTOCOL - SOFTWARE TPM EMULATOR (v1)
# "Fake it 'til you make it (on hardware)."
# ----------------------------------------------------
# Dependencies: pip install cryptography
# WARNING: DO NOT USE IN PRODUCTION. KEYS ARE STORED ON DISK.

class TPMEmulator:
    def __init__(self, storage_path="./soft_tpm_storage.json"):
        self.storage_path = storage_path
        self.keys = {}
        self._load_storage()
        
        # Standard Handles matching the Hardware spec
        self.EK_HANDLE = "0x81010001"
        self.AK_HANDLE = "0x81010002"

    def _load_storage(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                self.keys = json.load(f)

    def _save_storage(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.keys, f, indent=2)

    def check_availability(self) -> bool:
        """Always returns True for the Emulator."""
        print("[SoftTPM] Virtual Hardware Ready.")
        return True

    def perform_binding_ceremony(self) -> dict:
        """
        Simulates the hardware key generation ceremony.
        Instead of an Infineon chip, we use OpenSSL logic.
        """
        print("[SoftTPM] Initializing Virtual Ceremony...")
        
        # Generate RSA Key (Simulating the Identity Key)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Serialize Private Key (Insecure storage for dev)
        # In the real hardware, this never leaves the chip.
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        # Serialize Public Key
        pem_public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        # Store in "Virtual NVRAM" (JSON file)
        self.keys[self.AK_HANDLE] = {
            "private": pem_private,
            "public": pem_public,
            "created": datetime.now().isoformat()
        }
        self._save_storage()

        print("[SoftTPM] Identity Key Generated & Persisted to Disk.")
        
        return {
            "status": "BOUND (SOFTWARE)",
            "handle": self.AK_HANDLE,
            "public_key_pem": pem_public,
            "hardware_proof": "mock_tpm_quote_software_mode" 
        }

    def sign_heartbeat(self, timestamp: str, status: str) -> str:
        """
        Signs a payload using the software key.
        Matches the output format of the real hardware.
        """
        if self.AK_HANDLE not in self.keys:
            raise RuntimeError("SoftTPM not bound. Run ceremony first.")

        # Load Key
        pem_private = self.keys[self.AK_HANDLE]["private"]
        private_key = serialization.load_pem_private_key(
            pem_private.encode('utf-8'),
            password=None
        )

        # Prepare Payload
        payload = f"{timestamp}|{status}".encode('utf-8')
        
        # Sign (PKCS1v15 or PSS depending on TPM config, using PSS here)
        signature = private_key.sign(
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature.hex()

# --- CLI Usage for Developers ---
if __name__ == "__main__":
    tpm = TPMEmulator()
    print("⚠️  RUNNING IN SOFTWARE TPM MODE (DEV ONLY)")
    print("    This allows testing Node logic without a Raspberry Pi.")
    
    identity = tpm.perform_binding_ceremony()
    print(f"\n[+] Public Identity Key:\n{identity['public_key_pem']}")
    
    ts = datetime.now().isoformat()
    sig = tpm.sign_heartbeat(ts, "ONLINE")
    
    print(f"\n[+] Software Signature ({len(sig)} bytes):")
    print(f"{sig[:64]}...[truncated]")
