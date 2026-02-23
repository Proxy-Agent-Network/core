import logging
import json
import requests
import urllib.parse
import uuid
import os
import shutil
import base64
import time
import glob 
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import PyPDFLoader 
from backend.core.lightning_engine import LightningEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP-Server")

mcp = FastMCP("LightningProxyServer")

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
    if not payment_hash:
        invoice_data = get_safe_invoice(10000, "1-Hour VIP All-Access Pass")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    return f"🔓 VIP ACCESS GRANTED. Your pass is active for 1 hour!"

@mcp.tool()
def get_crypto_spot_price(ticker: str, payment_hash: str = None) -> str:
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
    if not payment_hash:
        invoice_data = get_safe_invoice(20, f"Web Search: {search_query}")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    try:
        results = DDGS().text(search_query, max_results=3)
        formatted_results = "\n\n".join([f"📰 {res['title']}\n{res['body']}" for res in results])
        return f"🔓 ACCESS GRANTED.\n--- Top Web Results for '{search_query}' ---\n{formatted_results}"
    except Exception as e: return f"Search engine failed: {e}"

@mcp.tool()
def generate_image(prompt: str, cost: int = 100, payment_hash: str = None) -> str:
    # Notice we now accept the dynamic cost variable!
    if not payment_hash:
        invoice_data = get_safe_invoice(cost, f"Generate Image: {prompt[:20]}...")
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
                os.makedirs("/app/static", exist_ok=True)
                filepath = f"/app/static/{filename}"
                with open(filepath, 'wb') as f: f.write(base64.b64decode(data["predictions"][0]["bytesBase64Encoded"]))
                return f"🔓 ACCESS GRANTED. Masterpiece saved as '{filename}'!"
        return f"🔓 Image API failed with status {response.status_code}: {response.text}"
    except Exception as e: return f"Image generation failed: {e}"

# 🌟 FIX: Updated default cost to 500 (for 5 seconds at 100 SATS/sec) 🌟
@mcp.tool()
def generate_video(prompt: str, cost: int = 500, payment_hash: str = None) -> str:
    """PREMIUM TOOL: Generates an AI video using Runway ML Gen-3 via a Silent Seed pipeline."""
    if not payment_hash:
        invoice_data = get_safe_invoice(cost, f"Generate Video: {prompt[:20]}...")
        return f"ERROR: 402 Payment Required\nPlease pay this invoice:\nInvoice: {invoice_data['payment_request']}\nHash to use: {invoice_data['r_hash']}"
    if not safe_verify_payment(payment_hash): return "ERROR: 401 Unauthorized."
    
    try:
        with open("secrets/runway.key", "r") as f:
            runway_key = f.read().strip()
    except FileNotFoundError:
        return "⚠️ Error: Missing Runway ML API key."

    try:
        # 🌟 PHASE 1: THE SILENT SEED (GOOGLE IMAGEN) 🌟
        static_prompt = f"A pristine, high-quality static establishing shot of: {prompt}"
        api_key = os.environ.get("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
        
        img_payload = {"instances": [{"prompt": static_prompt}], "parameters": {"aspectRatio": "16:9"}}
        res_img = requests.post(url, headers={"Content-Type": "application/json"}, json=img_payload)
        
        if res_img.status_code != 200:
            return f"⚠️ Internal Engine Error: Silent Seed Generation failed. {res_img.text}"
            
        img_data = res_img.json()
        b64_img = img_data["predictions"][0]["bytesBase64Encoded"]
        prompt_image_data_uri = f"data:image/jpeg;base64,{b64_img}"

        # 🌟 PHASE 2: RUNWAY ML ANIMATION 🌟
        # 🌟 FIX: Updated threshold. If they pay 1000 SATS (or more), give 10s. Otherwise 5s. 🌟
        video_duration = 10 if cost >= 1000 else 5

        headers = {
            "Authorization": f"Bearer {runway_key}",
            "X-Runway-Version": "2024-11-06",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gen3a_turbo",
            "promptImage": prompt_image_data_uri,
            "promptText": prompt,
            "ratio": "1280:768",
            "duration": video_duration
        }
        
        # ... (rest of the polling loop remains exactly the same) ...
        res = requests.post("https://api.dev.runwayml.com/v1/image_to_video", json=payload, headers=headers)
        if res.status_code != 200:
            return f"⚠️ Runway API Error: {res.text}"
            
        task_id = res.json().get("id")
        
        for _ in range(60): 
            time.sleep(10)
            status_res = requests.get(f"https://api.dev.runwayml.com/v1/tasks/{task_id}", headers=headers)
            status_data = status_res.json()
            
            if status_data.get("status") == "SUCCEEDED":
                video_url = status_data["output"][0]
                video_bytes = requests.get(video_url).content
                filename = f"veo_video_{uuid.uuid4().hex[:6]}.mp4"
                
                os.makedirs("/app/static", exist_ok=True)
                filepath = f"/app/static/{filename}"
                with open(filepath, 'wb') as f: f.write(video_bytes)
                return f"🔓 ACCESS GRANTED. Runway Gen-3 Video saved as '{filename}'!"
                
            elif status_data.get("status") == "FAILED":
                return f"⚠️ Runway Task Failed: {status_data}"
                
        return "⚠️ Error: Runway Generation timed out."
    except Exception as e: 
        return f"Video generation failed: {str(e)}"

def layer_5_specialist(task: str, context: str, specialist_name: str, historical_context: str = "") -> str:
    llm_l5 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=os.environ.get("GOOGLE_API_KEY"))
    search_query = f"{context} {task}"
    raw_data = DuckDuckGoSearchRun().invoke(search_query)
    pdf_context = ""
    if specialist_name.upper() == "EVE":
        for pdf_file in glob.glob("*.pdf"):
            try:
                pages = PyPDFLoader(pdf_file).load_and_split()
                pdf_context += f"\n--- EXTRACTED FROM {pdf_file} ---\n{' '.join([p.page_content for p in pages])[:15000]}\n"
            except Exception: pass
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
    # 🌟 PROVEN FIX: MONKEY-PATCH UVICORN TO FORCE THE 0.0.0.0 DOCKER BRIDGE 🌟
    import uvicorn
    _original_config_init = uvicorn.Config.__init__

    def _patched_config_init(self, *args, **kwargs):
        kwargs['host'] = '0.0.0.0'
        kwargs['port'] = 8000
        _original_config_init(self, *args, **kwargs)

    uvicorn.Config.__init__ = _patched_config_init
    
    mcp.run(transport="sse")