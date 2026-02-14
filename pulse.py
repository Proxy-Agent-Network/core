import requests
import time
import uuid

# Configuration
REGISTRY_URL = "http://localhost:5000"

# --- IDENTITY GENERATION ---
# This creates a unique ID based on your computer's hardware (MAC address)
NODE_ID = f"NODE-{hex(uuid.getnode()).upper()[2:]}"

def send_heartbeat():
    """Tells the Registry that this node is still alive and well"""
    try:
        url = f"{REGISTRY_URL}/api/v1/node/heartbeat"
        requests.post(url, json={"node_id": NODE_ID}, timeout=5)
    except Exception as e:
        print(f"[!] Heartbeat failed: {e}")

def claim_task(task_id):
    """Attempts to lock a task for this node"""
    print(f"[*] Attempting to claim task: {task_id}...")
    try:
        url = f"{REGISTRY_URL}/api/v1/tasks/claim"
        payload = {"task_id": task_id, "node_id": NODE_ID}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"[SUCCESS] Task {task_id} is now yours!")
            return True
        else:
            print(f"[FAILED] Could not claim: {response.json().get('error')}")
            return False
    except Exception as e:
        print(f"[-] Claim Error: {e}")
        return False

def submit_results(task_id):
    """Submits the 'Proof of Work' to the Registry"""
    print(f"[*] Submitting work for {task_id}...")
    try:
        url = f"{REGISTRY_URL}/api/v1/tasks/complete"
        payload = {
            "task_id": task_id, 
            "node_id": NODE_ID, 
            "results": "Audit complete: Logic gates verified."
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"[💰] SUCCESS: Work accepted for {task_id}!")
        else:
            print(f"[!] Submission failed: {response.status_code}")
    except Exception as e:
        print(f"[-] Submission Error: {e}")

def fetch_and_process():
    """Main logic: Find a job, claim it, 'work' on it, and finish it"""
    try:
        # Check for new tasks
        response = requests.get(f"{REGISTRY_URL}/debug/view_tasks")
        if response.status_code == 200:
            tasks = response.json()
            open_tasks = [t for t in tasks if t.get('status') == 'OPEN']
            
            if open_tasks:
                target_task = open_tasks[0]
                t_id = target_task['task_id']
                
                if claim_task(t_id):
                    print(f"[*] Processing task {t_id} (Simulating Hardware Load)...")
                    time.sleep(3) # Simulate the time it takes to do work
                    submit_results(t_id)
            else:
                print("[-] No open tasks. Monitoring market...")
    except Exception as e:
        print(f"[-] Market Query Error: {e}")

if __name__ == "__main__":
    print(f"--- PROXY NODE STARTED ---")
    print(f"HARDWARE ID: {NODE_ID}")
    print(f"TARGET: {REGISTRY_URL}")
    
    try:
        while True:
            # 1. Tell the dashboard we are online
            send_heartbeat()
            
            # 2. Look for work
            fetch_and_process()
            
            # 3. Wait 10 seconds before the next pulse
            print("[*] Sleeping 10s...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[!] Node shutting down.")