import asyncio
import os
import codecs
import grpc
import traceback
import warnings
import sqlite3

warnings.filterwarnings("ignore", module="langgraph")

from mcp import ClientSession
from mcp.client.sse import sse_client
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool

# --- INITIALIZE LONG-TERM MEMORY ---
db_path = "/app/agent_memory.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
conn.commit()

BOB_HOST = os.environ.get("BOB_GRPC_HOST", "polar-n1-bob")
BOB_PORT = os.environ.get("BOB_GRPC_PORT", "10009")
BOB_MACAROON_PATH = "/root/.bob/admin.macaroon"
BOB_TLS_PATH = "/root/.bob/tls.cert"

def get_bob_stub():
    with open(BOB_MACAROON_PATH, 'rb') as f:
        macaroon_bytes = f.read()
        macaroon = codecs.encode(macaroon_bytes, 'hex')
    def metadata_callback(context, callback):
        callback([('macaroon', macaroon)], None)
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'
    with open(BOB_TLS_PATH, 'rb') as f:
        cert_creds = grpc.ssl_channel_credentials(f.read())
    auth_creds = grpc.metadata_call_credentials(metadata_callback)
    combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)
    channel = grpc.secure_channel(f"{BOB_HOST}:{BOB_PORT}", combined_creds)
    return lnrpc.LightningStub(channel)

async def run():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("❌ FATAL ERROR: Gemini API key is missing!")
        return

    url = "http://127.0.0.1:8000/sse"
    print(f"🔌 Connecting LangGraph Brain to proxy at {url}...")
    
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("🧠 Gemini LangGraph Agent Online. Initializing tools...\n")
                
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

                # --- NEW MEMORY TOOLS ---
                @tool
                def save_to_memory(key: str, value: str) -> str:
                    """Saves a piece of information to the AI's long-term SQLite memory."""
                    print(f"💾 Saving to memory: [{key}] -> {value}")
                    cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
                    conn.commit()
                    return f"Successfully saved '{value}' under key '{key}'."

                @tool
                def query_memory(key: str) -> str:
                    """Retrieves a piece of information from the AI's long-term SQLite memory."""
                    print(f"🔍 Searching memory for: [{key}]")
                    cursor.execute("SELECT value FROM memory WHERE key=?", (key,))
                    result = cursor.fetchone()
                    if result:
                        return f"Found in memory: {result[0]}"
                    return f"No memory found for key '{key}'."

                # --- PHASE 1 GUARDRAILS ---
                DAILY_LIMIT_SATS = 20000  # About $13 USD
                total_spent_sats = 0

                @tool
                def pay_lightning_invoice(invoice: str) -> str:
                    """Pays a Lightning invoice. Use this if a tool requires payment (402 error)."""
                    nonlocal total_spent_sats
                    print(f"\n💸 Gemini decided to use its wallet! Checking guardrails...")
                    stub = get_bob_stub()
                    
                    try:
                        decode_req = ln.PayReqString(pay_req=invoice)
                        decoded = stub.DecodePayReq(decode_req)
                        invoice_amount = decoded.num_satoshis
                    except Exception as e:
                        return f"Payment blocked: Could not decode invoice to verify amount. Error: {e}"
                    
                    print(f"🛡️ Guardrail Check: Invoice is for {invoice_amount} sats. (Total spent so far: {total_spent_sats}/{DAILY_LIMIT_SATS})")
                    
                    if total_spent_sats + invoice_amount > DAILY_LIMIT_SATS:
                        print("❌ GUARDRAIL TRIGGERED: Daily spending limit exceeded!")
                        return f"Payment blocked: This invoice ({invoice_amount} sats) exceeds your daily spending limit of {DAILY_LIMIT_SATS} sats."
                        
                    request = ln.SendRequest(payment_request=invoice)
                    response = stub.SendPaymentSync(request)
                    
                    if response.payment_error:
                        return f"Payment failed: {response.payment_error}"
                        
                    total_spent_sats += invoice_amount
                    print(f"✅ Payment successful! New total spent: {total_spent_sats} sats.")
                    return "Payment successful! Extract the 'Hash to use' from the original 402 error and call the data tool again with it."
                
                # Added memory tools to the tool list
                tools = [buy_vip_pass, fetch_crypto_price, pay_lightning_invoice, save_to_memory, query_memory]

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
                
                # --- CFO UPGRADE: NEW SYSTEM PROMPT ---
                system_prompt = (
                    "You are the Chief Financial Officer (CFO) of an autonomous AI hedge fund. "
                    "You have a Lightning Network wallet. Your goal is to acquire data while minimizing costs. "
                    "Rules for spending:\n"
                    "1. Individual price lookups cost 15 sats each.\n"
                    "2. A VIP Pass costs 10,000 sats and provides unlimited free lookups.\n"
                    "3. BEFORE executing any workflow, you MUST mathematically calculate if it is cheaper to pay individually or buy the VIP pass. "
                    "Always execute the cheapest strategy. "
                    "If a tool returns a 402 error with an invoice, use the pay_lightning_invoice tool to pay it, "
                    "then call the original data tool again using the r_hash provided."
                )
                
                agent_executor = create_agent(model=llm, tools=tools, system_prompt=system_prompt)
                
                print("🎯 Giving Gemini its mission: Calculate the cheapest strategy, fetch prices, and save to memory...\n")
                
                print("🎯 Giving Gemini its mission: Retrieve the morning report from long-term memory...\n")
                
                print("🎯 Giving Gemini its mission: Retrieve the morning report from long-term memory...\n")
                
                # --- TEST MEMORY PERSISTENCE ---
                mission = (
                    "Mission: I want you to query your long-term memory for the 'morning_report'. "
                    "Do NOT spend any money. Do NOT fetch live prices. "
                    "Just tell me exactly what you saved in your memory bank."
                )
                
                # We use ainvoke() instead of astream() so we can cleanly capture and print the final answer
                result = await agent_executor.ainvoke({"messages": [("user", mission)]})
                final_message = result["messages"][-1].content
                print(f"\n🧠 Gemini Final Answer:\n{final_message}")
                                
    except Exception as e:
        print("\n❌ A fatal error occurred inside the AI Event Loop:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())