import requests
import time
import random

BASE_URL = "http://localhost:5000"
# MATCHING YOUR DASHBOARD EXACTLY
NODE_ID = "NODE-2C981180FC98" 

def run_verified_test():
    print(f"🚀 Starting Verified Payout Test for: {NODE_ID}")
    
    # 1. Ensure Node is Active
    requests.post(f"{BASE_URL}/api/v1/node/heartbeat", json={"node_id": NODE_ID})

    for i in range(1, 6):
        payout = random.choice([1500, 5500, 12000])
        
        # Step A: Post
        post_resp = requests.post(f"{BASE_URL}/api/v1/tasks/post", json={
            "agent_id": "STRESS-TEST-PRO",
            "type": "CORE_VAL",
            "bid_sats": payout
        })
        task_id = post_resp.json().get("task_id")
        print(f"[{i}] Task {task_id} Posted (+{payout} Sats)")

        # Step B: Claim (This is the missing link!)
        requests.post(f"{BASE_URL}/api/v1/tasks/claim", json={
            "task_id": task_id,
            "node_id": NODE_ID
        })

        # Step C: Complete
        time.sleep(1)
        requests.post(f"{BASE_URL}/api/v1/tasks/complete", json={
            "task_id": task_id,
            "node_id": NODE_ID,
            "payout": payout
        })
        print(f"    ✅ Payout Triggered.")
        time.sleep(2)

if __name__ == "__main__":
    run_verified_test()
