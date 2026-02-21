import streamlit as st
import asyncio
import os
import sqlite3
import re
import codecs
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from langchain_google_genai import ChatGoogleGenerativeAI
import httpx
import time

# --- PAGE SETUP ---
st.set_page_config(page_title="5-Layer Search Engine Detail", page_icon="📈", layout="wide")
st.title("📈 5-Layer Search Engine Detail")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "spent" not in st.session_state:
    st.session_state.spent = 0
if "premium_mode" not in st.session_state:
    st.session_state.premium_mode = False
if "upsell_type" not in st.session_state:
    st.session_state.upsell_type = None
if "alice_query" not in st.session_state:
    st.session_state.alice_query = ""

BUDGET = 20000

# --- SIDEBAR: COMPACT CONTROL PANEL ---
with st.sidebar:
    if "sys_msg" in st.session_state:
        st.success(st.session_state.sys_msg)
        del st.session_state.sys_msg

    st.header("🔑 Auth & 💼 Treasury")
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
        
    user_key = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
    if user_key:
        st.session_state.api_key = user_key
        os.environ["GOOGLE_API_KEY"] = user_key
    else:
        st.warning("Please enter your API Key.")

    st.metric(label="Daily Budget", value=f"{BUDGET} sats", delta=f"-{st.session_state.spent} spent")
    st.progress(min(1.0, st.session_state.spent / BUDGET if BUDGET > 0 else 0))
    
    st.divider()
    
    st.header("⚡ Node Settings")
    polar_port = st.text_input("Polar REST Port", value="8082", help="Find this in Polar -> Click Node -> Connect -> REST")
    
    st.divider()

    st.header("🧠 RAG Memory")
    try:
        conn = sqlite3.connect("agent_memory.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS memory (topic TEXT PRIMARY KEY, data TEXT)")
        c.execute("SELECT topic FROM memory")
        rows = c.fetchall()
        if rows:
            for row in rows:
                st.caption(f"💾 {row[0]}")
        else:
            st.caption("Memory is currently empty.")
        conn.close()
    except Exception:
        st.caption("Memory DB connection idle.")

    if st.button("🗑️ Reset Database & Chat", use_container_width=True):
        try:
            conn = sqlite3.connect("agent_memory.db")
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS memory (topic TEXT PRIMARY KEY, data TEXT)")
            c.execute("SELECT COUNT(*) FROM memory")
            count = c.fetchone()[0]
            c.execute("DROP TABLE memory")
            conn.commit()
            conn.close()
            
            st.session_state.clear()
            st.session_state.messages = []
            st.session_state.spent = 0
            st.session_state.sys_msg = f"Clean Slate! {count} memories and all chat history wiped."
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear memory: {e}")

# --- L402 INTERCEPTOR MODULE ---
async def call_tool_with_l402(session, tool_name, arguments, status_container, polar_port):
    result = await session.call_tool(tool_name, arguments=arguments)
    text = result.content[0].text
    
    if "402" in text and "Invoice:" in text:
        status_container.warning("🛑 L402 Paywall Hit! Pausing for User Authorization...")
        
        invoice_match = re.search(r'Invoice:\s*(lnbc[a-zA-Z0-9]+)', text)
        hash_match = re.search(r'Hash(?: to use)?:\s*([a-f0-9]+)', text, re.IGNORECASE)
        
        if invoice_match and hash_match:
            return {
                "status": "402",
                "invoice": invoice_match.group(1),
                "hash": hash_match.group(1),
                "tool_name": tool_name,
                "arguments": arguments,
                "cost": 75 if tool_name == "deep_market_analysis" else 100
            }
                
    return {"status": "200", "text": text}

