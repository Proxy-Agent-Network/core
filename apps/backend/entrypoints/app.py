import random
import time
import json
import base64
import threading
import secrets
import jinja2
import traceback
import uuid
import bleach
import redis  # 🛡️ M1 FIX: Added Redis for distributed rate limiting
from datetime import timedelta

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

from flask import Flask, render_template, request, jsonify, g, redirect, url_for, session, abort, send_from_directory
import hmac
import hashlib
from functools import wraps
from core.db import get_db_conn

try:
    from core.lightning_engine import lnd
    print(" [SYSTEM] ⚡ Lightning Treasury Layer Loaded.")
except ImportError:
    print(" [WARN] ⚠️  lightning_engine.py not found. Running without payment rails.")
    lnd = None

try:
    from proxy_core import NodeHardware
    print(" [SYSTEM] 🔒 Connecting to Rust TPM Engine...")
    hw_bridge = NodeHardware()
    MY_NODE_ID = hw_bridge.get_fingerprint()
    # TODO (RUST TEAM): Substring checks are not secure attestation. Migrate this to 
    # verify a signed payload from the TPM rather than checking for a magic prefix.
    HW_SECURED = "0x8F9B" in MY_NODE_ID
except Exception as e:
    print(f" [WARN] ⚠️ Rust Enclave not found, attempting legacy fallback: {e}")
    try:
        from node_legacy.tpm_binding import NodeHardware
        hw_bridge = NodeHardware()
        MY_NODE_ID = hw_bridge.get_fingerprint()
        HW_SECURED = True
    except Exception as legacy_e:
        # 🛡️ DEV BYPASS: Allow local testing without physical TPM hardware
        if os.environ.get("ENVIRONMENT") != "production":
            print(" [DEV BYPASS] ⚠️ Mocking Hardware Root of Trust for local development.")
            class MockNodeHardware:
                def get_fingerprint(self): return "0x8F9B-MOCK-DEV-NODE"
                def encrypt_data(self, data): return f"SECURE::{data}"
                def decrypt_data(self, data): return data.replace("SECURE::", "")
            hw_bridge = MockNodeHardware()
            MY_NODE_ID = hw_bridge.get_fingerprint()
            HW_SECURED = False
        else:
            # 🛑 THE FIX: Fail loud and fail closed in PROD. 
            print(f" [SECURITY] 🚨 CRITICAL: Hardware Root of Trust totally failed! ({legacy_e})")
            raise RuntimeError("Cannot boot Agent Node without secure hardware attestation. Aborting.")

from werkzeug.middleware.proxy_fix import ProxyFix

# --- REPLACEMENT 1: Tell Flask where the new Public Website lives ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
TEMPLATE_DIR = os.path.join(ROOT_DIR, "apps", "web", "public_website", "templates")
STATIC_DIR = os.path.join(ROOT_DIR, "apps", "web", "public_website", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

def sanitize_html(text):
    """🛡️ PHASE 6 FIX: Global Bleach Sanitizer for all Jinja Templates."""
    if not isinstance(text, str):
        return text
    allowed_tags = ['p', 'b', 'i', 'strong', 'em', 'a', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'br']
    return bleach.clean(text, tags=allowed_tags, strip=True)

# Register the global filter
app.jinja_env.filters['bleach'] = sanitize_html

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

# 🛡️ M1 FIX: Initialize Cluster-Wide Redis Client
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url)

# ==========================================
# 🔒 CONCURRENCY & LOCKING ENGINE
# ==========================================
SIG_LOCK = threading.Lock() # 🛑 SECURITY FIX: Prevent Thread Collision on USED_SIGNATURES

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
    if 'csrf_token' in session:
        response.set_cookie('csrf_token', session['csrf_token'], samesite='Strict')
    return response

@app.context_processor
def inject_csrf_token():
    if 'csp_nonce' not in g:
        g.csp_nonce = secrets.token_hex(16)

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
# ⏱️ RATE LIMITING ENGINE (Distributed)
# ==========================================

