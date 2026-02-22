import random
import time
import os
import json
import base64
from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session, flash
from backend.core.db import get_db_conn

try:
    from backend.core.lightning_engine import lnd
    print(" [SYSTEM] ⚡ Lightning Treasury Layer Loaded.")
except ImportError:
    print(" [WARN] ⚠️  lightning_engine.py not found. Running without payment rails.")
    lnd = None

try:
    from node.tpm_binding import NodeHardware
    print(" [SYSTEM] 🔒 Connecting to Rust TPM Engine...")
    hw_bridge = NodeHardware()
    MY_NODE_ID = hw_bridge.get_fingerprint()
    HW_SECURED = not MY_NODE_ID.startswith("MOCK")
    print(f" [SYSTEM] ✅ Identity Confirmed: {MY_NODE_ID}")
except:
    MY_NODE_ID = "NODE_SOFTWARE_FALLBACK"
    HW_SECURED = False

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_local_secret')

SHOP_ITEMS = {
    'license_auto': {'id': 'license_auto', 'name': 'Automation Daemon', 'desc': 'Unlocks the Auto-Accept loop for high-frequency task claiming.', 'price': 5000, 'icon': '🤖'},
    'license_speed': {'id': 'license_speed', 'name': 'Broadcast Turbo', 'desc': 'Overclocks the L2 handshake. Reduces broadcast delay by 50%.', 'price': 20000, 'icon': '⏩'},
    'theme_neon': {'id': 'theme_neon', 'name': 'UI: Synthwave', 'desc': 'Alternative dashboard visualization package.', 'price': 1000, 'icon': '🎨'},
    'disco': {'id': 'disco', 'name': 'UI: Studio 54', 'desc': 'Interactive audio-visual theme.', 'price': 1000, 'icon': '🪩'},
    'matrix': {'id': 'matrix', 'name': 'UI: The Matrix', 'desc': 'Digital rain simulation.', 'price': 0, 'icon': '🟩'}
}

LEGAL_DOCS = {
    'docs': {'title': 'PROTOCOL DOCUMENTATION v1.6', 'content': '<p>The Proxy Network is a decentralized grid of autonomous agents.</p>'},
    'aup': {'title': 'ACCEPTABLE USE POLICY', 'content': '<p>Network Flooding and malicious payloads are prohibited.</p>'},
    'terms': {'title': 'TERMS OF SERVICE', 'content': '<p>Service is provided AS-IS. You are responsible for executed compute.</p>'},
    'privacy': {'title': 'PRIVACY POLICY', 'content': '<p>All wallet balances are encrypted using ChaCha20-Poly1305.</p>'}
}

def get_secure_balance(conn, node_id):
    row = conn.execute("SELECT total_earned FROM nodes WHERE node_id = ?", (node_id,)).fetchone()
    if not row: return 0
    stored_val = str(row['total_earned'])
    try:
        decrypted = hw_bridge.decrypt_data(stored_val)
        if "ERR_" in decrypted or "ACCESS_DENIED" in decrypted: return int(float(stored_val))
        return int(decrypted)
    except: return int(float(stored_val)) if stored_val.isdigit() else 0

def update_secure_wallet(conn, node_id, amount):
    current_balance = get_secure_balance(conn, node_id)
    new_balance = current_balance + amount
    try: encrypted_balance = hw_bridge.encrypt_data(str(new_balance))
    except: encrypted_balance = str(new_balance)
    conn.execute("UPDATE nodes SET total_earned = ? WHERE node_id = ?", (encrypted_balance, node_id))
    return new_balance

def simulate_rival_snatch():
    conn = get_db()
    bids = conn.execute("SELECT * FROM marketplace_bids WHERE status='PENDING'").fetchall()
    if not bids: return
    RIVALS_META = {"OMNI_CORP_09": 0.05, "VOID_RUNNER": 0.03, "KAOS_ENGINE": 0.08}
    for bid in bids:
        value_mult = 1.5 if bid['sats_offered'] > 500 else 3.0 if bid['sats_offered'] > 1000 else 1.0
        attacker_name = random.choice(list(RIVALS_META.keys()))
        if random.random() < (RIVALS_META[attacker_name] * value_mult * 0.1):
            conn.execute("UPDATE marketplace_bids SET status='STOLEN' WHERE bid_id=?", (bid['bid_id'],))
            conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", ("THREAT", f"SECURITY ALERT: {attacker_name} intercepted Bid #{bid['bid_id']}"))
    conn.commit()

