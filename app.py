import sqlite3
import random
import time
from flask import Flask, render_template, request, jsonify, g, redirect, url_for

app = Flask(__name__)

# CONFIGURATION
# ---------------------------------------------------------
DATABASE = 'registry.db'

# SERVICE CATALOG (Professional Names)
SHOP_ITEMS = {
    'license_auto': {
        'id': 'license_auto',
        'name': 'Automation Daemon',
        'desc': 'Unlocks the Auto-Accept loop for high-frequency task claiming.',
        'price': 5000,
        'icon': '🤖',
        'type': 'license'
    },
    'instance_t2': {
        'id': 'instance_t2',
        'name': 'Compute Instance: Tier 2',
        'desc': 'Allocates dedicated throughput for faster task verification.',
        'price': 15000,
        'icon': '⚡',
        'type': 'infrastructure'
    },
    'security_hsm': {
        'id': 'security_hsm',
        'name': 'HSM Module',
        'desc': 'Hardware Security Module for handling Red-tier data.',
        'price': 25000,
        'icon': '🛡️',
        'type': 'security'
    },
    'theme_neon': {
        'id': 'theme_neon',
        'name': 'UI: Synthwave',
        'desc': 'Alternative dashboard visualization package.',
        'price': 1000,
        'icon': '🎨',
        'type': 'cosmetic'
    }
}

# DATABASE HELPER FUNCTIONS
# ---------------------------------------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# FRONTEND ROUTES
# ---------------------------------------------------------

@app.route('/')
def dashboard():
    """Main Dashboard View."""
    conn = get_db()
    
    target_node = "ROBER_NODE_01"
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    
    if not my_node:
        my_node = conn.execute('SELECT * FROM nodes ORDER BY last_seen DESC LIMIT 1').fetchone()

    if not my_node:
        my_node = {'id': 'UNKNOWN', 'sats_balance': 0, 'status': 'OFFLINE'}
    else:
        my_node = {
            'id': my_node['node_id'],
            'sats_balance': my_node['total_earned'],
            'status': 'ONLINE'
        }

    tasks = []
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY ROWID DESC LIMIT 5').fetchall()
    for t in db_tasks:
        tasks.append({
            'id': t['task_id'],
            'type': t['task_type'],
            'payload': 'WAITING_FOR_EXEC',
            'reward': t['bid_sats']
        })

    return render_template('dashboard.html', node=my_node, tasks=tasks)

@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    conn = get_db()
    
    try:
        conn.execute('ALTER TABLE marketplace_bids ADD COLUMN color TEXT')
    except sqlite3.OperationalError:
        pass 

    if request.method == 'POST':
        task_type = request.form.get('task_type')
        sats = request.form.get('sats')
        color = request.form.get('color') or '#2ecc71'
        req_id = f"REQ-{random.randint(10000, 99999)}"
        
        try:
            conn.execute('''
                INSERT INTO marketplace_bids 
                (requester_id, sats_offered, task_type, status, color) 
                VALUES (?, ?, ?, 'PENDING', ?)
            ''', (req_id, sats, task_type, color))
            conn.commit()
        except Exception as e:
            print(f"Error posting bid: {e}")
        return redirect(url_for('marketplace'))

    bids = conn.execute("SELECT * FROM marketplace_bids ORDER BY created_at DESC").fetchall()
    
    try:
        has_auto = conn.execute("SELECT 1 FROM purchases WHERE item_id='license_auto'").fetchone()
    except sqlite3.OperationalError:
        has_auto = False
    
    return render_template('marketplace.html', bids=bids, unlock_auto=bool(has_auto))

@app.route('/shop')
def shop():
    conn = get_db()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            item_id TEXT,
            purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    target_node = "ROBER_NODE_01"
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    
    if not my_node:
        my_node = conn.execute('SELECT * FROM nodes ORDER BY last_seen DESC LIMIT 1').fetchone()
    
    balance = my_node['total_earned'] if my_node else 0
    node_id = my_node['node_id'] if my_node else "UNKNOWN"

    try:
        owned_rows = conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (node_id,)).fetchall()
        owned_ids = [row['item_id'] for row in owned_rows]
    except sqlite3.OperationalError:
        owned_ids = []

    return render_template('shop.html', items=SHOP_ITEMS, balance=balance, owned=owned_ids, node_id=node_id)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    conn = get_db()
    error = None

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'post_task':
            task_id = request.form.get('task_id')
            try:
                bid = int(request.form.get('bid_sats'))
                if not task_id: raise ValueError("Task ID cannot be empty.")
                conn.execute('INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (?, ?, ?, ?)', 
                             (task_id, bid, 'OPEN', 'MANUAL'))
                conn.commit()
            except sqlite3.IntegrityError:
                error = f"Error: Task ID '{task_id}' already exists."
            except Exception as e:
                error = f"Error: {e}"
        
        elif action == 'fund_node':
            target_node = request.form.get('node_id')
            try:
                amount = int(request.form.get('amount'))
                conn.execute('UPDATE nodes SET total_earned = total_earned + ? WHERE node_id = ?', (amount, target_node))
                conn.commit()
            except Exception as e:
                error = f"Funding Error: {e}"

    nodes = conn.execute('SELECT * FROM nodes ORDER BY last_seen DESC').fetchall()
    return render_template('admin.html', nodes=nodes, error=error)

