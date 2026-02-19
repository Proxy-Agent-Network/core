import asyncio
import os
import codecs
import grpc
import traceback
import warnings

warnings.filterwarnings("ignore", module="langgraph")

from mcp import ClientSession
from mcp.client.sse import sse_client
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

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

                @tool
                def pay_lightning_invoice(invoice: str) -> str:
                    """Pays a Lightning invoice. Use this if a tool requires payment (402 error)."""
                    print(f"\n💸 Gemini decided to use its wallet! Paying invoice: {invoice[:10]}...")
                    stub = get_bob_stub()
                    request = ln.SendRequest(payment_request=invoice)
                    response = stub.SendPaymentSync(request)
                    if response.payment_error:
                        return f"Payment failed: {response.payment_error}"
                    return "Payment successful! Extract the 'Hash to use' from the original 402 error and call the data tool again with it."

                # For simplicity in this test, we only give it the 3 tools it needs
                tools = [buy_vip_pass, fetch_crypto_price, pay_lightning_invoice]

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
                
                system_prompt = (
                    "You are an autonomous financial AI with a Lightning Network wallet. "
                    "Your goal is to answer the user's questions using your tools. "
                    "If a tool requires payment (returns a 402 error with an invoice), "
                    "you must use the pay_lightning_invoice tool to pay it, and then "
                    "call the original data tool again using the r_hash provided in the 402 error."
                )
                
                agent_executor = create_react_agent(llm, tools, prompt=system_prompt)
                
                print("🎯 Giving Gemini its mission: Buy a VIP Pass and bulk-fetch prices...\n")
                
                # The ultimate test of logic
                mission = (
                    "Your mission is to fetch the live prices of BTC, ETH, and SOL. "
                    "Because buying 3 separate prices is inefficient, you must FIRST use the "
                    "buy_vip_pass tool to purchase a subscription. Then, use the exact r_hash "
                    "from that VIP pass as the payment_hash to authenticate ALL THREE of your crypto price requests! "
                    "Do not pay any individual 15-sat invoices!"
                )
                
                async for chunk in agent_executor.astream({"messages": [("user", mission)]}):
                    for node, values in chunk.items():
                        if node == "tools":
                            print(f"🛠️  Tool execution complete.")
                        elif node == "agent":
                            message = values["messages"][-1]
                            if message.content:
                                print(f"\n🧠 Gemini: {message.content}")
                            else:
                                print(f"\n🤔 Gemini is thinking / calling a tool...")
                                
    except Exception as e:
        print("\n❌ A fatal error occurred inside the AI Event Loop:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())