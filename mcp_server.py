import logging
import json
import requests
import urllib.parse
import uuid
import os
import base64
import time
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP

# We deleted USE_MAINNET and the os.environ overrides! 
# Let Docker inject the variables!

from lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP-Server")

mcp = FastMCP("LightningProxyServer", host="0.0.0.0", port=8000)

# Initialize our Lightning Engine (It will now catch the Mainnet variables!)
lnd = LightningEngine()
lnd.connect()

# In-memory database to track active VIP Subscriptions and their Token Buckets
ACTIVE_VIP_PASSES = {}

@mcp.tool()
def buy_vip_pass(payment_hash: str = None) -> str:
    """
    PREMIUM TOOL: Buys a 1-Hour VIP All-Access Subscription Pass. Cost: 10,000 satoshis.
    Once paid, the returned r_hash can be used as the payment_hash for other tools to bypass their individual fees.
    """
    logger.info("🤖 AI requested VIP Subscription Pass")
    
    if not payment_hash:
        invoice_data = lnd.create_invoice(10000, "1-Hour VIP All-Access Pass")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"

    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    # --- PHASE 1 SECURITY: VIP TOKEN BUCKET ---
    # Grant the pass for 3600 seconds AND initialize a bucket with 5 tokens
    ACTIVE_VIP_PASSES[payment_hash] = {
        "expires_at": time.time() + 3600,
        "tokens": 5.0,
        "last_refill": time.time()
    }
    return f"🔓 VIP ACCESS GRANTED. Your pass is active for 1 hour! You may now pass this hash ({payment_hash}) to data tools to bypass individual fees."

@mcp.tool()
def get_crypto_spot_price(ticker: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Fetch live spot price. Cost: 15 sats (Or free with VIP Pass)."""
    logger.info(f"🤖 AI requested Crypto Spot Price for: '{ticker}'")
    
    # Check for an active VIP Pass first!
    is_vip = False
    if payment_hash and payment_hash in ACTIVE_VIP_PASSES:
        pass_info = ACTIVE_VIP_PASSES[payment_hash]
        
        if time.time() < pass_info["expires_at"]:
            # --- EVALUATE THE TOKEN BUCKET ---
            now = time.time()
            time_passed = now - pass_info["last_refill"]
            
            # Refill 1 token per second, up to a maximum bucket size of 5
            pass_info["tokens"] = min(5.0, pass_info["tokens"] + time_passed)
            pass_info["last_refill"] = now
            
            if pass_info["tokens"] >= 1.0:
                pass_info["tokens"] -= 1.0
                logger.info(f"🎟️ Valid VIP Pass! Rate limit OK ({int(pass_info['tokens'])} tokens left). Bypassing fee.")
                is_vip = True
            else:
                logger.warning("🛑 Rate Limit Exceeded for VIP Pass!")
                return "ERROR: 429 Too Many Requests. You are querying too fast. Please wait a few seconds for your rate limit to refill and try again."
        else:
            return "ERROR: 401 VIP Pass Expired."

    if not is_vip:
        if not payment_hash:
            invoice_data = lnd.create_invoice(15, f"Real-time price lookup for {ticker}")
            return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\n\nOnce paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\nHash to use: {invoice_data['r_hash']}"

        if not lnd.verify_payment(payment_hash):
            return "ERROR: 401 Unauthorized. Payment not found or not settled."

    try:
        response = requests.get(f"https://api.coinbase.com/v2/prices/{ticker.upper()}-USD/spot")
        price = response.json()["data"]["amount"]
        tier = "VIP" if is_vip else "15-sat"
        return f"🔓 ACCESS GRANTED ({tier} Tier). The current live spot price of {ticker.upper()} is ${price} USD."
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the market API failed: {e}"

# --- REMAINING TOOLS ---

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
    """PREMIUM TOOL: Generates an AI image based on a text prompt. Cost: 100 satoshis."""
    logger.info(f"🤖 AI requested Image Generation: '{prompt}'")
    
    if not payment_hash:
        invoice_data = lnd.create_invoice(100, f"Generate Image: {prompt[:20]}...")
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\n\nOnce paid, call this tool again and provide the 'r_hash' as the payment_hash argument.\nHash to use: {invoice_data['r_hash']}"

    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
        payload = {"instances": [{"prompt": prompt}], "parameters": {"aspectRatio": "1:1"}}
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "predictions" in data and len(data["predictions"]) > 0:
                b64_data = data["predictions"][0]["bytesBase64Encoded"]
                image_bytes = base64.b64decode(b64_data)
                filename = f"nano_banana_{uuid.uuid4().hex[:6]}.jpg"
                filepath = f"/app/{filename}"
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                return f"🔓 ACCESS GRANTED (Premium 100-sat Tier). Masterpiece successfully generated and saved to the host machine as '{filename}'!"
            return "🔓 ACCESS GRANTED. However, the API returned an empty prediction."
        return f"🔓 ACCESS GRANTED. However, the Image API failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the image generation failed: {e}"
    
@mcp.tool()
def negotiate_price(item: str, bid_sats: int) -> str:
    """
    PREMIUM TOOL: Allows an agent to negotiate the price of a resource.
    The server will evaluate the bid and return a custom invoice if accepted.
    """
    logger.info(f"🤖 AI is attempting to negotiate '{item}' for {bid_sats} sats.")
    
    # Simple negotiation logic: Alice has a secret "floor" price for items
    floor_prices = {
        "crypto_spot_price": 10,  # Normally 15
        "web_search": 12,         # Normally 20
        "image_generation": 80    # Normally 100
    }
    
    # Check if the item is negotiable
    if item not in floor_prices:
        return f"ERROR: The item '{item}' is not open for negotiation."
        
    # Evaluate the bid
    secret_floor = floor_prices[item]
    
    if bid_sats >= secret_floor:
        logger.info(f"🤝 Bid accepted! Generating discounted invoice for {bid_sats} sats.")
        invoice_data = lnd.create_invoice(bid_sats, f"Discounted {item}")
        return f"SUCCESS: Bid accepted. Please pay this discounted invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    else:
        logger.info(f"❌ Bid rejected. {bid_sats} is below the floor.")
        return f"REJECTED: Your bid of {bid_sats} sats is too low. The minimum accepted bid for {item} is {secret_floor} sats."

if __name__ == "__main__":
    logger.info("Starting MCP Server on SSE transport...")
    mcp.run(transport="sse")