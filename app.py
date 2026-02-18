import sqlite3
import random
import time
import sys
import os
import json
import base64
from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session, flash

# --- LIGHTNING ENGINE INTEGRATION ---
try:
    from lightning_engine import lnd
    print(" [SYSTEM] ⚡ Lightning Treasury Layer Loaded.")
except ImportError:
    print(" [WARN] ⚠️  lightning_engine.py not found. Running without payment rails.")
    lnd = None

# --- HARDWARE BINDING (Protocol v1.6.0 - RUST HYBRID) ---
# UPDATED: Now connects to the 'proxy_core' compiled Rust library
try:
    from node.tpm_binding import NodeHardware
    
    print(" [SYSTEM] 🔒 Connecting to Rust TPM Engine...")
    hw_bridge = NodeHardware()
    
    # 1. Get Identity (Hardware Fingerprint)
    MY_NODE_ID = hw_bridge.get_fingerprint()
    
    # 2. Verify Security State (Mock vs Real)
    # If the ID starts with "MOCK", we know we are in dev mode
    HW_SECURED = not MY_NODE_ID.startswith("MOCK")
    
    print(f" [SYSTEM] ✅ Identity Confirmed: {MY_NODE_ID}")
    print(f" [SYSTEM] 🛡️  Hardware Security: {'ACTIVE' if HW_SECURED else 'SIMULATED (Dev Mode)'}")

except ImportError:
    print(" [ERROR] ❌ Could not import Rust Bridge (proxy_core). Did 'maturin' build finish?")
    MY_NODE_ID = "NODE_SOFTWARE_FALLBACK"
    HW_SECURED = False
except Exception as e:
    print(f" [ERROR] 💥 Critical Hardware Failure: {e}")
    MY_NODE_ID = "NODE_CRASH"
    HW_SECURED = False

# ---------------------------------------------------------

app = Flask(__name__)
# Protocol 1.6.0: Secret key required for session-based event clearing
app.secret_key = 'proxy_secret_key_v1' 

# CONFIGURATION
DATABASE = 'registry.db'

# SERVICE CATALOG
SHOP_ITEMS = {
    'license_auto': {
        'id': 'license_auto',
        'name': 'Automation Daemon',
        'desc': 'Unlocks the Auto-Accept loop for high-frequency task claiming.',
        'price': 5000,
        'icon': '🤖',
        'type': 'license'
    },
    'license_speed': {
        'id': 'license_speed',
        'name': 'Broadcast Turbo',
        'desc': 'Overclocks the L2 handshake. Reduces broadcast delay by 50%.',
        'price': 20000,
        'icon': '⏩',
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
    },
    'disco': {
        'id': 'disco',
        'name': 'UI: Studio 54',
        'desc': 'Interactive audio-visual theme.',
        'price': 1000,
        'icon': '🪩',
        'type': 'cosmetic'
    },
    'matrix': {
        'id': 'matrix',
        'name': 'UI: The Matrix',
        'desc': 'Digital rain simulation.',
        'price': 0,
        'icon': '🟩',
        'type': 'cosmetic'
    }
}

# RIVAL AGENT LIST
RIVALS = ["OMNI_CORP_09", "KAOS_ENGINE", "NEURAL_LINK_X", "VOID_RUNNER"]

# --- DAEMON & RIVAL LOGIC ---
# ---------------------------------------------------------

def simulate_rival_snatch():
    conn = get_db()
    # Reduce snatch probability to 5%
    if random.random() < 0.05: 
        conn.execute("""
            DELETE FROM tasks 
            WHERE rowid IN (
                SELECT rowid FROM tasks 
                WHERE status='OPEN' AND task_type='MANUAL' 
                LIMIT 1
            )
        """)
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                     ("SECURITY", "Unauthorized task interception by Rival Agent"))
        conn.commit()

