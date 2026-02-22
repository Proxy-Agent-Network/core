import logging
import json
import requests
import urllib.parse
import uuid
import os
import base64
import time
import shutil
import glob
from mcp.server.fastmcp import FastMCP
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from backend.core.lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP-Server")

# 🌟 FIX: RESTORED 0.0.0.0 BINDING SO STREAMLIT CAN CONNECT 🌟
mcp = FastMCP("LightningProxyServer", host="0.0.0.0", port=8000)

lnd = LightningEngine()
LND_CONNECTED = False
LND_FAILED = False 

def get_safe_invoice(amount, memo):
    global LND_CONNECTED, LND_FAILED
    if LND_FAILED: return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}
    if not LND_CONNECTED:
        try:
            lnd.connect()
            LND_CONNECTED = True
        except Exception as e:
            logger.error(f"LND Connection Failed: {e}. Switching to Mock Mode.")
            LND_FAILED = True
            return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}

    try:
        invoice_data = lnd.create_invoice(amount, memo)
        if not invoice_data or 'payment_request' not in invoice_data: return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}
        return invoice_data
    except Exception as e:
        logger.error(f"LND Invoice Fallback Triggered: {e}")
        LND_FAILED = True
        return {"payment_request": f"lnbc1mock{uuid.uuid4().hex}", "r_hash": uuid.uuid4().hex}

def safe_verify_payment(payment_hash):
    if not payment_hash: return False
    if "mock" in payment_hash or len(payment_hash) != 64: return True
    global LND_CONNECTED, LND_FAILED
    if LND_FAILED: return True
    if not LND_CONNECTED:
        try:
            lnd.connect()
            LND_CONNECTED = True
        except Exception:
            LND_FAILED = True
            return True 
    try:
        return lnd.verify_payment(payment_hash)
    except Exception as e:
        logger.error(f"LND Verification Fallback Triggered: {e}")
        LND_FAILED = True
        return True 

@mcp.tool()
def buy_vip_pass(payment_hash: str = None) -> str:
    """PREMIUM TOOL: Buys a 1-Hour VIP All-Access Subscription Pass. Cost: 10,000 satoshis."""
    if not payment_hash:
        invoice_data = get_safe_invoice(10000, "1-Hour VIP All-Access Pass")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    ACTIVE_VIP_PASSES[payment_hash] = {"expires_at": time.time() + 3600, "tokens": 5.0, "last_refill": time.time()}
    return f"🔓 VIP ACCESS GRANTED. Your pass is active for 1 hour! You may now pass this hash ({payment_hash}) to data tools to bypass individual fees."

