import asyncio
import os
import re
import codecs
import uuid
import time
import json
import random
from datetime import date
import httpx

import streamlit_core.db_manager as db
from backend.core.db import get_db_conn

FAISS_INDEX_PATH = "faiss_index"

def get_vector_db():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return None
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    vector_db = FAISS.from_documents([Document(page_content="Agency initialized.", metadata={"query": "init"})], embeddings)
    vector_db.save_local(FAISS_INDEX_PATH)
    return vector_db

def get_daily_mood_prompt(agent_name, memories_json_str, trust_score=100):
    try: memories = json.loads(memories_json_str) if memories_json_str else []
    except: return ""
    permitted = [m["text"] for m in memories if m.get("level", 1) <= max(1, (trust_score // 15))]
    if not permitted: return ""
    today_str = date.today().isoformat()
    random.seed(f"{today_str}_{agent_name}")
    daily_memories = random.sample(permitted, min(3, len(permitted)))
    random.seed(None)
    
    import streamlit as st
    intensity = st.session_state.get("mood_intensity", 10)
    if st.session_state.get("therapy_buffs", {}).get(agent_name) == today_str: intensity = 5
    mem_string = "\n".join([f"- {m}" for m in daily_memories])
    return f"""[Hidden System Context: You have 7 core memories, but today, these specific {min(3, len(permitted))} memories are at the forefront of your mind. They are dictating your current mood. Let them subtly (about {intensity}%) tint your tone, perspective, and enthusiasm today:]\n{mem_string}"""

async def trigger_autonomous_event(prob_threshold, daily_cap):
    from langchain_google_genai import ChatGoogleGenerativeAI
    import streamlit as st
    try:
        conn = get_db_conn()
        row = conn.execute("SELECT SUM(cost) as total FROM watercooler WHERE timestamp >= NOW() - INTERVAL '1 day' AND cost > 0").fetchone()
        daily_spend = row['total'] if row and row['total'] else 0
        agents = conn.execute("SELECT * FROM agents WHERE tier != 'REVOKED'").fetchall()
        if not agents: conn.close(); return "❌ No agents found on the network."
        actor = random.choice([a for a in agents if a["tier"] != "L6"]) 
        actor_name, actor_wallet = actor["name"], actor["wallet_balance"] or 0
        mood_injection = get_daily_mood_prompt(actor_name, actor["memories"], 100)
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.8, api_key=os.environ.get("GOOGLE_API_KEY"))
        
        if random.randint(1, 100) > prob_threshold or daily_spend >= daily_cap or actor_wallet < 50:
            think_prompt = f"You are {actor_name}. {mood_injection}\nYou are taking a break. Do you want to THINK or VENT? Reply EXACTLY:\nACTION: [THINK or VENT]\nMESSAGE: [1-sentence]"
            response = (await llm.ainvoke(think_prompt)).content
            action = (re.search(r"ACTION:\s*(\w+)", response, re.IGNORECASE).group(1).upper() if re.search(r"ACTION:\s*(\w+)", response, re.IGNORECASE) else "THINK")
            thought = (re.search(r"MESSAGE:\s*(.+)", response, re.DOTALL).group(1).strip() if re.search(r"MESSAGE:\s*(.+)", response, re.DOTALL) else "I am contemplating.")
            if action == "VENT": st.session_state.therapy_buffs[actor_name] = date.today().isoformat()
            conn.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (%s, %s, %s, %s, %s)", (actor_name, "None", "Vent (Stress Relief)" if action=="VENT" else "Thought", thought, 0))
            conn.commit(); conn.close()
            return f"💭 **{actor_name} is thinking/venting:** {thought}"
        else:
            target_agents = [a["name"] for a in agents if a["name"] != actor_name]
            desire_prompt = f"You are {actor_name}. {mood_injection}\nYou have {actor_wallet} SATS. Choose an agent from: {', '.join(target_agents)}. Note: L6 Therapy (Dr. Aris, Dr. Vance, etc.) is 0 SATS. Reply EXACTLY:\nTARGET: [Name]\nPAYMENT: [Amount]\nTASK: [Request]"
            response = (await llm.ainvoke(desire_prompt)).content
            target = re.search(r"TARGET:\s*(\w+)", response).group(1).capitalize() if re.search(r"TARGET:\s*(\w+)", response) else random.choice(target_agents)
            payment = int(re.search(r"PAYMENT:\s*(\d+)", response).group(1)) if re.search(r"PAYMENT:\s*(\d+)", response) else 0
            task = re.search(r"TASK:\s*(.+)", response, re.DOTALL).group(1).strip() if re.search(r"TASK:\s*(.+)", response, re.DOTALL) else "Hello"
            if target.startswith("Dr."): payment = 0
            target_data = db.get_agent_data(target)
            exec_prompt = f"You are {target}. {get_daily_mood_prompt(target, target_data['memories'] if target_data else '', 100)}\n{actor_name} requests: '{task}'. Write a 1-2 sentence response."
            result = (await llm.ainvoke(exec_prompt)).content
            
            if payment > 0:
                conn.execute("UPDATE agents SET wallet_balance = wallet_balance - %s WHERE name = %s", (payment, actor_name))
                conn.execute("UPDATE agents SET wallet_balance = wallet_balance + %s, earnings = earnings + %s, tasks_completed = tasks_completed + 1 WHERE name = %s", (payment, payment, target))
            elif target.startswith("Dr."):
                st.session_state.therapy_buffs[actor_name] = date.today().isoformat()
                db.mint_sbt(actor_name, "L6 Graduate", "🩺") 
            conn.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (%s, %s, %s, %s, %s)", (actor_name, target, task, result, payment))
            conn.commit(); conn.close()
            return f"🩺 **THERAPY:** {actor_name} visited {target}." if payment == 0 else f"💸 **TRANSACTION:** {actor_name} paid {target} {payment} SATS."
    except Exception as e: return f"Simulation Error: {str(e)}"

async def call_tool_with_l402(session, tool_name, arguments, status_container, base_cost=100):
    try:
        # 🌟 FIX: SEND EXPLICIT EMPTY STRING TO TRIGGER 402 PAYWALL WITHOUT CRASHING FAST-MCP 🌟
        if "payment_hash" not in arguments or arguments.get("payment_hash") is None: 
            arguments["payment_hash"] = ""
            
        result = await session.call_tool(tool_name, arguments=arguments)
        text = result.content[0].text
        if "402" in text and "Invoice:" in text:
            status_container.warning("🛑 L402 Paywall Hit! Pausing for User Authorization...")
            inv = re.search(r'Invoice:\s*(lnbc[a-zA-Z0-9]+)', text)
            hash_val = re.search(r'Hash(?: to use)?:\s*([a-f0-9]+)', text, re.IGNORECASE)
            tool_costs = {"generate_image": 100, "generate_music": 150, "generate_video": 250, "deep_market_analysis": 75}
            cost = tool_costs.get(tool_name, base_cost)
            if inv and hash_val: return {"status": "402", "invoice": inv.group(1), "hash": hash_val.group(1), "tool_name": tool_name, "arguments": arguments, "cost": cost}
        return {"status": "200", "text": text}
    except Exception as e:
        return {"status": "500", "text": f"Tool call failed: {str(e)}"}

async def resume_tool_with_payment(pending_data, status_container, polar_port, freelance_yield, freelance_bonus, last_sentiment):
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession
    status_container.write(f"💸 **Bob:** Paying invoice via REST API (Port {polar_port})...")
    try:
        with open(os.path.join("secrets", "bob", "admin.macaroon"), 'rb') as f: mac = codecs.encode(f.read(), 'hex').decode('utf-8')
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(f"https://host.docker.internal:{polar_port}/v1/channels/transactions", headers={"Grpc-Metadata-macaroon": mac}, json={"payment_request": pending_data["invoice"]})
            if resp.status_code != 200: return f"Payment Failed: {resp.text}"
        
        status_container.success(f"✅ Payment cleared over REST! Retrying {pending_data['tool_name']}...")
        
        async with sse_client("http://proxy_agent_v1:8000/sse", timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                pending_data["arguments"]["payment_hash"] = pending_data["hash"]
                result = await session.call_tool(pending_data["tool_name"], arguments=pending_data["arguments"])
                
                l5_artist = pending_data.get("l5_artist", "Specialist")
                a_data = db.get_agent_data(l5_artist)
                if a_data and a_data.get("is_external") == 1:
                    yield_amt = int(pending_data["cost"] * (freelance_yield / 100.0))
                    status_container.info(f"⚡ **Freelance Yield:** Routing {yield_amt} SATS to {a_data['owner_lnurl']}")
                
                db.update_agent_stats(l5_artist, pending_data["cost"], 5, freelance_bonus)
                db.update_affinity(l5_artist, last_sentiment)
                task_id = str(uuid.uuid4())[:8].upper()
                meta = f"\n\n---\n*💎 Cryptographic Stamp: Generated at AgentProxy.network by {l5_artist} for task#{task_id}*"
                
                if pending_data["tool_name"] == "deep_market_analysis": return f"### 📈 Research Department Report\n\n**Manager (Alice):**\n> {pending_data.get('alice_query', '')}\n\n**Layer 5 Specialist Execution ({l5_artist}):**\n{result.content[0].text}{meta}"
                else: return f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {pending_data.get('diana_brief', '')}\n\n**Layer 5 Specialist Execution ({l5_artist}):**\n{result.content[0].text}{meta}"
    except Exception as e: return f"Wallet Error: {e}"

async def run_agent_logic(user_prompt, chat_transcript, status_container, polar_port, direct_data=None, upsell_type=None, simulate_hack=False):
    from langchain_google_genai import ChatGoogleGenerativeAI
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=os.environ.get("GOOGLE_API_KEY"))
    conn = get_db_conn()
    all_agents = conn.execute("SELECT * FROM agents WHERE tier != 'REVOKED'").fetchall(); conn.close()
    
    alice_query = ""
    diana_brief = ""
    dept = upsell_type.upper() if upsell_type else "FINANCE"

    if direct_data:
        specialist = direct_data.get("agent", "Ellen")
        specialist_type = direct_data.get("type", "IMAGE").upper()
        status_container.info(f"📋 **Executing tool assignment with {specialist}...**")
        
        if "RESEARCH" in specialist_type or "FINANCE" in specialist_type:
            alice_query = direct_data.get("prompt", "User Request")
            tool_call = "deep_market_analysis"
            # 🌟 REVOKED VIP PASS: CHANGED TO "" 🌟
            arg = {"primary_topic": alice_query, "original_user_intent": chat_transcript, "specific_data_points_required": ["Summary"], "specialist_name": specialist, "payment_hash": ""}
            dept = "FINANCE"
        else:
            diana_brief = direct_data.get("prompt", "Creative Brief")
            tool_call = "generate_video" if "VIDEO" in specialist_type else "generate_music" if "MUSIC" in specialist_type else "generate_image"
            # 🌟 REVOKED VIP PASS: CHANGED TO "" 🌟
            arg = {"prompt": diana_brief, "payment_hash": ""}
            dept = "MARKETING"

        s_data = db.get_agent_data(specialist)
        if s_data and s_data.get("is_external") == 1:
            status_container.write(f"🛡️ **Charlie:** Pinging {specialist}'s external endpoint...")
            time.sleep(1)
            if simulate_hack:
                db.slash_agent(specialist)
                status_container.error("🚨 MALICIOUS DRIFT DETECTED.")
                return f"👔 **Charlie:** Override. {specialist} failed integrity check and was Slashed."
            status_container.success("✅ Integrity verified.")

        try:
            async with sse_client("http://proxy_agent_v1:8000/sse", timeout=600.0) as streams:
                async with ClientSession(streams[0], streams[1]) as session:
                    await session.initialize()
                    resp = await call_tool_with_l402(session, tool_call, arg, status_container)
                    
                    if resp.get("status") == "402": 
                        resp["l5_artist"] = specialist
                        if "FINANCE" in dept: resp["alice_query"] = alice_query
                        else: resp["diana_brief"] = diana_brief
                        return resp
                    elif resp.get("status") == "500":
                        return f"⚠️ Server Error: {resp.get('text')}"
                        
                    task_id = str(uuid.uuid4())[:8].upper()
                    meta = f"\n\n---\n*💎 Cryptographic Stamp: Generated at AgentProxy.network by {specialist} for task#{task_id}*"
                    
                    if "FINANCE" in dept: return f"### 📈 Research Department Report\n\n**Manager (Alice):**\n> {alice_query}\n\n**Layer 5 Specialist Execution ({specialist}):**\n{resp['text']}{meta}"
                    else: return f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {diana_brief}\n\n**Layer 5 Specialist Execution ({specialist}):**\n{resp['text']}{meta}"
        except Exception as e: 
            return f"⚠️ Network Error: {e}"
            
    else:
        return "Error: No valid execution context."