def run_automation_daemon(node_id):
    conn = get_db()
    if not conn.execute("SELECT 1 FROM purchases WHERE node_id = ? AND item_id = 'license_auto'", (node_id,)).fetchone(): return None
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE status = 'PENDING' ORDER BY sats_offered DESC LIMIT 1").fetchone()
    if bid:
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid['bid_id'],))
        new_id = f"AUTO-{random.randint(1000, 9999)}"
        conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (?, ?, 'OPEN', 'AUTOMATED')", (new_id, bid['sats_offered']))
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", ("AUTOMATION", f"Node {node_id} secured task {new_id}"))
        conn.commit()
        msg = f"Daemon secured task {new_id} (+{bid['sats_offered']} Sats)"
        session['daemon_msg'] = msg
        return msg
    if random.random() < 0.20:
        dust = random.randint(5, 45)
        junk_id = f"DUST-{random.randint(100, 999)}"
        update_secure_wallet(conn, node_id, dust)
        conn.execute("INSERT INTO xp_history (node_id, task_id, base_xp) VALUES (?, ?, ?)", (node_id, junk_id, 10))
        conn.commit()
        msg = f"Daemon scavenged {junk_id} (+{dust} Sats)"
        session['daemon_msg'] = msg
        return msg
    return None

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = get_db_conn()
        db.execute('''CREATE TABLE IF NOT EXISTS xp_history (id SERIAL PRIMARY KEY, node_id TEXT, task_id TEXT, base_xp INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS xp_bonuses (id SERIAL PRIMARY KEY, parent_id INTEGER, bonus_name TEXT, bonus_xp INTEGER, color TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS global_events (id SERIAL PRIMARY KEY, event_type TEXT, message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS nodes (node_id TEXT PRIMARY KEY, hostname TEXT, total_earned TEXT DEFAULT '0', xp INTEGER DEFAULT 0, last_seen DOUBLE PRECISION)''')
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, bid_sats INTEGER, status TEXT, task_type TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS marketplace_bids (bid_id SERIAL PRIMARY KEY, requester_id TEXT, task_type TEXT, sats_offered INTEGER, status TEXT, color TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS purchases (id SERIAL PRIMARY KEY, node_id TEXT, item_id TEXT, purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db.commit()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

@app.route('/search')
def search_engine():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (MY_NODE_ID,)).fetchall()]
    return render_template('search.html', balance=balance, owned=owned)

@app.route('/')
def dashboard():
    conn = get_db()
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (MY_NODE_ID,)).fetchone()
    balance = get_secure_balance(conn, MY_NODE_ID)
    my_node_data = {'id': my_node['node_id'], 'sats_balance': balance, 'status': 'ONLINE'} if my_node else {'id': MY_NODE_ID, 'sats_balance': 0, 'status': 'OFFLINE'}
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT 5').fetchall()
    tasks = [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks]
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (MY_NODE_ID,)).fetchall()]
    return render_template('dashboard.html', node=my_node_data, tasks=tasks, hw_secured=HW_SECURED, owned=owned, balance=balance) 

@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    conn = get_db()
    if request.method == 'POST':
        task_type = request.form.get('task_type')
        sats = int(request.form.get('sats', 100))
        color = request.form.get('color', '#2ecc71')
        if lnd:
            invoice = lnd.create_invoice(sats, f"Broadcast Task: {task_type}")
            if invoice:
                invoice['duration'] = 4 if conn.execute("SELECT 1 FROM purchases WHERE node_id = ? AND item_id = 'license_speed'", (MY_NODE_ID,)).fetchone() else 8
                invoice['color'] = color
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify({"status": "INVOICE_REQUIRED", "invoice": invoice})
        req_id = f"REQ-{random.randint(10000, 99999)}"
        conn.execute("INSERT INTO marketplace_bids (requester_id, sats_offered, task_type, status, color) VALUES (?, ?, ?, 'PENDING', ?)", (req_id, sats, task_type, color))
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", ("MARKET", f"New high-yield bid broadcast: {req_id} ({sats} Sats)"))
        conn.commit() 
        return redirect(url_for('marketplace'))

    bids = conn.execute("SELECT * FROM marketplace_bids WHERE status='PENDING' ORDER BY created_at DESC").fetchall() 
    max_radius = int(request.args.get('radius', 50))
    filtered_bids = []
    for bid in bids:
        random.seed(bid['bid_id']) 
        dist = random.randint(1, 100)
        random.seed() 
        bd = dict(bid); bd['distance'] = dist
        if dist <= max_radius: filtered_bids.append(bd)
    has_auto = conn.execute("SELECT 1 FROM purchases WHERE item_id='license_auto'").fetchone()
    balance = get_secure_balance(conn, MY_NODE_ID)
    return render_template('marketplace.html', bids=filtered_bids, unlock_auto=bool(has_auto), current_radius=max_radius, balance=balance)

