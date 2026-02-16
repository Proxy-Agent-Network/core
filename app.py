import sqlite3
import random
import time
from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session

app = Flask(__name__)
# Protocol 1.2.0: Secret key required for session-based event clearing
app.secret_key = 'proxy_secret_key_v1' 

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

# RIVAL AGENT LIST
RIVALS = ["OMNI_CORP_09", "KAOS_ENGINE", "NEURAL_LINK_X", "VOID_RUNNER"]

# --- DAEMON & RIVAL LOGIC ---
# ---------------------------------------------------------

def simulate_rival_snatch():
    conn = get_db()
    # Reduce snatch probability to 5% for more stable testing
    if random.random() < 0.05: 
        conn.execute("""
            DELETE FROM tasks 
            WHERE rowid IN (
                SELECT rowid FROM tasks 
                WHERE status='OPEN' AND task_type='MANUAL' 
                LIMIT 1
            )
        """)
        conn.commit()

def run_automation_daemon(node_id):
    """Automatically claims marketplace tasks and stores a one-time event message."""
    conn = get_db()
    
    # Verify license ownership
    has_license = conn.execute(
        "SELECT 1 FROM purchases WHERE node_id = ? AND item_id = 'license_auto'", 
        (node_id,)
    ).fetchone()
    
    if not has_license:
        return None

    # Scan for available marketplace bids
    bid = conn.execute(
        "SELECT * FROM marketplace_bids WHERE status = 'PENDING' ORDER BY sats_offered DESC LIMIT 1"
    ).fetchone()

    if bid:
        # Move bid to CLAIMED and generate an automated network task
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid['bid_id'],))
        
        new_task_id = f"AUTO-{random.randint(1000, 9999)}"
        conn.execute('''
            INSERT INTO tasks (task_id, bid_sats, status, task_type) 
            VALUES (?, ?, 'OPEN', 'AUTOMATED')
        ''', (new_task_id, bid['sats_offered']))
        
        conn.commit()
        
        # Store message in session so it can be cleared after one read (prevents audio loop)
        msg = f"Secured task {new_task_id} for {bid['sats_offered']} Sats"
        session['daemon_msg'] = msg
        return msg
    return None

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

    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY ROWID DESC LIMIT 5').fetchall()
    tasks = [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks]

    return render_template('dashboard.html', node=my_node, tasks=tasks)

# --- UPDATED RIVAL LOGIC ---
def simulate_rival_snatch():
    """Simulates rivals 'snatching' tasks with reduced frequency for testing."""
    conn = get_db()
    # Reduced from 0.2 to 0.05 to prevent 'disappearing' tasks during manual testing
    if random.random() < 0.05:
        conn.execute("""
            DELETE FROM tasks 
            WHERE rowid IN (
                SELECT rowid FROM tasks 
                WHERE status='OPEN' AND task_type='MANUAL' 
                LIMIT 1
            )
        """)
        conn.commit()

# --- UPDATED MARKETPLACE ROUTE ---
@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    conn = get_db()
    
    if request.method == 'POST':
        task_type = request.form.get('task_type')
        sats = request.form.get('sats')
        color = request.form.get('color') or '#2ecc71'
        req_id = f"REQ-{random.randint(10000, 99999)}"
        
        # Explicitly commit the new bid before redirecting to ensure it persists
        conn.execute('''
            INSERT INTO marketplace_bids 
            (requester_id, sats_offered, task_type, status, color) 
            VALUES (?, ?, ?, 'PENDING', ?)
        ''', (req_id, sats, task_type, color))
        conn.commit() 
        return redirect(url_for('marketplace'))

    # Fetch ALL bids to ensure the list populates correctly
    bids = conn.execute("SELECT * FROM marketplace_bids ORDER BY created_at DESC").fetchall()
    
    has_auto = False
    try:
        has_auto = conn.execute("SELECT 1 FROM purchases WHERE item_id='license_auto'").fetchone()
    except: pass
    
    return render_template('marketplace.html', bids=bids, unlock_auto=bool(has_auto))

