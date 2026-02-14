from flask import Flask, request, jsonify
from verifier import ProxyRegistryVerifier
import uuid
from datetime import datetime

app = Flask(__name__)
# This assumes verifier.py is in the same folder
verifier = ProxyRegistryVerifier()

issued_nonces = {}

@app.route('/api/v1/auth/challenge', methods=['GET'])
def get_challenge():
    nonce = uuid.uuid4().hex
    issued_nonces[nonce] = True 
    return jsonify({"nonce": nonce, "ttl": 300})

@app.route('/api/v1/nodes/enroll', methods=['POST'])
def enroll_node():
    payload = request.json
    nonce = payload.get("hardware_manifest", {}).get("nonce")
    if nonce not in issued_nonces:
        return jsonify({"error": "Invalid or expired nonce"}), 403
    result = verifier.verify_enrollment(payload)
    return jsonify(result)

# --- THE CRITICAL ROUTE ---
@app.route('/api/v1/tasks/post', methods=['POST'])
def post_task():
    data = request.json
    agent_id = data.get("agent_id", "UNKNOWN_AGENT")
    task_type = data.get("type", "GENERAL")
    bid_sats = data.get("bid_sats", 0)

    # This calls the create_task function in your verifier.py
    task_id = verifier.create_task(agent_id, task_type, bid_sats)
    
    print(f"[*] Task Created: {task_id} for {agent_id}")
    return jsonify({
        "status": "SUCCESS",
        "task_id": task_id,
        "message": "Task posted to Order Book"
    }), 201

@app.route('/debug/view_tasks', methods=['GET'])
def view_tasks():
    import sqlite3
    conn = sqlite3.connect('registry.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    
    tasks = []
    for row in rows:
        # We manually map the keys to be 100% sure Pulse can read them
        tasks.append({
            "task_id": row["task_id"],
            "agent_id": row["agent_id"],
            "type": row["task_type"] if "task_type" in row.keys() else row.get("type", "UNKNOWN"),
            "bid_sats": row["bid_sats"],
            "status": row["status"]
        })
    conn.close()
    return jsonify(tasks)

@app.route('/api/v1/tasks/claim', methods=['POST'])
def claim_task():
    data = request.json
    task_id = data.get('task_id')
    node_id = data.get('node_id')

    if not task_id or not node_id:
        return jsonify({"error": "Missing task_id or node_id"}), 400

    import sqlite3
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()

    # Verify task is still OPEN
    cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()

    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if task[0] != 'OPEN':
        return jsonify({"error": "Task already claimed or completed"}), 409

    # Update status to CLAIMED and assign to the node
    cursor.execute("""
        UPDATE tasks 
        SET status = 'CLAIMED', node_id = ? 
        WHERE task_id = ?
    """, (node_id, task_id))
    
    conn.commit()
    conn.close()

    print(f"[!] Task {task_id} successfully CLAIMED by {node_id}")
    return jsonify({"message": f"Task {task_id} claimed successfully"}), 200

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task():
    data = request.json
    task_id = data.get('task_id')
    node_id = data.get('node_id')
    results = data.get('results', "No data provided")

    import sqlite3
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()

    # Check if the node actually holds the claim
    cursor.execute("SELECT node_id, status FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()

    if not task:
        return jsonify({"error": "Task not found"}), 404
    if task[1] != 'CLAIMED' or task[0] != node_id:
        return jsonify({"error": "Unauthorized: Node does not hold this claim"}), 403

    # Mark as COMPLETED
    cursor.execute("""
        UPDATE tasks 
        SET status = 'COMPLETED'
        WHERE task_id = ?
    """, (task_id,))
    
    conn.commit()
    conn.close()

    print(f"[✔] Task {task_id} COMPLETED by {node_id}. Data: {results}")
    return jsonify({"message": "Work accepted. Satoshi transfer initiated."}), 200

if __name__ == '__main__':
    # host 0.0.0.0 lets your Raspberry Pi find this later
    app.run(host='0.0.0.0', port=5000, debug=True)
