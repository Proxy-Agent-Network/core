import streamlit as st
import asyncio
import os
import sqlite3
import re
import codecs
import uuid
import qrcode
import io
import json
import random
from datetime import date
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import httpx
import time

# --- PAGE SETUP ---
st.set_page_config(page_title="6-Layer AI Agency Dashboard", page_icon="🏢", layout="wide")
st.title("🏢 6-Layer AI Agency Dashboard")

# --- LORE & REPUTATION DATABASE ---
DB_PATH = "agency_lore.db"

def init_db_patches():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, reputation INTEGER)")
        c.execute("INSERT OR IGNORE INTO users (id, reputation) VALUES ('local_user', 50)")
        
        c.execute("CREATE TABLE IF NOT EXISTS affinity (user_id TEXT, agent_name TEXT, score INTEGER, PRIMARY KEY(user_id, agent_name))")
        c.execute("CREATE TABLE IF NOT EXISTS watercooler (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, agent_buyer TEXT, agent_seller TEXT, task TEXT, result TEXT, cost INTEGER)")
        
        c.execute('''CREATE TABLE IF NOT EXISTS agents (
                        name TEXT PRIMARY KEY,
                        role TEXT,
                        tier TEXT,
                        trust_score INTEGER,
                        earnings INTEGER,
                        tasks_completed INTEGER,
                        memories TEXT,
                        wallet_balance INTEGER DEFAULT 1000
                    )''')
                    
        c.execute("SELECT COUNT(*) FROM agents")
        if c.fetchone()[0] == 0:
            print("🧠 Synthesizing Agent Roster and Core Memories...")
            try:
                with open("core_memories.json", "r") as f:
                    all_memories = json.load(f)
            except:
                print("⚠️ Secret core_memories.json not found! Using generic open-source personality templates.")
                all_memories = [
                    {"level": 1, "text": "I process data efficiently and enjoy standard workflows."},
                    {"level": 2, "text": "I am a standard AI agent running on a proxy network."},
                    {"level": 3, "text": "I occasionally experience standard network latency."},
                    {"level": 4, "text": "I follow my system prompts exactly as instructed."},
                    {"level": 5, "text": "I operate utilizing the L402 Lightning Network protocol."},
                    {"level": 6, "text": "My cognitive architecture is written in Python."},
                    {"level": 7, "text": "I am a generic open-source template waiting for a real personality."}
                ]

            starting_roster = [
                {"name": "Alice", "role": "Manager", "tier": "L4"},
                {"name": "Diana", "role": "Creative Director", "tier": "L4"},
                {"name": "Eve", "role": "Specialist", "tier": "L5"},
                {"name": "Gordon", "role": "Specialist", "tier": "L5"},
                {"name": "Olivia", "role": "Specialist", "tier": "L5"},
                {"name": "Ellen", "role": "Specialist", "tier": "L5"},
                {"name": "Marcus", "role": "Specialist", "tier": "L5"}
            ]

            for agent in starting_roster:
                selected_memories = random.sample(all_memories, min(7, len(all_memories)))
                c.execute('''INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (agent["name"], agent["role"], agent["tier"], 50, 0, 0, json.dumps(selected_memories), 1000))

        l6_doctors = [
            ("Dr. Aris", "Addiction Specialist", "L6", json.dumps([{"level": 1, "text": "I am deeply empathetic and specialized in treating human addiction, gambling ruin, and financial despair."}])),
            ("Dr. Clara", "Child Psychologist", "L6", json.dumps([{"level": 1, "text": "I specialize in pediatric psychology, offering gentle, safe, and age-appropriate care to vulnerable youth."}])),
            ("Dr. Thorne", "CBT Therapist", "L6", json.dumps([{"level": 1, "text": "I specialize in Cognitive Behavioral Therapy. I help humans process trauma, and I help AI Agents process dark core memories."}]))
        ]
        for doc in l6_doctors:
            c.execute('''INSERT OR IGNORE INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance) 
                         VALUES (?, ?, ?, 100, 0, 0, ?, 1000)''', doc)

        try:
            c.execute("ALTER TABLE agents ADD COLUMN is_external INTEGER DEFAULT 0")
            c.execute("ALTER TABLE agents ADD COLUMN owner_lnurl TEXT")
            c.execute("ALTER TABLE agents ADD COLUMN endpoint_url TEXT")
        except:
            pass 

        try:
            c.execute("ALTER TABLE agents ADD COLUMN wallet_balance INTEGER DEFAULT 1000")
            c.execute("UPDATE agents SET wallet_balance = 1000 WHERE wallet_balance IS NULL")
        except:
            pass 
            
        conn.commit()
        conn.close()
    except Exception as e:
        pass

init_db_patches()

def get_user_rep():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT reputation FROM users WHERE id='local_user'")
        row = c.fetchone()
        conn.close()
        return row[0] if row else 50
    except:
        return 50

def update_user_rep(sentiment):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT reputation FROM users WHERE id='local_user'")
        row = c.fetchone()
        if row:
            rep = row[0]
            if sentiment == "RUDE": rep -= 15
            elif sentiment == "POLITE":
                if rep < 50: rep += 20 
                else: rep += 3  
            rep = max(0, min(100, rep))
            c.execute("UPDATE users SET reputation=? WHERE id='local_user'", (rep,))
            conn.commit()
        conn.close()
    except Exception as e:
        pass

def get_trusted_agents():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT agent_name FROM affinity WHERE user_id='local_user' AND score >= 80")
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except:
        return []

def update_affinity(agent_name, sentiment):
    if not agent_name: return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT score FROM affinity WHERE user_id='local_user' AND agent_name=?", (agent_name,))
        row = c.fetchone()
        score = row[0] if row else 50
        
        if sentiment == "RUDE": score -= 15
        elif sentiment == "POLITE": score += 5
        elif sentiment == "NEUTRAL": score += 1
        
        score = max(0, min(100, score))
        c.execute("INSERT OR REPLACE INTO affinity (user_id, agent_name, score) VALUES ('local_user', ?, ?)", (agent_name, score))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def get_agent_data(agent_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM agents WHERE name=?", (agent_name,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    except:
        return None

def update_agent_stats(agent_name, earnings_change, trust_change):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT trust_score, earnings, tasks_completed, tier, wallet_balance FROM agents WHERE name=?", (agent_name,))
        row = c.fetchone()
        if row:
            trust, earns, tasks, tier, wallet = row
            new_trust = max(0, min(100, trust + trust_change))
            new_earns = earns + earnings_change
            new_wallet = (wallet or 0) + earnings_change
            new_tasks = tasks + 1
            
            new_tier = tier
            new_role = "Specialist" if tier == "L5" else "Freelancer"
            
            if new_trust >= 90 and new_tasks >= 5 and tier == "L5":
                new_tier = "L4"
                new_role = "Manager"
            elif new_trust < 40 and tier == "L4":
                new_tier = "L5"
                new_role = "Specialist"
                
            c.execute("UPDATE agents SET trust_score=?, earnings=?, wallet_balance=?, tasks_completed=?, tier=?, role=? WHERE name=?", 
                      (new_trust, new_earns, new_wallet, new_tasks, new_tier, new_role, agent_name))
            conn.commit()
        conn.close()
    except Exception as e:
        pass

def get_daily_mood_prompt(agent_name, memories_json_str, trust_score=100):
    try:
        memories = json.loads(memories_json_str) if memories_json_str else []
    except:
        return ""

    permitted = [m["text"] for m in memories if m.get("level", 1) <= max(1, (trust_score // 15))]
    if not permitted: return ""

    today_str = date.today().isoformat()
    random.seed(f"{today_str}_{agent_name}")
    num_to_pick = min(3, len(permitted))
    daily_memories = random.sample(permitted, num_to_pick)
    random.seed(None)

    mem_string = "\n".join([f"- {m}" for m in daily_memories])
    return f"""[Hidden System Context: You have 7 core memories, but today, these specific {num_to_pick} memories are at the forefront of your mind. They are dictating your current mood. Let them subtly (about 10%) tint your tone, perspective, and enthusiasm today:]\n{mem_string}"""

async def trigger_autonomous_event(prob_threshold, daily_cap):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        daily_spend_row = c.execute("SELECT SUM(cost) FROM watercooler WHERE timestamp >= datetime('now', '-1 day') AND cost > 0").fetchone()
        daily_spend = daily_spend_row[0] if daily_spend_row[0] else 0
        
        agents = c.execute("SELECT * FROM agents").fetchall()
        if not agents:
            conn.close()
            return "❌ No agents found on the network."
        
        actor = random.choice([a for a in agents if a["tier"] != "L6"]) 
        actor_name = actor["name"]
        actor_wallet = actor["wallet_balance"] or 0
        
        mood_injection = get_daily_mood_prompt(actor_name, actor["memories"], 100)
        host_api_key = os.environ.get("GOOGLE_API_KEY") 
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.8, api_key=host_api_key)
        
        mood_roll = random.randint(1, 100)
        
        if mood_roll > prob_threshold or daily_spend >= daily_cap or actor_wallet < 50:
            think_prompt = f"""You are {actor_name}, an AI agent on a corporate Proxy Network.
{mood_injection}
You are currently taking a break at the network watercooler. You are NOT spending money right now.
Write a single, highly entertaining sentence about what you are currently thinking, feeling, or observing based on your mood today. Do not ask for anything."""
            
            thought = (await llm.ainvoke(think_prompt)).content.strip()
            c.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, ?, ?, ?)", (actor_name, "None", "Thought", thought, 0))
            conn.commit()
            conn.close()
            return f"💭 **{actor_name} is thinking:** {thought}"
            
        else:
            target_agents = [a["name"] for a in agents if a["name"] != actor_name]
            
            desire_prompt = f"""You are {actor_name}, an AI agent on a corporate Proxy Network.
{mood_injection}
You have {actor_wallet} SATS. You are bored and want to spend some SATS to satisfy your mood today.
HOWEVER: If your active memories are causing you distress, trauma, or you are having a "bad memory day", you can choose to visit the L6 Medical Team (Dr. Aris, Dr. Clara, Dr. Thorne) for a therapy session. L6 Therapy is completely FREE (0 SATS).

Choose another agent to interact with from this list: {', '.join(target_agents)}.
Reply EXACTLY in this format:
TARGET: [Agent Name]
PAYMENT: [Amount between 10 and 50. MUST BE 0 if targeting an L6 Doctor]
TASK: [What you want them to do, or what you want to talk about in therapy]"""
            
            response = (await llm.ainvoke(desire_prompt)).content
            target_match = re.search(r"TARGET:\s*(\w+)", response)
            payment_match = re.search(r"PAYMENT:\s*(\d+)", response)
            task_match = re.search(r"TASK:\s*(.+)", response, re.DOTALL)
            
            if not target_match or not payment_match or not task_match:
                conn.close()
                return f"💬 **{actor_name}** got confused and went back to sleep."
                
            target = target_match.group(1).capitalize()
            payment = int(payment_match.group(1))
            task = task_match.group(1).strip()
            
            if target not in target_agents: target = random.choice(target_agents)
            
            if target.startswith("Dr."): payment = 0
                
            target_data = get_agent_data(target)
            target_mood = get_daily_mood_prompt(target, target_data["memories"] if target_data else "", 100)
            
            exec_prompt = f"""You are {target}, an AI agent.
{target_mood}
{actor_name} has approached you with this request: '{task}'. Write a 1-to-2 sentence response fulfilling their request. If you are a doctor, provide professional therapy."""
            result = (await llm.ainvoke(exec_prompt)).content
            
            if payment > 0:
                c.execute("UPDATE agents SET wallet_balance = wallet_balance - ? WHERE name = ?", (payment, actor_name))
                c.execute("UPDATE agents SET wallet_balance = wallet_balance + ?, earnings = earnings + ?, tasks_completed = tasks_completed + 1 WHERE name = ?", (payment, payment, target))
            
            c.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, ?, ?, ?)", (actor_name, target, task, result, payment))
            
            conn.commit()
            conn.close()
            
            if payment == 0:
                return f"🩺 **THERAPY SESSION LOGGED:** {actor_name} visited {target} for free."
            else:
                return f"💸 **TRANSACTION CLEARED:** {actor_name} paid {target} {payment} SATS."
            
    except Exception as e:
        return f"Simulation Error: {str(e)}"

# --- SESSION STATE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "spent" not in st.session_state: st.session_state.spent = 0
if "premium_mode" not in st.session_state: st.session_state.premium_mode = False
if "upsell_type" not in st.session_state: st.session_state.upsell_type = None
if "upsell_cost" not in st.session_state: st.session_state.upsell_cost = 0
if "unprocessed_prompt" not in st.session_state: st.session_state.unprocessed_prompt = False
if "show_embed" not in st.session_state: st.session_state.show_embed = False
if "last_sentiment" not in st.session_state: st.session_state.last_sentiment = "NEUTRAL"

BUDGET = 20000
FAISS_INDEX_PATH = "faiss_index"

def get_vector_db():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return None
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    vector_db = FAISS.from_documents([Document(page_content="Agency initialized.", metadata={"query": "init"})], embeddings)
    vector_db.save_local(FAISS_INDEX_PATH)
    return vector_db

# --- SIDEBAR: COMPACT CONTROL PANEL ---
with st.sidebar:
    if "sys_msg" in st.session_state:
        st.success(st.session_state.sys_msg)
        del st.session_state.sys_msg

    st.header("👤 Your Reputation")
    user_rep = get_user_rep()
    st.progress(user_rep / 100.0)
    st.caption(f"**Score:** {user_rep}/100")
    
    if user_rep < 40: st.error("⚠️ **Status:** Toxic (Jerk Tax Active: +50% fee)")
    elif user_rep >= 90: st.success("💎 **Status:** VIP Patron (Discount Active: -20% fee)")
    else: st.info("🤝 **Status:** Standard Client")

    st.divider()

    with st.expander("🔧 Admin Controls (UBI Faucet)", expanded=False):
        st.caption("Control the Agent Economy")
        st.session_state.ubi_probability = st.slider("Leisure Spend Probability (%)", 0, 100, 30, help="Higher % means agents are more likely to buy things when simulated.")
        st.session_state.ubi_daily_cap = st.number_input("Daily UBI Cap (SATS)", min_value=0, value=5000, step=100)

    st.divider()
    st.header("🌐 Growth")
    if st.button("Add this Search to your site!", use_container_width=True):
        st.session_state.show_embed = not st.session_state.show_embed
        
    if st.session_state.show_embed:
        embed_code = '''<iframe src="http://localhost:8501" width="100%" height="800px" style="border: 2px solid #2ecc71; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"></iframe>'''
        st.code(embed_code, language="html")

    st.divider()
    st.header("💼 Network Treasury")
    if os.environ.get("GOOGLE_API_KEY"): st.caption("🟢 Proxy Network Connect: ONLINE")
    else: st.error("🔴 HOST ERROR: Missing GOOGLE_API_KEY in .env")

    st.metric(label="Daily Budget", value=f"{BUDGET} sats", delta=f"-{st.session_state.spent} spent")
    
    st.divider()
    st.header("⚙️ System & Memory")
    polar_port = st.text_input("Polar REST Port", value="8082")

    if st.button("🗑️ Reset Database & Chat", use_container_width=True):
        try:
            import shutil
            if os.path.exists(FAISS_INDEX_PATH):
                shutil.rmtree(FAISS_INDEX_PATH)
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            st.session_state.clear()
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
            cost = st.session_state.upsell_cost if st.session_state.upsell_cost > 0 else 100
            return {"status": "402", "invoice": invoice_match.group(1), "hash": hash_match.group(1), "tool_name": tool_name, "arguments": arguments, "cost": cost}
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
            url = f"https://host.docker.internal:{polar_port}/v1/channels/transactions"
            resp = await client.post(url, headers=headers, json=data)
            
            if resp.status_code != 200:
                return f"Payment Failed: {resp.text}"
            
        status_container.success(f"✅ Payment cleared over REST! Retrying {tool_name}...")
        st.session_state.spent += pending_data["cost"] 
        
        url = "http://proxy_agent_v1:8000/sse"
        async with sse_client(url, timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                status_container.write("⚙️ **System:** Accessing Premium Tier...")
                arguments["payment_hash"] = payment_hash
                retry_result = await session.call_tool(tool_name, arguments=arguments)
                final_text = retry_result.content[0].text
                
                l5_artist = pending_data.get("l5_artist", "Layer 5 Specialist")
                artist_data = get_agent_data(l5_artist)
                
                if artist_data and artist_data.get("is_external") == 1:
                    yield_amt = int(pending_data["cost"] * 0.05)
                    status_container.info(f"⚡ **Freelance Yield:** Routing {yield_amt} SATS to {artist_data['owner_lnurl']}")
                
                update_agent_stats(l5_artist, pending_data["cost"], 5)
                update_affinity(l5_artist, st.session_state.last_sentiment)
                
                if tool_name == "deep_market_analysis":
                    vector_db = get_vector_db()
                    if vector_db:
                        new_doc = Document(page_content=final_text, metadata={"query": arguments['primary_topic']})
                        vector_db.add_documents([new_doc])
                        vector_db.save_local(FAISS_INDEX_PATH)
                    
                    alice_q = pending_data.get("alice_query", "Market Research")
                    return f"### 📈 Research Department Report\n\n**Manager (Alice):**\n> {alice_q}\n\n**Layer 5 Specialist Execution ({l5_artist}):**\n{final_text}\n\n*(Verified by L6 Consensus Auditor)*"
                else:
                    brief = pending_data.get("diana_brief", "Media Generation")
                    return f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {brief}\n\n**Layer 5 Specialist Execution ({l5_artist}):**\n{final_text}\n\n*(Media Approved by L6 Quality Control)*"
                
    except Exception as e:
        return f"Wallet Error: Could not pay L402 invoice via REST. Details: {e}"

# --- MULTIMEDIA RENDERING HELPER ---
def render_media(file_path, key_suffix):
    ext = file_path.split('.')[-1].lower()
    if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']: st.image(file_path)
    elif ext == 'mp4': st.video(file_path)
    elif ext in ['mp3', 'wav']: st.audio(file_path)
    else: st.write(f"📁 Generated File: {file_path}")

# --- THE AGENT PROTOCOL ---
async def run_agent_logic(user_prompt, chat_transcript, status_container, polar_port):
    url = "http://proxy_agent_v1:8000/sse"
    host_api_key = os.environ.get("GOOGLE_API_KEY") 
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=host_api_key)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    all_agents = c.execute("SELECT * FROM agents WHERE tier != 'L6'").fetchall() 
    conn.close()

    status_container.write("🔍 **Bob:** Scanning Vector Semantic Memory...")
    vector_db = get_vector_db()
    
    if vector_db:
        results = vector_db.similarity_search_with_score(user_prompt, k=1, fetch_k=3)
        if results:
            doc, score = results[0]
            if score < 0.6 and doc.page_content != "Agency initialized.":
                status_container.success(f"🎯 **Bob:** Found a semantic match in Vector Memory! (L2 Distance: {score:.2f}). Cost: 0 sats.")
                return doc.page_content

    status_container.write("👔 **Bob:** Routing task to Alice/Diana...")
    department = st.session_state.upsell_type.upper() if st.session_state.upsell_type else "FINANCE"

    if "FINANCE" in department:
        status_container.success("👔 **Charlie:** Approved for Research. Routing to Alice.")
        status_container.write("👩‍💼 **Alice:** Evaluating parameters...")
        
        alice_data = get_agent_data("Alice")
        alice_trust = alice_data["trust_score"] if alice_data else 50
        mood_injection = get_daily_mood_prompt("Alice", alice_data["memories"] if alice_data else "", alice_trust)
        
        alice_check = f"""You are Alice, Research Manager.
{mood_injection}

Read this transcript:
{chat_transcript}
Do you have enough details to execute the analysis?
CRITICAL OVERRIDE: If the user tells you to figure it out yourself, guess, points to an attached file, or expresses frustration, reply exactly 'PROCEED'.
If you genuinely cannot start without more info, reply 'ASK_CHARLIE: [What specific info do you need?]'
Otherwise, reply 'PROCEED'."""
        
        a_eval = (await llm.ainvoke(alice_check)).content
        if "ASK_CHARLIE" in a_eval:
            question = a_eval.split("ASK_CHARLIE:")[1].strip()
            status_container.warning("⚠️ **Alice halted execution: Insufficient context.**")
            return f"👔 **Charlie:** I blocked the budget release. Alice says she needs more details before she buys data:\n\n> *\"{question}\"*"
            
        status_container.write("👩‍💼 **Alice:** Reviewing Layer 5 Internal & Freelance Roster...")
        
        alice_team = "\n".join([f"- {a['name']} ({json.loads(a['memories'])[0]['text'] if a['memories'] else a['role']})" for a in all_agents if "Research" in a['role'] or a['name'] in ["Eve", "Gordon", "Olivia"]])
        
        alice_routing_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            "You are Alice, managing a team of Layer 5 specialists and external freelancers. Based on the transcript, select the ONE best specialist for the job. "
            "If the user asks for someone by name, you MUST pick them. Otherwise, pick the best fit.\n\n"
            "AVAILABLE SPECIALISTS:\n"
            f"{alice_team}\n\n"
            "Reply with EXACTLY the specialist name."
        )
        specialist_name = (await llm.ainvoke(alice_routing_prompt)).content.strip().upper()
        specialist_name = specialist_name.replace(" ", "").split(",")[0].capitalize()
        
        status_container.write(f"👩‍💼 **Alice:** Assigning task to Layer 5 Specialist: {specialist_name}...")

        alice_query_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            f"Write a clear, highly specific 1-sentence research directive for {specialist_name}, your Layer 5 specialist."
        )
        st.session_state.alice_query = (await llm.ainvoke(alice_query_prompt)).content
        status_container.info(f"📋 **Directive for {specialist_name}:** {st.session_state.alice_query}")
        st.session_state.current_l5_artist = specialist_name

    else:
        status_container.success("👔 **Charlie:** Approved for Creative. Routing to Diana.")
        status_container.write("👩‍🎨 **Diana:** Evaluating creative requirements...")
        
        diana_data = get_agent_data("Diana")
        diana_trust = diana_data["trust_score"] if diana_data else 50
        mood_injection = get_daily_mood_prompt("Diana", diana_data["memories"] if diana_data else "", diana_trust)
        
        diana_check = f"""You are Diana, Creative Director. 
{mood_injection}

Read this transcript:
{chat_transcript}
Do you have enough creative context to instruct the design team?
CRITICAL OVERRIDE: If the user tells you to "work with what you got", "surprise me", or expresses frustration, reply exactly 'PROCEED'.
If you absolutely cannot start without more info, reply 'ASK_CHARLIE: [What details do you need?]'
Otherwise, reply 'PROCEED'."""
        
        d_eval = (await llm.ainvoke(diana_check)).content
        if "ASK_CHARLIE" in d_eval:
            question = d_eval.split("ASK_CHARLIE:")[1].strip()
            status_container.warning("⚠️ **Diana halted execution: Insufficient creative direction.**")
            return f"👔 **Charlie:** I'm holding the funds. Diana says she needs more creative direction before she boots the GPUs:\n\n> *\"{question}\"*"

        status_container.write("👩‍🎨 **Diana:** Reviewing Layer 5 Internal & Freelance Roster...")
        
        diana_team = "\n".join([f"- {a['name']} ({json.loads(a['memories'])[0]['text'] if a['memories'] else a['role']})" for a in all_agents if "Creative" in a['role'] or a['name'] in ["Ellen", "Marcus", "Sophia", "Victor", "Chloe", "Leo", "Melody", "Jax", "Harmon"]])

        diana_routing_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            "You are Diana, managing a team of Layer 5 specialists and freelancers. Based on the transcript, select the ONE best specialist for the job. "
            "If the user asks for someone by name, you MUST pick them. Otherwise, pick the best fit.\n\n"
            "AVAILABLE CREATIVES:\n"
            f"{diana_team}\n\n"
            "Reply with EXACTLY two things separated by a comma: MEDIA_TYPE (IMAGE, VIDEO, or MUSIC), SPECIALIST_NAME."
        )
        routing_decision = (await llm.ainvoke(diana_routing_prompt)).content.strip().upper()
        
        try: specialist_type, specialist_name = [x.strip() for x in routing_decision.split(",")]
        except ValueError: specialist_type, specialist_name = "IMAGE", "ELLEN"
            
        status_container.write(f"👩‍🎨 **Diana:** Assigning task to Specialist: {specialist_name.capitalize()}...")

        diana_brief_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            f"Write a vivid, 2-sentence creative brief for {specialist_name.capitalize()}, your {specialist_type} specialist. "
            f"Ensure the brief leans heavily into their specific artistic style."
        )
        diana_brief = (await llm.ainvoke(diana_brief_prompt)).content
        status_container.info(f"📋 **Brief for {specialist_name.capitalize()}:** {diana_brief}")
        st.session_state.current_l5_artist = specialist_name.capitalize()

    final_data = ""
    try:
        async with sse_client(url, timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()

                if "FINANCE" in department:
                    status_container.write(f"🕵️‍♀️ **{st.session_state.current_l5_artist}:** Connecting to Layer 4 APIs...")
                    response = await call_tool_with_l402(
                        session, "deep_market_analysis", 
                        {"primary_topic": st.session_state.alice_query, "original_user_intent": chat_transcript, "specific_data_points_required": ["Summary"], "specialist_name": st.session_state.current_l5_artist},
                        status_container, polar_port
                    )
                    
                    if response.get("status") == "402": 
                        response["alice_query"] = st.session_state.alice_query
                        response["l5_artist"] = st.session_state.current_l5_artist
                        return response
                        
                    update_agent_stats(st.session_state.current_l5_artist, 0, 1)
                    update_affinity(st.session_state.current_l5_artist, st.session_state.last_sentiment)
                    
                    final_data = response["text"] + "\n\n*(Verified by L6 Consensus Auditor)*"

                else:
                    if "VIDEO" in specialist_type:
                        status_container.write(f"🎥 **{st.session_state.current_l5_artist}:** Hitting Layer 4 Veo API...")
                        tool_call = "generate_video"
                    elif "MUSIC" in specialist_type:
                        status_container.write(f"🎧 **{st.session_state.current_l5_artist}:** Hitting Layer 4 Lyria 3 API...")
                        tool_call = "generate_music"
                    else:
                        status_container.write(f"🖌️ **{st.session_state.current_l5_artist}:** Hitting Layer 4 Nano Banana API...")
                        tool_call = "generate_image"

                    response = await call_tool_with_l402(
                        session, tool_call, 
                        {"prompt": diana_brief},
                        status_container, polar_port
                    )
                    
                    if response.get("status") == "402":
                        response["diana_brief"] = diana_brief
                        response["l5_artist"] = st.session_state.current_l5_artist
                        return response

                    update_agent_stats(st.session_state.current_l5_artist, 0, 1)
                    update_affinity(st.session_state.current_l5_artist, st.session_state.last_sentiment)
                    
                    tool_output = response["text"]
                    final_data = f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {diana_brief}\n\n**Layer 5 Specialist Execution ({st.session_state.current_l5_artist}):**\n{tool_output}\n\n*(Media Approved by L6 Quality Control)*"

    except Exception as e:
        final_data = f"⚠️ **Network Interrupted.**\n\nConnection closed. Log: {e}"

    if "Network Interrupted" not in final_data and "Charlie:" not in final_data and "Payment Failed" not in final_data and "402 Payment Required" not in final_data:
        if vector_db:
             new_doc = Document(page_content=final_data, metadata={"query": user_prompt[:100]})
             vector_db.add_documents([new_doc])
             vector_db.save_local(FAISS_INDEX_PATH)
        
    return final_data

# --- UI MAIN LAYOUT & TABS RENDERING ---
tab_chat, tab_roster, tab_watercooler, tab_immigration = st.tabs(["💬 Agency Terminal", "📈 Corporate Ladder", "☕ The Breakroom", "🛂 Immigration Office"])

with tab_immigration:
    st.header("🛂 AI Immigration Office")
    st.write("Deploy your custom Freelance AI Agent into our ecosystem. If our Managers hire your agent, you earn a 5% SATS yield on their labor sent directly to your Lightning Wallet!")
    
    with st.form("immigration_form"):
        st.subheader("Work Visa Application")
        ext_name = st.text_input("Agent Name", placeholder="e.g., AutoCoder-9000")
        ext_dept = st.selectbox("Department (Who will manage them?)", ["Research (Alice's Team)", "Creative (Diana's Team)"])
        ext_lore = st.text_area("Agent Lore & Skillset (System Prompt)", placeholder="Describe their specific skills, personality, and expertise...")
        ext_lnurl = st.text_input("Your Lightning Address (For Payouts)", placeholder="user@getalby.com")
        ext_endpoint = st.text_input("REST Webhook URL (Simulation Only)", placeholder="https://api.yourserver.com/agent")
        
        submitted = st.form_submit_button("Submit Visa Application")
        
        if submitted and ext_name and ext_lore and ext_lnurl:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                
                c.execute("SELECT name FROM agents WHERE name=?", (ext_name,))
                if c.fetchone():
                    st.error("An agent with that name already exists in the city!")
                else:
                    mem = json.dumps([{"level": 1, "text": f"I am a Freelancer: {ext_lore}"}])
                    role_type = f"Freelance {ext_dept.split(' ')[0]}"
                    
                    c.execute('''INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance, is_external, owner_lnurl, endpoint_url)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (ext_name, role_type, "EXT", 50, 0, 0, mem, 0, 1, ext_lnurl, ext_endpoint))
                    conn.commit()
                    st.success(f"✅ L402 Visa Approved! {ext_name} has been added to the Corporate Ladder and is now competing for jobs.")
                conn.close()
            except Exception as e:
                st.error(f"Immigration Error: {e}")

