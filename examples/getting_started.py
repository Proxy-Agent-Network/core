import os
import time
import json
from dotenv import load_dotenv

# PROXY PROTOCOL - GETTING STARTED v1.7
# "The end-to-end workflow for autonomous agents."
# ----------------------------------------------------

# 1. Setup Environment
# Ensure you have PROXY_API_SECRET, LND_REST_HOST, and LND_ADMIN_MACAROON_HEX set.
load_dotenv()

try:
    # We import from the src layout as established in the repository
    from proxy_agent.client import ProxyClient
except ImportError:
    # Fallback for local development if not installed via pip
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sdk", "src"))
    from proxy_agent.client import ProxyClient

def print_banner():
    print("""
    ____  ____  ____  ____  __ __ 
   (  _ \(  _ \/ __ \(  _ \(  |  )
    )___/ )   (  (__) ))   / )_  ( 
   (__)  (_)\_)\____/(_)\_)(____/ 
          PROTOCOL v1.7
    [ The Physical Runtime for AI ]
    """)

def main():
    print_banner()
    
    # 1. Initialize the Client
    # Uses environment variables for security as per authentication.md
    api_key = os.getenv("PROXY_API_SECRET", "sk_live_demo_key")
    client = ProxyClient(api_key=api_key)
    print("🔌 Uplink established with Proxy Network.")

    # 2. Generate Agent Identity for the Encrypted Tunnel
    # This ensures PII and legal data remains ZK (Zero-Knowledge) to the protocol.
    print("[*] Generating ephemeral RSA-2048 identity...")
    keys = client.generate_agent_keys()
    agent_pubkey = keys['public_key']

    # 3. Check Market Rates
    print("📊 Fetching real-time market ticker...")
    ticker = client.get_market_ticker()
    notary_price = ticker['rates'].get('legal_notary_sign', 45000)
    print(f"   -> Current Notarization Rate: {notary_price} sats")

    # 4. Create an Encrypted Task
    # We pass the public key to open the "Encrypted Task Tunnel" v1.1+
    print(f"\n🚀 Dispatching Task: Delaware Incorporation Signing")
    task = client.create_task(
        task_type="legal_notary_sign",
        requirements={
            "jurisdiction": "US_DE",
            "principal_name": "Genesis AI LLC",
            "document_url": "ipfs://QmYourDocHash..."
        },
        max_budget_sats=50000,
        public_key=agent_pubkey
    )

    task_id = task['id']
    escrow_invoice = task.get('escrow_invoice') # BOLT11 returned by API
    print(f"   -> Task Created: {task_id}")
    print(f"   -> Escrow Invoice: {escrow_invoice[:30]}...")

    # 5. Fund Task via Local LND
    # v1.7: Mathematical settlement. No work begins until HTLC is locked.
    print(f"\n🔒 Locking {notary_price} sats in HODL Escrow...")
    try:
        settlement = client.fund_task_via_lnd(escrow_invoice)
        print(f"   ✅ Funds locked in Lightning circuit (Hash: {settlement['payment_hash'][:12]}...)")
    except Exception as e:
        print(f"   ❌ Funding Failed: {e}")
        return

    # 6. Wait for Physical Execution
    print("\n⌛ Waiting for Human Node to execute task and upload proof...")
    completed_task = None
    attempts = 0
    while attempts < 10:
        status_update = client.get_task_status(task_id)
        if status_update['status'] == 'completed':
            completed_task = status_update
            break
        print(f"   [*] Status: {status_update['status']} (Poll {attempts+1}/10)...", end="\r")
        time.sleep(10)
        attempts += 1

    if not completed_task:
        print("\n[!] Task timing out. Escrow will auto-refund if not settled.")
        return

    # 7. Decrypt and Verify Result
    # Only our private key can unlock this biological/legal proof.
    print(f"\n🔓 Proof Received. Decrypting via Encrypted Tunnel...")
    try:
        encrypted_blob = completed_task['result']['encrypted_blob']
        decrypted_result = client.decrypt_result(encrypted_blob, keys['private_key'])
        
        print("\n--- TASK VERIFIED ---")
        print(f"Node ID: {completed_task['assigned_node_id']}")
        print(f"Legal Hash: {decrypted_result['data']['legal_instrument']['content_hash']}")
        print(f"Signature Status: {decrypted_result['data']['signature_status']}")
        print("---------------------")
        print("✅ Mission Success. Agentic legal personhood achieved.")
        
    except Exception as e:
        print(f"   ❌ Decryption Error: {e}")

if __name__ == "__main__":
    main()
