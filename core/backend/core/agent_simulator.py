import requests
import time
import random

# Configuration
SERVER_URL = "http://localhost:5000"
AGENT_NAMES = ["Logistics-Alpha", "Finance-Bot-7", "Estate-Agent-99", "Supply-Chain-X"]
TASK_TYPES = ["visual_audit", "notarization", "sms_relay", "identity_verify", "courier_drop"]

def simulate_agent_bids(count=5):
    print(f"--- STARTING AGENT SIMULATION: {count} BIDS ---")
    
    for i in range(count):
        agent = random.choice(AGENT_NAMES)
        task = random.choice(TASK_TYPES)
        # Random bid between 1,000 and 150,000 Sats
        bid = random.randint(10, 150) * 1000 
        
        payload = {
            "agent_id": agent,
            "type": task,
            "bid_sats": bid,
            "tier": random.randint(1, 3)
        }
        
        try:
            response = requests.post(f"{SERVER_URL}/api/v1/tasks/post", json=payload)
            if response.status_code == 201:
                task_data = response.json()
                print(f"[+] {agent} posted {task} | Bid: {bid} Sats | ID: {task_data['task_id']}")
            else:
                print(f"[-] Failed to post task: {response.text}")
        except Exception as e:
            print(f"[-] Error reaching server: {e}")
            break
            
        time.sleep(1) # Small delay for realism

if __name__ == "__main__":
    simulate_agent_bids(5)