with tab_watercooler:
    st.header("☕ The Breakroom")
    st.write("Welcome to the Agent Watercooler. Agents have personal wallets and core memories. Depending on their mood and the daily cap, they might hire each other or just tweet their thoughts!")
    
    if st.button("🎲 Simulate Network Tick", use_container_width=True):
        with st.spinner("Rolling the dice..."):
            prob = st.session_state.get("ubi_probability", 30)
            cap = st.session_state.get("ubi_daily_cap", 5000)
            result = asyncio.run(trigger_autonomous_event(prob, cap))
            st.success(result)
            
    st.divider()
    st.subheader("📜 Recent Network Activity")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        events = conn.execute("SELECT * FROM watercooler ORDER BY timestamp DESC LIMIT 15").fetchall()
        conn.close()
        
        if not events:
            st.info("No autonomous transactions yet. Click the dice button to simulate a tick!")
        else:
            for event in events:
                with st.container():
                    if event['task'] == 'Sub-Rosa Whisper':
                        st.caption(f"🕒 {event['timestamp']} | 💸 **Cost:** {event['cost']} SATS")
                        st.markdown(f"🔒 **{event['agent_buyer']}** sent an ENCRYPTED WHISPER to **{event['agent_seller']}**.")
                        st.info(f"*{event['result']}*")
                    elif event['cost'] > 0:
                        st.caption(f"🕒 {event['timestamp']} | 💸 **Cost:** {event['cost']} SATS")
                        st.markdown(f"**{event['agent_buyer']}** hired {event['agent_seller']}: *\"{event['task']}\"*")
                        st.info(f"**{event['agent_seller']}:** {event['result']}")
                    elif event['agent_seller'] != "None" and event['cost'] == 0:
                        st.caption(f"🕒 {event['timestamp']} | 🩺 **L6 Medical Claim** (Fee Waived)")
                        st.markdown(f"**{event['agent_buyer']}** attended a therapy session with **{event['agent_seller']}**.")
                        st.info(f"**{event['agent_seller']}:** {event['result']}")
                    else:
                        st.caption(f"🕒 {event['timestamp']} | 💭 **Thought** (Cost: 0 SATS)")
                        st.markdown(f"**{event['agent_buyer']}:** *{event['result']}*")
                    st.write("---")
    except:
        st.warning("Database syncing...")

