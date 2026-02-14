from flask import Flask, request, jsonify, render_template
import sqlite3
import uuid

app = Flask(__name__)

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
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

# --- ROUTES ---

@app.route('/')
def index():
    """Serves the Satoshi Dashboard"""
    return render_template('dashboard.html')

@app.route('/api/v1/tasks/post', methods=['POST'])
def post_task():
    """Allows Agents to post new work/bids"""
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
    
    return jsonify({"status": "success", "task_id": task_id}), 201

@app.route('/api/v1/tasks/claim', methods=['POST'])
def claim_task():
    """Allows Nodes to claim an OPEN task"""
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
    """Allows Nodes to submit work and finish task"""
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

@app.route('/api/v1/node/balance/<node_id>', methods=['GET'])
def get_balance(node_id):
    """Checks total Satoshi earnings for a specific Node"""
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(bid_sats) FROM tasks WHERE node_id = ? AND status = 'COMPLETED'", (node_id,))
    balance = cursor.fetchone()[0] or 0
    conn.close()
    return jsonify({"node_id": node_id, "total_earned_sats": balance})

@app.route('/debug/view_tasks', methods=['GET'])
def view_tasks():
    """Debug route for Pulse script to see the market"""
    conn = sqlite3.connect('registry.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    tasks = []
    for row in rows:
        tasks.append({
            "task_id": row["task_id"],
            "type": row["task_type"],
            "bid_sats": row["bid_sats"],
            "status": row["status"]
        })
    conn.close()
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True, port=5000)