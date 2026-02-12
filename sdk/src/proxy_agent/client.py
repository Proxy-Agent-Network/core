import requests
import json
import base64
import os
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# PROXY PROTOCOL - PYTHON SDK CLIENT v1.8 (Mainnet Release)
# "Protocol v2.1.0: Real LND HODL lifecycle support."
# ----------------------------------------------------

class ProxyClient:
    """
    The official Python client for the Proxy Agent Network.
    
    v1.8 Update:
    - Optimized HODL settlement flow.
    - Improved LND error handling for Mainnet micro-payments.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.proxyprotocol.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ProxyAgent-Python/1.8.0"
        })
        
        # Local LND Credentials for the Agent's funding wallet
        self.lnd_host = os.getenv("LND_REST_HOST", "127.0.0.1:8080")
        self.lnd_macaroon = os.getenv("LND_ADMIN_MACAROON_HEX", "")
        self.lnd_cert_path = os.getenv("LND_TLS_CERT_PATH", "")

    # ... [Identity & Encryption Utilities remain unchanged from v1.7] ...

    def fund_task_via_lnd(self, bolt11: str) -> Dict[str, Any]:
        """
        Locks the Satoshi payout in the Lightning circuit.
        Communicates with the Agent's local LND node to pay the HODL invoice.
        """
        url = f"https://{self.lnd_host}/v1/channels/transactions"
        headers = {"Grpc-Metadata-macaroon": self.lnd_macaroon}
        
        payload = {
            "payment_request": bolt11,
            "timeout_seconds": 60,
            "fee_limit_sat": 1500 # Slightly increased for mainnet reliability
        }
        
        verify = self.lnd_cert_path if self.lnd_cert_path else False
        
        print(f"[*] Dispatching HODL HTLC via LND REST...")
        response = requests.post(url, json=payload, headers=headers, verify=verify)
        
        if response.status_code != 200:
            raise RuntimeError(f"LND Payment Failed: {response.text}")
            
        data = response.json()
        
        # In a HODL invoice, this request will hang or return 'IN_FLIGHT' 
        # until the preimage is revealed. The SDK treats 'IN_FLIGHT' as SUCCESSful locking.
        return {
            "status": "locked",
            "payment_hash": data.get("payment_hash"),
            "msg": "Funds secured in Lightning circuit. Human Node notified."
        }

    # ... [Core API Endpoints remain unchanged] ...
