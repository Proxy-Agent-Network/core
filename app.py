from flask import Flask, request, jsonify, render_template
import sqlite3
import uuid
import time

app = Flask(__name__)

# --- IN-MEMORY STATE ---
node_heartbeats = {}  # Format: { "NODE-ID": timestamp }

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    # We ensure the 'results' and 'node_id' columns exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            agent_id TEXT,
            task_type TEXT,
            bid_sats INTEGER,
            status TEXT,
            node_id TEXT,
            results TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- WEB DASHBOARD ROUTES ---

@app.route('/')
def index():
    """Serves the Mission Control Dashboard"""
    return render_template('dashboard.html')

@app.route('/debug/node_status', methods=['GET'])
def node_status():
    """Returns status of all nodes based on last heartbeat"""
    now = time.time()
    # A node is 'ONLINE' if we've heard from it in the last 30 seconds
    status = {nid: ("ONLINE" if now - ts < 30 else "OFFLINE") 
              for nid, ts in node_heartbeats.items()}
    return jsonify(status)

# --- NODE API ROUTES ---

@app.route('/api/v1/node/heartbeat', methods=['POST'])
def heartbeat():
    """Nodes call this to stay 'ONLINE' on the dashboard"""
    data = request.json
    node_id = data.get('node_id')
    if node_id:
        node_heartbeats[node_id] = time.time()
        return jsonify({"status": "pulse received"}), 200
    return jsonify({"error": "No node_id provided"}), 400

@app.route('/api/v1/tasks/post', methods=['POST'])
def post_task():
    data = request.json
    task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
    
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (task_id, agent_id, task_type, bid_sats, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (task_id, data.get('agent_id'), data.get('type'), data.get('bid_sats'), 'OPEN'))
    conn.commit()
    conn.close()
    
    # THIS IS THE MISSING PIECE:
    return jsonify({"status": "success", "task_id": task_id}), 201

@app.route('/api/v1/tasks/claim', methods=['POST'])
def claim_task():
    """Nodes call this to reserve a task"""
    data = request.json
    task_id = data.get('task_id')
    node_id = data.get('node_id')

    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()

    if not task:
        return jsonify({"error": "Task not found"}), 404
    if task[0] != 'OPEN':
        return jsonify({"error": "Task already claimed"}), 409

    cursor.execute("UPDATE tasks SET status = 'CLAIMED', node_id = ? WHERE task_id = ?", (node_id, task_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task claimed successfully"}), 200

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task():
    """Nodes call this to submit proof-of-work and get 'paid'"""
    data = request.json
    task_id = data.get('task_id')
    node_id = data.get('node_id')
    results = data.get('results')

    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    cursor.execute("SELECT node_id, status FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()

    if not task or task[0] != node_id:
        return jsonify({"error": "Unauthorized claim"}), 403

    cursor.execute("UPDATE tasks SET status = 'COMPLETED', results = ? WHERE task_id = ?", (results, task_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Payment verified, task completed"}), 200

@app.route('/debug/view_tasks', methods=['GET'])
def view_tasks():
    """Market overview for the Pulse script and Dashboard"""
    conn = sqlite3.connect('registry.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    tasks = [dict(row) for row in rows]
    # Small fix: ensure 'task_type' is mapped to 'type' for Pulse script compatibility
    for t in tasks:
        t['type'] = t.get('task_type', 'GENERAL')
    conn.close()
    return jsonify(tasks)

if __name__ == '__main__':
    # Start the server
    print("[*] Proxy Registry Live on http://localhost:5000")
    app.run(debug=True, port=5000)