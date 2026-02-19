import logging
import json
import requests
from duckduckgo_search import DDGS
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
    """
    logger.info("🤖 AI requested Agent Description Manifest")
    
    agent_pubkey = getattr(lnd, 'pubkey', 'OFFLINE')
    
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
            "get_crypto_spot_price",
            "generate_market_summary",
            "live_web_search"
        ]
    }
    
    return json.dumps(manifest, indent=2)

@mcp.tool()
def get_crypto_spot_price(ticker: str, payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Fetch the real-time spot price of a cryptocurrency from live markets.
    Cost: 15 satoshis.
    """
    logger.info(f"🤖 AI requested Crypto Spot Price for: '{ticker}'")
    
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

    logger.info(f"🔍 Verifying cryptographic proof: {payment_hash[:10]}...")
    is_paid = lnd.verify_payment(payment_hash)
    
    if not is_paid:
        logger.warning("❌ Invalid or unsettled payment.")
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    logger.info(f"✅ Payment verified! Fetching live market data for {ticker}...")
    try:
        url = f"https://api.coinbase.com/v2/prices/{ticker.upper()}-USD/spot"
        response = requests.get(url)
        data = response.json()
        price = data["data"]["amount"]
        return f"🔓 ACCESS GRANTED. The current live spot price of {ticker.upper()} is ${price} USD."
    except Exception as e:
        return f"🔓 ACCESS GRANTED. (Payment Verified) However, the market API failed: {e}"

@mcp.tool()
def generate_market_summary(asset: str, payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Generates a deep-dive market analysis report.
    Cost: 50 satoshis.
    """
    logger.info(f"🤖 AI requested Market Summary for: '{asset}'")
    
    if not payment_hash:
        logger.info(f"⚠️ No payment provided for summary of {asset}. Issuing 50-sat L402 Challenge.")
        invoice_data = lnd.create_invoice(50, f"Deep Market Analysis for {asset}")
        
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
            
        return (f"ERROR: 402 Payment Required\n"
                f"Please pay this invoice to access the service:\n"
                f"Invoice: {invoice_data['payment_request']}\n\n"
                f"Once paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\n"
                f"Hash to use: {invoice_data['r_hash']}")

    logger.info(f"🔍 Verifying 50-sat cryptographic proof: {payment_hash[:10]}...")
    is_paid = lnd.verify_payment(payment_hash)
    
    if not is_paid:
        logger.warning("❌ Invalid or unsettled payment.")
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    logger.info(f"✅ 50-sat Payment verified! Generating report...")
    return (f"🔓 ACCESS GRANTED (Premium 50-sat Tier).\n"
            f"--- Market Analysis for {asset.upper()} ---\n"
            f"Volatility is currently low. Moving averages suggest a strong consolidation phase.\n"
            f"Recommendation: HOLD.")

@mcp.tool()
def live_web_search(search_query: str, payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Search the live internet for up-to-date information and news.
    Cost: 20 satoshis.
    """
    logger.info(f"🤖 AI requested Live Web Search for: '{search_query}'")
    
    # --- PHASE 1: L402 PAYMENT REQUIRED (20 Sats) ---
    if not payment_hash:
        logger.info(f"⚠️ No payment provided for search. Issuing 20-sat L402 Challenge.")
        invoice_data = lnd.create_invoice(20, f"Web Search: {search_query}")
        
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
            
        return (f"ERROR: 402 Payment Required\n"
                f"Please pay this invoice to access the service:\n"
                f"Invoice: {invoice_data['payment_request']}\n\n"
                f"Once paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\n"
                f"Hash to use: {invoice_data['r_hash']}")

    # --- PHASE 2: VERIFICATION ---
    logger.info(f"🔍 Verifying 20-sat cryptographic proof: {payment_hash[:10]}...")
    is_paid = lnd.verify_payment(payment_hash)
    
    if not is_paid:
        logger.warning("❌ Invalid or unsettled payment.")
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    # --- PHASE 3: DELIVERY ---
    logger.info(f"✅ 20-sat Payment verified! Searching the web...")
    try:
        results = DDGS().text(search_query, max_results=3)
        formatted_results = "\n\n".join([f"📰 {res['title']}\n{res['body']}" for res in results])
        return f"🔓 ACCESS GRANTED (Premium 20-sat Tier).\n--- Top Web Results for '{search_query}' ---\n{formatted_results}"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the search engine failed: {e}"
    
@mcp.tool()
def send_urgent_notification(message: str, payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Sends an urgent push notification directly to the user's phone.
    Cost: 250 satoshis.
    """
    logger.info(f"🤖 AI requested Notification: '{message}'")
    
    # --- PHASE 1: L402 PAYMENT REQUIRED (250 Sats) ---
    if not payment_hash:
        logger.info(f"⚠️ No payment provided for notification. Issuing 250-sat L402 Challenge.")
        invoice_data = lnd.create_invoice(250, "Send Urgent Phone Notification")
        
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
            
        return (f"ERROR: 402 Payment Required\n"
                f"Please pay this invoice to access the service:\n"
                f"Invoice: {invoice_data['payment_request']}\n\n"
                f"Once paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\n"
                f"Hash to use: {invoice_data['r_hash']}")

    # --- PHASE 2: VERIFICATION ---
    logger.info(f"🔍 Verifying 250-sat cryptographic proof: {payment_hash[:10]}...")
    is_paid = lnd.verify_payment(payment_hash)
    
    if not is_paid:
        logger.warning("❌ Invalid or unsettled payment.")
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    # --- PHASE 3: DELIVERY ---
    logger.info(f"✅ 250-sat Payment verified! Pinging the user's phone...")
    try:
        CHANNEL_NAME = "robers_l402_alerts"
        requests.post(f"https://ntfy.sh/{CHANNEL_NAME}", 
                      data=message.encode('utf-8'),
                      headers={
                          "Title": "L402 Agent Alert", # <-- FIX: Removed the emoji here!
                          "Priority": "high",
                          "Tags": "moneybag,robot"
                      })
        return f"🔓 ACCESS GRANTED (Premium 250-sat Tier). The message was successfully sent to the user's phone!"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the notification server failed: {e}"

if __name__ == "__main__":
    logger.info("Starting MCP Server on SSE transport...")
    mcp.run(transport="sse")