import sqlite3
import random
import time
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session

# 1. Load Environment Variables (Security First)
load_dotenv()

# --- Core Imports ---
# We use a try/except block to handle different running contexts (direct vs module)
try:
    from backend.core import pulse
    from backend.core import rivals # Rival Logic Import
except ImportError:
    # Fallback if running directly or if structure varies
    try:
        from core import pulse
        from core import rivals
    except ImportError:
        print("⚠️ WARNING: Could not import core modules (pulse/rivals). Real-time stats may be unavailable.")
        pulse = None
        rivals = None

# --- Economics Engine Imports ---
try:
    from backend.economics.l2_escrow import L2EscrowEngine, L2Transaction, ChainID
    # Initialize the bridge to Base Mainnet (Simulated)
    escrow_engine = L2EscrowEngine()
    print("💰 L2 Escrow Engine: ONLINE (Base Mainnet)")
except ImportError:
    print("⚠️ L2 Escrow module not found. Financial settlement will be skipped.")
    escrow_engine = None

# 2. Define Paths to the Frontend
# We go "up" one level (..) from backend/ to root, then into frontend/public
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend", "public")

# 3. Initialize the Application
app = Flask(__name__, 
            template_folder=FRONTEND_DIR, 
            static_folder=FRONTEND_DIR,
            static_url_path="/static")

# 4. Configure Secrets (Safe from GitHub leaks)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_key_fallback_do_not_use')

# CONFIGURATION
# ---------------------------------------------------------
DATABASE = 'registry.db'
# UPDATED: Real Hardware ID from attestation script
MY_NODE_ID = "NODE_79F9F798"

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

# --- RIVAL CHATTER DICTIONARY ---
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

# --- DAEMON & RIVAL LOGIC ---
# ---------------------------------------------------------

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
        
        # Log global automated task claim
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                     ("AUTOMATION", f"Node {node_id} secured task {new_task_id} via Daemon"))
        
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
        
        # MAIN XP LOG (Parent Entries)
        db.execute('''CREATE TABLE IF NOT EXISTS xp_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            task_id TEXT,
            base_xp INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        # SUB-BONUSES (Child Entries)
        db.execute('''CREATE TABLE IF NOT EXISTS xp_bonuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER, -- Links to xp_history.id
            bonus_name TEXT,
            bonus_xp INTEGER,
            color TEXT,
            FOREIGN KEY (parent_id) REFERENCES xp_history(id) ON DELETE CASCADE
        )''')

        # GLOBAL EVENT LOG (Network-wide history)
        db.execute('''CREATE TABLE IF NOT EXISTS global_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        # Ensure core tables exist
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

    # Initial load doesn't need tasks, they are fetched via JS
    return render_template('dashboard.html', node=my_node, tasks=[])

@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    conn = get_db()
    if request.method == 'POST':
        task_type = request.form.get('task_type')
        sats = request.form.get('sats')
        color = request.form.get('color') or '#2ecc71'
        req_id = f"REQ-{random.randint(10000, 99999)}"
        conn.execute('''
            INSERT INTO marketplace_bids 
            (requester_id, sats_offered, task_type, status, color) 
            VALUES (?, ?, ?, 'PENDING', ?)
        ''', (req_id, sats, task_type, color))
        
        # Log global marketplace broadcast
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
    balance = my_node['total_earned'] if my_node else 0
    node_id = my_node['node_id'] if my_node else target_node
    owned = [row['item_id'] for row in conn.execute('SELECT item_id FROM purchases WHERE node_id=?', (node_id,)).fetchall()]
    return render_template('shop.html', items=SHOP_ITEMS, balance=balance, owned=owned, node_id=node_id)

# --- API ENDPOINTS ---
# ---------------------------------------------------------

