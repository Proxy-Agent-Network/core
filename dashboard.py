import streamlit as st
import asyncio
import os
import sqlite3
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from langchain_google_genai import ChatGoogleGenerativeAI
import httpx  # Added to ensure we can explicitly handle timeouts

# --- PAGE SETUP ---
st.set_page_config(page_title="Agentic Hedge Fund", page_icon="📈", layout="wide")
st.title("📈 4-Layer Agentic Hedge Fund")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "spent" not in st.session_state:
    st.session_state.spent = 0
BUDGET = 20000

# --- SIDEBAR: AUTH, MEMORY & WALLET ---
with st.sidebar:
    st.header("🔑 Authentication")
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
        
    user_key = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
    if user_key:
        st.session_state.api_key = user_key
        os.environ["GOOGLE_API_KEY"] = user_key
        st.success("API Key Loaded.")
    else:
        st.warning("Please enter your Gemini API Key to wake up Bob.")

    st.divider()
    
    st.header("💼 Corporate Treasury")
    st.metric(label="Daily Budget", value=f"{BUDGET} sats")
    st.metric(label="Total Spent", value=f"{st.session_state.spent} sats")
    st.progress(min(1.0, st.session_state.spent / BUDGET if BUDGET > 0 else 0))
    
    st.divider()
    
    st.header("🧠 Bob's RAG Memory")
    try:
        conn = sqlite3.connect("agent_memory.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
        c.execute("SELECT key FROM memory")
        rows = c.fetchall()
        if rows:
            for row in rows:
                st.caption(f"💾 {row[0]}")
        else:
            st.caption("Memory is currently empty.")
        conn.close()
    except Exception as e:
        st.caption(f"Memory DB connection idle.")

    st.divider()
    if st.button("🗑️ Clear Fund Memory"):
        try:
            conn = sqlite3.connect("agent_memory.db")
            conn.cursor().execute("DELETE FROM memory")
            conn.commit()
            conn.close()
            st.success("Memory wiped!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear memory: {e}")

# --- THE AGENT PROTOCOL (LAZY CONNECTION & TIMEOUT OVERRIDE) ---
async def run_agent_logic(user_prompt, status_container):
    url = "http://127.0.0.1:8000/sse"
    
    current_key = st.session_state.api_key
    if not current_key:
        return "API key required. Please provide it in the sidebar."
        
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=current_key)

    # --- STEP 1: QUERY MEMORY ---
    status_container.write("🔍 **Bob:** Checking local SQLite memory...")
    conn = sqlite3.connect("agent_memory.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)")
    
    found_data = None
    words = user_prompt.split()
    for word in words:
        if len(word) > 3:
            c.execute("SELECT value FROM memory WHERE key LIKE ?", (f'%{word}%',))
            result = c.fetchone()
            if result:
                found_data = result[0]
                break
    conn.close()

    if found_data:
        status_container.success("🎯 **Bob:** Found matching research in memory! Cost: 0 sats.")
        return found_data

    # --- STEP 2: CHARLIE'S AUDIT ---
    status_container.write("👔 **Bob:** Submitting spend request to Charlie (CRO)...")
    charlie_prompt = (
        f"You are Charlie, the ruthless Risk Officer of a hedge fund. "
        f"A subordinate wants to spend money on this task: '{user_prompt}'. "
        "Is this a valid financial research expense? "
        "Reply 'APPROVED' or 'REJECTED: [reason]'."
    )
    decision = await llm.ainvoke(charlie_prompt)
    
    if "REJECTED" in decision.content:
        status_container.error(f"👔 **Charlie:** {decision.content}")
        return f"Transaction Blocked by Risk Management: {decision.content}"
    
    status_container.success("👔 **Charlie:** APPROVED")

    # --- STEP 3: ALICE & EVE (THE 4-LAYER CALL) ---
    status_container.write("💸 **Bob:** Paying 75 sats... Booting Layer 2 Manager...")
    
    # THE TIMEOUT FIX: We explicitly set the timeout to 300 seconds (5 minutes)
    async with sse_client(url, timeout=300.0) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            
            status_container.write("🕵️‍♀️ **Alice:** Executing web scraping swarm...")
            
            # Call the remote L2 Tool on the Docker Server
            result = await session.call_tool("deep_market_analysis", arguments={
                "primary_topic": user_prompt,
                "original_user_intent": user_prompt,
                "specific_data_points_required": ["Primary use case", "Open source status", "Network transport"]
            })
            
            final_data = result.content[0].text
            st.session_state.spent += 75

            # --- STEP 4: SAVE TO MEMORY ---
            status_container.write("💾 **Bob:** Writing final report to long-term memory...")
            conn = sqlite3.connect("agent_memory.db")
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (user_prompt[:30], final_data))
            conn.commit()
            conn.close()
            
            return final_data

# --- UI DISPLAY LOOP ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your research mission..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.status("🧠 Multi-Agent Orchestration in progress...", expanded=True) as status_container:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                final_answer = loop.run_until_complete(run_agent_logic(prompt, status_container))
                status_container.update(label="✅ Task Complete!", state="complete", expanded=False)
            except Exception as e:
                final_answer = f"🚨 Execution Error: {str(e)}"
                status_container.update(label="❌ Network Timeout", state="error")
            finally:
                loop.close()
            
        st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        st.rerun()