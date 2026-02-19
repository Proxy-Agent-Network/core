import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run():
    url = "http://127.0.0.1:8000/sse"
    print(f"🔌 Connecting to Network Proxy at {url}...")
    
    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("✅ Secure Connection Established!\n")
                
                print("📡 Initiating Discovery Protocol...")
                tools_response = await session.list_tools()
                
                # Check if the agent supports ADP
                tool_names = [tool.name for tool in tools_response.tools]
                if "get_agent_manifest" in tool_names:
                    print("✅ Agent supports ADP. Fetching identity manifest...\n")
                    
                    # Execute the ADP tool
                    result = await session.call_tool("get_agent_manifest", arguments={})
                    
                    print("📄 --- AGENT MANIFEST RECEIVED ---")
                    print(result.content[0].text)
                    print("---------------------------------")
                else:
                    print("⚠️ Agent does not support standard discovery manifests.")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())