@app.route('/shop')
def shop():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    if request.args.get('buy'):
        item_id = request.args.get('buy')
        if item_id in SHOP_ITEMS and balance >= SHOP_ITEMS[item_id]['price']:
            update_secure_wallet(conn, MY_NODE_ID, -SHOP_ITEMS[item_id]['price'])
            conn.execute("INSERT INTO purchases (node_id, item_id) VALUES (?, ?)", (MY_NODE_ID, item_id))
            conn.commit()
        return redirect(url_for('shop'))
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (MY_NODE_ID,)).fetchall()]
    return render_template('shop.html', items=SHOP_ITEMS, balance=balance, owned=owned, node_id=MY_NODE_ID)

@app.route('/faq')
def faq():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    owned = [row['item_id'] for row in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (MY_NODE_ID,)).fetchall()]
    return render_template('faq.html', node_id=MY_NODE_ID, balance=balance, hw_secured=HW_SECURED, owned=owned)

@app.route('/legal/<doc_type>')
def legal(doc_type):
    doc = LEGAL_DOCS.get(doc_type)
    if not doc: return redirect(url_for('dashboard'))
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (MY_NODE_ID,)).fetchall()]
    return render_template('legal.html', title=doc['title'], content=doc['content'], balance=balance, owned=owned)

@app.route('/api/v1/shop/buy', methods=['POST'])
def shop_buy_api():
    item_id = request.json.get('item_id')
    conn = get_db()
    if item_id not in SHOP_ITEMS: return jsonify({"success": False, "error": "Invalid Item ID"}), 400
    price = SHOP_ITEMS[item_id]['price']
    if get_secure_balance(conn, MY_NODE_ID) >= price:
        new_bal = update_secure_wallet(conn, MY_NODE_ID, -price)
        conn.execute("INSERT INTO purchases (node_id, item_id) VALUES (?, ?)", (MY_NODE_ID, item_id))
        conn.commit()
        return jsonify({"success": True, "new_balance": new_bal})
    return jsonify({"success": False, "error": "Insufficient Funds"}), 402

@app.route('/api/v1/invoice/status/<r_hash>')
def check_invoice_status(r_hash):
    return jsonify({"status": lnd.check_status(r_hash) if lnd else "UNKNOWN"})

@app.route('/api/v1/market/finalize_bid', methods=['POST'])
def finalize_bid():
    r_hash = request.json.get('r_hash')
    if lnd and lnd.check_status(r_hash) == "SETTLED":
        invoice = lnd.pending_invoices[r_hash]
        req_id = f"REQ-{random.randint(10000, 99999)}"
        conn = get_db()
        conn.execute("INSERT INTO marketplace_bids (requester_id, sats_offered, task_type, status, color) VALUES (?, ?, ?, 'PENDING', ?)", (req_id, invoice['amount'], invoice['memo'].replace("Broadcast Task: ", ""), invoice.get('color', '#2ecc71')))
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", ("MARKET", f"New high-yield bid broadcast: {req_id} ({invoice['amount']} Sats) [PAID]"))
        conn.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/v1/network/stats')
def get_network_stats():
    conn = get_db()
    active_nodes = conn.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE last_seen > ?", (time.time() - 300,)).fetchone()['cnt']
    return jsonify({"total_volume": "ENCRYPTED", "active_nodes": active_nodes, "protocol_v": "1.6.0", "status": "STABLE"})

@app.route('/api/v1/network/events/history')
def get_event_history():
    return jsonify([dict(e) for e in get_db().execute("SELECT * FROM global_events ORDER BY timestamp DESC LIMIT 20").fetchall()])

@app.route('/api/v1/network/leaderboard')
def get_leaderboard():
    my_node = get_db().execute('SELECT node_id, xp FROM nodes WHERE node_id = ?', (MY_NODE_ID,)).fetchone()
    standings = [{"id": MY_NODE_ID, "xp": my_node['xp'] if my_node else 0, "type": "HUMAN"}, {"id": "OMNI_CORP_09", "xp": 12500, "type": "RIVAL"}, {"id": "VOID_RUNNER", "xp": 8900, "type": "RIVAL"}]
    standings.sort(key=lambda x: x['xp'], reverse=True)
    return jsonify(standings)