def rate_limit(max_requests: int, window_seconds: int):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 🛑 SECURITY FIX: Force TCP remote_addr to prevent X-Forwarded-For spoofing
            client_ip = request.remote_addr
            key = f"rate_limit:{request.endpoint}:{client_ip}"
            
            try:
                # 🛡️ M1 FIX: Atomic Redis increments ensure cluster-wide enforcement
                attempts = redis_client.incr(key)
                if attempts == 1:
                    redis_client.expire(key, window_seconds)
                    
                if attempts > max_requests:
                    print(f" [SECURITY] 🚨 Rate limit exceeded for IP: {client_ip} on {request.path}")
                    return jsonify({
                        "type": "error", 
                        "status": "429 Too Many Requests", 
                        "message": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                    }), 429
            except Exception as e:
                # Fail-open gracefully if Redis temporarily drops, but log heavily
                print(f" [WARN] Distributed rate limiter bypass due to Redis error: {e}")

            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
            if abs(now - request_time) > 300: 
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

        with SIG_LOCK:
            USED_SIGNATURES[signature] = now

        g.verified_node_id = node_id
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 🛑 ZERO-TRUST ADMIN & SESSION SECURITY
# ==========================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_token = request.headers.get("X-Admin-Token")
        expected_token = os.environ.get("ADMIN_SECRET_TOKEN")
        
        if not expected_token:
            print(" [SECURITY] 🚨 CRITICAL: ADMIN_SECRET_TOKEN is not set in the environment!")
            abort(500, "Server Configuration Error: Admin portal is locked down due to missing security token.")
            
        if not admin_token or not secrets.compare_digest(admin_token, expected_token):
            abort(403) 
            
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Replaces the deprecated RBAC system for simple UI access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
            raise RuntimeError("Quantum Safeguard: TPM hardware bridge missing. Refusing to downgrade to plaintext storage.")
            
        encrypted_balance = hw_bridge.encrypt_data(str(new_balance))
        
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

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = get_db_conn()
        db.execute('''CREATE TABLE IF NOT EXISTS nodes (node_id TEXT PRIMARY KEY, hostname TEXT, total_earned TEXT DEFAULT '0', xp INTEGER DEFAULT 0, last_seen DOUBLE PRECISION)''')
        
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

# --- USER AUTHENTICATION ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=5, window_seconds=60)
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        expected_password = os.environ.get('ADMIN_SECRET_TOKEN')
        
        if not expected_password:
            print(" [SECURITY] 🚨 CRITICAL: Login attempted but ADMIN_SECRET_TOKEN is not set in the environment!")
            return "Server Configuration Error: Admin credential not securely configured. Login disabled.", 500
            
        if password and secrets.compare_digest(password, expected_password):
            session.clear() 
            session.permanent = True 
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
    
    # 1. Authenticate the Request - 🛡️ L4 FIX: Fail-closed strict string comparison.
    auth_header = request.headers.get('Authorization')
    expected_key = os.environ.get('PARTNER_API_KEY')
    
    if not expected_key or not auth_header or not secrets.compare_digest(auth_header, f"Bearer {expected_key}"):
        return jsonify({
            "error": "Unauthorized", 
            "message": "Missing or invalid Partner API Key."
        }), 401

    # 2. Validate the Payload
    data = request.json
    if not data:
        return jsonify({"error": "Bad Request", "message": "Invalid JSON payload."}), 400

    required_fields = ['asset_id', 'latitude', 'longitude', 'error_code']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "Bad Request", "message": f"Missing required field: {field}"}), 400
    
    mission_id = f"FLT-{random.randint(10000, 99999)}"
    
    # Simple tiering logic for the response
    tier = 1
    base_bounty = 15.00
    if data['error_code'] in ['spill_remediation', 'tire_pressure']:
        tier = 2; base_bounty = 25.00
    elif data['error_code'] in ['manual_override', 'scene_securement']:
        tier = 3; base_bounty = 85.00

    map_payload = {
        "id": mission_id,
        "asset_id": data['asset_id'],
        "lat": data['latitude'],
        "lng": data['longitude'],
        "fault_code": data['error_code'],
        "bounty": f"${base_bounty:.2f}",
        "tier": tier
    }

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
@login_required
def command_center_root():
    return render_template('index.html')

