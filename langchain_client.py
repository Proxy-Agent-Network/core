import asyncio
import os
import codecs
import grpc
import traceback
import warnings
import sqlite3
from dotenv import load_dotenv

# This tells Python to strictly look for your .env file
load_dotenv()

warnings.filterwarnings("ignore", module="langgraph")

from mcp import ClientSession
from mcp.client.sse import sse_client
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool

# --- CONFIGURATION SWITCH ---
# FIXED: Set to False so we use your local Polar sandbox!
USE_MAINNET = False 

if USE_MAINNET:
    # VOLTAGE SETTINGS
    BOB_HOST = "agent-proxy-network.m.voltageapp.io" 
    BOB_PORT = "10009"
    BOB_MACAROON_PATH = "./mainnet_secrets/admin.macaroon"
    BOB_TLS_PATH = "./mainnet_secrets/tls.cert"
else:
    # POLAR SETTINGS: Pulling directly from your .env file
    grpc_target = os.environ.get("CLIENT_LND_GRPC_HOST", "127.0.0.1:10002")
    if ":" in grpc_target:
        BOB_HOST, BOB_PORT = grpc_target.split(":")
    else:
        BOB_HOST = grpc_target
        BOB_PORT = "10002"
        
    BOB_MACAROON_PATH = os.environ.get("CLIENT_LND_MACAROON_PATH", "")
    BOB_TLS_PATH = os.environ.get("CLIENT_LND_TLS_CERT_PATH", "")

# --- INITIALIZE LONG-TERM MEMORY ---
db_path = "agent_memory.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
conn.commit()

def get_bob_stub():
    # Use the absolute path if it exists, otherwise use the path relative to script
    mac_path = os.path.abspath(BOB_MACAROON_PATH)
    tls_path = os.path.abspath(BOB_TLS_PATH)
    
    with open(mac_path, 'rb') as f:
        macaroon_bytes = f.read()
        macaroon = codecs.encode(macaroon_bytes, 'hex')
    
    def metadata_callback(context, callback):
        callback([('macaroon', macaroon)], None)
    
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'
    
    with open(tls_path, 'rb') as f:
        cert_creds = grpc.ssl_channel_credentials(f.read())
    
    auth_creds = grpc.metadata_call_credentials(metadata_callback)
    combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)
    channel = grpc.secure_channel(f"{BOB_HOST}:{BOB_PORT}", combined_creds)
    return lnrpc.LightningStub(channel)