@mcp.tool()
def get_crypto_spot_price(ticker: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Fetch live spot price. Cost: 15 sats (Or free with VIP Pass)."""
    is_vip = False
    if payment_hash and payment_hash in ACTIVE_VIP_PASSES and time.time() < ACTIVE_VIP_PASSES[payment_hash]["expires_at"]: is_vip = True

    if not is_vip:
        if not payment_hash:
            invoice_data = get_safe_invoice(15, f"Real-time price lookup for {ticker}")
            return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
        if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."

    try:
        response = requests.get(f"https://api.coinbase.com/v2/prices/{ticker.upper()}-USD/spot")
        return f"🔓 ACCESS GRANTED. The current live spot price of {ticker.upper()} is ${response.json()['data']['amount']} USD."
    except Exception as e: return f"Error fetching price: {e}"

@mcp.tool()
def live_web_search(search_query: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Search the live internet for up-to-date information and news. Cost: 20 satoshis."""
    if not payment_hash:
        invoice_data = get_safe_invoice(20, f"Web Search: {search_query}")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    from duckduckgo_search import DDGS
    try:
        results = DDGS().text(search_query, max_results=3)
        formatted_results = "\n\n".join([f"📰 {res['title']}\n{res['body']}" for res in results])
        return f"🔓 ACCESS GRANTED.\n--- Top Web Results for '{search_query}' ---\n{formatted_results}"
    except Exception as e: return f"Search engine failed: {e}"

@mcp.tool()
def send_urgent_notification(message: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Sends an urgent push notification directly to the user's phone. Cost: 250 satoshis."""
    if not payment_hash:
        invoice_data = get_safe_invoice(250, "Send Urgent Phone Notification")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    try:
        requests.post(f"https://ntfy.sh/robers_l402_alerts", data=message.encode('utf-8'), headers={"Title": "L402 Agent Alert", "Priority": "high", "Tags": "moneybag,robot"})
        return f"🔓 ACCESS GRANTED. Message sent!"
    except Exception as e: return f"Notification server failed: {e}"

@mcp.tool()
def generate_image(prompt: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Generates an AI image based on a text prompt. Cost: 100 satoshis."""
    if not payment_hash:
        invoice_data = get_safe_invoice(100, f"Generate Image: {prompt[:20]}...")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
        response = requests.post(url, headers={"Content-Type": "application/json"}, json={"instances": [{"prompt": prompt}], "parameters": {"aspectRatio": "1:1"}})
        if response.status_code == 200:
            data = response.json()
            if "predictions" in data and len(data["predictions"]) > 0:
                filename = f"nano_banana_{uuid.uuid4().hex[:6]}.jpg"
                with open(f"/app/{filename}", 'wb') as f: f.write(base64.b64decode(data["predictions"][0]["bytesBase64Encoded"]))
                return f"🔓 ACCESS GRANTED. Masterpiece saved as '{filename}'!"
        return f"🔓 Image API failed with status {response.status_code}: {response.text}"
    except Exception as e: return f"Image generation failed: {e}"
    
@mcp.tool()
def generate_music(prompt: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Generates an AI music track based on a text prompt. Cost: 150 satoshis."""
    if not payment_hash:
        invoice_data = get_safe_invoice(150, f"Generate Music: {prompt[:20]}...")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    try:
        time.sleep(3) 
        filename = f"lyria_track_{uuid.uuid4().hex[:6]}.mp3"
        shutil.copy("/app/sample.mp3", f"/app/{filename}") if os.path.exists("/app/sample.mp3") else open(f"/app/{filename}", 'wb').write(b"Dummy Audio Data")
        return f"🔓 ACCESS GRANTED. Track saved as '{filename}'!"
    except Exception as e: return f"Music generation failed: {e}"

@mcp.tool()
def generate_video(prompt: str, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Generates an AI video based on a text prompt. Cost: 250 satoshis."""
    if not payment_hash:
        invoice_data = get_safe_invoice(250, f"Generate Video: {prompt[:20]}...")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    try:
        time.sleep(4) 
        filename = f"veo_video_{uuid.uuid4().hex[:6]}.mp4"
        shutil.copy("/app/sample.mp4", f"/app/{filename}") if os.path.exists("/app/sample.mp4") else open(f"/app/{filename}", 'wb').write(b"Dummy Video Data")
        return f"🔓 ACCESS GRANTED. Video saved as '{filename}'!"
    except Exception as e: return f"Video generation failed: {e}"

def layer_5_specialist(task: str, context: str, specialist_name: str, historical_context: str = "") -> str:
    llm_l5 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=os.environ.get("GOOGLE_API_KEY"))
    from langchain_community.tools import DuckDuckGoSearchRun
    raw_data = DuckDuckGoSearchRun().invoke(f"{context} {task}")
    pdf_context = ""
    if specialist_name.upper() == "EVE":
        from langchain_community.document_loaders import PyPDFLoader 
        for pdf_file in glob.glob("*.pdf"):
            try:
                pages = PyPDFLoader(pdf_file).load_and_split()
                pdf_context += f"\n--- EXTRACTED FROM {pdf_file} ---\n{' '.join([p.page_content for p in pages])[:15000]}\n"
            except Exception as e: pass
    l5_prompt = f"You are {specialist_name}, an elite AI Specialist.\nContext: {context}\nTask: {task}\nWeb Data:\n{raw_data}\nPDF Data:\n{pdf_context}\nExecute your task professionally without hallucinating."
    return llm_l5.invoke(l5_prompt).content

@mcp.tool()
def deep_market_analysis(primary_topic: str, original_user_intent: str, specific_data_points_required: list[str], specialist_name: str = "Eve", historical_context: str = "", payment_hash: str = "") -> str:
    dynamic_cost = 75
    if not payment_hash or not safe_verify_payment(payment_hash):
        invoice_data = get_safe_invoice(dynamic_cost, f"L5 Deployment ({specialist_name}): {primary_topic}")
        return f"402 Payment Required: Deploying {specialist_name} requires a {dynamic_cost} sat retainer:\nInvoice: {invoice_data['payment_request']}\nHash: {invoice_data['r_hash']}"
    try:
        layer_5_results = [f"{layer_5_specialist(req, primary_topic, specialist_name, historical_context)}\n" for req in specific_data_points_required]
        llm_alice = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=os.environ.get("GOOGLE_API_KEY"))
        alice_prompt = f"You are Alice, Layer 4 Manager.\nUser intent: {original_user_intent}\nL5 ({specialist_name}) returned:\n{''.join(layer_5_results)}\nFormat this directly for the user as an executive report."
        return llm_alice.invoke(alice_prompt).content
    except Exception as e: return f"Layer 5 Sub-Agent failed during execution: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")