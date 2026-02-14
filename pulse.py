import requests
import time

REGISTRY_URL = "http://localhost:5000"
NODE_ID = "NODE-RPi4-001"

def claim_task(task_id):
    print(f"[*] Attempting to claim task: {task_id}...")
    payload = {"task_id": task_id, "node_id": NODE_ID}
    response = requests.post(f"{REGISTRY_URL}/api/v1/tasks/claim", json=payload)
    
    if response.status_code == 200:
        print(f"[SUCCESS] Task {task_id} is now yours!")
        return True
    else:
        print(f"[FAILED] Could not claim task: {response.json().get('error')}")
        return False

def submit_results(task_id):
    print(f"[*] Submitting work for {task_id}...")
    payload = {
        "task_id": task_id, 
        "node_id": NODE_ID, 
        "results": "Audit complete: All systems nominal."
    }
    response = requests.post(f"{REGISTRY_URL}/api/v1/tasks/complete", json=payload)
    if response.status_code == 200:
        print(f"[💰] SUCCESS: Work accepted for {task_id}!")
    else:
        print(f"[!] Submission failed: {response.json().get('error')}")

def fetch_and_claim():
    try:
        response = requests.get(f"{REGISTRY_URL}/debug/view_tasks")
        if response.status_code == 200:
            tasks = response.json()
            open_tasks = [t for t in tasks if t.get('status') == 'OPEN']
            
            if open_tasks:
                target_task = open_tasks[0]
                t_id = target_task['task_id']
                if claim_task(t_id):
                    # Simulate 'working' for 3 seconds
                    print(f"[*] Processing task {t_id}...")
                    time.sleep(3) 
                    submit_results(t_id)
            else:
                print("[-] No open tasks. Monitoring...")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    while True:
        fetch_and_claim()
        time.sleep(10)