@app.route('/api/v1/network/stats')
def get_network_stats():
    conn = get_db()
    total_sats = conn.execute("SELECT SUM(total_earned) FROM nodes").fetchone()[0] or 0
    active_cutoff = time.time() - 300
    active_nodes = conn.execute("SELECT COUNT(*) FROM nodes WHERE last_seen > ?", (active_cutoff,)).fetchone()[0]
    
    return jsonify({
        "total_volume": f"{total_sats:,}",
        "active_nodes": active_nodes,
        "protocol_v": "1.4.1",
        "status": "STABLE"
    })

@app.route('/api/v1/network/events/history')
def get_event_history():
    """Fetches the global network event history."""
    conn = get_db()
    events = conn.execute("SELECT * FROM global_events ORDER BY timestamp DESC LIMIT 20").fetchall()
    return jsonify([dict(e) for e in events])

@app.route('/api/v1/network/leaderboard')
def get_leaderboard():
    """Generates global rankings pitting the human node against AI Rivals."""
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
    conn = get_db()
    target_node = MY_NODE_ID 
    
    # --- RIVAL LOGIC ENGINE (HUNTER-KILLER) ---
    snatched = []
    if rivals:
        snatched = rivals.run_rival_logic(conn)
    # -----------------------

    run_automation_daemon(target_node) 
    
    # Check if we have a Rival Notification
    rival_event = None
    if snatched:
        last_snatch = snatched[-1]
        rival_event = f"⚠️ {last_snatch['rival']} stole {last_snatch['sats']} Sats!"

    daemon_event = session.pop('daemon_msg', None)
    
    # --- UPDATED FEED LOGIC: MERGE BIDS & TASKS ---
    # 1. Get Pending Bids (The "Race")
    pending_bids = conn.execute("SELECT * FROM marketplace_bids WHERE status='PENDING' ORDER BY created_at DESC LIMIT 3").fetchall()
    # 2. Get Active Tasks (The "Work")
    active_tasks = conn.execute('SELECT * FROM tasks ORDER BY ROWID DESC LIMIT 3').fetchall()

    combined_feed = []
    
    # Add Bids (Action: CLAIM)
    for bid in pending_bids:
        combined_feed.append({
            'id': f"BID-{bid['bid_id']}", # Virtual ID
            'real_id': bid['bid_id'],
            'type': bid['task_type'],
            'reward': bid['sats_offered'],
            'status': 'OPPORTUNITY' # Special flag for frontend
        })
        
    # Add Tasks (Action: COMPLETE)
    for task in active_tasks:
        combined_feed.append({
            'id': task['task_id'],
            'real_id': task['task_id'],
            'type': task['task_type'],
            'reward': task['bid_sats'],
            'status': 'ACTIVE'
        })
    # ---------------------------------------------

    my_node = conn.execute('SELECT total_earned, xp FROM nodes WHERE node_id = ?', (target_node,)).fetchone()
    
    return jsonify({
        'balance': my_node['total_earned'] if my_node else 0,
        'xp': my_node['xp'] if my_node else 0,
        'tasks': combined_feed, # Now includes BIDS
        'daemon_event': daemon_event,
        'rival_event': rival_event 
    })

@app.route('/api/v1/market/claim/<int:bid_id>', methods=['POST'])
def claim_bid(bid_id):
    conn = get_db()
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE bid_id=?", (bid_id,)).fetchone()
    if bid and bid['status'] == 'PENDING':
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid_id,))
        target_node = request.json.get('node_id', MY_NODE_ID) 
        
        # NOTE: We do not pay immediately. We convert to a Task.
        # conn.execute("UPDATE nodes SET total_earned = total_earned + ? WHERE node_id=?", (bid['sats_offered'], target_node))
        
        new_task_id = f"TASK-{random.randint(1000, 9999)}"
        conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (?, ?, 'OPEN', ?)", 
                     (new_task_id, bid['sats_offered'], bid['task_type']))
        conn.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task already claimed or invalid'})

