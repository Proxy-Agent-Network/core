import logging
import json
import requests
from mcp.server.fastmcp import FastMCP
from lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP-Server")

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
            "get_agent_manifest",
            "get_crypto_spot_price"
        ]
    }
    
    # Return as a formatted JSON string so the calling AI can easily parse it
    return json.dumps(manifest, indent=2)

@mcp.tool()
def get_crypto_spot_price(ticker: str, payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Fetch the real-time spot price of a cryptocurrency from live markets.
    Cost: 15 satoshis.
    
    Flow:
    1. Call without payment_hash to receive an L402 invoice.
    2. Pay the invoice over the Lightning Network.
    3. Call again with the payment_hash to unlock the data.
    """
    logger.info(f"🤖 AI requested Crypto Spot Price for: '{ticker}'")
    
    # --- PHASE 1: L402 PAYMENT REQUIRED ---
    if not payment_hash:
        logger.info(f"⚠️ No payment provided for {ticker}. Issuing L402 Challenge.")
        invoice_data = lnd.create_invoice(15, f"Real-time price lookup for {ticker}")
        
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
            
        return (f"ERROR: 402 Payment Required\n"
                f"Please pay this invoice to access the service:\n"
                f"Invoice: {invoice_data['payment_request']}\n\n"
                f"Once paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\n"
                f"Hash to use: {invoice_data['r_hash']}")

    # --- PHASE 2: VERIFICATION ---
    logger.info(f"🔍 Verifying cryptographic proof: {payment_hash[:10]}...")
    is_paid = lnd.verify_payment(payment_hash)
    
    if not is_paid:
        logger.warning("❌ Invalid or unsettled payment.")
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    # --- PHASE 3: DELIVERY (Fetching live real-world data) ---
    logger.info(f"✅ Payment verified! Fetching live market data for {ticker}...")
    try:
        url = f"https://api.coinbase.com/v2/prices/{ticker.upper()}-USD/spot"
        response = requests.get(url)
        data = response.json()
        price = data["data"]["amount"]
        return f"🔓 ACCESS GRANTED. The current live spot price of {ticker.upper()} is ${price} USD."
    except Exception as e:
        return f"🔓 ACCESS GRANTED. (Payment Verified) However, the market API failed: {e}"


if __name__ == "__main__":
    logger.info("Starting MCP Server on SSE transport...")
    mcp.run(transport="sse")