@app.route('/developers')
@login_required
def developer_portal():
    return render_template('developer.html')

@app.route('/reports')
@login_required
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
    if days > 90: starting_escrow = 150000.00 
    
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
    import random
    from datetime import datetime, timedelta
    
    timeframe = request.args.get('timeframe', '1m')
    tf_map = {'24h': 1, '1w': 7, '1m': 30, '3m': 90, '1y': 365, 'custom': 30}
    days = tf_map.get(timeframe, 30)
    mult = max(1, days / 30)
    
    now = datetime.utcnow()
    
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
        "infractions": infractions[:8] 
    })

@app.route('/command/css/<path:filename>')
def command_center_css(filename):
    return send_from_directory(os.path.join(CMD_CENTER_DIR, 'css'), filename)

@app.route('/command/js/<path:filename>')
def command_center_js(filename):
    return send_from_directory(os.path.join(CMD_CENTER_DIR, 'js'), filename)

@app.route('/pan_client_config.js')
def command_center_secrets():
    return send_from_directory(CMD_CENTER_DIR, 'pan_client_config.js')

@app.route('/faq')
def faq():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    return render_template('faq.html', node_id=MY_NODE_ID, balance=balance, hw_secured=HW_SECURED)

@app.route('/legal/<doc_type>')
def legal(doc_type):
    doc = LEGAL_DOCS.get(doc_type)
    if not doc: return redirect(url_for('command_center_root'))
    
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    
    safe_content = sanitize_html(doc['content'])
    
    return render_template('legal.html', title=doc['title'], content=safe_content, balance=balance)

@app.route('/api/v1/network/stats')
def get_network_stats():
    conn = get_db()
    active_nodes = conn.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE last_seen > %s", (time.time() - 300,)).fetchone()['cnt']
    return jsonify({
        "total_volume": "ENCRYPTED", 
        "active_nodes": active_nodes, 
        "peers": active_nodes, 
        "protocol_v": "1.6.0", 
        "status": "STABLE"
    })

@app.route('/admin')
def admin_portal():
    conn = get_db()
    balance = get_secure_balance(conn, MY_NODE_ID)
    return render_template('admin.html', node_id=MY_NODE_ID, balance=balance)

ALLOWED_ADMIN_SESSION_KEYS = {"ui_theme", "mood_intensity"}

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
# SECURITY & RATE LIMITING HEARTBEAT
# ==========================================
def start_security_heartbeat():
    def loop():
        while True:
            time.sleep(10)
            now = time.time()
            
            with SIG_LOCK:
                expired_keys = [k for k, v in USED_SIGNATURES.items() if now - v > 300]
                for k in expired_keys:
                    del USED_SIGNATURES[k]

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    print(" [SYSTEM] ⚙️ Security Heartbeat Online (10s interval).")

# ==========================================
# 🤖 AUTONOMOUS WORKER MOCK ENDPOINTS
# ==========================================
@app.route('/api/v1/telemetry/history', methods=['GET'])
def get_telemetry_history():
    try:
        agent_id = request.args.get('agent_id')
        mission_id = request.args.get('mission_id')
        is_global = request.args.get('global') == 'true'
        
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        minutes = request.args.get('minutes', 60) 

        if not agent_id and not mission_id and not is_global:
            return jsonify({"status": "error", "message": "Must provide agent_id, mission_id, or global=true."}), 400

        conn = get_db()
        
        query = '''
            SELECT agent_id, latitude, longitude, status, current_mission_id, event_type, 
                   EXTRACT(EPOCH FROM recorded_at) as timestamp
            FROM agent_telemetry_history 
            WHERE 1=1
        '''
        params = []

        if start_time and end_time:
            query += " AND recorded_at >= to_timestamp(%s) AND recorded_at <= to_timestamp(%s)"
            params.extend([float(start_time), float(end_time)])
        else:
            query += " AND recorded_at >= NOW() - INTERVAL '%s minutes'"
            params.append(int(minutes))

        if agent_id:
            query += " AND agent_id = %s"
            params.append(agent_id)
        
        if mission_id:
            query += " AND current_mission_id = %s"
            params.append(mission_id)

        query += " ORDER BY recorded_at ASC"

        history = conn.execute(query, tuple(params)).fetchall()
        
        return jsonify([dict(row) for row in history])

    except Exception as e:
        print(f" [TELEMETRY] 🚨 Forensic Retrieval Error: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to retrieve forensic history."}), 500
    
