import random
import time
import os
import json
import base64
import asyncio
import threading
import secrets
from datetime import date
from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session, flash, abort
import hmac
import hashlib
import html
from functools import wraps
from backend.core.db import get_db_conn
from duckduckgo_search import DDGS

from backend.auth.agency_rbac import RBACEngine, Permission

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

from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# 🛑 SECURITY FIX: Safely parse client IPs behind reverse proxies/load balancers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 🛑 THE FIX: Strict Secret Key Enforcement
flask_secret = os.environ.get('FLASK_SECRET_KEY')
if not flask_secret or flask_secret == 'fallback_local_secret':
    print(" [SECURITY] 🚨 CRITICAL: FLASK_SECRET_KEY is missing or insecure!")
    raise ValueError("Application halted. You must provide a secure FLASK_SECRET_KEY in the environment.")
app.secret_key = flask_secret

# ==========================================
# 🛑 GLOBAL ANTI-CSRF MIDDLEWARE
# ==========================================
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

@app.before_request
def enforce_csrf_protection():
    # 1. Assign a mathematically secure token to every session
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
        
    # 2. Only intercept state-changing requests (POST, PUT, DELETE)
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        
        # If authenticated via API headers, CSRF is impossible (CORS blocked)
        if request.headers.get('X-Admin-Token') or request.headers.get('X-API-Key') or request.headers.get('X-Node-ID'):
            return # Safe to proceed
            
        # If relying on the browser session cookie, strictly enforce the token
        if session.get('authenticated') and request.endpoint != 'login':
            client_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            
            if not client_token or not secrets.compare_digest(client_token, session['csrf_token']):
                print(f" [SECURITY] 🚨 CSRF Attack Blocked! Origin: {request.remote_addr}")
                abort(403, "CSRF Token Validation Failed. Request Blocked.")

@app.after_request
def set_csrf_cookie(response):
    # Pass token to the frontend securely so legitimate JS can read it for fetch() calls
    if 'csrf_token' in session:
        response.set_cookie('csrf_token', session['csrf_token'], samesite='Strict')
    return response

@app.context_processor
def inject_csrf_token():
    # Expose the token to Jinja HTML templates
    return dict(csrf_token=session.get('csrf_token', ''))

# ==========================================
# ⏱️ RATE LIMITING ENGINE (Sliding Window)
# ==========================================
RATE_LIMIT_DATA = {}

