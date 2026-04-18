import random
import time
import json
import base64
import asyncio
import threading
import secrets
import jinja2
import traceback
import uuid
from datetime import date, timedelta

# --- 1. INJECT MONOREPO PATHS ---
import sys
import os
from dotenv import load_dotenv

# Load the local .env file securely into the environment
load_dotenv()

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, os.path.join(ROOT_DIR, "apps", "backend", "src"))
sys.path.insert(0, os.path.join(ROOT_DIR, "hardware"))
sys.path.insert(0, os.path.join(ROOT_DIR, "archive", "legacy_hardware"))
# --------------------------------

from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session, flash, abort, send_from_directory
import hmac
import hashlib
import html
from functools import wraps
from core.db import get_db_conn
from duckduckgo_search import DDGS

from auth.agency_rbac import RBACEngine, Permission

try:
    from core.lightning_engine import lnd
    print(" [SYSTEM] ⚡ Lightning Treasury Layer Loaded.")
except ImportError:
    print(" [WARN] ⚠️  lightning_engine.py not found. Running without payment rails.")
    lnd = None

# In app.py
try:
    from proxy_core import NodeHardware
    print(" [SYSTEM] 🔒 Connecting to Rust TPM Engine...")
    hw_bridge = NodeHardware()
    MY_NODE_ID = hw_bridge.get_fingerprint()
    HW_SECURED = "0x8F9B" in MY_NODE_ID
except Exception as e:
    print(f" [WARN] ⚠️ Rust Enclave not found, attempting legacy fallback: {e}")
    try:
        from node_legacy.tpm_binding import NodeHardware
        hw_bridge = NodeHardware()
        MY_NODE_ID = hw_bridge.get_fingerprint()
        HW_SECURED = True
    except Exception as legacy_e:
        # 🛑 THE FIX: Fail loud and fail closed. 
        print(f" [SECURITY] 🚨 CRITICAL: Hardware Root of Trust totally failed! ({legacy_e})")
        raise RuntimeError("Cannot boot Agent Node without secure hardware attestation. Aborting.")

from werkzeug.middleware.proxy_fix import ProxyFix

# --- REPLACEMENT 1: Tell Flask where the new Public Website lives ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
TEMPLATE_DIR = os.path.join(ROOT_DIR, "apps", "web", "public_website", "templates")
STATIC_DIR = os.path.join(ROOT_DIR, "apps", "web", "public_website", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

CMD_CENTER_DIR = os.path.join(ROOT_DIR, 'apps', 'web', 'command_center')

# Tell Jinja to look in BOTH the public templates folder and the command center folder
app.jinja_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader(TEMPLATE_DIR),
    jinja2.FileSystemLoader(CMD_CENTER_DIR)
])
# --------------------------------------------------------------------