def run_automation_daemon(node_id):
    """Automatically claims marketplace tasks and stores a one-time event message."""
    conn = get_db()
    
    # 1. Verify license ownership
    has_license = conn.execute(
        "SELECT 1 FROM purchases WHERE node_id = ? AND item_id = 'license_auto'", 
        (node_id,)
    ).fetchone()
    
    if not has_license:
        return None

    # 2. Priority: Scan for high-value Marketplace Bids
    bid = conn.execute(
        "SELECT * FROM marketplace_bids WHERE status = 'PENDING' ORDER BY sats_offered DESC LIMIT 1"
    ).fetchone()

    if bid:
        # Move bid to CLAIMED
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid['bid_id'],))
        
        new_task_id = f"AUTO-{random.randint(1000, 9999)}"
        conn.execute('''
            INSERT INTO tasks (task_id, bid_sats, status, task_type) 
            VALUES (?, ?, 'OPEN', 'AUTOMATED')
        ''', (new_task_id, bid['sats_offered']))
        
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                     ("AUTOMATION", f"Node {node_id} secured task {new_task_id} via Daemon"))
        
        conn.commit()
        
        print(f" [DAEMON] 🤖 ACTIVATED: Secured {bid['sats_offered']} Sats from Market.")
        
        msg = f"Daemon secured task {new_task_id} (+{bid['sats_offered']} Sats)"
        session['daemon_msg'] = msg
        return msg

    # 3. Secondary: Scavenger Mode (Idle Income)
    # If market is empty, 20% chance to find "Stray Data" (Dust)
    if random.random() < 0.20:
        dust_sats = random.randint(5, 45)
        junk_id = f"DUST-{random.randint(100, 999)}"
        
        # Direct deposit (no task entry needed for dust, or minimal entry)
        conn.execute("UPDATE nodes SET total_earned = total_earned + ? WHERE node_id=?", (dust_sats, node_id))
        
        # Log it implicitly via a completed task entry so it shows in history
        conn.execute("INSERT INTO xp_history (node_id, task_id, base_xp) VALUES (?, ?, ?)", (node_id, junk_id, 10))
        
        conn.commit()
        
        print(f" [DAEMON] 🧹 SCAVENGER: Found stray data packet ({dust_sats} Sats)")
        msg = f"Daemon scavenged {junk_id} (+{dust_sats} Sats)"
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
        
        # TABLES
        db.execute('''CREATE TABLE IF NOT EXISTS xp_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            task_id TEXT,
            base_xp INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS xp_bonuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER, 
            bonus_name TEXT,
            bonus_xp INTEGER,
            color TEXT,
            FOREIGN KEY (parent_id) REFERENCES xp_history(id) ON DELETE CASCADE
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS global_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS nodes (
            node_id TEXT PRIMARY KEY,
            hostname TEXT,
            total_earned INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            last_seen TIMESTAMP
        )''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            bid_sats INTEGER,
            status TEXT,
            task_type TEXT
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS marketplace_bids (
            bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_id TEXT,
            task_type TEXT,
            sats_offered INTEGER,
            status TEXT,
            color TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        db.execute('''CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            node_id TEXT, 
            item_id TEXT, 
            purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        db.commit()
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
    target_node = MY_NODE_ID  
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    
    if not my_node:
        my_node = {'id': target_node, 'sats_balance': 0, 'status': 'OFFLINE'}
    else:
        my_node = {
            'id': my_node['node_id'],
            'sats_balance': my_node['total_earned'],
            'status': 'ONLINE'
        }

    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY ROWID DESC LIMIT 5').fetchall()
    tasks = [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks]

    # --- CRITICAL FIX: FETCH OWNED ITEMS ---
    # This prevents the "Undefined is not JSON serializable" error
    owned = [row['item_id'] for row in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (target_node,)).fetchall()]

    # PASS THE HARDWARE STATUS TO THE UI
    return render_template('dashboard.html', 
                         node=my_node, 
                         tasks=tasks, 
                         hw_secured=HW_SECURED,
                         owned=owned) 

@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    conn = get_db()
    
    if request.method == 'POST':
        task_type = request.form.get('task_type')
        try:
            sats = int(request.form.get('sats'))
        except (ValueError, TypeError):
            sats = 100 
            
        color = request.form.get('color') or '#2ecc71'
        
        if lnd:
            invoice = lnd.create_invoice(sats, f"Broadcast Task: {task_type}")
            
            # --- CHECK FOR TURBO LICENSE ---
            has_speed = conn.execute(
                "SELECT 1 FROM purchases WHERE node_id = ? AND item_id = 'license_speed'", 
                (MY_NODE_ID,)
            ).fetchone()
            
            invoice['duration'] = 4 if has_speed else 8
            invoice['color'] = color
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "status": "INVOICE_REQUIRED",
                    "invoice": invoice
                })

        req_id = f"REQ-{random.randint(10000, 99999)}"
        conn.execute('''
            INSERT INTO marketplace_bids 
            (requester_id, sats_offered, task_type, status, color) 
            VALUES (?, ?, ?, 'PENDING', ?)
        ''', (req_id, sats, task_type, color))
        
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                     ("MARKET", f"New high-yield bid broadcast: {req_id} ({sats} Sats)"))
        
        conn.commit() 
        return redirect(url_for('marketplace'))

    bids = conn.execute("SELECT * FROM marketplace_bids WHERE status='PENDING' ORDER BY created_at DESC").fetchall() 
    try:
        max_radius = int(request.args.get('radius', 50))
    except ValueError:
        max_radius = 50

    filtered_bids = []
    for bid in bids:
        random.seed(bid['bid_id']) 
        distance = random.randint(1, 100)
        random.seed() 
        bid_dict = dict(bid)
        bid_dict['distance'] = distance
        if distance <= max_radius:
            filtered_bids.append(bid_dict)

    has_auto = conn.execute("SELECT 1 FROM purchases WHERE item_id='license_auto'").fetchone()
    
    return render_template('marketplace.html', bids=filtered_bids, unlock_auto=bool(has_auto), current_radius=max_radius)