@app.route('/shop')
def shop():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT, item_id TEXT, purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP)')

    target_node = "ROBER_NODE_01"
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    balance = my_node['total_earned'] if my_node else 0
    node_id = my_node['node_id'] if my_node else "UNKNOWN"

    owned = [row['item_id'] for row in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (node_id,)).fetchall()]
    return render_template('shop.html', items=SHOP_ITEMS, balance=balance, owned=owned, node_id=node_id)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    conn = get_db()
    error = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'post_task':
            task_id, bid = request.form.get('task_id'), request.form.get('bid_sats')
            try:
                conn.execute('INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (?, ?, ?, ?)', (task_id, bid, 'OPEN', 'MANUAL'))
                conn.commit()
            except Exception as e: error = str(e)
        elif action == 'fund_node':
            conn.execute('UPDATE nodes SET total_earned = total_earned + ? WHERE node_id = ?', (request.form.get('amount'), request.form.get('node_id')))
            conn.commit()

    nodes = conn.execute('SELECT * FROM nodes ORDER BY last_seen DESC').fetchall()
    return render_template('admin.html', nodes=nodes, error=error)

@app.route('/node/<node_id>')
def node_detail(node_id):
    conn = get_db()
    node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (node_id,)).fetchone()
    purchases = conn.execute('SELECT item_id FROM purchases WHERE node_id = ?', (node_id,)).fetchall()
    return render_template('node_detail.html', node=node, purchases=purchases)

@app.route('/debug/reset_me')
def reset_network():
    conn = get_db()
    conn.execute('UPDATE nodes SET xp=0, level=1, total_earned=0')
    conn.execute('DELETE FROM tasks'); conn.execute('DELETE FROM marketplace_bids'); conn.execute('DELETE FROM purchases')
    conn.commit()
    return redirect(url_for('admin_panel'))

# --- API ENDPOINTS ---
# ---------------------------------------------------------

@app.route('/api/v1/dashboard/live')
def dashboard_live():
    """Returns real-time data and clears the daemon event after it is sent."""
    conn = get_db()
    target_node = "ROBER_NODE_01"
    
    simulate_rival_snatch()
    run_automation_daemon(target_node) # potentially sets session['daemon_msg']
    
    # Retrieve and then clear the daemon message from the session
    daemon_event = session.pop('daemon_msg', None)
    
    my_node = conn.execute('SELECT total_earned, xp FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY ROWID DESC LIMIT 5').fetchall()
    
    return jsonify({
        'balance': my_node['total_earned'] if my_node else 0,
        'xp': my_node['xp'] if my_node else 0,
        'tasks': [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks],
        'daemon_event': daemon_event
    })

@app.route('/api/v1/market/trends')
def market_trends():
    return jsonify({"labels": ["10:00", "10:05", "10:10", "10:15", "10:20"], "prices": [random.randint(50, 150) for _ in range(5)]})

@app.route('/api/v1/network/events')
def network_events():
    rival = random.choice(RIVALS)
    actions = [f"secured a contract ({random.randint(5000, 20000)} Sats)", "synchronized with mainnet", "failed handshake"]
    return jsonify({"event": f"[{rival}] {random.choice(actions)}", "timestamp": time.strftime("%H:%M:%S")})

@app.route('/api/v1/shop/buy', methods=['POST'])
def buy_item():
    conn = get_db()
    data = request.json
    item_id, node_id = data.get('item_id'), data.get('node_id')
    price = SHOP_ITEMS[item_id]['price']
    conn.execute('UPDATE nodes SET total_earned = total_earned - ? WHERE node_id=?', (price, node_id))
    conn.execute('INSERT INTO purchases (node_id, item_id) VALUES (?, ?)', (node_id, item_id))
    conn.commit()
    return jsonify({'success': True})

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task():
    data = request.json
    conn = get_db()
    conn.execute("UPDATE nodes SET total_earned = total_earned + ?, xp = xp + 100 WHERE node_id = ?", (data.get('payout'), data.get('node_id')))
    conn.execute("DELETE FROM tasks WHERE task_id = ?", (data.get('task_id'),))
    conn.commit()
    return jsonify({"status": "success"})

@app.route('/api/register', methods=['POST'])
def register_node():
    data = request.json
    conn = get_db(); conn.execute('INSERT INTO nodes (node_id, hostname, last_seen) VALUES (?, ?, ?) ON CONFLICT(node_id) DO UPDATE SET last_seen=excluded.last_seen', (data.get('node_id'), "Unknown-Host", time.time()))
    conn.commit()
    return jsonify({"status": "registered"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)