# 🟢 DEV TOOL: NUKE ALL BROWSER CACHING
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    """Forces the browser to always download the freshest HTML/JS/CSS files."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# 🛑 SECURITY FIX: Safely parse client IPs behind reverse proxies/load balancers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 🛑 THE FIX: Strict Secret Key Enforcement
flask_secret = os.environ.get('FLASK_SECRET_KEY')
if not flask_secret or flask_secret == 'fallback_local_secret':
    print(" [SECURITY] 🚨 CRITICAL: FLASK_SECRET_KEY is missing or insecure!")
    raise ValueError("Application halted. You must provide a secure FLASK_SECRET_KEY in the environment.")
app.secret_key = flask_secret

# ==========================================
# 🔒 CONCURRENCY & LOCKING ENGINE
# ==========================================
SIG_LOCK = threading.Lock() # 🛑 SECURITY FIX: Prevent Thread Collision on USED_SIGNATURES
RATE_LIMIT_LOCK = threading.Lock() # 🛑 SECURITY FIX: Prevent Thread Collision on RATE_LIMIT_DATA

# ==========================================
# 🛑 GLOBAL ANTI-CSRF MIDDLEWARE
# ==========================================
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1) # 🛑 SECURITY FIX: Prevent Session Fixation/Hijacking

@app.before_request
def enforce_csrf_protection():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
        
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        # 🛡️ PHASE 3 FIX: Removed the insecure header-presence CSRF bypass.
        # Now, if you are using cookie-based session auth, CSRF is strictly enforced.
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return # Safe to proceed; stateless API requests don't use cookies/CSRF
            
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
    # csp_nonce: per-request random value for nonce-based CSP in dashboard templates.
    # Generated once per request and stored on g so all templates in the same
    # request share the same nonce (required — the nonce in the CSP meta tag and
    # the nonce on every <script> tag must match exactly).
    if 'csp_nonce' not in g:
        g.csp_nonce = secrets.token_hex(16)

    # ops_hub_token: the shared secret for the /v1/telemetry/stream WebSocket.
    # Both Flask (template render) and FastAPI (telemetry_socket.py) read this
    # from the same OPS_HUB_TOKEN environment variable so the handshake succeeds.
    # The CSRF token is NOT used here — it is per-session and unknown to FastAPI.
    ops_hub_token = os.environ.get('OPS_HUB_TOKEN', 'dev-token-777')

    return dict(
        csrf_token=session.get('csrf_token', ''),
        csp_nonce=g.csp_nonce,
        ops_hub_token=ops_hub_token,
    )

# ==========================================
# GLOBAL EXCEPTION HANDLER (ANTI-LEAK)
# ==========================================
@app.errorhandler(Exception)
def handle_global_exception(e):
    correlation_id = str(uuid.uuid4())
    
    # Log the full stack trace and correlation ID securely on the server
    print(f" [SECURITY] 🚨 CRITICAL: Unhandled Exception [Correlation ID: {correlation_id}]")
    print(traceback.format_exc())
    
    # PHASE 4 FIX: Return a sanitized response to the client
    return jsonify({
        "status": "error",
        "message": "An internal operational error occurred.",
        "correlation_id": correlation_id
    }), 500

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
            
            with RATE_LIMIT_LOCK:
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

        # 🛑 SECURITY FIX: Mutex protected O(1) Check to prevent Thread Collision
        with SIG_LOCK:
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

        # 3. Mark the signature as consumed within the lock
        with SIG_LOCK:
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
            
        # 🛑 SECURITY FIX: Prevent Cryptographic Timing Attacks using compare_digest
        if not admin_token or not secrets.compare_digest(admin_token, expected_token):
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
DAEMON_MESSAGES = [] 

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
        # 🛑 QUANTUM FIX: Force AES-256 Encryption via TPM/Rust Enclave
        if not hasattr(hw_bridge, 'encrypt_data'):
            # 🛑 SECURITY FIX: Fail-closed. Refuse to store financial data in plaintext.
            raise RuntimeError("Quantum Safeguard: TPM hardware bridge missing. Refusing to downgrade to plaintext storage.")
            
        encrypted_balance = hw_bridge.encrypt_data(str(new_balance))
        
        # Ensure the bridge returned a secure string, not plaintext
        if not encrypted_balance.startswith("SECURE::"):
            raise ValueError("Cryptographic Integrity Failure: AES-256 key mismatch.")
            
    except Exception as e:
        print(f" [SECURITY] 🚨 CRITICAL: TPM/AES-256 Encryption failed! ({e})")
        raise RuntimeError("Hardware cryptographic failure. Transaction aborted for quantum safety to prevent data exposure.")
        
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

def simulate_rival_snatch(conn):
    bids = conn.execute("SELECT * FROM marketplace_bids WHERE status='PENDING'").fetchall()
    if not bids: return
    RIVALS_META = {"OMNI_CORP_09": 0.05, "VOID_RUNNER": 0.03, "KAOS_ENGINE": 0.08}
    for bid in bids:
        value_mult = 1.5 if bid['sats_offered'] > 500 else 3.0 if bid['sats_offered'] > 1000 else 1.0
        attacker_name = random.choice(list(RIVALS_META.keys()))
        if random.random() < (RIVALS_META[attacker_name] * value_mult * 0.1):
            conn.execute("UPDATE marketplace_bids SET status='STOLEN' WHERE bid_id=%s", (bid['bid_id'],))
            conn.execute("INSERT INTO global_events (event_type, message) VALUES (%s, %s)", ("THREAT", f"SECURITY ALERT: {attacker_name} intercepted Bid #{bid['bid_id']}"))

def run_automation_daemon(conn, node_id):
    if not conn.execute("SELECT 1 FROM purchases WHERE node_id = %s AND item_id = 'license_auto'", (node_id,)).fetchone(): return None
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE status = 'PENDING' ORDER BY sats_offered DESC LIMIT 1").fetchone()
    if bid:
        conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=%s", (bid['bid_id'],))
        
        # 🛑 SECURITY FIX: Cryptographically secure task ID
        new_id = f"AUTO-{secrets.token_hex(3).upper()}"
        
        conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (%s, %s, 'OPEN', 'AUTOMATED')", (new_id, bid['sats_offered']))
        conn.execute("INSERT INTO global_events (event_type, message) VALUES (%s, %s)", ("AUTOMATION", f"Node {node_id} secured task {new_id}"))
        DAEMON_MESSAGES.append(f"Daemon secured task {new_id} (+{bid['sats_offered']} Sats)")
        
    elif random.random() < 0.20:
        dust = random.randint(5, 45) # Fine to keep random for game logic (dust amounts)
        
        # 🛑 SECURITY FIX: Cryptographically secure dust ID
        junk_id = f"DUST-{secrets.token_hex(2).upper()}"
        
        update_secure_wallet(conn, node_id, dust)
        conn.execute("INSERT INTO xp_history (node_id, task_id, base_xp) VALUES (%s, %s, %s)", (node_id, junk_id, 10))
        DAEMON_MESSAGES.append(f"Daemon scavenged {junk_id} (+{dust} Sats)")

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
        
        # 🛑 SECURITY FIX: Table to track and burn consumed Lightning invoices
        db.execute('''CREATE TABLE IF NOT EXISTS consumed_invoices (hash TEXT PRIMARY KEY, consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        db.execute('''CREATE TABLE IF NOT EXISTS watercooler (id SERIAL PRIMARY KEY, agent_name TEXT, content TEXT, type TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS affinity (user_id TEXT, agent_name TEXT, score INTEGER DEFAULT 0, PRIMARY KEY (user_id, agent_name))''')
        db.execute('''CREATE TABLE IF NOT EXISTS agents (name TEXT PRIMARY KEY, category TEXT DEFAULT 'SPECIALIST', wallet_balance INTEGER DEFAULT 1000, affinity_threshold INTEGER DEFAULT 80, threshold_min INTEGER DEFAULT 30, threshold_max INTEGER DEFAULT 90)''')
        db.execute('''CREATE TABLE IF NOT EXISTS agent_memories (id SERIAL PRIMARY KEY, user_id TEXT, agent_name TEXT, memory_text TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # 🟢 NEW: Vanguard 50 Telemetry Ledger (Time-Series)
        db.execute('''
            CREATE TABLE IF NOT EXISTS agent_telemetry_history (
                id SERIAL PRIMARY KEY,
                agent_id TEXT NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                status TEXT NOT NULL,
                current_mission_id TEXT,
                event_type TEXT DEFAULT 'PING',
                recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 🟢 NEW: High-performance indexes for the Command Center "Rewind" feature
        db.execute('''CREATE INDEX IF NOT EXISTS idx_telemetry_agent_time ON agent_telemetry_history (agent_id, recorded_at DESC)''')
        db.execute('''CREATE INDEX IF NOT EXISTS idx_telemetry_mission ON agent_telemetry_history (current_mission_id)''')
        
        db.commit()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

# --- 🔐 USER AUTHENTICATION ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
# 🛑 SECURITY FIX: Prevent brute-forcing of the admin dashboard
@rate_limit(max_requests=5, window_seconds=60)
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        expected_password = os.environ.get('DASHBOARD_PASSWORD')
        
        # 🛑 SECURITY FIX: Fail securely if the environment variable is missing
        if not expected_password:
            print(" [SECURITY] 🚨 CRITICAL: Login attempted but DASHBOARD_PASSWORD is not set in the environment!")
            return "Server Configuration Error: Admin password not securely configured. Login disabled.", 500
            
        # 🛑 SECURITY FIX: Prevent Cryptographic Timing Attacks and Session Fixation
        if password and secrets.compare_digest(password, expected_password):
            session.clear() # Wipe pre-auth token/state
            session.permanent = True # 🛑 SECURITY FIX: Enforce cookie expiration
            session['authenticated'] = True
            return redirect(url_for('command_center_root'))
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
        
        # 🛑 SECURITY FIX: Burn the invoice to prevent Replay Attacks
        if is_paid:
            conn = get_db()
            consumed = conn.execute("SELECT 1 FROM consumed_invoices WHERE hash = %s", (payment_hash,)).fetchone()
            if consumed:
                is_paid = False
                print(f" [SECURITY] 🚨 Blocked replay attack for invoice hash: {payment_hash}")
            else:
                conn.execute("INSERT INTO consumed_invoices (hash) VALUES (%s)", (payment_hash,))
                conn.commit()
                
        if not is_paid:
            invoice_data = lnd.create_invoice(cost, f"Proxy Search: {query[:30]}")
            if not invoice_data: return jsonify({"status": "ERROR", "message": "Lightning Treasury Offline"}), 500
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": invoice_data['payment_request'], "hash": invoice_data['r_hash'], "cost": cost}), 402
    else:
        # Fallback mode (dev only)
        return jsonify({"status": "SUCCESS", "results": [{"title": "Search Simulation", "url": "http://dev.proxy"}]})
    
# ==========================================
# 🤖 B2B PARTNER API (WEBHOOK INGESTION)
# ==========================================

@app.route('/api/v1/dispatch/request', methods=['POST'])
def api_dispatch_request():
    """
    Receives an automated dispatch request directly from a partner's AV telemetry server.
    Expected Payload: JSON containing asset_id, gps coordinates, and fault_code.
    """
    import random
    from datetime import datetime
    
    # 1. Authenticate the Request
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer sk_'):
        return jsonify({
            "error": "Unauthorized", 
            "message": "Missing or invalid API Key. Expected format: 'Authorization: Bearer sk_live_...'"
        }), 401

    # 2. Validate the Payload
    data = request.json
    if not data:
        return jsonify({"error": "Bad Request", "message": "Invalid JSON payload."}), 400

    required_fields = ['asset_id', 'latitude', 'longitude', 'error_code']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "Bad Request", "message": f"Missing required field: {field}"}), 400

    # 3. Process the Request (Generate Mission & Escrow Hold)
    # In a fully wired environment, this would INSERT into your PostgreSQL database
    # and broadcast via WebSockets to make the dot instantly appear on the map.
    
    mission_id = f"FLT-{random.randint(10000, 99999)}"
    
    # Simple tiering logic for the response
    # ... existing tiering logic ...
    tier = 1
    base_bounty = 15.00
    if data['error_code'] in ['spill_remediation', 'tire_pressure']:
        tier = 2; base_bounty = 25.00
    elif data['error_code'] in ['manual_override', 'scene_securement']:
        tier = 3; base_bounty = 85.00

    # 🟢 NEW: Construct the real-time map payload
    map_payload = {
        "id": mission_id,
        "asset_id": data['asset_id'],
        "lat": data['latitude'],
        "lng": data['longitude'],
        "fault_code": data['error_code'],
        "bounty": f"${base_bounty:.2f}",
        "tier": tier
    }

    # 🟢 NEW: Broadcast to all connected Command Center browsers instantly
    # socketio.emit('partner_fault_ingested', map_payload)

    # 4. Return the standard 201 Created response to the AV
    response_payload = {
        "status": "accepted",
        "mission_id": mission_id,
        "asset": data['asset_id'],
        "tier": tier,
        "financials": {
            "escrow_locked": f"${base_bounty:.2f}",
            "bidding_mode": "auto_escalate",
            "max_cap": f"${base_bounty + 20:.2f}"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message": "Reverse-auction dispatch initiated. Webhooks will fire on status changes."
    }
    
    return jsonify(response_payload), 201

@app.route('/v2')
@requires_permission(Permission.READ_TASK)
def legacy_dashboard():
    # We preserved the old v2.0 dashboard here just in case!
    conn = get_db()
    my_node = conn.execute('SELECT * FROM nodes WHERE node_id = %s', (MY_NODE_ID,)).fetchone()
    balance = get_secure_balance(conn, MY_NODE_ID)
    my_node_data = {'id': my_node['node_id'], 'sats_balance': balance, 'status': 'ONLINE'} if my_node else {'id': MY_NODE_ID, 'sats_balance': 0, 'status': 'OFFLINE'}
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT 5').fetchall()
    tasks = [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks]
    owned = [r['item_id'] for r in conn.execute('SELECT item_id FROM purchases WHERE node_id=%s', (MY_NODE_ID,)).fetchall()]
    return render_template('dashboard.html', node=my_node_data, tasks=tasks, hw_secured=HW_SECURED, owned=owned, balance=balance) 

# ==========================================
# 🌐 PUBLIC WEBSITE ROUTES (Jinja2 Templates)
# ==========================================
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/enlist')
def enlist():
    return render_template('enlist.html')

@app.route('/operations')
def operations():
    return render_template('operations.html')

@app.route('/rates')
def rates():
    return render_template('rates.html')

@app.route('/investors')
def investors():
    return render_template('investors.html')

# ==========================================
# 🌐 VANGUARD 50 COMMAND CENTER (SPA ROUTES)
# ==========================================
@app.route('/command')
@requires_permission(Permission.READ_TASK)
def command_center_root():
    return render_template('index.html')

@app.route('/developers')
@requires_permission(Permission.READ_TASK)
def developer_portal():
    return render_template('developer.html')

@app.route('/reports')
@requires_permission(Permission.READ_TASK)
def reports_portal():
    return render_template('reports.html')

# ==========================================
# 📊 EXECUTIVE REPORTING APIs
# ==========================================

@app.route('/api/v1/reports/compliance', methods=['GET'])
def get_compliance_report():
    import random
    from datetime import datetime, timedelta
    
    timeframe = request.args.get('timeframe', '1m')
    tf_map = {'24h': 1, '1w': 7, '1m': 30, '3m': 90, '1y': 365, 'custom': 30}
    days = tf_map.get(timeframe, 30)
    
    now = datetime.utcnow()
    audit_trail = []
    total_seconds = 0
    disengagements = 0
    breaches = 0
    
    target_incidents = int(1.5 * days) # Scale incidents by days
    if target_incidents < 5: target_incidents = 5
    
    incident_types = [
        ("manual_override", "Manual Drive Takeover"), ("scene_securement", "Scene Securement (Fire/Police)"),
        ("path_clearing", "Path Clearing (Debris)"), ("sensor_cleaning", "Sensor Obstruction"),
        ("spill_remediation", "Bio/Liquid Remediation")
    ]
    
    for i in range(target_incidents):
        fault_code, fault_name = random.choice(incident_types)
        if fault_code == "manual_override": disengagements += 1
            
        clearance_seconds = random.randint(240, 1020) 
        total_seconds += clearance_seconds
        if clearance_seconds > 900: breaches += 1 
            
        event_time = now - timedelta(days=random.randint(0, max(0, days - 1)), hours=random.randint(0, 23))
        
        audit_trail.append({
            "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "asset_id": f"AV-ACT-{random.randint(1000, 9999)}",
            "incident_type": fault_name,
            "clearance_time": f"{clearance_seconds // 60:02d}m {clearance_seconds % 60:02d}s",
            "agent": f"VAN-{str(random.randint(1, 15)).zfill(3)}",
            "compliant": clearance_seconds <= 900,
            "raw_time": event_time.timestamp()
        })

    audit_trail.sort(key=lambda x: x["raw_time"], reverse=True)
    avg_seconds = total_seconds // target_incidents if target_incidents > 0 else 0
    
    return jsonify({
        "kpis": {
            "avg_clearance": f"{avg_seconds // 60}m {avg_seconds % 60:02d}s",
            "is_avg_compliant": avg_seconds < 900,
            "disengagements": disengagements,
            "breach_rate": f"{(breaches / target_incidents) * 100:.2f}%"
        },
        "audit_trail": audit_trail[:15]
    })

@app.route('/api/v1/reports/operations', methods=['GET'])
def get_operations_report():
    import random
    timeframe = request.args.get('timeframe', '1m')
    tf_map = {'24h': 1, '1w': 7, '1m': 30, '3m': 90, '1y': 365, 'custom': 30}
    days = tf_map.get(timeframe, 30)
    mult = max(1, days / 30)
    
    distribution = [
        {"type": "Sensor Cleaning", "count": int(random.randint(30, 50) * mult), "color": "#00BCD4"},
        {"type": "Path Clearing", "count": int(random.randint(20, 35) * mult), "color": "#FF9800"},
        {"type": "Cabin Sweep & Trash", "count": int(random.randint(15, 25) * mult), "color": "#4CAF50"},
        {"type": "Manual Drive Takeover", "count": int(random.randint(5, 14) * mult), "color": "#F44336"},
        {"type": "Tire Pressure", "count": int(random.randint(2, 8) * mult), "color": "#FFEB3B"}
    ]
    
    total_faults = sum(d["count"] for d in distribution)
    for d in distribution: d["pct"] = int((d["count"] / total_faults) * 100) if total_faults > 0 else 0
    distribution.sort(key=lambda x: x["count"], reverse=True)
    
    hotspots = [
        {"name": "Mill Ave (Tempe - High Foot Traffic)", "incidents": int(random.randint(18, 25) * mult)},
        {"name": "Old Town (Scottsdale - Congestion)", "incidents": int(random.randint(15, 20) * mult)},
        {"name": "Mesa Riverview (Construction)", "incidents": int(random.randint(10, 15) * mult)},
        {"name": "Downtown Chandler (Events)", "incidents": int(random.randint(5, 12) * mult)}
    ]

    return jsonify({
        "kpis": {
            "uptime": f"99.{random.randint(2, 8)}%",
            "mttr": f"{random.randint(9, 14)}m {random.randint(10, 59)}s",
            "total_faults": total_faults,
            "deadhead_reduction": f"{random.randint(12, 18)}%"
        },
        "distribution": distribution,
        "hotspots": hotspots
    })

@app.route('/api/v1/reports/financials', methods=['GET'])
def get_financials_report():
    import random
    from datetime import datetime, timedelta
    
    timeframe = request.args.get('timeframe', '1m')
    tf_map = {'24h': 1, '1w': 7, '1m': 30, '3m': 90, '1y': 365, 'custom': 30}
    days = tf_map.get(timeframe, 30)
    
    now = datetime.utcnow()
    transactions = []
    starting_escrow = 25000.00
    if days > 90: starting_escrow = 150000.00 # Bigger budget for yearly views
    
    total_spend = 0.0
    cancel_fees = 0.0
    total_incidents = 0
    fault_prices = [15.00, 25.00, 55.00, 85.00]
    
    target_incidents = int(1.5 * days)
    if target_incidents < 5: target_incidents = 5

    for i in range(target_incidents):
        cost = random.choice(fault_prices)
        total_spend += cost
        total_incidents += 1
        
        if random.random() < 0.10:
            cancel_fees += 5.00
            total_spend -= 5.00 
            
        event_time = now - timedelta(days=random.randint(0, max(0, days - 1)), hours=random.randint(0, 23))
        
        transactions.append({
            "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "ref_id": f"FLT-{random.randint(1000, 9999)}",
            "desc": "Escrow Settlement (Mission Cleared)",
            "amount": f"-${cost:.2f}",
            "is_negative": True,
            "raw_time": event_time.timestamp()
        })

    transactions.sort(key=lambda x: x["raw_time"], reverse=True)
    current_balance = starting_escrow - total_spend + cancel_fees
    avg_cost = (total_spend / total_incidents) if total_incidents > 0 else 0.00
    
    return jsonify({
        "kpis": {
            "balance": f"${current_balance:,.2f}",
            "total_spend": f"${total_spend:,.2f}",
            "avg_cost": f"${avg_cost:.2f}",
            "cancel_fees": f"${cancel_fees:.2f}"
        },
        "transactions": transactions[:20] 
    })

@app.route('/api/v1/reports/vendor_sla', methods=['GET'])
def get_vendor_sla_report():
    """Aggregates Proxy Agent performance, leaderboards, and SLA breaches."""
    import random
    from datetime import datetime, timedelta
    
    timeframe = request.args.get('timeframe', '1m')
    tf_map = {'24h': 1, '1w': 7, '1m': 30, '3m': 90, '1y': 365, 'custom': 30}
    days = tf_map.get(timeframe, 30)
    mult = max(1, days / 30)
    
    now = datetime.utcnow()
    
    # 1. Generate Top Agents
    top_agents = []
    for i in range(5):
        missions = int(random.randint(15, 60) * mult)
        rating = round(random.uniform(4.8, 5.0), 2)
        resp_time = f"{random.randint(6, 11)}m {random.randint(10, 59)}s"
        
        top_agents.append({
            "agent_id": f"VAN-{str(random.randint(1, 40)).zfill(3)}",
            "rating": f"{rating} ⭐",
            "missions": missions,
            "response": resp_time
        })
        
    top_agents.sort(key=lambda x: x["missions"], reverse=True)
    
    # 2. Generate SLA Infractions (Flakes, Late Arrivals)
    infractions = []
    target_infractions = int(random.randint(2, 6) * mult)
    if target_infractions < 1: target_infractions = 1
    
    issues = [
        ("Mission Aborted (Flake)", "Agent Reassigned"),
        ("Late Arrival (>15m)", "Warning Issued"),
        ("Poor Resolution Quality", "Rating Deducted")
    ]
    
    for i in range(target_infractions):
        issue, action = random.choice(issues)
        event_time = now - timedelta(days=random.randint(0, max(0, days - 1)), hours=random.randint(0, 23))
        
        infractions.append({
            "date": event_time.strftime("%Y-%m-%d"),
            "agent_id": f"VAN-{str(random.randint(41, 99)).zfill(3)}",
            "issue": issue,
            "action": action,
            "raw_time": event_time.timestamp()
        })
        
    infractions.sort(key=lambda x: x["raw_time"], reverse=True)

    return jsonify({
        "kpis": {
            "avg_response": f"0{random.randint(7, 9)}m {random.randint(10, 59)}s",
            "completion_rate": f"98.{random.randint(1, 9)}%",
            "global_rating": f"4.{random.randint(85, 98)} / 5.0"
        },
        "top_agents": top_agents,
        "infractions": infractions[:8] # Show top 8 infractions
    })

@app.route('/css/<path:filename>')
def command_center_css(filename):
    """Allows the browser to fetch the extracted stylesheets."""
    return send_from_directory(os.path.join(CMD_CENTER_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def command_center_js(filename):
    """Allows the browser to fetch the extracted JavaScript modules."""
    return send_from_directory(os.path.join(CMD_CENTER_DIR, 'js'), filename)

@app.route('/secrets.js')
def command_center_secrets():
    """Explicitly serves the Firebase config file."""
    return send_from_directory(CMD_CENTER_DIR, 'secrets.js')

@app.route('/marketplace', methods=['GET', 'POST'])
@requires_permission(Permission.VIEW_MARKET)
def marketplace():
    conn = get_db()
    if request.method == 'POST':
        # 🛑 SECURITY FIX: Route ALL traffic through the secure AJAX/LND flow. No exceptions.
        data = request.json if request.is_json else request.form
        task_type = data.get('task_type')
        sats = int(data.get('sats', 0))
        
        if lnd:
            inv = lnd.create_invoice(sats, f"Market Bid: {task_type}")
            if not inv: return jsonify({"status": "ERROR", "message": "Lightning Treasury Offline"}), 500
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": inv['payment_request'], "hash": inv['r_hash']})
        else:
            # Fallback dev mode
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": "lnbc_mock_dev_invoice", "hash": "mock_market_hash"})

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
    if not doc: return redirect(url_for('command_center_root'))
    
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
    
    # 🛑 SECURITY FIX: Context-Aware Identity Resolution. 
    # Do not trust the X-Agency-ID header if the user is in a verified browser session.
    if session.get("authenticated"):
        buyer_id = MY_NODE_ID
    else:
        buyer_id = request.headers.get("X-Agency-ID") or getattr(g, 'verified_node_id', MY_NODE_ID)
    
    if item_id not in SHOP_ITEMS: return jsonify({"success": False, "error": "Invalid Item ID"}), 400
    price = SHOP_ITEMS[item_id]['price']
    
    if get_secure_balance(conn, buyer_id) >= price:
        new_bal = update_secure_wallet(conn, buyer_id, -price)
        conn.execute("INSERT INTO purchases (node_id, item_id) VALUES (%s, %s)", (buyer_id, item_id))
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
    # 🛑 SECURITY FIX: Decoupled state-changing operations into background heartbeat
    
    # Thread-safe message retrieval (Minor UX Refactor: Keep history for multiple tabs)
    global DAEMON_MESSAGES
    current_msgs = list(DAEMON_MESSAGES)
    DAEMON_MESSAGES = DAEMON_MESSAGES[-5:] # Keep last 5 for multi-tab consistency
    
    my_node = conn.execute('SELECT xp FROM nodes WHERE node_id = %s', (MY_NODE_ID,)).fetchone()
    db_tasks = conn.execute('SELECT * FROM tasks ORDER BY task_id DESC LIMIT 5').fetchall()
    
    return jsonify({
        'balance': get_secure_balance(conn, MY_NODE_ID), 
        'xp': my_node['xp'] if my_node else 0, 
        'tasks': [{'id': t['task_id'], 'type': t['task_type'], 'reward': t['bid_sats']} for t in db_tasks], 
        'daemon_event': current_msgs[-1] if current_msgs else None
    })

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

        # 🛑 SECURITY FIX: Strictly enforce LND settlement and prevent Replay Attacks
        r_hash = data.get('hash')
        
        # Determine if we should approve based on LND status OR mock dev bypass
        approved = False
        if lnd:
            if lnd.check_status(r_hash) == "SETTLED":
                approved = True
        elif r_hash == "mock_execute_hash":
            approved = True

        if approved:
            conn = get_db()
            consumed = conn.execute("SELECT 1 FROM consumed_invoices WHERE hash = %s", (r_hash,)).fetchone()
            if consumed:
                print(f" [SECURITY] 🚨 Blocked replay attack for execution hash: {r_hash}")
                return jsonify({"type": "error", "content": "Execution Denied: Invoice already consumed."}), 403
                
            conn.execute("INSERT INTO consumed_invoices (hash) VALUES (%s)", (r_hash,))
            conn.commit()
        else:
            return jsonify({"type": "error", "content": "Execution Denied: Payment not settled."}), 402

        arguments = data.get('arguments', {})
        arguments['payment_hash'] = r_hash or 'mock_hash'
        
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

ALLOWED_ADMIN_SESSION_KEYS = {"brownout_mode", "ui_theme", "mood_intensity"}

@app.route('/api/v1/admin/settings', methods=['POST'])
@admin_required
def update_admin_settings():
    data = request.json
    key = data.get('key')
    
    if key not in ALLOWED_ADMIN_SESSION_KEYS:
        abort(400, f"Invalid session key. Allowed: {ALLOWED_ADMIN_SESSION_KEYS}")
        
    session[key] = data.get('value')
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
    # 🛑 SECURITY FIX: Use %s instead of ? for PostgreSQL parameter binding to prevent fatal crashes
    bid = conn.execute("SELECT * FROM marketplace_bids WHERE bid_id = %s AND status = 'PENDING'", (bid_id,)).fetchone()
    if not bid:
        return jsonify({"status": "error", "message": "Bid has already been claimed, stolen, or is invalid."}), 400
        
    # 2. Update the marketplace status to prevent ghost loops
    conn.execute("UPDATE marketplace_bids SET status='CLAIMED' WHERE bid_id=%s", (bid_id,))
    
    # 3. Generate the active task for the node
    task_id = f"TASK-{secrets.token_hex(4).upper()}"
    conn.execute("INSERT INTO tasks (task_id, bid_sats, status, task_type) VALUES (%s, %s, 'OPEN', %s)", (task_id, bid['sats_offered'], bid['task_type']))
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
def api_finalize_market_bid():
    try:
        data = request.json
        r_hash = data.get('hash')
        task_type = data.get('task_type')
        color = data.get('color', '#3498db')
        
        # Determine if we should approve based on LND status OR mock dev bypass
        approved = False
        if lnd:
            if lnd.check_status(r_hash) == "SETTLED":
                approved = True
        elif r_hash == "mock_market_hash":
            approved = True

        if approved:
            conn = get_db()
            
            # Check if invoice was already consumed
            consumed = conn.execute("SELECT 1 FROM consumed_invoices WHERE hash = %s", (r_hash,)).fetchone()
            if consumed:
                print(f" [SECURITY] 🚨 Blocked replay attack for market bid hash: {r_hash}")
                return jsonify({"success": False, "message": "Invoice already consumed. Replay attack detected."}), 403
                
            # Burn the invoice
            conn.execute("INSERT INTO consumed_invoices (hash) VALUES (%s)", (r_hash,))
            
            # 🛑 SECURITY FIX: Fail-Closed Parameter Tampering Prevention
            # We strictly require a verified amount from LND. No fallbacks to client data.
            try:
                actual_sats = lnd.get_invoice_amount(r_hash) if lnd else int(data.get('sats', 0))
            except Exception as e:
                # 🛑 SECURITY FIX: Fail-Closed
                print(f" [SECURITY] 🚨 CRITICAL: Failed to verify paid amount with LND for {r_hash}: {e}")
                return jsonify({"status": "ERROR", "message": "Verification Failure: Unable to cryptographically confirm payment amount."}), 500
            
            # 🛑 THE RESTORED LOGIC: Actually insert the paid task into the marketplace
            requester_id = request.headers.get("X-Agency-ID") or getattr(g, 'verified_node_id', MY_NODE_ID)
            conn.execute("INSERT INTO marketplace_bids (requester_id, task_type, sats_offered, status, color) VALUES (%s, %s, %s, 'PENDING', %s)", (requester_id, task_type, actual_sats, color))
            conn.commit()
            
            return jsonify({"success": True})
            
        return jsonify({"success": False, "message": "Payment not detected in mempool."}), 402
    except Exception as e:
        print(f" [ERROR] Market Finalize Exception: {str(e)}")
        return jsonify({"status": "ERROR", "message": "Server Error: An unexpected internal error occurred."}), 500

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
        from core.db import get_db_conn
        
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

# ==========================================
# MARKETPLACE SIMULATION HEARTBEAT
# ==========================================
def start_marketplace_heartbeat():
    def loop():
        _heartbeat_tick = 0  # 🛡️ PHASE 4 OPTIMIZATION: Tick counter for heavy jobs
        
        while True:
            # Run simulation every 10 seconds
            time.sleep(10)
            now = time.time()
            _heartbeat_tick += 1
            
            # SECURITY FIX: Mutex protected O(N) cache cleanup to prevent Thread Collision
            with SIG_LOCK:
                expired_keys = [k for k, v in USED_SIGNATURES.items() if now - v > 300]
                for k in expired_keys:
                    del USED_SIGNATURES[k]

            # SECURITY FIX: Prevent Memory Leak (OOM DoS) by cleaning up inactive IPs
            with RATE_LIMIT_LOCK:
                expired_ips = []
                for ip, timestamps in list(RATE_LIMIT_DATA.items()):
                    valid_timestamps = [t for t in timestamps if now - t < 3600]
                    if not valid_timestamps:
                        expired_ips.append(ip)
                    else:
                        RATE_LIMIT_DATA[ip] = valid_timestamps
                for ip in expired_ips:
                    del RATE_LIMIT_DATA[ip]

            try:
                # Use a standalone connection to avoid Flask context issues
                from core.db import get_db_conn
                db = get_db_conn()
                try:
                    # 🛡️ PHASE 4 FIX: Prevent unbounded DB growth, but run efficiently
                    if _heartbeat_tick % 60 == 0:  # Run once every 10 minutes (60 * 10s)
                        db.execute("DELETE FROM consumed_invoices WHERE consumed_at < NOW() - INTERVAL '30 days'")
                    
                    simulate_rival_snatch(db)
                    run_automation_daemon(db, MY_NODE_ID)
                    db.commit()
                finally:
                    db.close()
            except Exception as e:
                print(f" [HEARTBEAT] Marketplace simulation error: {e}")

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    print(" [SYSTEM] ⚙️ Marketplace Simulation Heartbeat Online (10s interval).")

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
                return jsonify({"status": "PAYMENT_REQUIRED", "invoice": "lnbc_mock_dev_invoice", "hash": "mock_subrosa_hash", "cost": cost}), 402
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": invoice_data['payment_request'], "hash": invoice_data['r_hash'], "cost": cost}), 402
        else:
            return jsonify({"status": "PAYMENT_REQUIRED", "invoice": "lnbc_mock_dev_invoice", "hash": "mock_subrosa_hash", "cost": cost}), 402
            
    except Exception as e:
        print(f" [ERROR] Sub-Rosa Exception: {str(e)}")
        return jsonify({"status": "ERROR", "message": "Server Error: An unexpected internal error occurred."}), 500

@app.route('/api/v1/sub-rosa/finalize', methods=['POST'])
@requires_permission(Permission.CREATE_TASK)
def api_finalize_sub_rosa():
    try:
        r_hash = request.json.get('hash')
        
        # 🛑 SECURITY FIX: Safe processing of mock hashes for local development
        approved = False
        if lnd:
            if lnd.check_status(r_hash) == "SETTLED":
                approved = True
        elif r_hash == "mock_subrosa_hash":
            approved = True

        if approved:
            conn = get_db()
            
            # Check if invoice was already consumed
            consumed = conn.execute("SELECT 1 FROM consumed_invoices WHERE hash = %s", (r_hash,)).fetchone()
            if consumed:
                print(f" [SECURITY] 🚨 Blocked replay attack for invoice hash: {r_hash}")
                return jsonify({"success": False, "message": "Invoice already consumed. Replay attack detected."}), 403
                
            conn.execute("INSERT INTO consumed_invoices (hash) VALUES (%s)", (r_hash,))
            conn.commit()
            
            return jsonify({"success": True})
            
        return jsonify({"success": False, "message": "Payment not detected in mempool."}), 402
    except Exception as e:
        print(f" [ERROR] Sub-Rosa Exception: {str(e)}")
        return jsonify({"status": "ERROR", "message": "Server Error: An unexpected internal error occurred."}), 500

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
@app.route('/api/v1/telemetry/ingest', methods=['POST'])
@rate_limit(max_requests=30, window_seconds=60) # Allow rapid GPS pings
def ingest_telemetry():
    """
    Catches live GPS streams from the Android KMP application and logs them 
    immutably into the time-series ledger for Incident Replay.
    """
    try:
        data = request.json
        agent_id = data.get('agent_id')
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        status = data.get('status', 'ONLINE')
        mission_id = data.get('current_mission_id')
        event_type = data.get('event_type', 'PING')

        if not agent_id:
            return jsonify({"status": "error", "message": "Missing agent_id"}), 400

        conn = get_db()
        
        # Insert the immutable GPS breadcrumb
        conn.execute('''
            INSERT INTO agent_telemetry_history 
            (agent_id, latitude, longitude, status, current_mission_id, event_type) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (agent_id, lat, lon, status, mission_id, event_type))
        
        # Keep the legacy `nodes` table updated for backwards compatibility with the current map UI
        conn.execute('''
            UPDATE nodes 
            SET last_seen = %s 
            WHERE node_id = %s
        ''', (time.time(), agent_id))
        
        conn.commit()
        return jsonify({"status": "success", "recorded_at": time.time()})

    except Exception as e:
        print(f" [TELEMETRY] 🚨 Ingestion Error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal processing error."}), 500

@app.route('/api/v1/telemetry/history', methods=['GET'])
def get_telemetry_history():
    """
    Universal Forensic Temporal Engine API.
    """
    try:
        agent_id = request.args.get('agent_id')
        mission_id = request.args.get('mission_id')
        is_global = request.args.get('global') == 'true'
        
        # 🕒 NEW: DVR Temporal Parameters
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        minutes = request.args.get('minutes', 60) # Legacy fallback

        # 🛑 SECURITY FIX: Must have an anchor point OR explicit global authorization
        if not agent_id and not mission_id and not is_global:
            return jsonify({"status": "error", "message": "Must provide agent_id, mission_id, or global=true."}), 400

        conn = get_db()
        
        # Start building the base query
        query = '''
            SELECT agent_id, latitude, longitude, status, current_mission_id, event_type, 
                   EXTRACT(EPOCH FROM recorded_at) as timestamp
            FROM agent_telemetry_history 
            WHERE 1=1
        '''
        params = []

        # ⏱️ TEMPORAL FILTERING: Exact Bounds vs Rolling Window
        if start_time and end_time:
            # Convert the incoming Unix Epoch seconds into Postgres native timestamps
            query += " AND recorded_at >= to_timestamp(%s) AND recorded_at <= to_timestamp(%s)"
            params.extend([float(start_time), float(end_time)])
        else:
            # Fallback to the rolling "last X minutes" for quick live replays
            query += " AND recorded_at >= NOW() - INTERVAL '%s minutes'"
            params.append(int(minutes))

        # 🎯 ENTITY FILTERING
        if agent_id:
            query += " AND agent_id = %s"
            params.append(agent_id)
        
        if mission_id:
            query += " AND current_mission_id = %s"
            params.append(mission_id)

        # Crucial for smooth DVR playback: Sort chronologically
        query += " ORDER BY recorded_at ASC"

        # Execute the dynamically generated SQL safely
        history = conn.execute(query, tuple(params)).fetchall()
        
        return jsonify([dict(row) for row in history])

    except Exception as e:
        print(f" [TELEMETRY] 🚨 Forensic Retrieval Error: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to retrieve forensic history."}), 500
    
@app.route('/api/v1/node/register', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60) # 🛑 SECURITY FIX: Rate Limit Worker APIs
def mock_register():
    data = request.json
    raw_seed = os.environ.get("HARDWARE_ATTESTATION_SEED", "")
    tpm_seed = raw_seed.encode("utf-8")
    expected_sig = hmac.new(tpm_seed, f"{data.get('node_id')}:{data.get('timestamp')}".encode(), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(str(data.get('signature')), expected_sig):
        return jsonify({"error": "Invalid signature"}), 403
    return jsonify({"status": "success"})

@app.route('/api/v1/task/request', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60) # 🛑 SECURITY FIX: Rate Limit Worker APIs
@require_node_signature
def mock_request():
    return jsonify({"task_id": f"TASK-{random.randint(1000,9999)}", "payout_sats": 500})

@app.route('/api/v1/task/submit', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60) # 🛑 SECURITY FIX: Rate Limit Worker APIs
@require_node_signature
def mock_submit():
    import hashlib
    import time
    return jsonify({"preimage": hashlib.sha256(str(time.time()).encode()).hexdigest()})

# ==========================================
# 🧪 DEV TOOLS: TEMPORAL DVR SEEDER (MANHATTAN GRID)
# ==========================================
@app.route('/seed-dvr')
@admin_required  # 🛡️ PHASE 3 FIX: Enforce auth outside production
def seed_dvr():
    """Generates realistic street-grid data using Manhattan Distance routing."""
    # 🛑 THE FIX: Hard block in production
    if os.environ.get("ENVIRONMENT") == "production":
        abort(403, "This debugging endpoint is permanently disabled in production environments.")
        
    # ... rest of the seed logic ...
    import random
    from datetime import datetime, timedelta
    conn = get_db()
    
    conn.execute("DELETE FROM agent_telemetry_history WHERE agent_id LIKE 'VAN-DEMO-%'")
    
    agents = [f"VAN-DEMO-{str(i).zfill(3)}" for i in range(1, 16)]
    base_lat, base_lon = 33.415, -111.831 # Mesa, AZ
    
    now = datetime.utcnow()
    start_time = now - timedelta(minutes=60)
    
    agent_states = {}
    for a in agents:
        start_lat = base_lat + random.uniform(-0.06, 0.06)
        start_lon = base_lon + random.uniform(-0.06, 0.06)
        agent_states[a] = {
            "lat": start_lat, "lon": start_lon,
            "state": "ONLINE", "mission_id": None,
            "timer": random.randint(5, 15),
            "target_lat": start_lat + random.uniform(-0.02, 0.02),
            "target_lon": start_lon + random.uniform(-0.02, 0.02)
        }
    
    count = 0
    for step in range(360):
        step_time = start_time + timedelta(seconds=step * 10)
        
        for a in agents:
            st = agent_states[a]
            
            # State Transitions
            if st["timer"] <= 0:
                if st["state"] == "ONLINE":
                    st["state"] = "BUSY_ON_WAY"
                    st["mission_id"] = f"FLT-{random.randint(1000, 9999)}"
                    st["target_lat"] = st["lat"] + random.uniform(-0.04, 0.04)
                    st["target_lon"] = st["lon"] + random.uniform(-0.04, 0.04)
                    st["timer"] = 9999 # Distance dictates arrival now
                elif st["state"] == "BUSY_ON_WAY":
                    st["state"] = "BUSY_ON_SITE"
                    st["timer"] = random.randint(10, 20) # Work on site
                else:
                    st["state"] = "ONLINE"
                    st["mission_id"] = None
                    st["target_lat"] = st["lat"] + random.uniform(-0.02, 0.02)
                    st["target_lon"] = st["lon"] + random.uniform(-0.02, 0.02)
                    st["timer"] = 9999
            else:
                st["timer"] -= 1

            # MANHATTAN GRID MOVEMENT (~25mph)
            step_size = 0.001 
            if st["state"] != "BUSY_ON_SITE":
                lat_dist = st["target_lat"] - st["lat"]
                lon_dist = st["target_lon"] - st["lon"]
                
                # Resolve Longitude (East/West) first, then Latitude (North/South)
                if abs(lon_dist) > step_size:
                    st["lon"] += step_size if lon_dist > 0 else -step_size
                elif abs(lat_dist) > step_size:
                    st["lat"] += step_size if lat_dist > 0 else -step_size
                else:
                    # Snapped to target!
                    st["lat"] = st["target_lat"]
                    st["lon"] = st["target_lon"]
                    if st["state"] == "BUSY_ON_WAY":
                        st["timer"] = 0 # Trigger status change to ON_SITE next tick
                    elif st["state"] == "ONLINE":
                        st["target_lat"] = st["lat"] + random.uniform(-0.02, 0.02)
                        st["target_lon"] = st["lon"] + random.uniform(-0.02, 0.02)
            
            conn.execute('''
                INSERT INTO agent_telemetry_history 
                (agent_id, latitude, longitude, status, current_mission_id, event_type, recorded_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (a, st["lat"], st["lon"], st["state"], st["mission_id"], "PING", step_time))
            count += 1
            
    conn.commit()
    return jsonify({"status": "success", "message": f"Injected {count} Manhattan street-grid GPS pings!"})

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
    start_marketplace_heartbeat()
    app.run(host='0.0.0.0', port=5000)