@app.route('/api/v1/node/xp_ledger/<node_id>')
def get_xp_ledger(node_id):
    conn = get_db()
    parents = conn.execute("SELECT * FROM xp_history WHERE node_id=? ORDER BY timestamp DESC", (node_id,)).fetchall()
    ledger = []
    for p in parents:
        bonuses = conn.execute("SELECT * FROM xp_bonuses WHERE parent_id=?", (p['id'],)).fetchall()
        ledger.append({"time": str(p['timestamp']).split(' ')[1], "taskId": p['task_id'], "totalXp": p['base_xp'] + sum(b['bonus_xp'] for b in bonuses), "bonuses": [{"name": b['bonus_name'], "xp": b['bonus_xp'], "color": b['color']} for b in bonuses]})
    return jsonify(ledger)

@app.route('/api/v1/dashboard/live')
def dashboard_live():
    conn = get_db()
    simulate_rival_snatch(); run_automation_daemon(MY_NODE_ID)
    daemon_event = session.pop('daemon_msg', None)
    my_node = conn.execute('SELECT xp FROM nodes WHERE node_id = ?', (MY_NODE_ID,)).fetchone()
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT 5').fetchall()
    return jsonify({'balance': get_secure_balance(conn, MY_NODE_ID), 'xp': my_node['xp'] if my_node else 0, 'tasks': [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks], 'daemon_event': daemon_event})

@app.route('/api/v1/market/claim/<int:bid_id>', methods=['POST'])
def claim_bid(bid_id):
    conn = get_db()
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE bid_id=?", (bid_id,)).fetchone()
    if bid and bid['status'] == 'PENDING':
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid_id,))
        update_secure_wallet(conn, MY_NODE_ID, bid['sats_offered'])
        conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (?, ?, 'OPEN', ?)", (f"TASK-{random.randint(1000, 9999)}", bid['sats_offered'], bid['task_type']))
        conn.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task invalid'})

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task_api():
    data = request.json; conn = get_db(); payout = data.get('payout', 0)
    c = conn.execute("INSERT INTO xp_history (node_id, task_id, base_xp) VALUES (?, ?, ?) RETURNING id", (data.get('node_id'), data.get('task_id'), 500))
    parent_db_id = c.fetchone()['id']
    conn.execute("INSERT INTO xp_bonuses (parent_id, bonus_name, bonus_xp, color) VALUES (?, ?, ?, ?)", (parent_db_id, f"Boost ({data.get('task_id')})", payout, "#ff9f00"))
    bypass_bonus = 30 if data.get('bypass') else 0
    if bypass_bonus: conn.execute("INSERT INTO xp_bonuses (parent_id, bonus_name, bonus_xp, color) VALUES (?, ?, ?, ?)", (parent_db_id, "Secret Bypass", bypass_bonus, "#2ecc71"))
    update_secure_wallet(conn, data.get('node_id'), payout)
    conn.execute("UPDATE nodes SET xp = xp + ? WHERE node_id = ?", (500 + payout + bypass_bonus, data.get('node_id')))
    conn.execute("DELETE FROM tasks WHERE task_id = ?", (data.get('task_id'),))
    conn.commit()
    return jsonify({"status": "success"})

@app.route('/api/register', methods=['POST'])
def register_node():
    node_id = request.json.get('node_id'); conn = get_db()
    conn.execute("INSERT INTO nodes (node_id, hostname, last_seen) VALUES (?, ?, ?) ON CONFLICT(node_id) DO UPDATE SET last_seen=EXCLUDED.last_seen", (node_id, "Docker-Hybrid", time.time()))
    conn.commit()
    return jsonify({"status": "pulse_received"})

@app.route('/api/v1/rivals/feed')
def rival_feed():
    if random.random() > 0.3:
        rv = random.choice(["OMNI_CORP_09", "VOID_RUNNER", "KAOS_ENGINE"])
        return jsonify({'has_msg': True, 'rival': rv, 'message': f"Task #{random.randint(1000,9999)} seized.", 'timestamp': time.strftime("%H:%M:%S")})
    return jsonify({'has_msg': False})

if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO nodes (node_id, total_earned, xp, last_seen) VALUES (?, '0', 0, ?) ON CONFLICT (node_id) DO NOTHING", (MY_NODE_ID, time.time()))
        db.commit()
    app.run(host='0.0.0.0', port=5000)