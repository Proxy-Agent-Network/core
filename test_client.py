import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run():
    url = "http://127.0.0.1:8000/sse"
    print(f"🔌 Connecting to AI Proxy at {url}...")
    
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("✅ Connected to MCP Server!\n")
                
                print("🚀 AI is attempting to execute 'premium_data_query'...")
                
                # We are now sending the proof of payment!
                result = await session.call_tool(
                    "premium_data_query", 
                    arguments={
                        "query": "What is the secret of the universe?",
                        "payment_hash": "8c41ccb6570c2dace18519d9e2773028a07359f2538ec1b82510ffdb0208b556"
                    }
                )
                
                print("\n🎯 Result from LND Node:")
                print(result.content[0].text)
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())