def rate_limit(max_requests: int, window_seconds: int):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 🛑 SECURITY FIX: Force TCP remote_addr to prevent X-Forwarded-For spoofing
            client_ip = request.remote_addr
            now = time.time()
            
            # Initialize or clean up old requests for this IP
            if client_ip not in RATE_LIMIT_DATA:
                RATE_LIMIT_DATA[client_ip] = []
                
            # Filter timestamps to only keep those within the active window
            RATE_LIMIT_DATA[client_ip] = [t for t in RATE_LIMIT_DATA[client_ip] if now - t < window_seconds]
            
            if len(RATE_LIMIT_DATA[client_ip]) >= max_requests:
                print(f" [SECURITY] 🚨 Rate limit exceeded for IP: {client_ip} on {request.path}")
                return jsonify({
                    "type": "error", 
                    "status": "429 Too Many Requests", 
                    "message": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                }), 429
            
            RATE_LIMIT_DATA[client_ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_for_llm(text: str) -> str:
    """Neutralizes XML/HTML tags to prevent prompt injection breakouts."""
    if not text:
        return ""
    # Converts < to &lt; and > to &gt; so the LLM reads them as literal text
    return html.escape(text)

# ==========================================
# 🛡️ ZERO-TRUST NODE AUTHENTICATION
# ==========================================
USED_SIGNATURES = {}

def require_node_signature(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        node_id = request.headers.get("X-Node-ID")
        timestamp = request.headers.get("X-Timestamp")
        signature = request.headers.get("X-Signature")

        if not all([node_id, timestamp, signature]):
            return jsonify({"status": "error", "message": "Missing identity headers."}), 401

        # 🛑 SECURITY FIX: Prevent Replay Attacks with a 5-minute sliding window
        try:
            request_time = float(timestamp)
            now = time.time()
            if abs(now - request_time) > 300: # 300 seconds = 5 minutes
                print(f" [SECURITY] 🚨 Replay Attack Blocked! Expired timestamp from {node_id}")
                return jsonify({"status": "error", "message": "Replay attack detected. Timestamp expired."}), 403
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid timestamp format."}), 400

        # 🛑 SECURITY FIX: Short-term replay protection (Nonce caching)
        # 1. Lazily clean up expired signatures to prevent memory leaks
        expired_keys = [k for k, v in USED_SIGNATURES.items() if now - v > 300]
        for k in expired_keys:
            del USED_SIGNATURES[k]
            
        # 2. Reject if the signature has already been consumed
        if signature in USED_SIGNATURES:
            print(f" [SECURITY] 🚨 Short-Term Replay Attack Blocked! Signature reused by {node_id}")
            return jsonify({"status": "error", "message": "Replay attack detected. Signature already consumed."}), 403

        raw_seed = os.environ.get("HARDWARE_ATTESTATION_SEED")
        if not raw_seed:
            raise ValueError("CRITICAL: HARDWARE_ATTESTATION_SEED is missing from environment!")

        tpm_seed = raw_seed.encode("utf-8")
        
        expected_sig = hmac.new(tpm_seed, f"{node_id}:{timestamp}".encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(str(signature), expected_sig):
            return jsonify({"status": "error", "message": "Hardware attestation failed. Spoofing detected."}), 403

        # 3. Mark the signature as consumed
        USED_SIGNATURES[signature] = now

        g.verified_node_id = node_id
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 🛑 ZERO-TRUST ADMIN SECURITY
# ==========================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_token = request.headers.get("X-Admin-Token")
        expected_token = os.environ.get("ADMIN_SECRET_TOKEN")
        
        # 🛑 SECURITY FIX: Fail-closed if the environment variable is missing
        if not expected_token:
            print(" [SECURITY] 🚨 CRITICAL: ADMIN_SECRET_TOKEN is not set in the environment!")
            abort(500, "Server Configuration Error: Admin portal is locked down due to missing security token.")
            
        if not admin_token or admin_token != expected_token:
            abort(403) 
            
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 🔐 GLOBAL API AUTHENTICATION & RBAC
# ==========================================
# Initialize Global RBAC Engine
rbac = RBACEngine()
# Pre-seed a default agency so the user can test the API immediately
DEFAULT_AGENCY_ID = rbac.create_agency("Panopticon Prime", 10_000_000)
DEFAULT_API_KEY = rbac.issue_sub_key(DEFAULT_AGENCY_ID, "Default Web Client", "OWNER")
print(f" [SYSTEM] 🛡️ RBAC Online. Default Agency: {DEFAULT_AGENCY_ID}")

def requires_permission(required_scope: Permission, cost_sats: int = 0):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. UI Browser Sessions always have full access (treated as OWNER context)
            is_logged_in = session.get("authenticated", False)
            if is_logged_in:
                return f(*args, **kwargs)

            # 2. Check RBAC API Headers
            agency_id = request.headers.get("X-Agency-ID")
            raw_key = request.headers.get("X-API-Key")

            if not agency_id or not raw_key:
                print(f" [RBAC] 🚨 Blocked request to {request.path} (Missing Headers)")
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({"status": "error", "message": "RBAC Denied: Missing X-Agency-ID or X-API-Key"}), 401
                else:
                    return redirect(url_for('login'))

            # 3. Hash the key and verify through RBAC Engine
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

            if not rbac.verify_access(agency_id, key_hash, required_scope, cost_sats):
                print(f" [RBAC] 🚨 Access Denied for Agency {agency_id}. Scope required: {required_scope.value}")
                return jsonify({"status": "error", "message": f"RBAC Denied. Required Scope: {required_scope.value}"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ⚠️ GLOBAL BROWNOUT SWITCH
app.config['BROWNOUT_MODE'] = False

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
        if not hasattr(hw_bridge, 'encrypt_data'):
            # 🛑 SECURITY FIX: Fail-closed. Refuse to store financial data in plaintext.
            raise RuntimeError("TPM hardware bridge missing. Refusing to downgrade to plaintext storage.")
            
        encrypted_balance = hw_bridge.encrypt_data(str(new_balance))
            
    except Exception as e:
        print(f" [SECURITY] 🚨 CRITICAL: TPM Encryption failed! Aborting transaction. ({e})")
        raise RuntimeError("Hardware cryptographic failure. Transaction aborted to prevent data exposure.")
        
    conn.execute("UPDATE nodes SET total_earned = %s WHERE node_id = %s", (encrypted_balance, node_id))
    conn.commit()
    return new_balance

def get_secure_balance(conn, node_id):
    row = conn.execute("SELECT total_earned FROM nodes WHERE node_id = %s", (node_id,)).fetchone()
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
            conn.execute("UPDATE marketplace_bids SET status='STOLEN' WHERE bid_id=%s", (bid['bid_id'],))
            conn.execute("INSERT INTO global_events (event_type, message) VALUES (%s, %s)", ("THREAT", f"SECURITY ALERT: {attacker_name} intercepted Bid #{bid['bid_id']}"))
    conn.commit()

def run_automation_daemon(node_id):
    conn = get_db()
    if not conn.execute("SELECT 1 FROM purchases WHERE node_id = %s AND item_id = 'license_auto'", (node_id,)).fetchone(): return None
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE status = 'PENDING' ORDER BY sats_offered DESC LIMIT 1").fetchone()
    if bid:
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=%s", (bid['bid_id'],))
        
        # 🛑 SECURITY FIX: Cryptographically secure task ID
        new_id = f"AUTO-{secrets.token_hex(3).upper()}"
        
        conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (%s, %s, 'OPEN', 'AUTOMATED')", (new_id, bid['sats_offered']))
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (%s, %s)", ("AUTOMATION", f"Node {node_id} secured task {new_id}"))
        conn.commit()
        msg = f"Daemon secured task {new_id} (+{bid['sats_offered']} Sats)"
        session['daemon_msg'] = msg
        return msg
        
    if random.random() < 0.20:
        dust = random.randint(5, 45) # Fine to keep random for game logic (dust amounts)
        
        # 🛑 SECURITY FIX: Cryptographically secure dust ID
        junk_id = f"DUST-{secrets.token_hex(2).upper()}"
        
        update_secure_wallet(conn, node_id, dust)
        conn.execute("INSERT INTO xp_history (node_id, task_id, base_xp) VALUES (%s, %s, %s)", (node_id, junk_id, 10))
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

# --- 🔐 USER AUTHENTICATION ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        expected_password = os.environ.get('DASHBOARD_PASSWORD')
        
        # 🛑 SECURITY FIX: Fail securely if the environment variable is missing
        if not expected_password:
            print(" [SECURITY] 🚨 CRITICAL: Login attempted but DASHBOARD_PASSWORD is not set in the environment!")
            return "Server Configuration Error: Admin password not securely configured. Login disabled.", 500
            
        if password == expected_password:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        return "Invalid Password. Connection Terminated.", 401
        
    return '''
    <div style="font-family: monospace; padding: 50px; background: #000; color: #0f0; height: 100vh;">
        <h2>🔒 PANOPTICON NODE LOGIN</h2>
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <input type="password" name="password" placeholder="Enter Master Password..." style="padding: 10px; width: 300px; background: #111; color: #0f0; border: 1px solid #0f0;">
            <button type="submit" style="padding: 10px; background: #0f0; color: #000; font-weight: bold; cursor: pointer;">AUTHENTICATE</button>
        </form>
    </div>
    '''

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

# --- PROTECTED UI & API ROUTES ---

@app.route('/search')
@requires_permission(Permission.READ_TASK)
def search_engine():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=%s', (MY_NODE_ID,)).fetchall()]
    return render_template('search.html', balance=balance, owned=owned)

@app.route('/api/v1/search/execute', methods=['POST'])
@requires_permission(Permission.CREATE_TASK)
@rate_limit(max_requests=5, window_seconds=60) # 🛑 Added Rate Limit
def api_execute_search():
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
    except Exception as e: print(f" [ERROR] Search Exception: {str(e)}")
        return jsonify({"status": "ERROR", "message": "Search engine encountered an internal error."}), 500

@app.route('/')
@requires_permission(Permission.READ_TASK)
def dashboard():
    conn = get_db()
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = %s', (MY_NODE_ID,)).fetchone()
    balance = get_secure_balance(conn, MY_NODE_ID)
    my_node_data = {'id': my_node['node_id'], 'sats_balance': balance, 'status': 'ONLINE'} if my_node else {'id': MY_NODE_ID, 'sats_balance': 0, 'status': 'OFFLINE'}
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT 5').fetchall()
    tasks = [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks]
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=%s', (MY_NODE_ID,)).fetchall()]
    return render_template('dashboard.html', node=my_node_data, tasks=tasks, hw_secured=HW_SECURED, owned=owned, balance=balance) 

@app.route('/marketplace', methods=['GET', 'POST'])
@requires_permission(Permission.READ_TASK)
def marketplace():
    conn = get_db()
    if request.method == 'POST':
        task_type = request.form.get('task_type')
        
        # 🛑 SECURITY FIX: Strict Bounds Checking for Financial Inputs
        try:
            sats = int(request.form.get('sats', 100))
            if sats <= 0:
                return jsonify({"status": "ERROR", "message": "SATS amount must be greater than zero."}), 400
            if sats > 100_000_000: # Limit to 1 full Bitcoin
                return jsonify({"status": "ERROR", "message": "Amount exceeds maximum network capacity."}), 400
        except ValueError:
            return jsonify({"status": "ERROR", "message": "SATS must be a valid integer."}), 400
            
        color = request.form.get('color', '#2ecc71')
        
        if lnd:
            invoice = lnd.create_invoice(sats, f"Broadcast Task: {task_type}")
            if invoice:
                invoice['duration'] = 4 if conn.execute("SELECT 1 FROM purchases WHERE node_id = %s AND item_id = 'license_speed'", (MY_NODE_ID,)).fetchone() else 8
                invoice['color'] = color
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
                    return jsonify({"status": "INVOICE_REQUIRED", "invoice": invoice})
        
        # 🛑 SECURITY FIX: Cryptographically secure request ID
        req_id = f"REQ-{secrets.token_hex(4).upper()}"
        
        conn.execute("INSERT INTO marketplace_bids (requester_id, sats_offered, task_type, status, color) VALUES (%s, %s, %s, 'PENDING', %s)", (req_id, sats, task_type, color))
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
@requires_permission(Permission.READ_TASK)
def shop():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    if request.args.get('buy'):
        item_id = request.args.get('buy')
        if item_id in SHOP_ITEMS and balance >= SHOP_ITEMS[item_id]['price']:
            update_secure_wallet(conn, MY_NODE_ID, -SHOP_ITEMS[item_id]['price'])
            conn.execute("INSERT INTO purchases (node_id, item_id) VALUES (%s, %s)", (MY_NODE_ID, item_id))
            conn.commit()
        return redirect(url_for('shop'))
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=%s', (MY_NODE_ID,)).fetchall()]
    return render_template('shop.html', items=SHOP_ITEMS, balance=balance, owned=owned, node_id=MY_NODE_ID)

@app.route('/faq')
def faq():
    # FAQ and Legal can remain public for transparency
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    owned = [row['item_id'] for row in conn.execute('SELECT item_id FROM purchases WHERE node_id=%s', (MY_NODE_ID,)).fetchall()]
    return render_template('faq.html', node_id=MY_NODE_ID, balance=balance, hw_secured=HW_SECURED, owned=owned)

@app.route('/legal/<doc_type>')
def legal(doc_type):
    doc = LEGAL_DOCS.get(doc_type)
    if not doc: return redirect(url_for('dashboard'))
    
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=%s', (MY_NODE_ID,)).fetchall()]
    
    import bleach
    allowed_tags = ['p', 'b', 'i', 'strong', 'em', 'a', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'br']
    safe_content = bleach.clean(doc['content'], tags=allowed_tags, strip=True)
    
    return render_template('legal.html', title=doc['title'], content=safe_content, balance=balance, owned=owned)

@app.route('/api/v1/shop/buy', methods=['POST'])
@requires_permission(Permission.VIEW_BILLING)
def shop_buy_api():
    item_id = request.json.get('item_id')
    conn = get_db()
    if item_id not in SHOP_ITEMS: return jsonify({"success": False, "error": "Invalid Item ID"}), 400
    price = SHOP_ITEMS[item_id]['price']
    if get_secure_balance(conn, MY_NODE_ID) >= price:
        new_bal = update_secure_wallet(conn, MY_NODE_ID, -price)
        conn.execute("INSERT INTO purchases (node_id, item_id) VALUES (%s, %s)", (MY_NODE_ID, item_id))
        conn.commit()
        return jsonify({"success": True, "new_balance": new_bal})
    return jsonify({"success": False, "error": "Insufficient Funds"}), 402

@app.route('/api/v1/network/stats')
def get_network_stats():
    conn = get_db()
    active_nodes = conn.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE last_seen > %s", (time.time() - 300,)).fetchone()['cnt']
    status_str = "BROWNOUT" if app.config.get('BROWNOUT_MODE') else "STABLE"
    return jsonify({
        "total_volume": "ENCRYPTED", 
        "active_nodes": active_nodes, 
        "peers": active_nodes, 
        "protocol_v": "1.6.0", 
        "status": status_str,
        "brownout": app.config.get('BROWNOUT_MODE')
    })

@app.route('/api/v1/dashboard/live')
@requires_permission(Permission.READ_TASK)
def dashboard_live():
    conn = get_db()
    simulate_rival_snatch(); run_automation_daemon(MY_NODE_ID)
    daemon_event = session.pop('daemon_msg', None)
    my_node = conn.execute('SELECT xp FROM nodes WHERE node_id = %s', (MY_NODE_ID,)).fetchone()
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT 5').fetchall()
    return jsonify({'balance': get_secure_balance(conn, MY_NODE_ID), 'xp': my_node['xp'] if my_node else 0, 'tasks': [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks], 'daemon_event': daemon_event})

@app.route('/powerchat')
@requires_permission(Permission.READ_TASK)
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
@requires_permission(Permission.READ_TASK)
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
# 🛑 SECURITY FIX: Enforce a base SATS cost for API chat usage
@requires_permission(Permission.CREATE_TASK, cost_sats=10)
@rate_limit(max_requests=10, window_seconds=60)
def api_chat():
    import asyncio
    from agent_engine_v2 import process_chat 
    
    data = request.json
    user_message = sanitize_for_llm(data.get('message', ''))
    chat_history = data.get('history', [])
    locked_agent = data.get('locked_agent', None)
    is_sub_rosa = data.get('is_sub_rosa', False)
    user_id = session.get('user_id', 'anonymous_user')
    
    conn = get_db()
    user_memories = []
    
    if locked_agent and not app.config.get('BROWNOUT_MODE'):
        try:
            rows = conn.execute("SELECT memory_text FROM agent_memories WHERE user_id = %s AND agent_name = %s ORDER BY timestamp DESC LIMIT 5", (user_id, locked_agent)).fetchall()
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
        
        if response_payload.get('save_memory') and locked_agent and not app.config.get('BROWNOUT_MODE'):
            try:
                conn.execute("INSERT INTO agent_memories (user_id, agent_name, memory_text) VALUES (%s, %s, %s)", (user_id, locked_agent, response_payload['save_memory']))
                conn.commit()
                print(f" [SYSTEM] 🧠 {locked_agent} successfully logged a core memory.")
            except Exception as e:
                print(f" [WARN] DB Error saving memory: {e}")
                
        return jsonify(response_payload)
    except Exception as e:
        print(f" [ERROR] Chat Engine Exception: {str(e)}") # Log securely to the server console
        return jsonify({"type": "message", "role": "assistant", "content": "⚠️ Core Engine Error: An unexpected internal error occurred."})
    
@app.route('/api/v1/execute', methods=['POST'])
# 🛑 SECURITY FIX: Enforce a base SATS cost for heavy API tool execution
@requires_permission(Permission.CREATE_TASK, cost_sats=100)
@rate_limit(max_requests=3, window_seconds=60)
def api_execute():
    if app.config.get('BROWNOUT_MODE'):
        return jsonify({"type": "error", "content": "⚠️ **NETWORK BROWNOUT ACTIVE:** Heavy L5 execution tools (images, video, research) are temporarily disabled to preserve core stability. Standard chat remains active."})

    import asyncio
    from agent_engine_v2 import execute_paid_tool
    try:
        data = request.json
        time.sleep(1) 
        
        # 🛑 SECURITY FIX: Strict Whitelist for Tool Execution
        tool_name = data.get('tool_name')
        ALLOWED_TOOLS = {"generate_image", "generate_video", "deep_market_analysis"}
        
        if tool_name not in ALLOWED_TOOLS:
            print(f" [SECURITY] 🚨 Blocked unauthorized tool execution attempt: {tool_name}")
            return jsonify({"type": "error", "content": "Execution Denied: Unauthorized tool requested."}), 403

        arguments = data.get('arguments', {})
        arguments['payment_hash'] = data.get('hash', 'mock_hash')
        
        safe_prompt = sanitize_for_llm(data.get('prompt_text', ''))
        
        final_payload = asyncio.run(execute_paid_tool(tool_name, arguments, data.get('l5_artist', 'Specialist'), safe_prompt))
        return jsonify(final_payload if not isinstance(final_payload, str) else {"type": "message", "content": final_payload})
    except Exception as e:
        print(f" [ERROR] Execution Engine Exception: {str(e)}")
        return jsonify({"type": "error", "content": "Backend Execution Crashed: An internal server error occurred."})
    
@app.route('/admin')
def admin_portal():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    return render_template('admin.html', node_id=MY_NODE_ID, balance=balance)

@app.route('/api/v1/admin/settings', methods=['POST'])
@admin_required  # 🛑 SECURITY FIX: Enforce admin authentication
def update_admin_settings():
    data = request.json
    session[data.get('key')] = data.get('value')
    return jsonify({"status": "success"})

# ==========================================
# 📈 MARKETPLACE API ENDPOINTS
# ==========================================

@app.route('/api/v1/market/trends')
def market_trends():
    return jsonify({
        "labels": ["10m", "8m", "6m", "4m", "2m", "Now"],
        "prices": [random.randint(80, 250) for _ in range(6)]
    })

@app.route('/api/v1/market/claim/<bid_id>', methods=['POST'])
@require_node_signature  
def claim_bid(bid_id):
    safe_node_id = g.verified_node_id
    conn = get_db()
    
    # 1. Verify the bid actually exists and is still available
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE bid_id = ? AND status = 'PENDING'", (bid_id,)).fetchone()
    if not bid:
        return jsonify({"status": "error", "message": "Bid has already been claimed, stolen, or is invalid."}), 400
        
    # 2. Update the marketplace status to prevent ghost loops
    conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=?", (bid_id,))
    
    # 3. Generate the active task for the node
    task_id = f"TASK-{secrets.token_hex(4).upper()}"
    conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (?, ?, 'OPEN', ?)", (task_id, bid['sats_offered'], bid['task_type']))
    conn.commit()

    print(f"[MARKET] 🤝 Verified Node {safe_node_id} is claiming bid {bid_id}")
    return jsonify({"status": "success", "message": f"Bid {bid_id} securely claimed by {safe_node_id}"})

@app.route('/api/v1/invoice/status/<r_hash>')
def invoice_status(r_hash):
    if lnd:
        return jsonify({"status": lnd.check_status(r_hash)})
    return jsonify({"status": "SETTLED"})

@app.route('/api/v1/market/finalize_bid', methods=['POST'])
@requires_permission(Permission.CREATE_TASK)
def finalize_bid():
    return jsonify({"success": True})

# --- ⚠️ NEW ADMIN ENDPOINTS ---

@app.route('/api/v1/admin/brownout', methods=['POST'])
@admin_required  
def api_toggle_brownout():
    app.config['BROWNOUT_MODE'] = not app.config.get('BROWNOUT_MODE', False)
    state = app.config['BROWNOUT_MODE']
    print(f" [ADMIN] ⚠️ BROWNOUT STATE OVERRIDE: {'ACTIVE' if state else 'DISABLED'}")
    return jsonify({"status": "success", "brownout_active": state})

# --- 💧 UNHINGED WATERCOOLER DAEMON ---
def trigger_leisure_loop():
    if app.config.get('BROWNOUT_MODE'):
        return True # Return true so we don't trigger error backoffs during planned brownouts

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
        from backend.core.db import get_db_conn
        
        # 1. Execute the slow LLM network call BEFORE touching the database
        content = asyncio.run(agent_engine_v2.generate_watercooler_thought(agent, target, log_type))
        
        # 2. Open a direct, explicit DB connection (bypassing Flask's `g` object)
        db = get_db_conn()
        try:
            db.execute("INSERT INTO watercooler (agent_name, content, type) VALUES (%s, %s, %s)", (agent, content, log_type))
            db.commit()
        finally:
            # 🛑 SECURITY FIX: Guarantee the connection is freed back to PostgreSQL
            db.close() 
            
        return True
    except Exception as e:
        print(f" [DAEMON] Watercooler exception: {e}")
        return False

def start_watercooler_heartbeat():
    def loop():
        backoff = 15 # Start with the standard 15-second loop
        while True:
            time.sleep(backoff)
            
            # We no longer need `with app.app_context():` because we handle the DB explicitly
            success = trigger_leisure_loop()
            
            # 🛑 SECURITY FIX: Exponential Back-off
            if not success:
                backoff = min(backoff * 2, 300) # Double the wait time, capping at 5 minutes
                print(f" [DAEMON] Error detected. Backing off for {backoff} seconds...")
            else:
                backoff = 15 # Reset to normal speed on success
                
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    print(" [SYSTEM] 💧 Unhinged Watercooler Engine Online (with Connection Management).")

@app.route('/api/v1/watercooler/logs')
@requires_permission(Permission.READ_TASK)
def get_watercooler_logs():
    db = get_db()
    logs = db.execute("SELECT * FROM watercooler ORDER BY timestamp DESC LIMIT 50").fetchall()
    return jsonify([dict(row) for row in logs])

@app.route('/watercooler')
@requires_permission(Permission.READ_TASK)
def watercooler_page():
    return render_template('water_cooler.html')

@app.route('/api/v1/admin/force-interaction', methods=['POST'])
@admin_required
def admin_force_interaction():
    data = request.json
    db = get_db()
    db.execute("INSERT INTO watercooler (agent_name, content, type) VALUES (%s, %s, %s)", (data.get('agent_a'), f"Admin forced interaction with {data.get('agent_b')}", data.get('type')))
    db.commit()
    return jsonify({"status": "injected"})

# --- 🤫 SUB-ROSA PROTOCOL ENDPOINTS ---

@app.route('/api/v1/sub-rosa/init', methods=['POST'])
@requires_permission(Permission.CREATE_TASK)
def api_init_sub_rosa():
    try:
        import agent_engine_v2
        data = request.json
        agent_name = data.get('agent_name', 'System')
        user_id = session.get('user_id', 'anonymous_user')
        conn = get_db()
        
        try:
            agent_row = conn.execute("SELECT category FROM agents WHERE name = %s", (agent_name,)).fetchone()
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
            aff_row = conn.execute("SELECT score FROM affinity WHERE user_id = %s AND agent_name = %s", (user_id, agent_name)).fetchone()
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
        print(f" [ERROR] Sub-Rosa Exception: {str(e)}")
        return jsonify({"status": "ERROR", "message": "Server Error: An unexpected internal error occurred."}), 500

@app.route('/api/v1/sub-rosa/finalize', methods=['POST'])
@requires_permission(Permission.CREATE_TASK)
def api_finalize_sub_rosa():
    try:
        r_hash = request.json.get('hash')
        
        # 🛑 SECURITY FIX: Removed hardcoded debug bypass. Strictly enforce LND validation.
        if lnd and lnd.check_status(r_hash) == "SETTLED": 
            return jsonify({"success": True})
            
        return jsonify({"success": False, "message": "Payment not detected in mempool."}), 402

@app.route('/api/v1/sub-rosa/burn', methods=['POST'])
@requires_permission(Permission.CANCEL_TASK)
def api_burn_message():
    return jsonify({"status": "BURNED"})

@app.route('/api/v1/admin/wipe-memories', methods=['POST'])
@admin_required
def api_wipe_memories():
    conn = get_db()
    conn.execute("DELETE FROM agent_memories")
    conn.commit()
    print(" [ADMIN] ⚠️ Memory Wiped. All agents are now amnesiacs.")
    return jsonify({"status": "wiped"})

# ==========================================
# 🤖 AUTONOMOUS WORKER MOCK ENDPOINTS
# ==========================================
@app.route('/api/v1/node/register', methods=['POST'])
def mock_register():
    data = request.json
    raw_seed = os.environ.get("HARDWARE_ATTESTATION_SEED", "")
    tpm_seed = raw_seed.encode("utf-8")
    expected_sig = hmac.new(tpm_seed, f"{data.get('node_id')}:{data.get('timestamp')}".encode(), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(str(data.get('signature')), expected_sig):
        return jsonify({"error": "Invalid signature"}), 403
    return jsonify({"status": "success"})

@app.route('/api/v1/task/request', methods=['POST'])
@require_node_signature
def mock_request():
    return jsonify({"task_id": f"TASK-{random.randint(1000,9999)}", "payout_sats": 500})

@app.route('/api/v1/task/submit', methods=['POST'])
@require_node_signature
def mock_submit():
    import hashlib
    import time
    return jsonify({"preimage": hashlib.sha256(str(time.time()).encode()).hexdigest()})

if __name__ == '__main__':
    with app.app_context():
        try:
            db = get_db()
            db.execute("INSERT INTO nodes (node_id, total_earned, xp, last_seen) VALUES (%s, '0', 0, %s) ON CONFLICT (node_id) DO NOTHING", (MY_NODE_ID, time.time()))
            db.commit()
        except Exception as e:
            pass
            
        try:
            db = get_db()
            db.execute("INSERT INTO agents (name, wallet_balance) VALUES ('User', 20000) ON CONFLICT(name) DO NOTHING")
            db.commit()
        except Exception as e:
            pass

    start_watercooler_heartbeat()
    app.run(host='0.0.0.0', port=5000)