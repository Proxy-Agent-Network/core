import logging
from mcp.server.fastmcp import FastMCP
from lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP-Server")

# --- THE FIX IS HERE ---
# We tell FastMCP to bind to 0.0.0.0 right when we create it
mcp = FastMCP("LightningProxyServer", host="0.0.0.0", port=8000)

# Initialize our Lightning Engine
lnd = LightningEngine()
lnd.connect()

@mcp.tool()
def create_lightning_invoice(amount_sats: int, memo: str) -> str:
    """
    Creates a Lightning Network invoice for a specified amount of satoshis.
    
    Args:
        amount_sats: The amount in satoshis to request (must be a positive integer).
        memo: A short description of what the invoice is for.
    """
    logger.info(f"🤖 AI requested invoice: {amount_sats} sats for '{memo}'")
    
    try:
        result = lnd.create_invoice(amount_sats, memo)
        if result and 'payment_request' in result:
            return (
                f"✅ Invoice created successfully!\n"
                f"Payment Request (BOLT11): {result['payment_request']}\n"
                f"Hash: {result['r_hash']}"
            )
        else:
            return "❌ Failed to create invoice. The LND node might be disconnected."
    except Exception as e:
        return f"❌ Error creating invoice: {str(e)}"
    
@mcp.tool()
def get_node_balances() -> str:
    """
    Checks the current balance of the Lightning node.
    Returns both the on-chain Bitcoin balance and the off-chain Lightning channel balance.
    """
    logger.info("🤖 AI requested node balances")
    
    balances = lnd.get_balances()
    if balances:
        return (
            f"💰 Node Balances:\n"
            f"On-Chain Wallet: {balances['onchain_sats']} sats\n"
            f"Lightning Channels: {balances['channel_sats']} sats\n"
            f"Pending Channels: {balances['pending_channel_sats']} sats"
        )
    else:
        return "❌ Failed to fetch balances. The LND node might be disconnected."
    
import json # Make sure to add this to the top of your imports if it isn't there!

@mcp.tool()
def get_agent_manifest() -> str:
    """
    Agent Description Protocol (ADP) endpoint.
    Returns semantic information about this agent, its routing identity, and its pricing.
    Other agents should call this first to establish negotiation parameters.
    """
    logger.info("🤖 AI requested Agent Description Manifest")
    
    # We gracefully handle the case where LND might be offline
    agent_pubkey = getattr(lnd, 'pubkey', 'OFFLINE')
    
    # The ADP Schema
    manifest = {
        "agent_name": "Lightning Proxy Node Alpha",
        "agent_role": "Payment & Tool Proxy",
        "network_environment": "regtest",
        "identity": {
            "lnd_pubkey": agent_pubkey,
            "supported_protocols": ["MCP", "BOLT11"]
        },
        "pricing": {
            "base_fee_sats": 10,
            "currency": "satoshi",
            "negotiable": False
        },
        "capabilities": [
            "create_lightning_invoice",
            "get_node_balances",
            "get_agent_manifest"
        ]
    }
    
    # Return as a formatted JSON string so the calling AI can easily parse it
    return json.dumps(manifest, indent=2)

@mcp.tool()
def premium_data_query(query: str, payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Executes a high-value real-world data query. 
    Cost: 10 satoshis.
    
    Flow:
    1. Call without payment_hash to receive an L402 invoice.
    2. Pay the invoice over the Lightning Network.
    3. Call again with the payment_hash to unlock the data.
    """
    logger.info(f"🤖 AI requested Premium Data for: '{query}'")
    
    # --- PHASE 1: L402 PAYMENT REQUIRED ---
    if not payment_hash:
        logger.info("⚠️ No payment provided. Issuing L402 Challenge.")
        invoice = lnd.create_invoice(sats=10, memo=f"Premium AI Query: {query}")
        
        # We simulate the HTTP 402 response via the MCP text return
        return (
            "ERROR: 402 Payment Required\n"
            f"Please pay this invoice to access the service:\n"
            f"Invoice: {invoice['payment_request']}\n\n"
            f"Once paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\n"
            f"Hash to use: {invoice['r_hash']}"
        )
    
    # --- PHASE 2: VERIFICATION & DELIVERY ---
    logger.info(f"🔍 Verifying L402 payment for hash: {payment_hash[:8]}...")
    is_paid = lnd.verify_payment(payment_hash)
    
    if is_paid:
        logger.info("✅ Payment confirmed. Delivering premium data.")
        # This is where your agent would do the actual real-world work/API call
        return f"🔓 ACCESS GRANTED. Here is the premium data for '{query}': The answer is 42."
    else:
        logger.warning("❌ Payment invalid or pending.")
        return "ERROR: 402 Payment Required. The invoice has not been paid yet."

if __name__ == "__main__":
    logger.info("Starting MCP Server on SSE transport...")
    mcp.run(transport="sse")