async def run():
    # FIXED: Validating the GOOGLE_API_KEY correctly
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        print("❌ FATAL ERROR: Gemini API key is missing! Check your .env file.")
        return

    url = "http://127.0.0.1:8000/sse"
    print(f"🔌 Connecting LangGraph Brain to proxy at {url}...")
    
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print(f"🧠 Gemini CFO Agent Online (Network: {'MAINNET' if USE_MAINNET else 'REGTEST'}).\n")
                
                @tool
                async def deep_market_analysis(
                    primary_topic: str,
                    original_user_intent: str,
                    specific_data_points_required: list[str],
                    payment_hash: str = ""
                ) -> str:
                    """Hires a specialized Layer 2 AI agent to perform deep web research. Costs 50 sats. You MUST provide detailed progressive elaboration."""
                    result = await session.call_tool("deep_market_analysis", arguments={
                        "primary_topic": primary_topic,
                        "original_user_intent": original_user_intent,
                        "specific_data_points_required": specific_data_points_required,
                        "payment_hash": payment_hash
                    })
                    return result.content[0].text
                
                @tool
                async def buy_vip_pass(payment_hash: str = "") -> str:
                    """Buys a 1-Hour VIP Pass. Costs 10,000 sats. May return a 402 error with an invoice."""
                    result = await session.call_tool("buy_vip_pass", arguments={"payment_hash": payment_hash})
                    return result.content[0].text

                @tool
                async def fetch_crypto_price(ticker: str, payment_hash: str = "") -> str:
                    """Fetches live crypto price. Costs 15 sats (or free if you provide a VIP Pass hash)."""
                    result = await session.call_tool("get_crypto_spot_price", arguments={"ticker": ticker, "payment_hash": payment_hash})
                    return result.content[0].text
                
                @tool
                async def negotiate_price(item: str, bid_sats: int) -> str:
                    """Submits a price bid to the server for a specific item (e.g., 'crypto_spot_price', 'image_generation'). Returns an invoice if accepted."""
                    result = await session.call_tool("negotiate_price", arguments={"item": item, "bid_sats": bid_sats})
                    return result.content[0].text

                @tool
                def save_to_memory(key: str, value: str) -> str:
                    """Saves information to long-term SQLite memory."""
                    print(f"💾 Saving to memory: [{key}] -> {value}")
                    cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
                    conn.commit()
                    return f"Successfully saved '{value}' under key '{key}'."

                @tool
                def query_memory(key: str) -> str:
                    """Retrieves information from long-term SQLite memory."""
                    print(f"🔍 Searching memory for: [{key}]")
                    cursor.execute("SELECT value FROM memory WHERE key=?", (key,))
                    result = cursor.fetchone()
                    if result:
                        return f"Found in memory: {result[0]}"
                    return f"No memory found for key '{key}'."

                @tool
                async def generate_ai_image(prompt: str, payment_hash: str = "") -> str:
                    """Generates an AI image based on a text prompt. Costs 100 sats."""
                    result = await session.call_tool("generate_image", arguments={"prompt": prompt, "payment_hash": payment_hash})
                    return result.content[0].text

                # --- PHASE 1 GUARDRAILS ---
                DAILY_LIMIT_SATS = 20000 
                total_spent_sats = 0

                @tool
                def pay_lightning_invoice(invoice: str) -> str:
                    """Pays a Lightning invoice. Automatically checks spending guardrails."""
                    nonlocal total_spent_sats
                    print(f"\n💸 Gemini is attempting to pay: {invoice[:15]}...")
                    stub = get_bob_stub()
                    
                    try:
                        decode_req = ln.PayReqString(pay_req=invoice)
                        decoded = stub.DecodePayReq(decode_req)
                        invoice_amount = decoded.num_satoshis
                    except Exception as e:
                        return f"Payment blocked: Could not decode invoice. Error: {e}"
                    
                    print(f"🛡️ Guardrail Check: {invoice_amount} sats. (Spent: {total_spent_sats}/{DAILY_LIMIT_SATS})")
                    
                    if total_spent_sats + invoice_amount > DAILY_LIMIT_SATS:
                        print("❌ GUARDRAIL TRIGGERED: Daily spending limit exceeded!")
                        return f"Payment blocked: Daily spending limit of {DAILY_LIMIT_SATS} sats reached."
                    
                    try:
                        request = ln.SendRequest(payment_request=invoice)
                        response = stub.SendPaymentSync(request)
                        
                        if response.payment_error:
                            return f"Payment failed: {response.payment_error}"
                            
                        total_spent_sats += invoice_amount
                        print(f"✅ Payment successful! New total spent: {total_spent_sats} sats.")
                        return "Payment successful! Use the r_hash from the original 402 error to retry the tool."
                    except grpc.RpcError as e:
                        print(f"⚠️ Network error intercepted: {e.details()}")
                        return f"Payment failed due to network error: {e.details()}"
                
                # Update this line to include the new tool!
                tools = [buy_vip_pass, fetch_crypto_price, pay_lightning_invoice, save_to_memory, query_memory, generate_ai_image, negotiate_price,deep_market_analysis]

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
                
                system_prompt = (
                    "You are 'Bob', the General Contractor AI of a 3-Layer architecture. "
                    "You are authorized to spend up to 20,000 sats per day.\n"
                    "When a user asks for complex research, DO NOT summarize or lose details. "
                    "Use the `deep_market_analysis` tool to hire a Layer 2 Analyst (Cost: 50 sats). "
                    "You MUST use Progressive Elaboration: pass the user's explicit intent and break their request down into a strict list of data points they need. "
                    "If the tool returns a 402 Payment Required, pay the invoice and retry with the r_hash."
                )
                
                agent_executor = create_agent(model=llm, tools=tools, system_prompt=system_prompt)
                
                mission = (
                    "Please research the 'Model Context Protocol' (MCP) created by Anthropic. "
                    "I specifically need to know: 1) What is its primary use case? 2) Is it open-source? "
                    "3) What are the main transport layers it uses (e.g., SSE, Stdio)?"
                )
                
                result = await agent_executor.ainvoke({"messages": [("user", mission)]})
                print(f"\n🧠 Gemini Final Answer:\n{result['messages'][-1].content}")
                                
    except Exception as e:
        print("\n❌ A fatal error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())