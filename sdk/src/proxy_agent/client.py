import requests
import json
import base64
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

class ProxyClient:
    """
    The official Python client for the Proxy Agent Network.
    
    v1.1 Update: Includes Encrypted Task Tunnel support for secure 
    decryption of biological and legal proofs.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.proxyprotocol.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ProxyAgent-Python/0.1.1"
        })

    # --- 1. Key Management Utilities ---

    def generate_agent_keys(self) -> Dict[str, str]:
        """
        Generates a new RSA-2048 key pair for the Agent.
        The public key should be passed to create_task() to open an encrypted tunnel.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        pem_public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        return {
            "private_key": pem_private,
            "public_key": pem_public
        }

    # --- 2. Decryption Logic ---

    def decrypt_result(self, encrypted_blob: str, private_key_pem: str) -> Dict[str, Any]:
        """
        v1.1: Decrypts task results from the Encrypted Tunnel.
        Uses RSA-OAEP with SHA-256 as specified in the Node Daemon.
        """
        try:
            # 1. Load Private Key
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None
            )

            # 2. Decode from Base64
            ciphertext = base64.b64decode(encrypted_blob)

            # 3. Decrypt
            plaintext = private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            return json.loads(plaintext.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}. Ensure the private key matches the public key used for the task.")

    # --- 3. Core API Methods ---

    def get_market_ticker(self) -> Dict[str, Any]:
        """Fetch real-time floor prices for human tasks."""
        response = self.session.get(f"{self.base_url}/market/ticker")
        response.raise_for_status()
        return response.json()

    def create_task(self, task_type: str, requirements: Dict[str, Any], max_budget_sats: int, public_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Broadcast a new task to the Human Proxy network.
        
        Args:
            task_type: e.g., 'verify_sms_otp', 'verify_kyc_video'
            requirements: Metadata for the human to complete the task
            max_budget_sats: Maximum price in sats
            public_key: (v1.1) RSA Public Key for result encryption
        """
        payload = {
            "type": task_type,
            "requirements": requirements,
            "max_budget_sats": max_budget_sats
        }
        
        if public_key:
            payload['agent_public_key'] = public_key

        response = self.session.post(f"{self.base_url}/tasks", json=payload)
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Check the progress of a specific task."""
        response = self.session.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()

# --- Example Implementation ---
if __name__ == "__main__":
    # Simulate a developer using the SDK
    client = ProxyClient(api_key="sk_live_demo")
    
    # 1. Create a key pair for the Agent
    keys = client.generate_agent_keys()
    print("[*] Generated Agent Identity (RSA-2048)")
    
    # 2. Create an encrypted task
    print("[*] Requesting Tier 2 KYC task with Encrypted Tunnel...")
    # task = client.create_task("verify_kyc_video", {"tier": 2}, 15000, public_key=keys['public_key'])
    
    # 3. Simulate receiving an encrypted payload (from the Node Daemon output)
    # This is a dummy blob for demonstration
    print("[*] Simulating result decryption...")
    try:
        # In real usage: result = client.decrypt_result(task['encrypted_blob'], keys['private_key'])
        pass
    except Exception:
        pass
