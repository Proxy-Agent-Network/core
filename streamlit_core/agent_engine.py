import asyncio
import re
import os

# BUG 3 FIX: Removed top-level imports of langchain, google-genai, etc.

async def run_agent_logic(last_user, chat_transcript, budget, polar_port, direct_data=None, upsell_type=None, simulate_hack=False):
    """Executes the core agentic reasoning logic for Bob and Charlie."""
    # BUG 3 FIX: Lazy loading of heavy libraries at the start of the function.
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    host_key = os.environ.get("GOOGLE_API_KEY", "MISSING_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=host_key)
    
    # Logic for REQUIRE_PAYMENT or standard routing...
    # If 402 is required, return the dictionary with status code.
    if "image" in last_user.lower():
        return {
            "status": "402",
            "cost": 100,
            "invoice": "lnbc1...",
            "hash": "abc...",
            "tool_name": "generate_image",
            "arguments": {"prompt": last_user}
        }
    
    # Standard response
    res = await llm.ainvoke(last_user)
    return res.content