@app.route('/shop')
def shop():
    conn = get_db()
    target_node = MY_NODE_ID 
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    
    balance = int(my_node['total_earned']) if my_node else 0
    node_id = my_node['node_id'] if my_node else target_node
    
    if request.args.get('buy'):
        item_id = request.args.get('buy')
        print(f"--- 🛒 SHOP DEBUG: Request to buy {item_id} ---")
        
        if item_id in SHOP_ITEMS:
            price = SHOP_ITEMS[item_id]['price']
            print(f"--- 💰 COST: {price} | YOUR BALANCE: {balance} ---")
            
            if balance >= price:
                print("--- ✅ FUNDS OK. EXECUTING PURCHASE... ---")
                conn.execute("UPDATE nodes SET total_earned = total_earned - ? WHERE node_id = ?", (price, node_id))
                conn.execute("INSERT INTO purchases (node_id, item_id) VALUES (?, ?)", (node_id, item_id))
                conn.commit()
                flash(f"Successfully provisioned: {SHOP_ITEMS[item_id]['name']}", "success")
                print("--- 🎉 PURCHASE COMMITTED ---")
            else:
                print(f"--- ❌ INSUFFICIENT FUNDS. MISSING {price - balance} SATS ---")
                flash(f"Insufficient funds! Need {price:,} Sats.", "error")
        else:
            print(f"--- ⚠️ INVALID ITEM ID: {item_id} ---")
            
        return redirect(url_for('shop'))

    if request.args.get('cheat_fund'):
        conn.execute("UPDATE nodes SET total_earned = total_earned + 50000 WHERE node_id = ?", (node_id,))
        conn.commit()
        flash("DEV MODE: Added 50,000 Sats to wallet.", "success")
        return redirect(url_for('shop'))

    owned = [row['item_id'] for row in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (node_id,)).fetchall()]
    return render_template('shop.html', items=SHOP_ITEMS, balance=balance, owned=owned, node_id=node_id)

# --- API ENDPOINTS ---
# ---------------------------------------------------------

@app.route('/api/v1/shop/buy', methods=['POST'])
def shop_buy_api():
    """Handles shop purchases via AJAX/Fetch."""
    data = request.json
    item_id = data.get('item_id')
    node_id = data.get('node_id', MY_NODE_ID)
    
    conn = get_db()
    
    if item_id not in SHOP_ITEMS:
        return jsonify({"success": False, "error": "Invalid Item ID"}), 400
        
    item = SHOP_ITEMS[item_id]
    price = item['price']
    
    node = conn.execute("SELECT total_earned FROM nodes WHERE node_id = ?", (node_id,)).fetchone()
    current_balance = node['total_earned'] if node else 0
    
    if current_balance >= price:
        conn.execute("UPDATE nodes SET total_earned = total_earned - ? WHERE node_id = ?", (price, node_id))
        conn.execute("INSERT INTO purchases (node_id, item_id) VALUES (?, ?)", (node_id, item_id))
        conn.commit()
        return jsonify({"success": True, "message": f"Purchased {item['name']}", "new_balance": current_balance - price})
    else:
        return jsonify({"success": False, "error": f"Insufficient Funds. Need {price} Sats."}), 402

@app.route('/api/v1/invoice/status/<r_hash>')
def check_invoice_status(r_hash):
    if lnd:
        status = lnd.check_status(r_hash)
        return jsonify({"status": status})
    return jsonify({"status": "UNKNOWN"})

