import argparse
import hmac
import hashlib
import time
import json
import requests
import uuid

# PROXY PROTOCOL - WEBHOOK SIMULATOR v1.0
# "Test your listeners before you go live."

GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m'

def sign_payload(secret: str, timestamp: str, payload_body: str) -> str:
    """
    Computes the HMAC-SHA256 signature for the request.
    Format: hmac(secret, timestamp + "." + raw_json)
    """
    message = f"{timestamp}.{payload_body}"
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def generate_mock_payload(event_type: str) -> dict:
    """Generates realistic mock data based on event type."""
    task_id = f"task_mock_{uuid.uuid4().hex[:8]}"
    
    base_event = {
        "id": f"evt_{uuid.uuid4().hex}",
        "object": "event",
        "created": int(time.time()),
        "type": event_type,
        "data": {}
    }

    if event_type == "task.completed":
        base_event["data"] = {
            "task_id": task_id,
            "status": "completed",
            "result": {
                "summary": "Document successfully signed and notarized.",
                "proof_url": "https://ipfs.proxy.network/ipfs/QmMockHash123",
                "human_signature": "3045022100...mock...sig"
            }
        }
    elif event_type == "task.failed":
        base_event["data"] = {
            "task_id": task_id,
            "status": "failed",
            "reason": "Human Node timed out (4h SLA exceeded).",
            "refund_tx": "tx_btc_mock_refund_99"
        }
    elif event_type == "task.matched":
        base_event["data"] = {
            "task_id": task_id,
            "status": "matching",
            "node_id": "node_pubkey_mock_alpha",
            "estimated_completion": "15m"
        }
    elif event_type == "escrow.locked":
        base_event["data"] = {
            "invoice_hash": "lnbc1...mock...invoice",
            "amount_sats": 5000,
            "status": "held"
        }
    
    return base_event

def main():
    parser = argparse.ArgumentParser(description="Simulate Proxy Protocol Webhooks")
    parser.add_argument("--url", required=True, help="Your local or staging endpoint (e.g. http://localhost:8000/webhook)")
    parser.add_argument("--secret", required=True, help="The webhook signing secret (whsec_...)")
    parser.add_argument("--event", default="task.completed", 
                        choices=["task.completed", "task.failed", "task.matched", "escrow.locked"],
                        help="The type of event to simulate")
    
    args = parser.parse_args()

    # 1. Prepare Payload
    print(f"[*] Generating mock event: {args.event}")
    payload_dict = generate_mock_payload(args.event)
    payload_json = json.dumps(payload_dict)
    
    # 2. Sign Request
    timestamp = str(int(time.time()))
    signature = sign_payload(args.secret, timestamp, payload_json)
    
    headers = {
        "Content-Type": "application/json",
        "X-Proxy-Signature": signature,
        "X-Proxy-Request-Timestamp": timestamp,
        "User-Agent": "ProxyProtocol-Simulator/1.0"
    }

    # 3. Transmit
    print(f"[*] Targeting: {args.url}")
    print(f"[*] Signature: {signature[:10]}...")
    
    try:
        start_time = time.time()
        response = requests.post(args.url, data=payload_json, headers=headers, timeout=5)
        duration = (time.time() - start_time) * 1000

        print(f"[*] Latency: {duration:.0f}ms")
        
        if response.status_code >= 200 and response.status_code < 300:
            print(f"{GREEN}[SUCCESS] Server responded {response.status_code}{NC}")
        else:
            print(f"{RED}[FAILURE] Server responded {response.status_code}{NC}")
            print(f"Response Body: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"{RED}[ERROR] Could not connect to {args.url}{NC}")
        print("Is your server running? If testing localhost, ensure it's listening on the correct port.")

if __name__ == "__main__":
    main()
