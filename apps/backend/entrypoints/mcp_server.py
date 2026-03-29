import logging
import json
import time
import uuid
import os
import redis.asyncio as redis
from mcp.server.fastmcp import FastMCP
from backend.core.lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PAN-MCP-Gateway")

# Initialize FastMCP Server
mcp = FastMCP("PAN_Tactical_Gateway")

# ---------------------------------------------------------------------------
# LAZY STATE MANAGEMENT (Test-Safe)
# ---------------------------------------------------------------------------
_redis_client = None
_lnd = None
LND_CONNECTED = False
LND_FAILED = False 

def get_redis():
    """Lazy initialization of Redis to prevent import-time connection errors during testing."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"), 
            port=int(os.getenv("REDIS_PORT", 6379)), 
            db=0
        )
    return _redis_client

def get_lnd():
    """Lazy initialization of the Lightning Engine."""
    global _lnd
    if _lnd is None:
        _lnd = LightningEngine()
    return _lnd

def get_safe_invoice(amount, memo):
    global LND_CONNECTED, LND_FAILED
    lnd = get_lnd()
    
    if LND_FAILED: 
        return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}
        
    if not LND_CONNECTED:
        try:
            lnd.connect()
            LND_CONNECTED = True
        except Exception as e:
            logger.error(f"LND Connection Failed: {e}. Switching to Mock Mode.")
            LND_FAILED = True
            return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}

    try:
        # NOTE: lightning_engine.py must be updated to include create_invoice() for B2B billing
        invoice_data = lnd.create_invoice(amount, memo)
        if not invoice_data or 'payment_request' not in invoice_data: 
            return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}
        return invoice_data
    except Exception as e:
        logger.error(f"LND Invoice Fallback Triggered: {e}")
        LND_FAILED = True
        return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}

def safe_verify_payment(payment_hash):
    if not payment_hash: return False
    
    global LND_CONNECTED, LND_FAILED
    lnd = get_lnd()
    
    if LND_FAILED: return False # Fail Closed
    
    if not LND_CONNECTED:
        try:
            lnd.connect()
            LND_CONNECTED = True
        except Exception:
            LND_FAILED = True
            return False 
            
    try:
        if len(payment_hash) != 64: return False 
        # 🟢 THE FIX: Correct method name mapped to lightning_engine.py
        return lnd.verify_payment_hash(payment_hash)
    except Exception as e:
        logger.error(f"LND Verification Fallback Triggered: {e}")
        LND_FAILED = True
        return False

# ---------------------------------------------------------------------------
# PAN TACTICAL B2B TOOLS (For Fleet Partner AIs)
# ---------------------------------------------------------------------------

@mcp.tool()
async def check_network_surge() -> str:
    """Queries the PAN Surge Pricing Engine to determine current multiplier and active agent count."""
    redis_client = get_redis()
    try:
        queue_depth = await redis_client.llen("pan:dispatch:active_tasks")
        
        cursor = 0
        online_agents = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="agent:*", count=100)
            for key in keys:
                status = await redis_client.hget(key, "status")
                if status and status.decode('utf-8') in ["ONLINE", "EN_ROUTE"]:
                    online_agents += 1
            if cursor == 0: break
            
        return f"NETWORK STATUS: {online_agents} Vanguard Agents active. Dispatch Queue Depth: {queue_depth}. (Use this to decide if dispatch is viable)."
    except Exception as e:
        return f"Error querying network: {e}"

@mcp.tool()
async def dispatch_vanguard_agent(vin: str, fault_code: str, lat: float, lon: float, osm_color: str = "YELLOW", base_bounty_usd: float = 45.0, payment_hash: str = None) -> str:
    """Dispatches a physical Vanguard Agent to a stranded autonomous vehicle. Requires L402 API payment."""
    redis_client = get_redis()
    
    # MCP Gateway Fee (1000 Sats) to prevent AI spam
    if not payment_hash:
        invoice_data = get_safe_invoice(1000, f"API Dispatch Fee: {vin}")
        return f"ERROR: 402 Payment Required\nPay this Lightning invoice to execute dispatch:\nInvoice: {invoice_data['payment_request']}\nHash: {invoice_data['r_hash']}"
    
    if not safe_verify_payment(payment_hash): 
        return "ERROR: 401 Unauthorized. Invoice unpaid."

    try:
        task_id = f"tsk_{uuid.uuid4().hex[:12]}"
        
        task_record = {
            "fleet_id": "MCP_API_CLIENT",
            "vin": vin,
            "fault_code": fault_code,
            "lat": lat,
            "lon": lon,
            "bounty_usd": base_bounty_usd,
            "base_bounty_usd": base_bounty_usd, 
            "osm_color": osm_color.upper(),
            "timestamp": int(time.time()),
            "status": "pending",
            "mcp_payment_hash": payment_hash
        }
        
        await redis_client.hset(f"pan:task:{task_id}", mapping=task_record)
        await redis_client.rpush("pan:dispatch:active_tasks", task_id)
        
        return f"✅ SUCCESS: Distress signal injected. Task ID: {task_id}. A Vanguard Agent is being routed via OSRM."
    except Exception as e:
        return f"Dispatch injection failed: {e}"

@mcp.tool()
async def check_mission_status(task_id: str) -> str:
    """Checks the real-time status and assigned agent for a dispatched task."""
    redis_client = get_redis()
    try:
        raw_task = await redis_client.hgetall(f"pan:task:{task_id}")
        if not raw_task:
            return f"ERROR: Task {task_id} not found."
            
        status = raw_task.get(b"status", b"UNKNOWN").decode('utf-8')
        
        mission_key = f"mission:active:{task_id}"
        raw_mission = await redis_client.hgetall(mission_key)
        
        if raw_mission:
            agent_id = raw_mission.get(b"agent_id", b"Unassigned").decode('utf-8')
            sla_status = raw_mission.get(b"sla_status", b"OK").decode('utf-8')
            return f"STATUS: {status} | Agent Assigned: {agent_id} | SLA: {sla_status}"
            
        return f"STATUS: {status} | Waiting for Matching Engine to route an agent."
    except Exception as e:
        return f"Status lookup failed: {e}"

@mcp.tool()
async def pull_sb1417_report(task_id: str, payment_hash: str = None) -> str:
    """Retrieves the sealed SB 1417 Optical Health Report (Photos + Hash) for a completed mission."""
    redis_client = get_redis()
    
    # MCP Report Retrieval Fee (500 Sats)
    if not payment_hash:
        invoice_data = get_safe_invoice(500, f"SB1417 Export: {task_id}")
        return f"ERROR: 402 Payment Required\nPay this Lightning invoice to decrypt report:\nInvoice: {invoice_data['payment_request']}\nHash: {invoice_data['r_hash']}"
    
    if not safe_verify_payment(payment_hash): 
        return "ERROR: 401 Unauthorized. Invoice unpaid."
        
    try:
        report_json = await redis_client.hget("pan:compliance:reports", task_id)
        if not report_json:
            return f"ERROR: No SB 1417 report found for {task_id}. Ensure task is COMPLETED."
            
        return f"✅ COMPLIANCE REPORT DECRYPTED:\n{report_json.decode('utf-8')}"
    except Exception as e:
        return f"Report retrieval failed: {e}"

if __name__ == "__main__":
    logger.info("🚀 PAN Tactical MCP Gateway Online. Awaiting Fleet AI Connections...")
    # 🟢 THE FIX: Clean configuration without fragile monkey-patching
    mcp.run(transport="sse", host="0.0.0.0", port=8000)