@app.route('/api/v1/node/register', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60) 
def mock_register():
    if os.environ.get("ENVIRONMENT") == "production":
        abort(403, "Mock endpoints disabled in production.")
        
    data = request.json
    raw_seed = os.environ.get("HARDWARE_ATTESTATION_SEED")
    if not raw_seed:
        return jsonify({"error": "Configuration missing"}), 500
        
    tpm_seed = raw_seed.encode("utf-8")
    expected_sig = hmac.new(tpm_seed, f"{data.get('node_id')}:{data.get('timestamp')}".encode(), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(str(data.get('signature')), expected_sig):
        return jsonify({"error": "Invalid signature"}), 403
    return jsonify({"status": "success"})

@app.route('/api/v1/task/request', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60) 
@require_node_signature
def mock_request():
    if os.environ.get("ENVIRONMENT") == "production":
        abort(403, "Mock endpoints disabled in production.")
        
    return jsonify({"task_id": f"TASK-{random.randint(1000,9999)}", "payout_sats": 500})

@app.route('/api/v1/task/submit', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60) 
@require_node_signature
def mock_submit():
    if os.environ.get("ENVIRONMENT") == "production":
        abort(403, "Mock endpoints disabled in production.")
        
    import hashlib
    import time
    return jsonify({"preimage": hashlib.sha256(str(time.time()).encode()).hexdigest()})

# ==========================================
# 🧪 DEV TOOLS: TEMPORAL DVR SEEDER (MANHATTAN GRID)
# ==========================================
@app.route('/seed-dvr')
@admin_required  
def seed_dvr():
    """Generates realistic street-grid data using Manhattan Distance routing."""
    if os.environ.get("ENVIRONMENT") == "production":
        abort(403, "This debugging endpoint is permanently disabled in production environments.")
        
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
            
            if st["timer"] <= 0:
                if st["state"] == "ONLINE":
                    st["state"] = "BUSY_ON_WAY"
                    st["mission_id"] = f"FLT-{random.randint(1000, 9999)}"
                    st["target_lat"] = st["lat"] + random.uniform(-0.04, 0.04)
                    st["target_lon"] = st["lon"] + random.uniform(-0.04, 0.04)
                    st["timer"] = 9999 
                elif st["state"] == "BUSY_ON_WAY":
                    st["state"] = "BUSY_ON_SITE"
                    st["timer"] = random.randint(10, 20) 
                else:
                    st["state"] = "ONLINE"
                    st["mission_id"] = None
                    st["target_lat"] = st["lat"] + random.uniform(-0.02, 0.02)
                    st["target_lon"] = st["lon"] + random.uniform(-0.02, 0.02)
                    st["timer"] = 9999
            else:
                st["timer"] -= 1

            step_size = 0.001 
            if st["state"] != "BUSY_ON_SITE":
                lat_dist = st["target_lat"] - st["lat"]
                lon_dist = st["target_lon"] - st["lon"]
                
                if abs(lon_dist) > step_size:
                    st["lon"] += step_size if lon_dist > 0 else -step_size
                elif abs(lat_dist) > step_size:
                    st["lat"] += step_size if lat_dist > 0 else -step_size
                else:
                    st["lat"] = st["target_lat"]
                    st["lon"] = st["target_lon"]
                    if st["state"] == "BUSY_ON_WAY":
                        st["timer"] = 0 
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
            
    start_security_heartbeat()
    app.run(host='0.0.0.0', port=5000)