import requests
import time
import random
import json

BASE_URL = "http://localhost:5000"
NODE_ID = "NODE-TEST-BOT-001"

def run_simulation():
    print(f"🚀 Starting Stress Test for Node: {NODE_ID}")
    
    # 1. Heartbeat to Register
    try:
        print("💓 Sending Heartbeat...")
        requests.post(f"{BASE_URL}/api/v1/node/heartbeat", json={"node_id": NODE_ID})
    except Exception as e:
        print(f"❌ Server seems offline: {e}")
        return

    # 2. Loop through 10 Tasks
    for i in range(1, 11):
        task_type = random.choice(["VIDEO_VERIFY", "NOTARY_SIGN", "COURIER_DROP"])
        payout = random.choice([500, 1500, 5500]) # Bronze, Silver, Gold tiers
        
        # Step A: Agent Posts Task
        print(f"\n[Task {i}] Posting new job ({task_type})...")
        post_resp = requests.post(f"{BASE_URL}/api/v1/tasks/post", json={
            "agent_id": "AGENT-SIM-99",
            "type": task_type,
            "bid_sats": payout
        })
        
        if post_resp.status_code == 201:
            task_data = post_resp.json()
            task_id = task_data.get("task_id")
            print(f"   ✅ Posted! ID: {task_id} | Value: {payout}")
            
            # Step B: Node Completes Task
            time.sleep(1) # Simulate work
            print(f"   🛠️ Completing task...")
            
            complete_resp = requests.post(f"{BASE_URL}/api/v1/tasks/complete", json={
                "task_id": task_id,
                "node_id": NODE_ID,
                "payout": payout  # Explicitly passing payout to ensure XP calc works
            })
            
            if complete_resp.status_code == 200:
                print(f"   🎉 Success! XP Gained.")
            else:
                print(f"   ⚠️ Completion Failed: {complete_resp.text}")
                
        else:
            print(f"   ❌ Post Failed: {post_resp.text}")
            
        time.sleep(2) # Pause between tasks so you can watch the UI update

if __name__ == "__main__":
    run_simulation()
