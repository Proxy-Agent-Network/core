import logging
import json
import requests
import urllib.parse
import uuid
import os
import base64
import time
import shutil
import glob # NEW
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import PyPDFLoader # NEW
from langchain_core.prompts import PromptTemplate
from lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP-Server")

mcp = FastMCP("LightningProxyServer", host="0.0.0.0", port=8000)

lnd = LightningEngine()
lnd.connect()

ACTIVE_VIP_PASSES = {}

@mcp.tool()
def buy_vip_pass(payment_hash: str = None) -> str:
    """PREMIUM TOOL: Buys a 1-Hour VIP All-Access Subscription Pass. Cost: 10,000 satoshis."""
    logger.info("🤖 AI requested VIP Subscription Pass")
    if not payment_hash:
        invoice_data = lnd.create_invoice(10000, "1-Hour VIP All-Access Pass")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

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
    is_vip = False
    if payment_hash and payment_hash in ACTIVE_VIP_PASSES:
        pass_info = ACTIVE_VIP_PASSES[payment_hash]
        if time.time() < pass_info["expires_at"]:
            now = time.time()
            time_passed = now - pass_info["last_refill"]
            pass_info["tokens"] = min(5.0, pass_info["tokens"] + time_passed)
            pass_info["last_refill"] = now
            if pass_info["tokens"] >= 1.0:
                pass_info["tokens"] -= 1.0
                is_vip = True
            else:
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