@app.route('/node/<node_id>')
def node_detail(node_id):
    conn = get_db()
    
    node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (node_id,)).fetchone()
    
    if not node:
        return "Node not found", 404
        
    try:
        purchases = conn.execute('SELECT item_id FROM purchases WHERE node_id = ?', (node_id,)).fetchall()
    except sqlite3.OperationalError:
        purchases = []
    
    return render_template('node_detail.html', node=node, purchases=purchases)

@app.route('/debug/reset_me')
def reset_network():
    conn = get_db()
    try:
        conn.execute('UPDATE nodes SET xp=0, level=1, total_earned=0, streak_days=0')
        conn.execute('DELETE FROM tasks')
        conn.execute('DELETE FROM marketplace_bids')
        conn.execute('DELETE FROM purchases') 
        conn.commit()
    except Exception as e:
        return f"Error: {e}"
    return redirect(url_for('admin_panel'))

# API ENDPOINTS
# ---------------------------------------------------------

# --- NEW: LIVE DASHBOARD POLLING ---
@app.route('/api/v1/dashboard/live')
def dashboard_live():
    conn = get_db()
    
    # 1. Get Balance for Main Node
    target_node = "ROBER_NODE_01"
    my_node = conn.execute('SELECT total_earned, xp FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    balance = my_node['total_earned'] if my_node else 0
    xp = my_node['xp'] if my_node else 0

    # 2. Get Recent Tasks
    tasks = []
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY ROWID DESC LIMIT 5').fetchall()
    for t in db_tasks:
        tasks.append({
            'id': t['task_id'],
            'type': t['task_type'],
            'reward': t['bid_sats']
        })
        
    return jsonify({
        'balance': balance,
        'xp': xp,
        'tasks': tasks
    })

@app.route('/api/v1/shop/buy', methods=['POST'])
def buy_item():
    conn = get_db()
    data = request.json
    item_id = data.get('item_id')
    node_id = data.get('node_id')

    if item_id not in SHOP_ITEMS:
        return jsonify({'success': False, 'error': 'Invalid Item'})

    item = SHOP_ITEMS[item_id]
    price = item['price']

    node = conn.execute('SELECT total_earned FROM nodes WHERE node_id=?', (node_id,)).fetchone()
    if not node or node['total_earned'] < price:
        return jsonify({'success': False, 'error': 'Insufficient Funds'})

    try:
        conn.execute('UPDATE nodes SET total_earned = total_earned - ? WHERE node_id=?', (price, node_id))
        conn.execute('INSERT INTO purchases (node_id, item_id) VALUES (?, ?)', (node_id, item_id))
        conn.commit()
        return jsonify({'success': True, 'new_balance': node['total_earned'] - price})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/v1/marvin')
def ask_marvin():
    quotes = ["System optimal.", "Network latency: 12ms.", "All nodes operational."]
    return jsonify({"thought": random.choice(quotes)})

@app.route('/api/v1/market/claim/<int:bid_id>', methods=['POST'])
def claim_market_task(bid_id):
    conn = get_db()
    data = request.json
    node_id = data.get('node_id') 

    try:
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid_id,))
        bid = conn.execute("SELECT * FROM marketplace_bids WHERE bid_id=?", (bid_id,)).fetchone()
        
        if bid:
            new_task_id = f"MARKET-{random.randint(1000,9999)}"
            conn.execute('''
                INSERT INTO tasks (task_id, bid_sats, status, task_type) 
                VALUES (?, ?, 'OPEN', ?)
            ''', (new_task_id, bid['sats_offered'], bid['task_type']))
            conn.commit()
            return jsonify({"success": True})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    return jsonify({"success": False, "error": "Bid not found"})

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task():
    data = request.json
    return jsonify({"status": "success", "reward": data.get('payout', 0)})

@app.route('/api/v1/xp/status')
def xp_status():
    return jsonify({"total_xp": 1250})

@app.route('/api/v1/market/trends')
def market_trends():
    return jsonify({
        "labels": ["10:00", "10:05", "10:10", "10:15", "10:20"],
        "prices": [random.randint(50, 150) for _ in range(5)]
    })

@app.route('/api/register', methods=['POST'])
def register_node():
    data = request.json
    node_id = data.get('node_id')
    conn = get_db()
    conn.execute('''
        INSERT INTO nodes (node_id, hostname, last_seen) 
        VALUES (?, ?, ?)
        ON CONFLICT(node_id) DO UPDATE SET last_seen=excluded.last_seen
    ''', (node_id, "Unknown-Host", time.time()))
    conn.commit()
    return jsonify({"status": "registered"})

@app.route('/api/poll_task', methods=['GET'])
def poll_task():
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE status='OPEN' LIMIT 1").fetchone()
    if task:
        conn.execute("UPDATE tasks SET status='PENDING' WHERE task_id=?", (task['task_id'],))
        conn.commit()
        return jsonify(dict(task))
    return jsonify({"message": "No tasks available"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)