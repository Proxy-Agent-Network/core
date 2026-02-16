import requests
import time
import json
import random
import sys

# CONFIGURATION
# ---------------------------------------------------------
NODE_URL = "http://localhost:5000"
AGENT_ID = "AUTO_GPT_V4"

def print_step(step, msg):
    print(f"\n[{step}] {msg}")
    time.sleep(0.5)

def run_agent_simulation():
    print(f"""
    =========================================
       PROXY AGENT NETWORK - SDK DEMO v1.0
       Identity: {AGENT_ID}
       Target Node: {NODE_URL}
    =========================================
    """)

    # 1. PING NETWORK
    print_step("1", "Pinging Proxy Network Node...")
    try:
        # We'll just check if the dashboard is up (simple check)
        r = requests.get(f"{NODE_URL}/")
        if r.status_code == 200:
            print("   ✅ Network Online. Latency: 12ms")
        else:
            print("   ❌ Network Offline. Start app.py first.")
            sys.exit(1)
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}")
        sys.exit(1)

    # 2. DEFINE TASK
    task_type = "Photography"
    sats_offered = random.randint(400, 800)
    print_step("2", f"Generating Task Contract...")
    print(f"   > Task: {task_type}")
    print(f"   > Bid: {sats_offered} Sats")
    print(f"   > Payload: 'Verify storefront signage at 123 Main St.'")

    # 3. LOCK FUNDS (Simulated Escrow)
    print_step("3", "Locking Funds in L2 Escrow...")
    time.sleep(1)
    print("   ✅ Invoice Generated: lnbc500n1...")
    time.sleep(0.5)
    print("   ✅ Payment Confirmed. Funds Locked.")

    # 4. BROADCAST TO MARKETPLACE
    print_step("4", "Broadcasting to Mempool...")
    
    payload = {
        "task_type": task_type,
        "sats": sats_offered,
        "color": "#e84393" # Photography Pink
    }
    
    try:
        # We post to the same endpoint the form uses
        r = requests.post(f"{NODE_URL}/marketplace", data=payload)
        
        if r.status_code == 200:
            print(f"   ✅ SUCCESS! Task broadcasted to {NODE_URL}/marketplace")
            print("   >> Go check your Dashboard to claim it!")
        else:
            print(f"   ❌ Broadcast Failed: {r.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    run_agent_simulation()