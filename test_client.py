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
                
                print("🛠️  Asking for available tools...")
                tools_response = await session.list_tools()
                for tool in tools_response.tools:
                    print(f"🔹 Discovered: {tool.name}")
                
                # --- THE NEW EXECUTION CODE ---
                print("\n🚀 AI is executing 'get_node_balances'...")
                
                # We call the tool by its exact name, passing an empty dictionary for arguments
                result = await session.call_tool("get_node_balances", arguments={})
                
                print("\n🎯 Result from LND Node:")
                # MCP returns an array of content blocks, we want the text from the first one
                print(result.content[0].text)
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())