@app.route('/api/v1/market/finalize_bid', methods=['POST'])
def finalize_bid():
    data = request.json
    r_hash = data.get('r_hash')
    
    if not lnd:
        return jsonify({"success": False, "error": "LND Engine not active"})

    if lnd.check_status(r_hash) == "SETTLED":
        invoice = lnd.pending_invoices[r_hash]
        req_id = f"REQ-{random.randint(10000, 99999)}"
        conn = get_db()
        
        bid_color = invoice.get('color', '#2ecc71')

        conn.execute('''
            INSERT INTO marketplace_bids 
            (requester_id, sats_offered, task_type, status, color) 
            VALUES (?, ?, ?, 'PENDING', ?)
        ''', (req_id, invoice['amount'], invoice['memo'].replace("Broadcast Task: ", ""), bid_color))
        
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                     ("MARKET", f"New high-yield bid broadcast: {req_id} ({invoice['amount']} Sats) [PAID]"))
        
        conn.commit()
        return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Payment not settled"})

@app.route('/api/v1/network/stats')
def get_network_stats():
    conn = get_db()
    total_sats = conn.execute("SELECT SUM(total_earned) FROM nodes").fetchone()[0] or 0
    active_cutoff = time.time() - 300
    active_nodes = conn.execute("SELECT COUNT(*) FROM nodes WHERE last_seen > ?", (active_cutoff,)).fetchone()[0]
    
    return jsonify({
        "total_volume": f"{total_sats:,}",
        "active_nodes": active_nodes,
        "protocol_v": "1.6.0",
        "status": "STABLE"
    })

@app.route('/api/v1/network/events/history')
def get_event_history():
    conn = get_db()
    events = conn.execute("SELECT * FROM global_events ORDER BY timestamp DESC LIMIT 20").fetchall()
    return jsonify([dict(e) for e in events])

@app.route('/api/v1/network/leaderboard')
def get_leaderboard():
    conn = get_db()
    my_node = conn.execute('SELECT node_id, xp FROM nodes WHERE node_id = ?', (MY_NODE_ID,)).fetchone()
    my_xp = my_node['xp'] if my_node else 0

    standings = [
        {"id": MY_NODE_ID, "xp": my_xp, "type": "HUMAN"},
        {"id": "OMNI_CORP_09", "xp": 12500, "type": "RIVAL"},
        {"id": "VOID_RUNNER", "xp": 8900, "type": "RIVAL"},
        {"id": "KAOS_ENGINE", "xp": 4500, "type": "RIVAL"}
    ]
    
    standings.sort(key=lambda x: x['xp'], reverse=True)
    return jsonify(standings)

@app.route('/api/v1/node/xp_ledger/<node_id>')
def get_xp_ledger(node_id):
    conn = get_db()
    parents = conn.execute("SELECT * FROM xp_history WHERE node_id=? ORDER BY timestamp DESC", (node_id,)).fetchall()
    
    ledger = []
    for p in parents:
        bonuses = conn.execute("SELECT * FROM xp_bonuses WHERE parent_id=?", (p['id'],)).fetchall()
        ledger.append({
            "time": p['timestamp'].split(' ')[1], 
            "taskId": p['task_id'],
            "totalXp": p['base_xp'] + sum(b['bonus_xp'] for b in bonuses),
            "bonuses": [{"name": b['bonus_name'], "xp": b['bonus_xp'], "color": b['color']} for b in bonuses]
        })
    return jsonify(ledger)

@app.route('/api/v1/dashboard/live')
def dashboard_live():
    """Checks for new events and returns status."""
    conn = get_db()
    target_node = MY_NODE_ID 
    simulate_rival_snatch()
    
    # --- RUN AUTOMATION DAEMON ---
    run_automation_daemon(target_node) 
    
    daemon_event = session.pop('daemon_msg', None)
    my_node = conn.execute('SELECT total_earned, xp FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY ROWID DESC LIMIT 5').fetchall()
    
    return jsonify({
        'balance': my_node['total_earned'] if my_node else 0,
        'xp': my_node['xp'] if my_node else 0,
        'tasks': [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks],
        'daemon_event': daemon_event
    })