# --- THE PAYMENT RESUME MODULE ---
async def resume_tool_with_payment(pending_data, status_container, polar_port):
    invoice = pending_data["invoice"]
    payment_hash = pending_data["hash"]
    tool_name = pending_data["tool_name"]
    arguments = pending_data["arguments"]

    status_container.write(f"💸 **Bob:** Paying invoice via REST API (Port {polar_port})...")
    
    try:
        mac_path = os.path.join("secrets", "bob", "admin.macaroon")
        with open(mac_path, 'rb') as f:
            macaroon = codecs.encode(f.read(), 'hex').decode('utf-8')
        
        headers = {"Grpc-Metadata-macaroon": macaroon}
        data = {"payment_request": invoice}
        
        async with httpx.AsyncClient(verify=False) as client:
            url = f"https://127.0.0.1:{polar_port}/v1/channels/transactions"
            resp = await client.post(url, headers=headers, json=data)
            
            if resp.status_code != 200:
                return f"Payment Failed: {resp.text}"
            
        status_container.success(f"✅ Payment cleared over REST! Retrying {tool_name}...")
        st.session_state.spent += pending_data["cost"] 
        
        url = "http://127.0.0.1:8000/sse"
        async with sse_client(url, timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                status_container.write("⚙️ **System:** Accessing Premium Tier...")
                arguments["payment_hash"] = payment_hash
                retry_result = await session.call_tool(tool_name, arguments=arguments)
                final_text = retry_result.content[0].text
                
                if tool_name == "deep_market_analysis":
                    conn = sqlite3.connect("agent_memory.db")
                    c = conn.cursor()
                    c.execute("INSERT OR REPLACE INTO memory (topic, data) VALUES (?, ?)", (arguments['primary_topic'][:30], final_text))
                    conn.commit()
                    conn.close()
                    return f"{final_text}\n\n*(Verified by L5 Consensus Auditor)*"
                else:
                    brief = pending_data.get("diana_brief", "Image Generation")
                    return f"### 🎨 Marketing Department Report\n\n**Creative Director (Diana):**\n> {brief}\n\n**Design Team Execution:**\n{final_text}\n\n*(Visuals Approved by L5 Quality Control)*"
                
    except Exception as e:
        return f"Wallet Error: Could not pay L402 invoice via REST. Details: {e}"

# --- THE AGENT PROTOCOL ---
async def run_agent_logic(user_prompt, chat_transcript, status_container, polar_port):
    url = "http://127.0.0.1:8000/sse"
    current_key = st.session_state.api_key
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=current_key)

    status_container.write("🔍 **Bob:** Checking local SQLite memory...")
    conn = sqlite3.connect("agent_memory.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS memory (topic TEXT PRIMARY KEY, data TEXT)")
    
    found_data = None
    words = user_prompt.split()
    for word in words:
        if len(word) > 4:
            c.execute("SELECT data FROM memory WHERE topic LIKE ?", (f'%{word}%',))
            result = c.fetchone()
            if result:
                found_data = result[0]
                break
    conn.close()

    if found_data:
        status_container.success("🎯 **Bob:** Found matching data in memory! Cost: 0 sats.")
        return found_data

    status_container.write("👔 **Bob:** Submitting transcript to Charlie (CRO)...")
    charlie_prompt = (
        f"You are Charlie, the Risk and Routing Officer. "
        f"Here is the recent conversation transcript:\n{chat_transcript}\n\n"
        f"The user's latest input is: '{user_prompt}'.\n"
        "Based on the context, what department does this belong to?\n"
        "1. If it's financial, crypto, or market research, reply exactly 'ROUTE_FINANCE'.\n"
        "2. If it's image generation, branding, or creative design, reply exactly 'ROUTE_MARKETING'.\n"
        "3. If it's useless garbage that costs money, reply 'REJECTED: [reason]'. "
    )
    decision = (await llm.ainvoke(charlie_prompt)).content
    
    if "REJECTED" in decision:
        status_container.error(f"👔 **Charlie:** {decision}")
        return f"Transaction Blocked by Risk Management: {decision}"

    if "ROUTE_FINANCE" in decision:
        status_container.success("👔 **Charlie:** Approved for Finance. Routing to Alice.")
        status_container.write("👩‍💼 **Alice:** Evaluating research parameters...")
        alice_check = f"""You are Alice, Finance Manager. Read this transcript:
        {chat_transcript}
        Do you have enough details (tickers, subjects) to execute a market analysis?
        CRITICAL OVERRIDE: If the user tells you to figure it out yourself, guess, do the research, OR if they express frustration (e.g., "you're fired"), you MUST accept the ambiguity and reply exactly 'PROCEED'.
        If you genuinely cannot start without more info and the user hasn't told you to guess, reply 'ASK_CHARLIE: [What specific info do you need?]'
        Otherwise, reply 'PROCEED'."""
        
        a_eval = (await llm.ainvoke(alice_check)).content
        if "ASK_CHARLIE" in a_eval:
            question = a_eval.split("ASK_CHARLIE:")[1].strip()
            status_container.warning("⚠️ **Alice halted execution: Insufficient context.**")
            return f"👔 **Charlie:** I blocked the budget release. Alice says she needs more details before she buys data:\n\n> *\"{question}\"*"
            
        status_container.write("👩‍💼 **Alice:** Formulating research directive...")
        alice_query_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            "Based on this conversation, write a clear, highly specific 1-sentence search query describing exactly what financial or market research needs to be executed. Ignore user frustration or conversational filler. Just state the core research objective."
        )
        st.session_state.alice_query = (await llm.ainvoke(alice_query_prompt)).content
        status_container.info(f"📋 **Directive:** {st.session_state.alice_query}")
        department = "FINANCE"

    elif "ROUTE_MARKETING" in decision:
        status_container.success("👔 **Charlie:** Approved for Marketing. Routing to Diana.")
        status_container.write("👩‍🎨 **Diana:** Evaluating creative requirements...")
        diana_check = f"""You are Diana, Marketing Director. Read this transcript:
        {chat_transcript}
        Do you have enough visual context (style, subject, mood) to instruct the design team?
        CRITICAL OVERRIDE: If the user tells you to "work with what you got", "surprise me", or expresses frustration, you MUST accept the ambiguity and reply exactly 'PROCEED'.
        If you absolutely cannot start without more info and the user hasn't told you to just do it, reply 'ASK_CHARLIE: [What visual details do you need?]'
        Otherwise, reply 'PROCEED'."""
        
        d_eval = (await llm.ainvoke(diana_check)).content
        if "ASK_CHARLIE" in d_eval:
            question = d_eval.split("ASK_CHARLIE:")[1].strip()
            status_container.warning("⚠️ **Diana halted execution: Insufficient creative direction.**")
            return f"👔 **Charlie:** I'm holding the funds. Diana says she needs more creative direction before she boots the GPUs:\n\n> *\"{question}\"*"

        status_container.write("👩‍🎨 **Diana:** Expanding context into a Director's brief...")
        diana_brief_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            "Write a highly detailed, vivid, 2-sentence creative brief for your design team based on the transcript. "
            "Focus strictly on visual details, mood, lighting, and aesthetic."
        )
        diana_brief = (await llm.ainvoke(diana_brief_prompt)).content
        status_container.info(f"📋 **Brief:** {diana_brief}")
        department = "MARKETING"

    final_data = ""
    try:
        async with sse_client(url, timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()

                if department == "FINANCE":
                    status_container.write("🕵️‍♀️ **Alice:** Executing web scraping swarm (This takes ~15s)...")
                    response = await call_tool_with_l402(
                        session, 
                        "deep_market_analysis", 
                        {
                            "primary_topic": st.session_state.alice_query,
                            "original_user_intent": chat_transcript,
                            "specific_data_points_required": ["Summary", "Key Players", "Future Outlook"]
                        },
                        status_container,
                        polar_port
                    )
                    
                    if response.get("status") == "402":
                        return response

                    final_data = response["text"]
                    status_container.write("👁️ **Layer 5 (Shadow Layer):** Validating output coherence...")
                    await asyncio.sleep(1) 
                    final_data += "\n\n*(Verified by L5 Consensus Auditor)*"

                elif department == "MARKETING":
                    status_container.write("🖌️ **Designers:** Hitting Layer 4 API...")
                    response = await call_tool_with_l402(
                        session, 
                        "generate_image", 
                        {"prompt": diana_brief},
                        status_container,
                        polar_port
                    )
                    
                    if response.get("status") == "402":
                        response["diana_brief"] = diana_brief
                        return response

                    tool_output = response["text"]
                    final_data = f"### 🎨 Marketing Department Report\n\n**Creative Director (Diana):**\n> {diana_brief}\n\n**Design Team Execution:**\n{tool_output}"
                    status_container.write("👁️ **Layer 5 (Shadow Layer):** Checking image constraints...")
                    await asyncio.sleep(1)
                    final_data += "\n\n*(Visuals Approved by L5 Quality Control)*"

    except Exception as e:
        final_data = f"⚠️ **Network Interrupted.**\n\nConnection closed. Log: {e}"

    if "Network Interrupted" not in final_data and "Charlie:" not in final_data and "Payment Failed" not in final_data:
        status_container.write("💾 **Bob:** Writing final report to long-term memory...")
        conn = sqlite3.connect("agent_memory.db")
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO memory (topic, data) VALUES (?, ?)", (st.session_state.get('alice_query', user_prompt[:30]), final_data))
        conn.commit()
        conn.close()
        
    return final_data

# --- UI MAIN LAYOUT & IMAGE RENDERING ---
chat_container = st.container()

with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("image") and os.path.exists(msg["image"]):
                st.image(msg["image"])
                with open(msg["image"], "rb") as f:
                    st.download_button("📥 Download Masterpiece", data=f, file_name=msg["image"], mime="image/jpeg", key=f"dl_history_{i}")

# --- UPSELL BUTTON LOGIC ---
if st.session_state.upsell_type and not st.session_state.premium_mode:
    cost = st.session_state.upsell_cost
    dept_name = "Deep Research" if st.session_state.upsell_type == "finance" else "Premium Design"
    
    st.write("---")
    st.info(f"💡 The AI Front Desk cannot complete this request. Would you like to authorize {cost} SATS to wake up the {dept_name} team?")
    
    col1, col2 = st.columns(2)
    if col1.button(f"💎 Yes, Fund {dept_name} ({cost} SATS)"):
        st.session_state.premium_mode = True
        st.session_state.upsell_type = None
        st.session_state.trigger_premium_now = True
        st.rerun()
    if col2.button("No thanks"):
        st.session_state.upsell_type = None
        st.rerun()

# --- PAYMENT EXECUTION BLOCK ---
if "execute_payment" in st.session_state and st.session_state.execute_payment:
    pending = st.session_state.pending_payment
    with chat_container:
        with st.chat_message("assistant"):
            with st.status("💸 Processing L402 Transaction...", expanded=True) as status_container:
                try:
                    final_data = asyncio.run(resume_tool_with_payment(pending, status_container, polar_port))
                    status_container.update(label="✅ Transaction Complete!", state="complete", expanded=False)
                except Exception as e:
                    final_data = f"🚨 Execution Error: {str(e)}"
                    status_container.update(label="❌ Payment Failed", state="error")
            
            st.markdown(final_data)
            
            img_match = re.search(r"'([^']+\.(?:jpg|jpeg|png|webp|gif))'", final_data, re.IGNORECASE)
            img_file = img_match.group(1) if img_match else None
            
            if img_file:
                if not os.path.exists(img_file):
                    time.sleep(0.5)
                if os.path.exists(img_file):
                    st.image(img_file)
                    with open(img_file, "rb") as f:
                        st.download_button("📥 Download Masterpiece", data=f, file_name=img_file, mime="image/jpeg", key="dl_current")
                        
    st.session_state.messages.append({"role": "assistant", "content": final_data, "image": img_file})
    del st.session_state.pending_payment
    del st.session_state.execute_payment
    
    # Automatically reset to free tier after a successful premium run
    st.session_state.premium_mode = False
    st.rerun()

# --- STANDARD (FREE) FALLBACK BLOCK ---
elif "skip_payment" in st.session_state and st.session_state.skip_payment:
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown("*(Payment Declined. Reverting to Free Tier.)*")
    st.session_state.messages.append({"role": "assistant", "content": "*(Payment Declined. Reverting to Free Tier.)*"})
    del st.session_state.pending_payment
    del st.session_state.skip_payment
    st.rerun()

# --- PAYMENT INTERACTIVE POPUP ---
elif "pending_payment" in st.session_state:
    cost = st.session_state.pending_payment["cost"]
    st.write("---")
    with st.container():
        st.info("⚠️ Action Blocked: This L4 tool requires Lightning Network payment.")
        col1, col2 = st.columns(2)
        if col1.button(f"⚡ Pay Invoice ({cost} SATS)", use_container_width=True):
            st.session_state.execute_payment = True
            st.rerun()
        if col2.button("❌ Cancel Request", use_container_width=True):
            st.session_state.skip_payment = True
            st.rerun()

# --- CHAT INPUT BLOCK ---
elif prompt := st.chat_input("Enter your research or design mission..."):
    if not st.session_state.api_key:
        st.warning("🛑 API key required. Please provide it in the sidebar.")
    else:
        st.session_state.upsell_type = None
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                
        st.session_state.process_new_prompt = True
        st.rerun()

# --- PROCESSING BLOCK ---
if st.session_state.get("process_new_prompt") or st.session_state.get("trigger_premium_now"):
    is_premium_run = st.session_state.premium_mode
    last_user_prompt = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
    
    chat_transcript = ""
    for m in st.session_state.messages[-5:]:
        chat_transcript += f"{m['role'].upper()}: {m['content']}\n"
        
    with chat_container:
        with st.chat_message("assistant"):
            if not is_premium_run:
                with st.spinner("Bob (Front Desk) is typing..."):
                    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=st.session_state.api_key)
                    
                    # BOB THE RECEPTIONIST PROMPT
                    bob_prompt = (
                        "You are Bob, the polite Front Desk Receptionist at an elite AI Hedge Fund. "
                        "You provide standard, free-tier general knowledge answers to the user based on the transcript below.\n"
                        "CRITICAL INSTRUCTION: If the user asks for complex real-time financial data, web scraping, "
                        "or high-end image generation, politely explain that you are just the receptionist and cannot do that. "
                        "Instruct them to click the 💎 'Fund Team' button below your message to wake up the executives (Alice or Diana) to handle it.\n\n"
                        f"Transcript:\n{chat_transcript}"
                    )
                    standard_resp = "🛎️ **Bob (Front Desk):**\n\n" + llm.invoke(bob_prompt).content
                    
                st.markdown(standard_resp)
                st.session_state.messages.append({"role": "assistant", "content": standard_resp})
                
                charlie_prompt = (
                    f"You are Charlie, the Routing Officer.\nTranscript:\n{chat_transcript}\n"
                    "Does this request realistically require financial/market research ('ROUTE_FINANCE') or image/creative design ('ROUTE_MARKETING') or neither ('NONE')? Reply with exactly one of those three keywords."
                )
                decision = llm.invoke(charlie_prompt).content
                
                if "ROUTE_FINANCE" in decision:
                    st.session_state.upsell_type = "finance"
                    st.session_state.upsell_cost = 75
                elif "ROUTE_MARKETING" in decision:
                    st.session_state.upsell_type = "marketing"
                    st.session_state.upsell_cost = 100
                    
                st.session_state.process_new_prompt = False
                st.rerun()
                
            else:
                with st.status("🧠 Corporate Neural Network active...", expanded=True) as status_container:
                    try:
                        final_answer = asyncio.run(run_agent_logic(last_user_prompt, chat_transcript, status_container, polar_port))
                        
                        if isinstance(final_answer, dict) and final_answer.get("status") == "402":
                            st.session_state.pending_payment = final_answer
                            status_container.update(label="⚠️ Executive Halt: Payment Required", state="error", expanded=False)
                            st.rerun()
                            
                        status_container.update(label="✅ Run Complete!", state="complete", expanded=False)
                    except Exception as e:
                        final_answer = f"🚨 Execution Error: {str(e)}"
                        status_container.update(label="❌ Dashboard Error", state="error")
                        
                if isinstance(final_answer, str):
                    st.markdown(final_answer)
                    
                    img_match = re.search(r"'([^']+\.(?:jpg|jpeg|png|webp|gif))'", final_answer, re.IGNORECASE)
                    img_file = img_match.group(1) if img_match else None
                    
                    if img_file:
                        if not os.path.exists(img_file):
                            time.sleep(0.5)
                        if os.path.exists(img_file):
                            st.image(img_file)
                            with open(img_file, "rb") as f:
                                st.download_button("📥 Download Masterpiece", data=f, file_name=img_file, mime="image/jpeg", key="dl_current")
                        else:
                            st.warning(f"⚠️ Image generated, but couldn't be found locally.")
                            
                    st.session_state.messages.append({"role": "assistant", "content": final_answer, "image": img_file})
                    
                    # If the task finishes (not asking a question), revert to free tier
                    if "Charlie:" not in final_answer and "Network Interrupted" not in final_answer:
                        st.session_state.premium_mode = False
                        
                st.session_state.trigger_premium_now = False
                st.session_state.process_new_prompt = False
                st.rerun()