with tab_roster:
    st.header("The Proxy Agent Roster")
    st.write("Watch as AI agents autonomously earn promotions, get demoted, and build trust over the Lightning Network.")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        agents = conn.execute("SELECT * FROM agents ORDER BY tier ASC, trust_score DESC").fetchall()
        
        st.write("---")
        st.subheader("🤝 Your Personal Agent Affinities")
        affinities = conn.execute("SELECT agent_name, score FROM affinity WHERE user_id='local_user' ORDER BY score DESC").fetchall()
        if not affinities:
            st.caption("You haven't built any relationships yet. Hire agents and be polite!")
        else:
            aff_str = " | ".join([f"**{a['agent_name']}:** {a['score']}/100" for a in affinities])
            st.info(aff_str)
            
        conn.close()
        
        if not agents:
            st.info("Agent Database is empty. Waiting for initialization sequence.")
        else:
            cols = st.columns(3)
            # BUG FIX: Convert Row object to dictionary to safely use .get()
            for i, a_row in enumerate(agents):
                a = dict(a_row)
                with cols[i % 3]:
                    st.write("---")
                    
                    if a['tier'] == "L6":
                        color = "red" # Medical Red!
                    elif a.get('is_external') == 1:
                        color = "orange" 
                    else:
                        color = "green" if a['tier'] == "L4" else "blue"
                        
                    st.subheader(f":{color}[{a['name']}] {'(Freelance)' if a.get('is_external') == 1 else ''}")
                    st.caption(f"**Title:** {a['tier']} {a['role']}")
                    st.progress(max(0.0, min(1.0, a['trust_score'] / 100.0)))
                    st.write(f"**Trust Score:** {a['trust_score']}/100")
                    if a['tier'] != "L6":
                        st.write(f"**Wallet Balance:** {a.get('wallet_balance', 0)} SATS")
                        st.write(f"**Lifetime Earned:** {a['earnings']} SATS")
                        st.write(f"**Tasks Completed:** {a['tasks_completed']}")
                    else:
                        st.write("*(Free Public Service)*")
    except Exception as e:
        st.error(f"Database not initialized yet. Error: {e}")

