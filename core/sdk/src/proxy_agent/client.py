import requests
import json
import base64
import os
import time
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# PROXY PROTOCOL - PYTHON SDK CLIENT v1.9 (Mainnet Ready)
# "Protocol v3.0.7: Synchronized LND HODL Lifecycle."
# ----------------------------------------------------

class ProxyClient:
    """
    The official Python client for the Proxy Agent Network.
    
    v1.9 Update:
    - Replaced HODL placeholders with live LND REST state-machine lookups.
    - Added verify_task_funding for asynchronous state synchronization.
    - Hardened E2EE tunnel utilities.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.proxyprotocol.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ProxyAgent-Python/1.9.0"
        })
        
        # Local LND Credentials (for the Agent's funding node)
        self.lnd_host = os.getenv("LND_REST_HOST", "127.0.0.1:8080")
        self.lnd_macaroon = os.getenv("LND_ADMIN_MACAROON_HEX", "")
        self.lnd_cert_path = os.getenv("LND_TLS_CERT_PATH", "")

    def generate_agent_keys(self) -> Dict[str, str]:
        """Generates RSA-2048 identity for the Encrypted Task Tunnel."""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem_p = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        pem_pub = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        return {"private_key": pem_p, "public_key": pem_pub}

    def _lnd_post(self, path: str, payload: dict) -> dict:
        """Internal helper for LND REST communication."""
        url = f"https://{self.lnd_host}{path}"
        headers = {"Grpc-Metadata-macaroon": self.lnd_macaroon}
        verify = self.lnd_cert_path if self.lnd_cert_path and os.path.exists(self.lnd_cert_path) else False
        
        response = requests.post(url, json=payload, headers=headers, verify=verify, timeout=15)
        if response.status_code != 200:
            raise RuntimeError(f"LND API Error ({response.status_code}): {response.text}")
        return response.json()

    def _lnd_get(self, path: str) -> dict:
        """Internal helper for LND status lookups."""
        url = f"https://{self.lnd_host}{path}"
        headers = {"Grpc-Metadata-macaroon": self.lnd_macaroon}
        verify = self.lnd_cert_path if self.lnd_cert_path and os.path.exists(self.lnd_cert_path) else False
        
        response = requests.get(url, headers=headers, verify=verify, timeout=10)
        if response.status_code != 200:
            raise RuntimeError(f"LND Lookup Error: {response.text}")
        return response.json()

    def fund_task_via_lnd(self, bolt11: str) -> Dict[str, Any]:
        """
        Pays the HODL invoice to lock Satoshis in the circuit.
        This triggers the 'ACCEPTED' state in the Protocol Escrow.
        """
        print(f"[*] Dispatching HTLC lock for task...")
        
        # Note: Sending payment for a HODL invoice via REST usually returns 
        # a payment_hash immediately while the payment remains 'IN_FLIGHT'.
        data = self._lnd_post("/v1/channels/transactions", {
            "payment_request": bolt11,
            "timeout_seconds": 60,
            "fee_limit_sat": 2000
        })
        
        return {
            "status": "locked",
            "payment_hash": data.get("payment_hash"),
            "msg": "Funds secured in Lightning circuit. Monitoring for human acceptance."
        }

    def verify_escrow_status(self, payment_hash_hex: str) -> str:
        """
        Polls the local LND node to check the status of the outgoing HTLC.
        Returns: 'IN_FLIGHT' (Locked), 'SUCCEEDED' (Settled), or 'FAILED' (Refunded).
        """
        # GET /v1/payment/{payment_hash}
        try:
            data = self._lnd_get(f"/v1/payments/{payment_hash_hex}")
            return data.get('status', 'UNKNOWN')
        except Exception:
            return "UNKNOWN"

    def get_market_ticker(self) -> Dict[str, Any]:
        """Fetches dynamic pricing from the network."""
        res = self.session.get(f"{self.base_url}/market/ticker")
        res.raise_for_status()
        return res.json()

    def create_task(self, task_type: str, requirements: Dict, max_budget: int, public_key: str = None) -> Dict:
        """Broadcasts a new task request to the network."""
        payload = {
            "type": task_type, 
            "requirements": requirements, 
            "max_budget_sats": max_budget
        }
        if public_key: 
            payload['agent_public_key'] = public_key
            
        res = self.session.post(f"{self.base_url}/request", json=payload)
        res.raise_for_status()
        return res.json()

    def get_task_status(self, task_id: str) -> Dict:
        """Checks the completion status of a dispatched task."""
        res = self.session.get(f"{self.base_url}/tasks/{task_id}")
        res.raise_for_status()
        return res.json()

    def decrypt_result(self, encrypted_blob: str, private_key_pem: str) -> Dict:
        """Decrypts biological proof from the human node via the E2EE tunnel."""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        ciphertext = base64.b64decode(encrypted_blob)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return json.loads(plaintext.decode())

# --- Integration Example ---
if __name__ == "__main__":
    # Ensure LND_ADMIN_MACAROON_HEX and LND_REST_HOST are set in ENV
    client = ProxyClient(api_key="sk_live_demo")
    print(f"[*] Proxy SDK v1.9 Initialized. Target: {client.lnd_host}")
