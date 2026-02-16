import hashlib
import secrets
import time
import requests
import os
import base64
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List

# PROXY PROTOCOL - HODL ESCROW STATE MACHINE (v2.0)
# "Mainnet-ready LND HODL invoice lifecycle integration."
# ----------------------------------------------------

class EscrowState(Enum):
    OPEN = "OPEN"               # Invoice created, awaiting payer
    ACCEPTED = "ACCEPTED"       # Payment HELD by LND (HTLC locked)
    IN_PROGRESS = "IN_PROGRESS" # Human Node has accepted work
    SETTLED = "SETTLED"         # Preimage revealed; Satoshis moved
    CANCELLED = "CANCELLED"     # Timed out or manually cancelled

@dataclass
class HodlContract:
    contract_id: str
    payment_hash: str
    preimage: str           # HELD SERVER-SIDE
    amount_sats: int
    agent_id: str
    task_id: str
    expiry: int
    state: EscrowState = EscrowState.OPEN
    node_id: Optional[str] = None
    lnd_payment_request: str = ""

class EscrowManager:
    """
    Coordinates the real-time lifecycle of HODL invoices via LND REST API.
    """
    def __init__(self, lnd_host: str = None, macaroon: str = None, cert: str = None):
        self.contracts: Dict[str, HodlContract] = {}
        self.task_map: Dict[str, str] = {}
        
        # LND Backend Credentials
        self.lnd_host = lnd_host or os.getenv("LND_REST_HOST", "127.0.0.1:8080")
        self.macaroon = macaroon or os.getenv("LND_ADMIN_MACAROON_HEX", "")
        self.cert = cert or os.getenv("LND_TLS_CERT_PATH", "")

    def _lnd_request(self, method: str, path: str, body: dict = None):
        """Helper to communicate with the physical LND node."""
        url = f"https://{self.lnd_host}{path}"
        headers = {"Grpc-Metadata-macaroon": self.macaroon}
        verify = self.cert if self.cert and os.path.exists(self.cert) else False
        
        try:
            if method == "POST":
                return requests.post(url, json=body, headers=headers, verify=verify, timeout=10).json()
            return requests.get(url, headers=headers, verify=verify, timeout=10).json()
        except Exception as e:
            return {"error": str(e)}

    def create_hodl_invoice(self, agent_id: str, task_id: str, amount: int) -> Dict:
        """
        Calls LND to create a real HODL invoice.
        """
        preimage = secrets.token_bytes(32)
        payment_hash = hashlib.sha256(preimage).hexdigest()
        
        # 1. Register with LND (HODL endpoint)
        lnd_payload = {
            "hash": base64.b64encode(bytes.fromhex(payment_hash)).decode(),
            "value": amount,
            "memo": f"Proxy Task: {task_id}",
            "expiry": 14400 # 4 hours
        }
        
        lnd_response = self._lnd_request("POST", "/v1/invoices/hodl", lnd_payload)
        bolt11 = lnd_response.get("payment_request")

        if not bolt11:
            raise RuntimeError(f"Failed to generate HODL invoice: {lnd_response.get('error')}")

        # 2. Store internal state
        contract = HodlContract(
            contract_id=f"escrow_{payment_hash[:12]}",
            payment_hash=payment_hash,
            preimage=preimage.hex(),
            amount_sats=amount,
            agent_id=agent_id,
            task_id=task_id,
            expiry=int(time.time()) + 14400,
            lnd_payment_request=bolt11
        )
        
        self.contracts[payment_hash] = contract
        self.task_map[task_id] = payment_hash
        
        return {"payment_hash": payment_hash, "bolt11": bolt11}

    def sync_invoice_state(self, payment_hash: str):
        """
        Polls LND to see if the Agent has paid and the funds are 'ACCEPTED'.
        """
        contract = self.contracts.get(payment_hash)
        if not contract or contract.state in [EscrowState.SETTLED, EscrowState.CANCELLED]:
            return

        # Lookup invoice status in LND
        lnd_data = self._lnd_request("GET", f"/v1/invoice/{payment_hash}")
        lnd_state = lnd_data.get("state") # OPEN, SETTLED, ACCEPTED, CANCELED

        if lnd_state == "ACCEPTED" and contract.state == EscrowState.OPEN:
            contract.state = EscrowState.ACCEPTED
            print(f"[Escrow] 🔒 HTLC LOCK DETECTED for {contract.task_id}. Dispatching.")
        elif lnd_state == "SETTLED":
            contract.state = EscrowState.SETTLED
        elif lnd_state == "CANCELED":
            contract.state = EscrowState.CANCELLED

    def release_preimage(self, payment_hash: str) -> bool:
        """
        Final step: Reveal the secret to settle the invoice and pay the node.
        """
        contract = self.contracts.get(payment_hash)
        if not contract or contract.state != EscrowState.ACCEPTED:
            return False

        # POST /v1/invoices/settle
        payload = {"preimage": base64.b64encode(bytes.fromhex(contract.preimage)).decode()}
        resp = self._lnd_request("POST", "/v1/invoices/settle", payload)
        
        if "error" not in resp:
            contract.state = EscrowState.SETTLED
            return True
        return False