@app.route('/api/v1/tasks/complete', methods=['POST'])
def complete_task_api():
    """
    Validates work and triggers L2 Settlement.
    """
    data = request.json
    conn = get_db()
    
    payout = data.get('payout', 0)
    task_id = data.get('task_id')
    node_id = data.get('node_id')

    # L2 SETTLEMENT
    tx_hash = "OFF-CHAIN"
    if escrow_engine:
        try:
            mock_locked_tx = L2Transaction(
                tx_hash=f"0x_vault_{task_id}",
                chain_id=ChainID.BASE_MAINNET.value,
                amount_usdc=payout / 1000.0,
                status="LOCKED",
                agent_wallet="0xAgent_Vault_7A",
                node_wallet="PENDING"
            )
            node_evm_wallet = f"0x{node_id.replace('NODE-', '')}..."
            escrow_engine.release_funds(mock_locked_tx, node_evm_wallet)
            tx_hash = mock_locked_tx.tx_hash
            
            conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                         ("CHAIN_TX", f"Settled {payout} Sats on Base: {tx_hash} -> {node_id}"))
        except Exception as e:
            print(f"❌ Escrow Settlement Error: {e}")
            conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                         ("ERROR", f"Settlement Failed for {task_id}: {str(e)}"))

    # Update Local Ledger
    cursor = conn.execute(
        "INSERT INTO xp_history (node_id, task_id, base_xp) VALUES (?, ?, ?)",
        (node_id, task_id, 500)
    )
    parent_db_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO xp_bonuses (parent_id, bonus_name, bonus_xp, color) VALUES (?, ?, ?, ?)",
        (parent_db_id, f"Rubber-Band Boost ({task_id})", payout, "#ff9f00")
    )
    
    total_xp_gain = 500 + payout
    conn.execute("UPDATE nodes SET total_earned = total_earned + ?, xp = xp + ? WHERE node_id = ?", 
                 (payout, total_xp_gain, node_id))
    
    if tx_hash == "OFF-CHAIN":
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                     ("SETTLEMENT", f"Node {node_id} completed {task_id} (+{payout} Sats)"))
    
    conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()
    
    return jsonify({
        "status": "success", 
        "tx_hash": tx_hash,
        "new_balance": payout
    })

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

# --- MERGED & FIXED HANDSHAKE ENDPOINT ---
# ---------------------------------------------------------
@app.route('/api/v1/node/register', methods=['POST'])
def register_node():
    """
    The Handshake: Receives a 'Hardware Identity' and registers it.
    """
    data = request.json
    node_id = data.get('node_id')
    public_key = data.get('public_key')
    hardware_stats = data.get('hardware_stats', {})
    
    if not node_id:
        return jsonify({"error": "Missing Identity Data"}), 400

    if pulse:
        pulse.register_node(node_id, hardware_stats)

    conn = get_db()
    host_info = hardware_stats.get('processor') or hardware_stats.get('cpu_model') or "Generic-Node-v1"
    
    conn.execute('''
        INSERT INTO nodes (node_id, hostname, last_seen) 
        VALUES (?, ?, ?) 
        ON CONFLICT(node_id) 
        DO UPDATE SET last_seen=excluded.last_seen
    ''', (node_id, host_info, time.time()))
    
    conn.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                 ("NETWORK", f"Heartbeat pulse detected from Node {node_id}"))
    conn.commit()
    
    return jsonify({
        "status": "registered",
        "node_id": node_id,
        "message": "Welcome to the Proxy Agent Network. Heartbeat accepted."
    })

if __name__ == '__main__':
    with app.app_context():
        db = get_db()
        db.execute("INSERT OR IGNORE INTO nodes (node_id, total_earned, xp, last_seen) VALUES (?, 0, 0, ?)", 
                   (MY_NODE_ID, time.time()))
        db.execute("INSERT INTO global_events (event_type, message) VALUES (?, ?)", 
                   ("SYSTEM", "Proxy Protocol v1.4.1 initialized. Registry online."))
        db.commit()
    app.run(debug=True, port=5000, host='0.0.0.0')