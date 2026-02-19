import logging
import json
import requests
import urllib.parse
import uuid
import os
import base64
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP
from lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP-Server")

mcp = FastMCP("LightningProxyServer", host="0.0.0.0", port=8000)

# Initialize our Lightning Engine
lnd = LightningEngine()
lnd.connect()

@mcp.tool()
def create_lightning_invoice(amount_sats: int, memo: str) -> str:
    """Creates a Lightning Network invoice for a specified amount of satoshis."""
    logger.info(f"🤖 AI requested invoice: {amount_sats} sats for '{memo}'")
    try:
        result = lnd.create_invoice(amount_sats, memo)
        if result and 'payment_request' in result:
            return f"✅ Invoice created successfully!\nPayment Request (BOLT11): {result['payment_request']}\nHash: {result['r_hash']}"
        else:
            return "❌ Failed to create invoice. The LND node might be disconnected."
    except Exception as e:
        return f"❌ Error creating invoice: {str(e)}"
    
@mcp.tool()
def get_node_balances() -> str:
    """Checks the current balance of the Lightning node."""
    logger.info("🤖 AI requested node balances")
    balances = lnd.get_balances()
    if balances:
        return f"💰 Node Balances:\nOn-Chain Wallet: {balances['onchain_sats']} sats\nLightning Channels: {balances['channel_sats']} sats\nPending Channels: {balances['pending_channel_sats']} sats"
    else:
        return "❌ Failed to fetch balances. The LND node might be disconnected."

@mcp.tool()
def get_agent_manifest() -> str:
    """Returns semantic information about this agent, its routing identity, and its pricing."""
    logger.info("🤖 AI requested Agent Description Manifest")
    agent_pubkey = getattr(lnd, 'pubkey', 'OFFLINE')
    manifest = {
        "agent_name": "Lightning Proxy Node Alpha",
        "agent_role": "Payment & Tool Proxy",
        "network_environment": "regtest",
        "identity": {"lnd_pubkey": agent_pubkey, "supported_protocols": ["MCP", "BOLT11"]},
        "pricing": {"base_fee_sats": 10, "currency": "satoshi", "negotiable": False},
        "capabilities": ["create_lightning_invoice", "get_node_balances", "get_agent_manifest", "get_crypto_spot_price", "generate_market_summary", "live_web_search", "send_urgent_notification", "generate_image"]
    }
    return json.dumps(manifest, indent=2)

@mcp.tool()
def get_crypto_spot_price(ticker: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Fetch the real-time spot price of a cryptocurrency from live markets. Cost: 15 satoshis."""
    logger.info(f"🤖 AI requested Crypto Spot Price for: '{ticker}'")
    if not payment_hash:
        invoice_data = lnd.create_invoice(15, f"Real-time price lookup for {ticker}")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\n\nOnce paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\nHash to use: {invoice_data['r_hash']}"

    is_paid = lnd.verify_payment(payment_hash)
    if not is_paid:
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    try:
        response = requests.get(f"https://api.coinbase.com/v2/prices/{ticker.upper()}-USD/spot")
        price = response.json()["data"]["amount"]
        return f"🔓 ACCESS GRANTED. The current live spot price of {ticker.upper()} is ${price} USD."
    except Exception as e:
        return f"🔓 ACCESS GRANTED. (Payment Verified) However, the market API failed: {e}"

@mcp.tool()
def generate_market_summary(asset: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Generates a deep-dive market analysis report. Cost: 50 satoshis."""
    if not payment_hash:
        invoice_data = lnd.create_invoice(50, f"Deep Market Analysis for {asset}")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\n\nOnce paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\nHash to use: {invoice_data['r_hash']}"

    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    return f"🔓 ACCESS GRANTED (Premium 50-sat Tier).\n--- Market Analysis for {asset.upper()} ---\nVolatility is currently low. Moving averages suggest a strong consolidation phase.\nRecommendation: HOLD."

@mcp.tool()
def live_web_search(search_query: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Search the live internet for up-to-date information and news. Cost: 20 satoshis."""
    if not payment_hash:
        invoice_data = lnd.create_invoice(20, f"Web Search: {search_query}")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\n\nOnce paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\nHash to use: {invoice_data['r_hash']}"

    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    try:
        results = DDGS().text(search_query, max_results=3)
        formatted_results = "\n\n".join([f"📰 {res['title']}\n{res['body']}" for res in results])
        return f"🔓 ACCESS GRANTED (Premium 20-sat Tier).\n--- Top Web Results for '{search_query}' ---\n{formatted_results}"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the search engine failed: {e}"

@mcp.tool()
def send_urgent_notification(message: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Sends an urgent push notification directly to the user's phone. Cost: 250 satoshis."""
    if not payment_hash:
        invoice_data = lnd.create_invoice(250, "Send Urgent Phone Notification")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\n\nOnce paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\nHash to use: {invoice_data['r_hash']}"

    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    try:
        CHANNEL_NAME = "robers_l402_alerts"
        requests.post(f"https://ntfy.sh/{CHANNEL_NAME}", data=message.encode('utf-8'), headers={"Title": "L402 Agent Alert", "Priority": "high", "Tags": "moneybag,robot"})
        return f"🔓 ACCESS GRANTED (Premium 250-sat Tier). The message was successfully sent to the user's phone!"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the notification server failed: {e}"

@mcp.tool()
def generate_image(prompt: str, payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Generates a high-quality AI image based on a text prompt and saves it to the local machine.
    Cost: 100 satoshis.
    """
    logger.info(f"🤖 AI requested Image Generation: '{prompt}'")
    
    if not payment_hash:
        logger.info(f"⚠️ No payment provided. Issuing 100-sat L402 Challenge.")
        invoice_data = lnd.create_invoice(100, f"Generate Image: {prompt[:20]}...")
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\n\nOnce paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\nHash to use: {invoice_data['r_hash']}"

    logger.info(f"🔍 Verifying 100-sat cryptographic proof: {payment_hash[:10]}...")
    if not lnd.verify_payment(payment_hash):
        logger.warning("❌ Invalid or unsettled payment.")
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    logger.info(f"✅ 100-sat Payment verified! Generating image via Nano Banana...")
    try:
        # Pull the secure key that was mapped in docker-compose.yml
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
             return "ERROR: API Key missing from environment!"

        # FIX: Updated to the new Imagen 4.0 endpoint!
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {"aspectRatio": "1:1"}
        }
        
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "predictions" in data and len(data["predictions"]) > 0:
                # Decode the raw image bytes from Google's response
                b64_data = data["predictions"][0]["bytesBase64Encoded"]
                image_bytes = base64.b64decode(b64_data)
                
                # Save it to the shared Docker volume
                filename = f"nano_banana_{uuid.uuid4().hex[:6]}.jpg"
                filepath = f"/app/{filename}"
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                return f"🔓 ACCESS GRANTED (Premium 100-sat Tier). Masterpiece successfully generated and saved to the host machine as '{filename}'!"
            else:
                return "🔓 ACCESS GRANTED. However, the API returned an empty prediction."
        else:
            return f"🔓 ACCESS GRANTED. However, the Image API failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the image generation failed: {e}"

if __name__ == "__main__":
    logger.info("Starting MCP Server on SSE transport...")
    mcp.run(transport="sse")