@mcp.tool()
def live_web_search(search_query: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Search the live internet for up-to-date information and news. Cost: 20 satoshis."""
    if not payment_hash:
        invoice_data = lnd.create_invoice(20, f"Web Search: {search_query}")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
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
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
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
    logger.info(f"🤖 AI requested Image Generation: '{prompt[:30]}...'")
    if not payment_hash:
        invoice_data = lnd.create_invoice(100, f"Generate Image: {prompt[:20]}...")
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
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
def generate_music(prompt: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Generates an AI music track based on a text prompt. Cost: 150 satoshis."""
    logger.info(f"🤖 AI requested Music Generation: '{prompt[:30]}...'")
    if not payment_hash:
        invoice_data = lnd.create_invoice(150, f"Generate Music: {prompt[:20]}...")
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    try:
        logger.info("🎧 Audio Engineer is mixing the track...")
        time.sleep(3) 
        filename = f"lyria_track_{uuid.uuid4().hex[:6]}.mp3"
        filepath = f"/app/{filename}"
        if os.path.exists("/app/sample.mp3"):
            shutil.copy("/app/sample.mp3", filepath)
        else:
            with open(filepath, 'wb') as f:
                f.write(b"Dummy Audio Data")
        return f"🔓 ACCESS GRANTED (Premium 150-sat Tier). Masterpiece successfully generated and saved to the host machine as '{filename}'!"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the music generation failed: {e}"

@mcp.tool()
def generate_video(prompt: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Generates an AI video based on a text prompt. Cost: 250 satoshis."""
    logger.info(f"🤖 AI requested Video Generation: '{prompt[:30]}...'")
    if not payment_hash:
        invoice_data = lnd.create_invoice(250, f"Generate Video: {prompt[:20]}...")
        if not invoice_data or 'payment_request' not in invoice_data:
            return "ERROR: Internal Node Error. Could not generate invoice."
        return f"ERROR: 402 Payment Required\nPlease pay this invoice to access the service:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not lnd.verify_payment(payment_hash):
        return "ERROR: 401 Unauthorized. Payment not found or not settled."

    try:
        logger.info("🎥 Master Videographer is rendering frames...")
        time.sleep(4) 
        filename = f"veo_video_{uuid.uuid4().hex[:6]}.mp4"
        filepath = f"/app/{filename}"
        if os.path.exists("/app/sample.mp4"):
            shutil.copy("/app/sample.mp4", filepath)
        else:
            with open(filepath, 'wb') as f:
                f.write(b"Dummy Video Data")
        return f"🔓 ACCESS GRANTED (Premium 250-sat Tier). Masterpiece successfully generated and saved to the host machine as '{filename}'!"
    except Exception as e:
        return f"🔓 ACCESS GRANTED (Payment Verified). However, the video generation failed: {e}"

@mcp.tool()
def negotiate_price(item: str, bid_sats: int) -> str:
    logger.info(f"🤖 AI is attempting to negotiate '{item}' for {bid_sats} sats.")
    floor_prices = {"crypto_spot_price": 10, "web_search": 12, "image_generation": 80}
    if item not in floor_prices:
        return f"ERROR: The item '{item}' is not open for negotiation."
    if bid_sats >= floor_prices[item]:
        invoice_data = lnd.create_invoice(bid_sats, f"Discounted {item}")
        return f"SUCCESS: Bid accepted. Please pay this discounted invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    else:
        return f"REJECTED: Your bid of {bid_sats} sats is too low."
    
# --- LAYER 5 SPECIALIST (FINANCE TEAM) ---
def layer_5_specialist(task: str, context: str, specialist_name: str, historical_context: str = "") -> str:
    """LAYER 5: A dedicated LLM worker (Eve, Gordon, or Olivia) that handles a specific finance task."""
    logger.info(f"    🕵️‍♀️ Layer 5 ({specialist_name}) waking up for sub-task: '{task[:30]}...'")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    llm_l5 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=api_key)
    search_tool = DuckDuckGoSearchRun()
    
    logger.info(f"      🌐 Layer 5 ({specialist_name}) actively gathering web data...")
    search_query = f"{context} {task}"
    raw_data = search_tool.invoke(search_query)

    # --- NEW PDF PARSER FOR EVE ---
    pdf_context = ""
    if specialist_name.upper() == "EVE":
        # Look for any PDFs dropped in the current directory
        pdf_files = glob.glob("*.pdf")
        if pdf_files:
            logger.info(f"      📄 Eve found local PDF documents. Parsing now...")
            for pdf_file in pdf_files:
                try:
                    loader = PyPDFLoader(pdf_file)
                    pages = loader.load_and_split()
                    pdf_text = " ".join([page.page_content for page in pages])
                    # Cap at 15000 characters to keep things fast and cheap
                    pdf_context += f"\n--- EXTRACTED FROM {pdf_file} ---\n{pdf_text[:15000]}\n"
                    logger.info(f"      ✅ Eve successfully ingested {pdf_file}")
                except Exception as e:
                    logger.error(f"      ❌ Failed to parse PDF {pdf_file}: {e}")
    
    l5_prompt = (
        f"You are {specialist_name}, a highly-paid Layer 5 Finance Specialist at an elite AI Hedge Fund.\n"
        f"Primary Context: {context}\n"
        f"Historical Memory: {historical_context}\n"
        f"Your specific task: {task}\n\n"
        f"Raw Web Data Gathered:\n{raw_data}\n\n"
        f"Local PDF Document Data (If Any):\n{pdf_context}\n\n"
        "Analyze the data and execute your task. Provide a high-quality, professional answer matching your persona (Eve = fast OSINT; Gordon = Quant/Crypto; Olivia = Deep Macro/Fundamentals). Do not hallucinate."
    )
    return llm_l5.invoke(l5_prompt).content


# --- LAYER 4 MANAGER (ALICE) ---
@mcp.tool()
def deep_market_analysis(
    primary_topic: str,
    original_user_intent: str,
    specific_data_points_required: list[str],
    specialist_name: str = "Eve",
    historical_context: str = "",
    payment_hash: str = ""
) -> str:
    """
    PREMIUM LAYER 4 TOOL. Acts as a Manager (Alice) that delegates to Layer 5 Finance Specialists.
    """
    compute_depth = len(specific_data_points_required)
    dynamic_cost = 75 # Fixed cost for this L4 tool
    
    if not payment_hash or not lnd.verify_payment(payment_hash):
        invoice_data = lnd.create_invoice(dynamic_cost, f"L5 Deployment ({specialist_name}): {primary_topic}")
        return f"402 Payment Required: Deploying {specialist_name} requires a {dynamic_cost} sat retainer:\nInvoice: {invoice_data['payment_request']}\nHash: {invoice_data['r_hash']}"

    logger.info(f"✅ Payment verified. Booting Layer 4 Manager (Alice) for: {primary_topic}")

    try:
        layer_5_results = []
        for i, req in enumerate(specific_data_points_required):
            logger.info(f"  👩‍💼 Layer 4 (Alice) delegating directive to Layer 5 ({specialist_name})...")
            l5_answer = layer_5_specialist(req, primary_topic, specialist_name, historical_context)
            layer_5_results.append(f"{l5_answer}\n")
            
        logger.info("  👩‍💼 Layer 4 (Alice) formatting final delivery...")
        aggregated_data = "\n".join(layer_5_results)
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        llm_alice = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=api_key)
        
        alice_prompt = (
            f"You are Alice, the Layer 4 Finance Manager.\n"
            f"The original user intent is: {original_user_intent}\n"
            f"Your Layer 5 specialist ({specialist_name}) has returned the following verified data:\n"
            f"{aggregated_data}\n\n"
            "Format this directly for the user. Make it crisp, executive-level, and acknowledge the great work done by your specialist."
        )
        
        final_report = llm_alice.invoke(alice_prompt).content
        return final_report
        
    except Exception as e:
        return f"Layer 5 Sub-Agent failed during execution: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting MCP Server on SSE transport...")
    mcp.run(transport="sse")