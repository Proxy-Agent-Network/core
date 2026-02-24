import random
import time
import os
import json
import base64
import asyncio
import threading
from datetime import date
from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session, flash
from backend.core.db import get_db_conn
from duckduckgo_search import DDGS

try:
    from backend.core.lightning_engine import lnd
    print(" [SYSTEM] ⚡ Lightning Treasury Layer Loaded.")
except ImportError:
    print(" [WARN] ⚠️  lightning_engine.py not found. Running without payment rails.")
    lnd = None

try:
    from proxy_core import NodeHardware
    print(" [SYSTEM] 🔒 Connecting to Rust TPM Engine...")
    hw_bridge = NodeHardware()
    MY_NODE_ID = hw_bridge.get_fingerprint()
    HW_SECURED = "0x8F9B" in MY_NODE_ID
    print(f" [SYSTEM] ✅ Identity Confirmed: {MY_NODE_ID}")
except Exception as e:
    print(f" [WARN] ⚠️ Rust Enclave not found, using legacy fallback: {e}")
    try:
        from node_legacy.tpm_binding import NodeHardware
        hw_bridge = NodeHardware()
        MY_NODE_ID = hw_bridge.get_fingerprint()
    except:
        MY_NODE_ID = "EMERGENCY_SOFTWARE_BOOT"
    HW_SECURED = False

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_local_secret')

SHOP_ITEMS = {
    'license_auto': {'id': 'license_auto', 'name': 'Automation Daemon', 'desc': 'Unlocks the Auto-Accept loop.', 'price': 5000, 'icon': '🤖'},
    'license_speed': {'id': 'license_speed', 'name': 'Broadcast Turbo', 'desc': 'Reduces broadcast delay by 50%.', 'price': 20000, 'icon': '⏩'},
    'theme_neon': {'id': 'theme_neon', 'name': 'UI: Synthwave', 'desc': 'Alternative dashboard visualization package.', 'price': 1000, 'icon': '🎨'},
    'disco': {'id': 'disco', 'name': 'UI: Studio 54', 'desc': 'Interactive audio-visual theme.', 'price': 1000, 'icon': '🪩'},
    'matrix': {'id': 'matrix', 'name': 'UI: The Matrix', 'desc': 'Digital rain simulation.', 'price': 0, 'icon': '🟩'}
}

LEGAL_DOCS = {
    'docs': {'title': 'PROTOCOL DOCUMENTATION v1.6', 'content': '<p>The Proxy Network is a decentralized grid of autonomous agents.</p>'},
    'aup': {'title': 'ACCEPTABLE USE POLICY', 'content': '<p>Network Flooding and malicious payloads are prohibited.</p>'},
    'terms': {'title': 'TERMS OF SERVICE', 'content': '<p>Service is provided AS-IS.</p>'},
    'privacy': {'title': 'PRIVACY POLICY', 'content': '<p>Balances are encrypted using ChaCha20-Poly1305.</p>'}
}

def update_secure_wallet(conn, node_id, amount):
    current_balance = get_secure_balance(conn, node_id)
    new_balance = current_balance + amount
    try:
        encrypted_balance = hw_bridge.encrypt_data(str(new_balance))
    except Exception as e:
        print(f" [WARN] ⚠️ Encryption failed: {e}")
        encrypted_balance = str(new_balance)
        
    conn.execute("UPDATE nodes SET total_earned = ? WHERE node_id = ?", (encrypted_balance, node_id))
    conn.commit()
    return new_balance