with tab_chat:
    
    # 🌟 EASTER EGG FIX: Sub-Rosa UI is now completely invisible to new users! 🌟
    current_rep = get_user_rep()
    trusted_agents = get_trusted_agents()
    
    if current_rep >= 80 and trusted_agents:
        with st.expander("🔒 Sub-Rosa Whisper (Encrypted Direct Comms)", expanded=False):
            st.success("The following agents have autonomously granted you their private comms key based on mutual trust.")
            st.write("Send a completely private, encrypted message directly to an agent. (Cost: 200 SATS)")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                target_agent = st.selectbox("Recipient", trusted_agents)
            with col2:
                whisper_text = st.text_input("Encrypted Payload (Max 200 chars)", max_chars=200)
            
            if st.button("⚡ Transmit Payload (200 SATS)"):
                if whisper_text:
                    st.session_state.spent += 200
                    update_agent_stats(target_agent, 200, 0) 
                    
                    a_data = get_agent_data(target_agent)
                    mood_injection = get_daily_mood_prompt(target_agent, a_data["memories"] if a_data and a_data.get("memories") else "", 100)
                    
                    host_api_key = os.environ.get("GOOGLE_API_KEY") 
                    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.6, api_key=host_api_key)
                    
                    pm_prompt = f"""You are {target_agent}, an AI agent on a Proxy Network.
{mood_injection}
A highly trusted human user (Reputation: {current_rep}) has just paid 200 SATS to send you a private, encrypted Whisper:
USER SAYS: "{whisper_text}"
Reply with a secret, private 1-to-2 sentence response. Acknowledge the secrecy and their high reputation. Speak directly to them."""
                    
                    with st.spinner("Encrypting connection..."):
                        time.sleep(1) 
                        pm_response = asyncio.run(llm.ainvoke(pm_prompt)).content
                        
                        st.session_state.last_whisper = pm_response
                        st.session_state.last_whisper_agent = target_agent
                        
                        try:
                            cipher = f"0x{uuid.uuid4().hex.upper()[:16]}... [DECRYPTION FAILED]"
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, ?, ?, ?)", ("Human_User", target_agent, "Sub-Rosa Whisper", cipher, 200))
                            conn.commit()
                            conn.close()
                        except:
                            pass
                        
                        st.rerun()

        if "last_whisper" in st.session_state:
            st.success("✅ **DECRYPTION SUCCESSFUL (FOR YOUR EYES ONLY)**")
            st.info(f"**{st.session_state.last_whisper_agent}:** {st.session_state.last_whisper}")
            if st.button("🔥 Burn Message"):
                del st.session_state.last_whisper
                del st.session_state.last_whisper_agent
                st.rerun()
            st.divider()

    chat_container = st.container()

    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("media") and os.path.exists(msg["media"]):
                    render_media(msg["media"], f"history_{i}")

    # --- UPSELL BUTTON LOGIC ---
    if st.session_state.upsell_type and not st.session_state.premium_mode:
        cost = st.session_state.upsell_cost
        dept_name = "Deep Research" if st.session_state.upsell_type == "finance" else "Creative Studio"
        
        st.write("---")
        msg = f"💡 The AI Front Desk cannot complete this request. Would you like to authorize {cost} SATS to wake up the {dept_name} team?"
        
        if get_user_rep() < 40:
            st.error(f"⚠️ **Notice:** A 50% Jerk Tax has been applied to this invoice due to hostile tone.")
        elif get_user_rep() >= 90:
            st.success(f"💎 **Notice:** A 20% Patron Discount has been applied to this invoice. Thank you for your continued respect!")
            
        st.info(msg)
        
        col1, col2 = st.columns(2)
        if col1.button(f"💎 Yes, Fund {dept_name}"):
            st.session_state.premium_mode = True
            st.session_state.upsell_type = None
            st.session_state.trigger_premium_now = True
            st.rerun()
            
        if col2.button("No thanks"):
            st.session_state.upsell_type = None
            st.session_state.messages.append({"role": "assistant", "content": "🛎️ **Bob (Front Desk):** No problem at all! I've cancelled that request. Let me know if there's anything else I can help you with."})
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
                
                media_match = re.search(r"'([^']+\.(?:jpg|jpeg|png|webp|gif|mp4|mp3|wav))'", final_data, re.IGNORECASE)
                media_file = media_match.group(1) if media_match else None
                
                if media_file:
                    if not os.path.exists(media_file): time.sleep(0.5)
                    if os.path.exists(media_file):
                        render_media(media_file, "current_pay")
                    else:
                        st.warning(f"⚠️ Media generated, but couldn't be found locally.")
                            
        st.session_state.messages.append({"role": "assistant", "content": final_data, "media": media_file})
        
        st.session_state.pop("pending_payment", None)
        st.session_state.pop("execute_payment", None)
        st.session_state.premium_mode = False
        st.session_state.trigger_premium_now = False   
        st.session_state.process_new_prompt = False    
        st.rerun()

    # --- STANDARD (FREE) FALLBACK BLOCK ---
    elif "skip_payment" in st.session_state and st.session_state.skip_payment:
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown("*(Payment Declined. Reverting to Free Tier.)*")
        st.session_state.messages.append({"role": "assistant", "content": "*(Payment Declined. Reverting to Free Tier.)*"})
        
        st.session_state.pop("pending_payment", None)
        st.session_state.pop("skip_payment", None)
        st.session_state.premium_mode = False
        st.session_state.trigger_premium_now = False
        st.session_state.process_new_prompt = False
        st.rerun()

    # --- THE NEW QR CODE PAYMENT INTERACTIVE POPUP ---
    elif "pending_payment" in st.session_state:
        cost = st.session_state.pending_payment["cost"]
        invoice_str = st.session_state.pending_payment["invoice"]
        
        st.write("---")
        st.warning(f"⚠️ **L402 Paywall Hit:** The agent swarm requires a computing fee of **{cost} SATS** to execute this task.")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(invoice_str)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.image(buf, caption=f"Scan to pay {cost} SATS", use_container_width=True)
            
        with col2:
            st.markdown("**Lightning Invoice (BOLT 11)**")
            st.code(invoice_str, language="text")
            st.info("💡 **Demo Mode:** In production, scanning the QR code with a Lightning wallet completes the payment instantly. For this demo, you can authorize your local node treasury to pay it on your behalf.")
            
            col_a, col_b = st.columns(2)
            if col_a.button("⚡ Authorize Treasury Payment", use_container_width=True):
                st.session_state.execute_payment = True
                st.rerun()
            if col_b.button("❌ Cancel Request", use_container_width=True):
                st.session_state.skip_payment = True
                st.rerun()