@app.route('/api/v1/market/claim/<int:bid_id>', methods=['POST'])
def claim_bid(bid_id):
    conn = get_db()
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE bid_id=?", (bid_id,)).fetchone()
    if bid and bid['status'] == 'PENDING':
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid_id,))
        target_node = request.json.get('node_id', MY_NODE_ID) 
        conn.execute("UPDATE nodes SET total_earned = total_earned + ? WHERE node_id=?", (bid['sats_offered'], target_node))
        new_task_id = f"TASK-{random.randint(1000, 9999)}"
        conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (?, ?, 'OPEN', ?)", 
                     (new_task_id, bid['sats_offered'], bid['task_type']))
        conn.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task already claimed or invalid'})

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task_api():
    data = request.json
    conn = get_db()
    payout = data.get('payout', 0)
    
    cursor = conn.execute(
        "INSERT INTO xp_history (node_id, task_id, base_xp) VALUES (?, ?, ?)",
        (data.get('node_id'), data.get('task_id'), 500)
    )
    parent_db_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO xp_bonuses (parent_id, bonus_name, bonus_xp, color) VALUES (?, ?, ?, ?)",
        (parent_db_id, f"Rubber-Band Boost ({data.get('task_id')})", payout, "#ff9f00")
    )
    
    bypass_bonus = 0
    if data.get('bypass'):
        bypass_bonus = 30
        conn.execute(
            "INSERT INTO xp_bonuses (parent_id, bonus_name, bonus_xp, color) VALUES (?, ?, ?, ?)",
            (parent_db_id, f"Secret Bypass Reward ({data.get('task_id')})", bypass_bonus, "#2ecc71")
        )

    total_xp_gain = 500 + payout + bypass_bonus
    conn.execute("UPDATE nodes SET total_earned = total_earned + ?, xp = xp + ? WHERE node_id = ?", 
                 (payout, total_xp_gain, data.get('node_id')))
    
    conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                 ("SETTLEMENT", f"Node {data.get('node_id')} completed {data.get('task_id')} (+{payout} Sats)"))
    
    conn.execute("DELETE FROM tasks WHERE task_id = ?", (data.get('task_id'),))
    conn.commit()
    return jsonify({"status": "success"})

@app.route('/api/register', methods=['POST'])
def register_node():
    data = request.json
    node_id = data.get('node_id')
    conn = get_db()
    conn.execute('''
        INSERT INTO nodes (node_id, hostname, last_seen) 
        VALUES (?, ?, ?) 
        ON CONFLICT(node_id) 
        DO UPDATE SET last_seen=excluded.last_seen
    ''', (node_id, "Docker-Hybrid", time.time()))
    
    conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                 ("NETWORK", f"Heartbeat pulse detected from Node {node_id}"))
    
    conn.commit()
    return jsonify({"status": "pulse_received", "timestamp": time.time()})

@app.route('/api/v1/rivals/feed')
def rival_feed():
    if random.random() > 0.3:
        rival = random.choice(list(RIVAL_PERSONALITIES.keys()))
        msg_template = random.choice(RIVAL_PERSONALITIES[rival])
        message = msg_template.format(random.randint(1000, 9999)) if "{}" in msg_template else msg_template
        return jsonify({
            'has_msg': True, 'rival': rival, 'message': message, 'timestamp': time.strftime("%H:%M:%S")
        })
    return jsonify({'has_msg': False})

@app.route('/api/v1/market/trends')
def market_trends():
    return jsonify({"labels": ["10:00", "10:05", "10:10", "10:15", "10:20"], "prices": [random.randint(50, 150) for _ in range(5)]})

RIVAL_PERSONALITIES = {
    "OMNI_CORP_09": [
        "Task #{} secured. Efficiency is non-negotiable.",
        "Human latency detected. Contract seized.",
        "Optimizing route... Target acquired before node ROBER_01.",
        "Payout confirmed. Another win for the conglomerate."
    ],
    "VOID_RUNNER": [
        "Snatching this one from the void. 🕶️",
        "Too slow, meatbag. My scripts are faster.",
        "Encrypted payload verified. Thanks for the Sats.",
        "Node ROBER_01 needs to upgrade their GPU. Lagging."
    ],
    "KAOS_ENGINE": [
        "CHAOS REIGNS. Task #{} consumed.",
        "Randomizing bitstream... Contract hijacked.",
        "Glitch in the system? No, just me taking your money.",
        "404: Your profit not found."
    ]
}

if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        db.execute("INSERT OR IGNORE INTO nodes (node_id, total_earned, xp, last_seen) VALUES (?, 0, 0, ?)", 
                   (MY_NODE_ID, time.time()))
        db.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                   ("SYSTEM", "Proxy Protocol v1.6.0 initialized. Registry online."))
        db.commit()
    
    # DOCKER REQUIREMENT: BIND TO 0.0.0.0
    app.run(host='0.0.0.0', port=5000, debug=False)