from flask import Flask, request, jsonify, render_template
import sqlite3
import uuid
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    
    # 1. Tasks
    cursor.execute('CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, agent_id TEXT, task_type TEXT, bid_sats INTEGER, status TEXT, node_id TEXT, results TEXT)')

    # 2. Nodes (Identity & XP)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            node_id TEXT PRIMARY KEY, hostname TEXT, last_seen REAL,
            xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1,
            total_earned INTEGER DEFAULT 0, streak_days INTEGER DEFAULT 0,
            last_work_date TEXT
        )
    ''')

    # 3. Achievement Definitions
    cursor.execute('CREATE TABLE IF NOT EXISTS achievements_def (achievement_id TEXT PRIMARY KEY, name TEXT, description TEXT, icon TEXT, xp_reward INTEGER)')

    # 4. Earned Badges
    cursor.execute('CREATE TABLE IF NOT EXISTS node_achievements (node_id TEXT, achievement_id TEXT, date_earned TEXT, PRIMARY KEY (node_id, achievement_id))')
    
    starter_badges = [
        ('FIRST_PULSE', 'Genesis Pulse', 'Completed your very first task!', '🚀', 500),
        ('SATS_STRIKER', 'Sats Striker', 'Earned over 100,000 total Sats.', '💰', 1000)
    ]
    cursor.executemany("INSERT OR IGNORE INTO achievements_def VALUES (?,?,?,?,?)", starter_badges)
    
    conn.commit()
    conn.close()

init_db()

# --- THE CHEAT CODE (RESET) ---
@app.route('/debug/reset_me', methods=['GET'])
def reset_me():
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE nodes SET xp = 0, level = 1, total_earned = 0, streak_days = 0, last_work_date = NULL")
    cursor.execute("DELETE FROM node_achievements")
    cursor.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()
    return "<h1>🔄 System Reset Successful!</h1><p>XP, Levels, and Tasks have been zeroed out.</p>"

# --- CORE API ROUTES ---

@app.route('/api/v1/tasks/post', methods=['POST'])
def post_task():
    data = request.json
    task_id = "TASK-" + str(uuid.uuid4()).split('-')[0].upper()
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task_id, agent_id, task_type, bid_sats, status) VALUES (?, ?, ?, ?, ?)",
                   (task_id, data.get('agent_id'), data.get('type'), data.get('bid_sats'), 'OPEN'))
    conn.commit()
    conn.close()
    return jsonify({"status": "posted", "task_id": task_id}), 201

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task():
    data = request.json
    task_id, node_id = data.get('task_id'), data.get('node_id')
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT bid_sats FROM tasks WHERE task_id = ?", (task_id,))
    task = cursor.fetchone()
    cursor.execute("SELECT level, xp, last_work_date, streak_days FROM nodes WHERE node_id = ?", (node_id,))
    node = cursor.fetchone()

    if not task or not node:
        conn.close()
        return jsonify({"error": "Missing task/node"}), 404

    bid_sats = task[0]
    current_level, current_xp, last_date, streak = node

    # Mario Kart Buff logic
    xp_gain = int(bid_sats / 10)
    if current_level < 3: xp_gain *= 2
    
    new_xp = current_xp + xp_gain
    new_level = (new_xp // 5000) + 1
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    new_streak = streak + 1 if last_date == yesterday else (streak if last_date == today else 1)

    cursor.execute('''
        UPDATE nodes SET xp = ?, level = ?, streak_days = ?, 
        total_earned = total_earned + ?, last_work_date = ? 
        WHERE node_id = ?
    ''', (new_xp, new_level, new_streak, bid_sats, today, node_id))
    
    cursor.execute("UPDATE tasks SET status = 'COMPLETED' WHERE task_id = ?", (task_id,))
    
    # TRIGGER ACHIEVEMENTS
    check_achievements(node_id, cursor)
    
    conn.commit()
    conn.close()
    return jsonify({"status": "Success", "xp_gained": xp_gain}), 200

def check_achievements(node_id, cursor):
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE node_id = ? AND status = 'COMPLETED'", (node_id,))
    if cursor.fetchone()[0] == 1:
        award_badge(node_id, 'FIRST_PULSE', cursor)

    cursor.execute("SELECT total_earned FROM nodes WHERE node_id = ?", (node_id,))
    if cursor.fetchone()[0] >= 100000:
        award_badge(node_id, 'SATS_STRIKER', cursor)

def award_badge(node_id, badge_id, cursor):
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("INSERT OR IGNORE INTO node_achievements VALUES (?, ?, ?)", (node_id, badge_id, today))
    if cursor.rowcount > 0:
        cursor.execute("SELECT xp_reward FROM achievements_def WHERE achievement_id = ?", (badge_id,))
        xp = cursor.fetchone()[0]
        cursor.execute("UPDATE nodes SET xp = xp + ? WHERE node_id = ?", (xp, node_id))

# --- DASHBOARD DATA ROUTES ---

@app.route('/debug/node_status', methods=['GET'])
def node_status():
    conn = sqlite3.connect('registry.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nodes")
    rows = cursor.fetchall()

    nodes_data = {}
    for row in rows:
        node_id = row['node_id']
        cursor.execute('''
            SELECT a.icon FROM node_achievements na 
            JOIN achievements_def a ON na.achievement_id = a.achievement_id 
            WHERE na.node_id = ?
        ''', (node_id,))
        badges = [b['icon'] for b in cursor.fetchall()]

        nodes_data[node_id] = {
            "status": "ONLINE" if time.time() - row['last_seen'] < 60 else "OFFLINE",
            "xp": row['xp'], "level": row['level'], "streak": row['streak_days'],
            "total_earned": row['total_earned'], "badges": badges
        }
    conn.close()
    return jsonify(nodes_data)

@app.route('/debug/view_tasks', methods=['GET'])
def view_tasks():
    conn = sqlite3.connect('registry.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    tasks = [dict(row) for row in rows]
    conn.close()
    return jsonify(tasks)

# Standard Flask boiler plate... (heartbeat, index, etc)
@app.route('/')
def index(): return render_template('dashboard.html')

@app.route('/api/v1/node/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    node_id = data.get('node_id')
    now = time.time()
    conn = sqlite3.connect('registry.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO nodes (node_id, last_seen) VALUES (?, ?) ON CONFLICT(node_id) DO UPDATE SET last_seen = excluded.last_seen", (node_id, now))
    conn.commit()
    conn.close()
    return jsonify({"status": "pulse received"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)