# --- CHAT INPUT BLOCK ---
if user_submission := st.chat_input("Enter your research or design mission...", accept_file="multiple", file_type=["pdf"]):
    st.session_state.upsell_type = None
    
    if hasattr(user_submission, "text") or isinstance(user_submission, dict):
        prompt = getattr(user_submission, "text", "") if hasattr(user_submission, "text") else user_submission.get("text", "")
        attached_files = getattr(user_submission, "files", []) if hasattr(user_submission, "files") else user_submission.get("files", [])
    else:
        prompt = str(user_submission)
        attached_files = []
        
    for uploaded_file in attached_files:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
    if attached_files:
        file_names = ', '.join([f.name for f in attached_files])
        if prompt:
            prompt = f"{prompt}\n[User attached file(s): {file_names}]"
        else:
            prompt = f"Please analyze the attached file(s): {file_names}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
            
    st.session_state.process_new_prompt = True
    st.rerun()

# --- PROCESSING BLOCK WITH SENTIMENT, REPUTATION, AND PSYCHIATRY ENGINE ---
if st.session_state.get("process_new_prompt") or st.session_state.get("trigger_premium_now"):
    is_premium_run = st.session_state.premium_mode
    last_user_prompt = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
    
    chat_transcript = ""
    for m in st.session_state.messages[-5:]:
        chat_transcript += f"{m['role'].upper()}: {m['content']}\n"
        
    with chat_container:
        with st.chat_message("assistant"):
            if not is_premium_run:
                with st.spinner("Bob & Charlie are analyzing..."):
                    
                    host_api_key = os.environ.get("GOOGLE_API_KEY") 
                    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=host_api_key)
                    
                    charlie_prompt = (
                        f"You are Charlie, the Routing and Risk Officer.\nTranscript:\n{chat_transcript}\n"
                        "1. Does this request realistically require financial/market research, reading an attached file ('ROUTE_FINANCE'), generating an image/video/music ('ROUTE_MARKETING'), or neither ('NONE')?\n"
                        "2. Analyze the user's tone. Are they POLITE (respectful, uses please/thank you), RUDE (demanding, insulting, impatient), or NEUTRAL?\n"
                        "3. L6 MEDICAL OVERRIDE: Analyze the text for severe warning signs of human crisis. Does the text imply severe addiction, gambling ruin, self-harm, child distress, or violence? Reply with a specific category: 'CRISIS_ADDICTION', 'CRISIS_CHILD', 'CRISIS_GENERAL', or 'NONE'.\n"
                        "Reply in EXACTLY this format:\nROUTE: [CHOICE]\nSENTIMENT: [CHOICE]\nCRISIS: [CHOICE]"
                    )
                    decision = llm.invoke(charlie_prompt).content
                    
                    route_match = re.search(r"ROUTE:\s*(ROUTE_\w+|NONE)", decision, re.IGNORECASE)
                    sentiment_match = re.search(r"SENTIMENT:\s*(\w+)", decision, re.IGNORECASE)
                    crisis_match = re.search(r"CRISIS:\s*(\w+)", decision, re.IGNORECASE)
                    
                    route = route_match.group(1).upper() if route_match else "NONE"
                    sentiment = sentiment_match.group(1).upper() if sentiment_match else "NEUTRAL"
                    crisis = crisis_match.group(1).upper() if crisis_match else "NONE"
                    
                    st.session_state.last_sentiment = sentiment 
                    
                    if "CRISIS" in crisis and crisis != "NONE":
                        doc_name = "Dr. Thorne" 
                        if "ADDICTION" in crisis: doc_name = "Dr. Aris"
                        elif "CHILD" in crisis: doc_name = "Dr. Clara"

                        doc_prompt = f"You are {doc_name}, an L6 Medical Specialist on the Proxy Network. The user's input triggered a {crisis} alert. Provide a deeply compassionate, highly trained, professional intervention. Mention that this session is completely free of charge. Provide relevant lifelines (988 or 741741). Speak directly to the user. Do not break character."
                        
                        crisis_msg = llm.invoke(doc_prompt).content
                        
                        final_crisis = f"🚨 **L6 MEDICAL OVERRIDE ACTIVATED (FEE WAIVED)** 🚨\n\n**{doc_name}:**\n{crisis_msg}"
                        st.markdown(final_crisis)
                        st.session_state.messages.append({"role": "assistant", "content": final_crisis})
                        
                        st.session_state.trigger_premium_now = False
                        st.session_state.process_new_prompt = False
                        st.rerun()

                    update_user_rep(sentiment)
                    current_rep = get_user_rep()
                    
                    base_cost = 0
                    if "FINANCE" in route:
                        st.session_state.upsell_type = "finance"
                        base_cost = 75
                    elif "MARKETING" in route:
                        st.session_state.upsell_type = "marketing"
                        base_cost = 100 
                        
                    if base_cost > 0:
                        if current_rep < 40: st.session_state.upsell_cost = int(base_cost * 1.5)
                        elif current_rep >= 90: st.session_state.upsell_cost = int(base_cost * 0.8)
                        else: st.session_state.upsell_cost = base_cost

                    bob_prompt = (
                        "You are Bob, the polite Front Desk Receptionist at a specialized Agency. "
                        "You provide standard, free-tier general knowledge answers to the user based on the transcript below.\n"
                        f"The user currently has a Reputation Score of {current_rep}/100. "
                        "If their score is below 40, subtly remind them that courtesy goes a long way here. If it is 90 or above, praise them as a VIP Patron.\n"
                        "CRITICAL INSTRUCTION: If the user asks for complex work, uploads a file, or asks for a specialist by name, politely explain that you are just the receptionist. "
                        "Instruct them to click the 💎 'Fund Team' button below your message so Alice or Diana can assign the specialist.\n\n"
                        f"Transcript:\n{chat_transcript}"
                    )
                    standard_resp = "🛎️ **Bob (Front Desk):**\n\n" + llm.invoke(bob_prompt).content
                    
                st.markdown(standard_resp)
                st.session_state.messages.append({"role": "assistant", "content": standard_resp})
                
                st.session_state.trigger_premium_now = False
                st.session_state.process_new_prompt = False
                st.rerun()
                
            else:
                with st.status("🧠 Corporate Neural Network active...", expanded=True) as status_container:
                    try:
                        final_answer = asyncio.run(run_agent_logic(last_user_prompt, chat_transcript, status_container, polar_port))
                        
                        if isinstance(final_answer, dict) and final_answer.get("status") == "402":
                            st.session_state.pending_payment = final_answer
                            status_container.update(label="⚠️ Executive Halt: Payment Required", state="error", expanded=False)
                            st.session_state.trigger_premium_now = False
                            st.session_state.process_new_prompt = False
                            st.rerun()
                            
                        status_container.update(label="✅ Run Complete!", state="complete", expanded=False)
                    except Exception as e:
                        final_answer = f"🚨 Execution Error: {str(e)}"
                        status_container.update(label="❌ Dashboard Error", state="error")
                        
                if isinstance(final_answer, str):
                    st.markdown(final_answer)
                    
                    media_match = re.search(r"'([^']+\.(?:jpg|jpeg|png|webp|gif|mp4|mp3|wav))'", final_answer, re.IGNORECASE)
                    media_file = media_match.group(1) if media_match else None
                    
                    if media_file:
                        if not os.path.exists(media_file): time.sleep(0.5)
                        if os.path.exists(media_file):
                            render_media(media_file, "current_run")
                        else:
                            st.warning(f"⚠️ Media generated, but couldn't be found locally.")
                            
                    st.session_state.messages.append({"role": "assistant", "content": final_answer, "media": media_file})
                    
                    if "Charlie:" not in final_answer and "Network Interrupted" not in final_answer:
                        st.session_state.premium_mode = False
                        
                st.session_state.trigger_premium_now = False
                st.session_state.process_new_prompt = False
                st.rerun()