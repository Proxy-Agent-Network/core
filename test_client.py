import asyncio
import os
import codecs
import grpc
import re
from mcp import ClientSession
from mcp.client.sse import sse_client

import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc

# Setup Bob's gRPC connection
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

def pay_invoice_with_bob(payment_request):
    print("\n💸 AI Agent is authorizing Bob to pay the invoice...")
    stub = get_bob_stub()
    request = ln.SendRequest(payment_request=payment_request)
    response = stub.SendPaymentSync(request)
    if response.payment_error:
        raise Exception(f"Payment failed: {response.payment_error}")
    print("✅ Payment successfully routed over Lightning!")
    return response

async def execute_premium_tool(session, tool_name: str, arguments: dict):
    """A universal router that calls a tool, catches 402 errors, pays them, and retries."""
    print(f"\n🚀 Attempting to execute '{tool_name}'...")
    
    # Strike 1: Initial Request
    result = await session.call_tool(tool_name, arguments=arguments)
    response_text = result.content[0].text
    
    # Check for Paywall
    if "402 Payment Required" in response_text:
        print(f"🛑 Hit L402 Paywall for {tool_name}! Engaging autonomous payment protocol...")
        
        # Parse Invoice and Hash
        invoice_match = re.search(r"Invoice: (lnbc[a-zA-Z0-9]+)", response_text)
        hash_match = re.search(r"Hash to use: ([a-f0-9]+)", response_text)
        
        if invoice_match and hash_match:
            invoice = invoice_match.group(1)
            r_hash = hash_match.group(1)
            
            # Autonomously Pay the Invoice
            pay_invoice_with_bob(invoice)
            
            # Strike 2: Re-request with proof
            print(f"🚀 Re-requesting '{tool_name}' with cryptographic proof: {r_hash[:10]}...")
            arguments["payment_hash"] = r_hash # Inject the proof into the arguments
            
            result2 = await session.call_tool(tool_name, arguments=arguments)
            return result2.content[0].text
        else:
            return "❌ Failed to parse invoice or hash."
            
    # If no paywall (or it was a free tool), just return the result
    return response_text

async def run():
    url = "http://127.0.0.1:8000/sse"
    print(f"🔌 Connecting Universal AI Agent to proxy at {url}...")
    
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("🤖 Agent Online. Entering marketplace...\n")
                
                # TASK 1: Buy the 15-sat Spot Price
                print("=== TASK 1: Fetching BTC Spot Price (15 sats) ===")
                result1 = await execute_premium_tool(session, "get_crypto_spot_price", {"ticker": "BTC"})
                print(f"🎯 Final Result:\n{result1}\n")
                
                # TASK 2: Buy the 50-sat Market Summary
                print("=== TASK 2: Fetching ETH Market Summary (50 sats) ===")
                result2 = await execute_premium_tool(session, "generate_market_summary", {"asset": "ETH"})
                print(f"🎯 Final Result:\n{result2}\n")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())