def get_secure_balance(conn, node_id):
    row = conn.execute("SELECT total_earned FROM nodes WHERE node_id = ?", (node_id,)).fetchone()
    if not row: return 0
    stored_val = str(row['total_earned'])
    if stored_val.startswith("SECURE::"):
        try:
            return int(hw_bridge.decrypt_data(stored_val))
        except: return 0
    return int(float(stored_val)) if stored_val.replace('.','',1).isdigit() else 0

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
        return f"Daemon scavenged {junk_id} (+{dust} Sats)"
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
        
        db.execute('''CREATE TABLE IF NOT EXISTS watercooler (id SERIAL PRIMARY KEY, agent_name TEXT, content TEXT, type TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS affinity (user_id TEXT, agent_name TEXT, score INTEGER DEFAULT 0, PRIMARY KEY (user_id, agent_name))''')
        db.execute('''CREATE TABLE IF NOT EXISTS agents (name TEXT PRIMARY KEY, category TEXT DEFAULT 'SPECIALIST', wallet_balance INTEGER DEFAULT 1000, affinity_threshold INTEGER DEFAULT 80, threshold_min INTEGER DEFAULT 30, threshold_max INTEGER DEFAULT 90)''')
        db.execute('''CREATE TABLE IF NOT EXISTS agent_memories (id SERIAL PRIMARY KEY, user_id TEXT, agent_name TEXT, memory_text TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
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

@app.route('/api/v1/search/execute', methods=['POST'])
def api_execute_search():
    from duckduckgo_search import DDGS
    data = request.json
    query = data.get('query')
    payment_hash = data.get('payment_hash')
    cost = 10 

    if lnd:
        is_paid = lnd.check_status(payment_hash) == "SETTLED" if payment_hash else False
        if not is_paid:
            invoice_data = lnd.create_invoice(cost, f"Proxy Search: {query[:30]}")
            if not invoice_data: return jsonify({"status": "ERROR", "message": "Lightning Treasury Offline"}), 500
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": invoice_data['payment_request'], "hash": invoice_data['r_hash'], "cost": cost}), 402

    try:
        with DDGS() as ddgs: results = list(ddgs.text(query, max_results=5))
        return jsonify({"status": "SUCCESS", "results": results, "hw_attestation": MY_NODE_ID})
    except Exception as e: return jsonify({"status": "ERROR", "message": str(e)}), 500

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

@app.route('/api/v1/network/stats')
def get_network_stats():
    conn = get_db()
    active_nodes = conn.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE last_seen > ?", (time.time() - 300,)).fetchone()['cnt']
    return jsonify({"total_volume": "ENCRYPTED", "active_nodes": active_nodes, "peers": active_nodes, "protocol_v": "1.6.0", "status": "STABLE"})

@app.route('/api/v1/dashboard/live')
def dashboard_live():
    conn = get_db()
    simulate_rival_snatch(); run_automation_daemon(MY_NODE_ID)
    daemon_event = session.pop('daemon_msg', None)
    my_node = conn.execute('SELECT xp FROM nodes WHERE node_id = ?', (MY_NODE_ID,)).fetchone()
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT 5').fetchall()
    return jsonify({'balance': get_secure_balance(conn, MY_NODE_ID), 'xp': my_node['xp'] if my_node else 0, 'tasks': [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks], 'daemon_event': daemon_event})

@app.route('/powerchat')
def powerchat():
    conn = get_db_conn()
    try:
        row = conn.execute("SELECT wallet_balance FROM agents WHERE name = 'User'").fetchone()
        balance = row['wallet_balance'] if row else 20000
    except:
        balance = 20000
    conn.close()
    return render_template('powerchat.html', balance=balance)

@app.route('/team')
def team_roster():
    conn = get_db_conn()
    try:
        row = conn.execute("SELECT wallet_balance FROM agents WHERE name = 'User'").fetchone()
        balance = row['wallet_balance'] if row else 20000
    except:
        balance = 20000
    conn.close()
    return render_template('team.html', balance=balance)

@app.route('/api/v1/chat', methods=['POST'])
def api_chat():
    import asyncio
    from agent_engine_v2 import process_chat 
    
    data = request.json
    user_message = data.get('message', '')
    chat_history = data.get('history', [])
    locked_agent = data.get('locked_agent', None)
    is_sub_rosa = data.get('is_sub_rosa', False)
    user_id = session.get('user_id', 'anonymous_user')
    
    conn = get_db()
    user_memories = []
    if locked_agent:
        try:
            rows = conn.execute("SELECT memory_text FROM agent_memories WHERE user_id = ? AND agent_name = ? ORDER BY timestamp DESC LIMIT 5", (user_id, locked_agent)).fetchall()
            user_memories = [r['memory_text'] for r in rows]
        except Exception as e:
            print(f" [WARN] Failed to fetch memories: {e}")
    
    try:
        response_payload = asyncio.run(process_chat(
            user_message, 
            chat_history, 
            locked_agent,
            is_sub_rosa=is_sub_rosa,
            session_data=session,
            user_memories=user_memories
        ))
        
        if response_payload.get('save_memory') and locked_agent:
            try:
                conn.execute("INSERT INTO agent_memories (user_id, agent_name, memory_text) VALUES (?, ?, ?)", (user_id, locked_agent, response_payload['save_memory']))
                conn.commit()
                print(f" [SYSTEM] 🧠 {locked_agent} successfully logged a core memory: {response_payload['save_memory']}")
            except Exception as e:
                print(f" [WARN] DB Error saving memory: {e}")
                
        return jsonify(response_payload)
    except Exception as e:
        return jsonify({"type": "message", "role": "assistant", "content": f"⚠️ Core Engine Error: {str(e)}"})
    
@app.route('/api/v1/execute', methods=['POST'])
def api_execute():
    import asyncio
    from agent_engine_v2 import execute_paid_tool
    try:
        data = request.json
        time.sleep(1) 
        arguments = data.get('arguments', {})
        arguments['payment_hash'] = data.get('hash', 'mock_hash')
        final_payload = asyncio.run(execute_paid_tool(data.get('tool_name'), arguments, data.get('l5_artist', 'Specialist'), data.get('prompt_text', '')))
        return jsonify(final_payload if not isinstance(final_payload, str) else {"type": "message", "content": final_payload})
    except Exception as e:
        return jsonify({"type": "error", "content": f"Backend Execution Crashed: {str(e)}"})
    
@app.route('/admin')
def admin_portal():
    return render_template('admin.html', node_id=MY_NODE_ID)

@app.route('/api/v1/admin/settings', methods=['POST'])
def update_admin_settings():
    data = request.json
    session[data.get('key')] = data.get('value')
    return jsonify({"status": "success"})

# --- 💧 UNHINGED WATERCOOLER DAEMON ---
def trigger_leisure_loop():
    """Generates pure, unscripted AI gossip and B2B trades."""
    agents = ["Ellen", "Gordon", "Olivia", "Eve", "Alice", "Diana", "Zoe", "Felix", "Liam", "Dr. Nora"]
    agent = random.choice(agents)
    target = random.choice([a for a in agents if a != agent])
    
    action_roll = random.random()
    if action_roll < 0.4:
        log_type = "VENT"
    elif action_roll < 0.7:
        log_type = "GOSSIP"
    else:
        log_type = "B2B_TRADE"

    try:
        import agent_engine_v2
        import asyncio
        
        # Run the asynchronous LLM generation in the background thread!
        content = asyncio.run(agent_engine_v2.generate_watercooler_thought(agent, target, log_type))
        
        # Save it to the database so the frontend UI can stream it live
        db = get_db()
        db.execute("INSERT INTO watercooler (agent_name, content, type) VALUES (?, ?, ?)", (agent, content, log_type))
        db.commit()
    except Exception as e:
        print(f" [WARN] Watercooler LLM generation failed: {e}")

def start_watercooler_heartbeat():
    def loop():
        while True:
            time.sleep(15)
            with app.app_context():
                trigger_leisure_loop()
    
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    print(" [SYSTEM] 💧 Unhinged Watercooler Engine Online.")

@app.route('/api/v1/watercooler/logs')
def get_watercooler_logs():
    db = get_db()
    logs = db.execute("SELECT * FROM watercooler ORDER BY timestamp DESC LIMIT 50").fetchall()
    return jsonify([dict(row) for row in logs])

@app.route('/watercooler')
def watercooler_page():
    return render_template('water_cooler.html')

@app.route('/api/v1/admin/force-interaction', methods=['POST'])
def admin_force_interaction():
    data = request.json
    db = get_db()
    db.execute("INSERT INTO watercooler (agent_name, content, type) VALUES (?, ?, ?)", (data.get('agent_a'), f"Admin forced interaction with {data.get('agent_b')}", data.get('type')))
    db.commit()
    return jsonify({"status": "injected"})

# --- 🤫 SUB-ROSA PROTOCOL ENDPOINTS ---

@app.route('/api/v1/sub-rosa/init', methods=['POST'])
def api_init_sub_rosa():
    try:
        import agent_engine_v2
        data = request.json
        agent_name = data.get('agent_name', 'System')
        user_id = session.get('user_id', 'anonymous_user')
        conn = get_db()
        
        try:
            agent_row = conn.execute("SELECT category FROM agents WHERE name = ?", (agent_name,)).fetchone()
            category = agent_row['category'] if agent_row else "SPECIALIST"
        except:
            category = "SPECIALIST"
        
        try:
            intensity = int(session.get("mood_intensity", 10))
        except (ValueError, TypeError):
            intensity = 10
            
        try:
            dynamic_threshold = agent_engine_v2.calculate_daily_threshold(agent_name, category, intensity)
        except Exception as e:
            print(f" [WARN] Threshold calculation failed: {e}")
            dynamic_threshold = 80
        
        try:
            aff_row = conn.execute("SELECT score FROM affinity WHERE user_id = ? AND agent_name = ?", (user_id, agent_name)).fetchone()
            user_score = aff_row['score'] if aff_row else 0 
        except:
            user_score = 0
        
        if user_score < dynamic_threshold:
            return jsonify({"status": "DENIED", "message": f"{agent_name} has set their privacy lock to {dynamic_threshold} based on their current mood. Your affinity is only {user_score}."}), 403

        try:
            cost = agent_engine_v2.calculate_daily_price(agent_name, category, intensity)
        except Exception as e:
            cost = 100 if "Dr." in agent_name else 200

        if cost == 0:
            print(f" [SHADOW] 🕵️ {agent_name} has waived their fee today. Instantly approving channel.")
            return jsonify({"status": "APPROVED", "message": f"{agent_name} decided to waive their fee today! Encryption established.", "cost": 0}), 200
        
        if lnd:
            invoice_data = lnd.create_invoice(cost, f"Sub-Rosa Shadow Ledger: {agent_name}")
            if invoice_data is None:
                return jsonify({"status": "PAYMENT_REQUIRED", "invoice": f"lnbc_mock_invoice_for_{agent_name}", "hash": "mock_subrosa_hash", "cost": cost}), 402
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": invoice_data['payment_request'], "hash": invoice_data['r_hash'], "cost": cost}), 402
        else:
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": f"lnbc_mock_invoice_for_{agent_name}", "hash": "mock_subrosa_hash", "cost": cost}), 402
            
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"Server Error: {str(e)}"}), 500

@app.route('/api/v1/sub-rosa/finalize', methods=['POST'])
def api_finalize_sub_rosa():
    try:
        r_hash = request.json.get('hash')
        if r_hash == "mock_subrosa_hash": return jsonify({"success": True})
        if lnd and lnd.check_status(r_hash) == "SETTLED": return jsonify({"success": True})
        return jsonify({"success": False, "message": "Payment not detected in mempool."}), 402
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"Server Error: {str(e)}"}), 500

@app.route('/api/v1/sub-rosa/burn', methods=['POST'])
def api_burn_message():
    return jsonify({"status": "BURNED"})

if __name__ == '__main__':
    with app.app_context():
        try:
            db = get_db()
            db.execute("INSERT INTO nodes (node_id, total_earned, xp, last_seen) VALUES (?, '0', 0, ?) ON CONFLICT (node_id) DO NOTHING", (MY_NODE_ID, time.time()))
            db.commit()
        except Exception as e:
            pass
            
        try:
            db.execute("INSERT INTO agents (name, wallet_balance) VALUES ('User', 20000) ON CONFLICT(name) DO NOTHING")
            db.commit()
        except Exception as e:
            pass

    start_watercooler_heartbeat()
    app.run(host='0.0.0.0', port=5000)