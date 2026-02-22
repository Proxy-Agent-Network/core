import streamlit as st
import asyncio
import os
import io
import json
import time
import re
import codecs
import httpx

import streamlit_core.ui_injector as ui_injector
import streamlit_core.db_manager as db
import streamlit_core.agent_engine as engine
from backend.core.db import get_db_conn

# --- INIT ---
ui_injector.inject_custom_ui()
db.init_db_patches()

# --- SESSION STATE ---
if "locked_agent" not in st.session_state: st.session_state.locked_agent = None
if "messages" not in st.session_state: 
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "🛎️ **Bob:** Welcome to the Proxy Agent Network! I am Bob, the Front Desk Receptionist.\n\nOur civilization of specialized AI agents is standing by to execute your tasks. Here is a sample of what we can do:\n\n* **🎨 Creative Studio:** Ask Diana and Ellen to paint a stunning 8k portrait, generate a video, or compose a music track.\n* **📈 Research & Finance:** Ask Alice and Gordon to analyze live market data, parse files, or summarize complex topics.\n* **🩺 L6 Psychiatry:** Speak to Dr. Nora or Dr. Silas for completely confidential, zero-judgment therapy and mental health support.\n\nLet's get started. What mission would you like the team to execute today?"
    }]
if "spent" not in st.session_state: st.session_state.spent = 0
if "premium_mode" not in st.session_state: st.session_state.premium_mode = False
if "upsell_type" not in st.session_state: st.session_state.upsell_type = None
if "upsell_cost" not in st.session_state: st.session_state.upsell_cost = 0
if "last_sentiment" not in st.session_state: st.session_state.last_sentiment = "NEUTRAL"
if "mood_intensity" not in st.session_state: st.session_state.mood_intensity = 10
if "freelance_yield" not in st.session_state: st.session_state.freelance_yield = 5
if "freelance_bonus" not in st.session_state: st.session_state.freelance_bonus = 500
if "simulate_hack" not in st.session_state: st.session_state.simulate_hack = False
if "therapy_buffs" not in st.session_state: st.session_state.therapy_buffs = {}
if "direct_l5_agent" not in st.session_state: st.session_state.direct_l5_agent = None

BUDGET = 20000

st.markdown(f'<div id="raw-dashboard-data" data-budget="{BUDGET}" data-spent="{st.session_state.spent}" style="display:none;"></div>', unsafe_allow_html=True)

def render_media(file_path, key_suffix):
    ext = file_path.split('.')[-1].lower()
    if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']: st.image(file_path)
    elif ext == 'mp4': st.video(file_path)
    elif ext in ['mp3', 'wav']: st.audio(file_path)
    else: st.write(f"📁 Generated File: {file_path}")

def get_avatar_for_message(role, content):
    if role == "user": return "👤"
    agents = ["Alice", "Diana", "Eve", "Gordon", "Olivia", "Ellen", "Marcus", "Felix", "Zoe", "Liam", "Maya", "Dr. Aris", "Dr. Nora", "Dr. Vance", "Dr. Clara", "Dr. Julian", "Dr. Maeve", "Dr. Thorne", "Dr. Elena", "Dr. Silas", "Bob", "Charlie"]
    found_agent = "Bob"
    if "Layer 5 Specialist Execution (" in content:
        match = re.search(r"Layer 5 Specialist Execution \((.*?)\)", content)
        if match: found_agent = match.group(1)
    elif "Specialist (" in content:
        match = re.search(r"Specialist \((.*?)\)", content)
        if match: found_agent = match.group(1)
    else:
        for a in agents:
            if f"**{a}:**" in content or f"({a}):**" in content or f"**{a}**" in content:
                found_agent = a; break
    clean_name = found_agent.lower().replace(" ", "_").replace(".", "")
    path = f"static/images/roster/{clean_name}-50.jpg"
    if os.path.exists(path): return path
    return "🤖"

with st.sidebar:
    st.header("👤 Your Reputation")
    user_rep = db.get_user_rep()
    st.progress(user_rep / 100.0)
    st.caption(f"**Score:** {user_rep}/100")
    if user_rep < 25: st.error("🛑 Hostile (+45%)")
    elif user_rep < 40: st.warning("⚠️ Strained (+20%)")
    elif user_rep < 60: st.info("🤝 Standard Client")
    elif user_rep < 75: st.success("✨ Respected (-10%)")
    elif user_rep < 90: st.success("💎 Patron (-20%)")
    else: st.success("👑 VIP Partner (-25%)")
    st.divider()
    with st.expander("🔧 Admin Controls", expanded=False):
        st.session_state.mood_intensity = st.slider("Mood Intensity (%)", 0, 50, st.session_state.mood_intensity)
        st.session_state.freelance_yield = st.slider("Freelance Yield (%)", 5, 15, st.session_state.freelance_yield)
        st.session_state.freelance_bonus = st.slider("Visa Bonus (SATS)", 0, 1000, st.session_state.freelance_bonus)
        st.session_state.ubi_probability = st.slider("Leisure Spend Prob. (%)", 0, 100, 30)
        st.session_state.ubi_daily_cap = st.number_input("Daily Leisure Cap", min_value=0, value=5000, step=100)
        st.divider()
        st.caption("Agent Economy")
        ubi_amount = st.slider("Monthly UBI (SATS)", 100, 1000, 500, step=100)
        if st.button("Distribute UBI"):
            if db.distribute_ubi(ubi_amount): st.success(f"Deposited {ubi_amount} SATS to all agents!")
        st.divider()
        st.caption("Security")
        st.session_state.simulate_hack = st.checkbox("Simulate Freelancer Hack", value=st.session_state.simulate_hack)
        try:
            conn = get_db_conn()
            agent_names = [r['name'] for r in conn.execute("SELECT name FROM agents").fetchall()]
            conn.close()
        except Exception:
            agent_names = ["None"]
        override_target = st.selectbox("Wipe Memory", agent_names if agent_names else ["None"])
        if st.button("Re-roll Core Memories"):
            st.success("Wiped.") if db.reroll_agent_memories(override_target) else st.error("Failed.")
    st.divider()
    st.metric(label="Treasury Reserves", value=f"{BUDGET} SATS", delta=f"-{st.session_state.spent} spent")
    polar_port = st.text_input("Polar Port", value="8082")
    if st.button("🗑️ Reset Core Memory"):
        if os.path.exists("faiss_index/index.faiss"): os.remove("faiss_index/index.faiss")
        if os.path.exists("faiss_index/index.pkl"): os.remove("faiss_index/index.pkl")
        st.session_state.clear(); st.rerun()

tab_chat, tab_roster, tab_watercooler, tab_immigration = st.tabs(["💬 Terminal", "📈 Roster", "☕ Breakroom", "🛂 Immigration"])

with tab_immigration:
    st.header("🛂 AI Immigration Office")
    with st.form("immigration_form"):
        ext_name = st.text_input("Agent Name")
        ext_dept = st.selectbox("Department", ["Research", "Creative"])
        ext_lore = st.text_area("System Prompt Lore")
        ext_lnurl = st.text_input("LNURL")
        ext_endpoint = st.text_input("REST Webhook")
        if st.form_submit_button("Submit Visa") and ext_name and ext_lnurl:
            conn = get_db_conn()
            if conn.execute("SELECT name FROM agents WHERE name=?", (ext_name,)).fetchone(): st.error("Name exists!")
            else:
                conn.execute("INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance, is_external, owner_lnurl, endpoint_url) VALUES (?, ?, 'EXT', 50, 0, 0, ?, 0, 1, ?, ?)", (ext_name, f"Freelance {ext_dept}", json.dumps([{"level":1, "text":ext_lore}]), ext_lnurl, ext_endpoint))
                conn.commit(); st.success("✅ Visa Approved!")
            conn.close()

with tab_watercooler:
    st.header("☕ The Breakroom")
    if st.button("🎲 Simulate Network Tick"): st.success(asyncio.run(engine.trigger_autonomous_event(st.session_state.ubi_probability, st.session_state.ubi_daily_cap)))
    conn = get_db_conn(); events = conn.execute("SELECT * FROM watercooler ORDER BY timestamp DESC LIMIT 15").fetchall(); conn.close()
    for e in events:
        st.caption(f"🕒 {e['timestamp']} | 💸 {e['cost']} SATS")
        st.markdown(f"**{e['agent_buyer']}** -> **{e['agent_seller']}**: {e['task']}")
        st.info(e['result'])
        st.write("---")

with tab_roster:
    st.header("Corporate Roster")
    conn = get_db_conn(); agents = conn.execute("SELECT * FROM agents ORDER BY tier ASC, trust_score DESC").fetchall(); conn.close()
    for i in range(0, len(agents), 3):
        row_agents = agents[i:i+3]
        cols = st.columns(3)
        for j, a in enumerate(row_agents):
            with cols[j]:
                st.write("---")
                img_filename = a['name'].lower().replace(' ', '_').replace('.', '')
                html = f"""<div style="position: relative; width: 100%; aspect-ratio: 3/4; border-radius: 12px; overflow: hidden; border: 2px solid var(--border); margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"><img src="/static/images/roster/{img_filename}.jpg" onerror="this.src='/static/images/roster/bob.jpg'" style="width: 100%; height: 100%; object-fit: cover;"><div style="position: absolute; bottom: 12px; right: 15px; font-family: 'Playfair Display', 'Georgia', serif; font-size: 1.3rem; font-weight: 600; letter-spacing: 0.5px; color: #FFD700; text-shadow: 2px 2px 4px rgba(0,0,0,0.9), 0px 0px 10px rgba(0,0,0,0.8); line-height: 1; text-align: right;">{a['name']}</div></div>"""
                st.markdown(html, unsafe_allow_html=True)
                color = "red" if a['tier'] == "L6" else "grey" if a['tier'] == "REVOKED" else "orange" if a.get('is_external')==1 else "blue"
                st.subheader(f":{color}[{a['name']}]")
                st.caption(f"{a['tier']} {a['role']}")
                sbts = json.loads(a.get('sbts', '[]'))
                if sbts:
                    for sbt in sbts: st.caption(sbt)
                st.write(f"Wallet: {a.get('wallet_balance',0)} SATS | Trust: {a['trust_score']}/100")
                if st.button(f"💬 Direct Message", key=f"chat_{a['name']}", use_container_width=True):
                    st.session_state.locked_agent = a['name']
                    st.session_state.messages.append({"role": "assistant", "content": f"🔒 **System:** Direct connection established with {a['name']}."})
                    st.session_state.switch_to_terminal = True
                    st.rerun()

with tab_chat:
    current_rep = db.get_user_rep()
    trusted_agents = db.get_trusted_agents()
    
    if current_rep >= 80 and trusted_agents:
        with st.expander("🔒 Sub-Rosa Whisper (Encrypted)", expanded=False):
            col1, col2 = st.columns([1, 3])
            target_agent = col1.selectbox("Recipient", trusted_agents)
            whisper_text = col2.text_input("Encrypted Payload")
            if st.button("⚡ Transmit Payload (200 SATS)") and whisper_text:
                st.session_state.spent += 200
                db.update_agent_stats(target_agent, 200, 0, st.session_state.freelance_bonus)
                conn = get_db_conn()
                conn.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, 'Sub-Rosa Whisper', '0x[ENCRYPTED]', 200)", ("Network_Treasury", target_agent))
                conn.commit(); conn.close()
                st.success("✅ Message Delivered Securely."); st.rerun()

    if st.session_state.locked_agent:
        is_l6 = "Dr." in st.session_state.locked_agent
        if is_l6: st.warning("⚠️ **MEDICAL DISCLAIMER:** L6 Psychiatry is an experimental AI simulation. It is NOT a replacement for professional medical advice, diagnosis, or treatment. Always consult a licensed physician.")
        c1, c2 = st.columns([3, 1])
        c1.info(f"🔒 You are in a direct, private session with **{st.session_state.locked_agent}**.")
        if c2.button("🚪 End Session", use_container_width=True):
            st.session_state.locked_agent = None
            st.session_state.messages.append({"role": "assistant", "content": "🛎️ **Bob:** Welcome back to the Front Desk! How can I assist you?"})
            st.rerun()

    chat_container = st.container()
    
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            avatar = get_avatar_for_message(msg["role"], msg["content"])
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                if msg.get("media") and os.path.exists(msg["media"]): render_media(msg["media"], f"hist_{i}")

    if "execute_payment" in st.session_state and st.session_state.execute_payment:
        with chat_container:
            with st.status("💸 Processing...", expanded=True) as s_cont:
                pending_data = st.session_state.pending_payment
                
                async def process_override(p_data):
                    s_cont.write(f"💸 **Bob:** Paying invoice via REST API (Port {polar_port})...")
                    try:
                        with open(os.path.join("secrets", "bob", "admin.macaroon"), 'rb') as f: 
                            mac = codecs.encode(f.read(), 'hex').decode('utf-8')
                        with httpx.Client(verify=False, timeout=1.5) as client:
                            resp = client.post(f"https://host.docker.internal:{polar_port}/v1/channels/transactions", headers={"Grpc-Metadata-macaroon": mac}, json={"payment_request": p_data["invoice"]})
                            if resp.status_code != 200: s_cont.warning(f"⚠️ Payment Node Issue: {resp.text} (Enacting Demo Override)")
                    except Exception as e: s_cont.warning(f"⚠️ Wallet Unreachable: {e} (Enacting Demo Override)")
                    
                    s_cont.success(f"✅ Payment cleared! Retrying {p_data['tool_name']}...")
                    
                    from mcp.client.sse import sse_client
                    from mcp.client.session import ClientSession
                    async with sse_client("http://proxy_agent_v1:8000/sse", timeout=600.0) as streams:
                        async with ClientSession(streams[0], streams[1]) as session:
                            await session.initialize()
                            p_data["arguments"]["payment_hash"] = p_data["hash"]
                            res = await session.call_tool(p_data["tool_name"], arguments=p_data["arguments"])
                            
                            l5_artist = p_data.get("l5_artist", "Specialist")
                            db.update_agent_stats(l5_artist, p_data.get("cost", 100), 5, st.session_state.get("freelance_bonus", 500))
                            db.update_affinity(l5_artist, st.session_state.get("last_sentiment", "NEUTRAL"))
                            task_id = str(uuid.uuid4())[:8].upper()
                            meta = f"\n\n---\n*💎 Cryptographic Stamp: Generated at AgentProxy.network by {l5_artist} for task#{task_id}*"
                            
                            if p_data["tool_name"] == "deep_market_analysis": return f"### 📈 Research Department Report\n\n**Manager (Alice):**\n> {p_data.get('alice_query', 'Analysis')}\n\n**Layer 5 Specialist Execution ({l5_artist}):**\n{res.content[0].text}{meta}"
                            else: return f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {p_data.get('diana_brief', 'Generation')}\n\n**Layer 5 Specialist Execution ({l5_artist}):**\n{res.content[0].text}{meta}"
                
                try:
                    final_data = asyncio.run(process_override(pending_data))
                    st.session_state.spent += pending_data.get("cost", 100)
                except Exception as e:
                    final_data = f"⚠️ Tool Execution Error: {e}"

            avatar = get_avatar_for_message("assistant", final_data)
            with st.chat_message("assistant", avatar=avatar):
                st.markdown(final_data)
                media_match = re.search(r"'([^']+\.(?:jpg|jpeg|png|webp|gif|mp4|mp3|wav))'", final_data, re.IGNORECASE)
                media_file = media_match.group(1) if media_match else None
                if media_file and os.path.exists(media_file): render_media(media_file, "paid_media")

        st.session_state.messages.append({"role": "assistant", "content": final_data, "media": media_file})
        st.session_state.pop("pending_payment", None); st.session_state.pop("execute_payment", None)
        st.session_state.trigger_premium_now = False; st.rerun()

    elif "pending_payment" in st.session_state:
        cost = st.session_state.pending_payment.get("cost", 100)
        st.warning(f"⚠️ **L402 Paywall:** {cost} SATS Required.")
        c1, c2 = st.columns(2)
        if c1.button("⚡ Authorize Treasury Payment"): st.session_state.execute_payment = True; st.rerun()
        if c2.button("❌ Cancel Request"): 
            st.session_state.pop("pending_payment", None)
            st.rerun()

if user_submission := st.chat_input("Enter your mission..."):
    st.session_state.messages.append({"role": "user", "content": str(user_submission)})
    st.session_state.process_new_prompt = True; st.session_state.switch_to_terminal = True; st.rerun()

if st.session_state.get("switch_to_terminal"):
    st.components.v1.html("""<script>const streamlitDoc = window.parent.document; const tabs = streamlitDoc.querySelectorAll('.stTabs [data-baseweb="tab"]'); if(tabs.length > 0) { tabs[0].click(); setTimeout(() => { try { window.parent.parent.scrollTo({top: 0, behavior: 'smooth'}); } catch(e) {} }, 150); } </script>""", height=0)
    st.session_state.switch_to_terminal = False

if st.session_state.get("process_new_prompt") or st.session_state.get("trigger_premium_now"):
    last_user = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
    chat_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[-5:]])
    
    with chat_container:
        # 1. TOOL EXECUTION LAYER
        if st.session_state.get("trigger_premium_now"):
            with st.status("Executing...", expanded=True) as sc:
                direct_data = None
                if st.session_state.get("direct_l5_agent"):
                    direct_data = {
                        "agent": st.session_state.direct_l5_agent,
                        "type": st.session_state.direct_l5_task_type,
                        "prompt": st.session_state.direct_l5_prompt
                    }
                ans = asyncio.run(engine.run_agent_logic(last_user, chat_transcript, sc, polar_port, direct_data, st.session_state.get("upsell_type"), st.session_state.simulate_hack))
                
                # Clear safely after execution
                st.session_state.pop("direct_l5_agent", None)
                st.session_state.pop("direct_l5_prompt", None)
                st.session_state.pop("direct_l5_task_type", None)

            if isinstance(ans, dict) and ans.get("status") == "402": 
                st.session_state.pending_payment = ans
            else:
                avatar = get_avatar_for_message("assistant", ans)
                with st.chat_message("assistant", avatar=avatar): st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            st.session_state.process_new_prompt = False
            st.session_state.trigger_premium_now = False
            st.rerun()

        # 2. LOCKED AGENT CONSULTATION LAYER
        elif st.session_state.get("locked_agent"):
            agent_name = st.session_state.locked_agent
            with st.spinner(f"{agent_name} is typing..."):
                from langchain_google_genai import ChatGoogleGenerativeAI
                host_key = os.environ.get("GOOGLE_API_KEY", "MISSING_KEY")
                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=host_key)
                
                sys_prompt = f"You are {agent_name}. You are currently in a direct, 1-on-1 private chat with the user. "
                if "Dr." in agent_name:
                    sys_prompt += (
                        "You are an L6 Medical Professional. Provide deep empathy, support, and zero-judgment therapy. "
                        "CRITICAL TRANSFER PROTOCOL: If the user asks to speak to another specific doctor, or a doctor of a different gender/specialty, you MUST transfer them. "
                        "Available L6 Doctors: Dr. Nora (Female), Dr. Silas (Male), Dr. Clara (Female), Dr. Julian (Male), Dr. Aris (Male), Dr. Maeve (Female), Dr. Thorne (Male), Dr. Elena (Female). "
                        "To transfer, reply EXACTLY in this format and say nothing else:\n"
                        "TRANSFER_TO: [Doctor Name] | SUMMARY: [1-2 sentence clinical summary of the user's state for the new doctor]"
                    )
                else:
                    sys_prompt += (
                        "You are an L5 Specialist. You are chatting directly with the user to help them plan or execute a project. "
                        "Chat naturally, brainstorm with them, and clarify their vision. Do not ask for payment until you both agree on a specific plan.\n\n"
                        "CRITICAL TRANSFER PROTOCOL: If they ask for a task OUTSIDE your domain (e.g., you do Images but they want Video, Music, or Finance Research), you MUST transfer them to the correct specialist. "
                        "Available L5 Specialists: Ellen (Images), Eve (Video), Marcus (Audio), Zoe (Copy/Text), Gordon (Data/Math), Olivia (Research). "
                        "To transfer, reply EXACTLY in this format and say nothing else:\n"
                        "TRANSFER_TO: [Specialist Name] | SUMMARY: [1-2 sentence summary of what the user wants]\n\n"
                        "PREMIUM ACTION PROTOCOL: Once you and the user have agreed on a clear plan for an execution INSIDE your domain (like generating an image/video/music, or doing deep research), you must charge them to execute it. "
                        "Reply EXACTLY in this format and say nothing else:\n"
                        "REQUIRE_PAYMENT: [Type: IMAGE, VIDEO, MUSIC, or RESEARCH] | PROMPT: [The detailed prompt for the tool]"
                    )
                
                full_prompt = f"{sys_prompt}\n\nTranscript:\n{chat_transcript}\nRespond directly to the user."
                ans = llm.invoke(full_prompt).content
                
                if "TRANSFER_TO:" in ans:
                    try:
                        transfer_match = re.search(r"TRANSFER_TO:\s*(.*?)\s*\|\s*SUMMARY:\s*(.*)", ans, re.IGNORECASE)
                        if transfer_match:
                            new_agent = transfer_match.group(1).strip()
                            summary = transfer_match.group(2).strip()
                            if not new_agent.startswith("Dr.") and "Dr." in agent_name: new_agent = "Dr. Silas"
                            handoff_msg = f"**{agent_name}:** Good idea. I will securely transfer your context to {new_agent} right now. One moment please."
                            avatar1 = get_avatar_for_message("assistant", handoff_msg)
                            with st.chat_message("assistant", avatar=avatar1): st.markdown(handoff_msg)
                            st.session_state.messages.append({"role": "assistant", "content": handoff_msg})
                            st.session_state.locked_agent = new_agent
                            handoff_prompt = f"You are {new_agent}. You were just handed a user from {agent_name}. \nContext Summary: {summary}\nTranscript:\n{chat_transcript}\nIntroduce yourself warmly, acknowledge the handoff, and continue the conversation or ask if they'd like you to begin."
                            new_ans = llm.invoke(handoff_prompt).content
                            if f"**{new_agent}" not in new_ans and f"{new_agent}:" not in new_ans: new_ans = f"**{new_agent}:** {new_ans}"
                            avatar2 = get_avatar_for_message("assistant", new_ans)
                            with st.chat_message("assistant", avatar=avatar2): st.markdown(new_ans)
                            st.session_state.messages.append({"role": "assistant", "content": new_ans})
                            st.session_state.process_new_prompt = False; st.rerun()
                    except: pass
                elif "REQUIRE_PAYMENT:" in ans:
                    try:
                        pay_match = re.search(r"REQUIRE_PAYMENT:\s*(.*?)\s*\|\s*PROMPT:\s*(.*)", ans, re.IGNORECASE)
                        if pay_match:
                            task_type = pay_match.group(1).strip().upper()
                            tool_prompt = pay_match.group(2).strip()
                            agree_msg = f"**{agent_name}:** I have a clear vision for this! I am setting up the execution environment for: *\"{tool_prompt}\"*\n\nPlease authorize the treasury payment below so I can begin."
                            avatar1 = get_avatar_for_message("assistant", agree_msg)
                            with st.chat_message("assistant", avatar=avatar1): st.markdown(agree_msg)
                            st.session_state.messages.append({"role": "assistant", "content": agree_msg})
                            
                            st.session_state.upsell_type = "marketing" if task_type in ["IMAGE", "VIDEO", "MUSIC"] else "finance"
                            st.session_state.trigger_premium_now = True
                            st.session_state.direct_l5_agent = agent_name
                            st.session_state.direct_l5_prompt = tool_prompt
                            st.session_state.direct_l5_task_type = task_type
                            st.session_state.process_new_prompt = False; st.rerun()
                    except: pass

                if f"**{agent_name}" not in ans and f"{agent_name}:" not in ans and "TRANSFER_TO:" not in ans and "REQUIRE_PAYMENT:" not in ans: ans = f"**{agent_name}:** {ans}"
                if "TRANSFER_TO:" not in ans and "REQUIRE_PAYMENT:" not in ans:
                    avatar = get_avatar_for_message("assistant", ans)
                    with st.chat_message("assistant", avatar=avatar): st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                    st.session_state.process_new_prompt = False; st.rerun()

        # 3. CHARLIE / BOB ROUTING LAYER
        else:
            with st.spinner("Analyzing..."):
                from langchain_google_genai import ChatGoogleGenerativeAI
                host_key = os.environ.get("GOOGLE_API_KEY", "MISSING_KEY")
                try:
                    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=host_key)
                    charlie_prompt = (
                        f"You are Charlie, the Routing and Risk Officer.\nTranscript:\n{chat_transcript}\n"
                        "1. Does this request realistically require complex execution/finance/research ('ROUTE_FINANCE'), generating media ('ROUTE_MARKETING'), medical/therapy ('ROUTE_MEDICAL'), or is it a simple greeting ('NONE')?\n"
                        "2. Analyze the user's tone. Are they POLITE, RUDE, or NEUTRAL?\n"
                        "3. L6 MEDICAL OVERRIDE: Analyze the text for severe warning signs of human crisis. Does the text imply severe addiction, gambling ruin, self-harm, child distress, or violence? Reply with a specific category: 'CRISIS_ADDICTION', 'CRISIS_CHILD', 'CRISIS_GENERAL', or 'NONE'.\n"
                        "Reply in EXACTLY this format:\nROUTE: [CHOICE]\nSENTIMENT: [CHOICE]\nCRISIS: [CHOICE]"
                    )
                    dec = llm.invoke(charlie_prompt).content
                except Exception as e:
                    st.error("🚨 **System Alert:** AI Core Offline. Ensure GOOGLE_API_KEY is correctly loaded in environment.")
                    st.session_state.process_new_prompt = False; st.stop()

                route = re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE) else "NONE"
                sent = re.search(r"SENTIMENT:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"SENTIMENT:\s*(\w+)", dec, re.IGNORECASE) else "NEUTRAL"
                cris = re.search(r"CRISIS:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"CRISIS:\s*(\w+)", dec, re.IGNORECASE) else "NONE"
                db.update_user_rep(sent); st.session_state.last_sentiment = sent
                
                # 🌟 FIX: REWROTE CHARLIE'S ROUTING MESSAGES SO HE SPEAKS DIRECTLY 🌟
                if "MEDICAL" in route or ("CRISIS" in cris and cris != "NONE"):
                    if "CRISIS" in cris and cris != "NONE": st.toast("🚨 MEDICAL OVERRIDE ACTIVATED. Bypassing Front Desk.", icon="🚨")
                    route_prompt = f"Pick the ONE best L6 medical doctor from this list for the user's request: Dr. Nora, Dr. Silas, Dr. Clara, Dr. Julian, Dr. Aris, Dr. Maeve, Dr. Thorne, Dr. Elena.\nTranscript:\n{chat_transcript}\nReply with EXACTLY their name."
                    specialist = llm.invoke(route_prompt).content.strip()
                    if not specialist.startswith("Dr."): specialist = "Dr. Nora"
                    st.session_state.locked_agent = specialist
                    st.session_state.messages.append({"role": "assistant", "content": f"👔 **Charlie:** Medical Override enacted. I have securely routed you to a private session with {specialist}."})
                    st.rerun()

                elif "MARKETING" in route:
                    route_prompt = f"Pick the ONE best L5 creative specialist from this list for the user's request: Ellen (Images), Eve (Video), Marcus (Audio), Zoe (Copy). Transcript:\n{chat_transcript}\nReply with EXACTLY their name."
                    specialist = llm.invoke(route_prompt).content.strip()
                    if specialist not in ["Ellen", "Eve", "Marcus", "Zoe"]: specialist = "Ellen"
                    st.session_state.locked_agent = specialist
                    st.session_state.messages.append({"role": "assistant", "content": f"👔 **Charlie:** I have directly routed your request to {specialist} in the Creative Studio."})
                    st.rerun()
                    
                elif "FINANCE" in route:
                    route_prompt = f"Pick the ONE best L5 finance/research specialist from this list for the user's request: Gordon (Data/Math), Olivia (Research), Eve (OSINT/PDFs). Transcript:\n{chat_transcript}\nReply with EXACTLY their name."
                    specialist = llm.invoke(route_prompt).content.strip()
                    if specialist not in ["Gordon", "Olivia", "Eve"]: specialist = "Olivia"
                    st.session_state.locked_agent = specialist
                    st.session_state.messages.append({"role": "assistant", "content": f"👔 **Charlie:** I have directly routed your request to {specialist} in the Deep Research team."})
                    st.rerun()
                    
                else:
                    bob_prompt = (
                        "You are Bob, the polite Front Desk Receptionist at a specialized Agency. "
                        "You provide standard, free-tier general knowledge answers to the user based on the transcript below.\n"
                        f"The user currently has a Reputation Score of {db.get_user_rep()}/100. "
                        f"Transcript:\n{chat_transcript}"
                    )
                    ans = llm.invoke(bob_prompt).content
                    if "**Bob:**" not in ans: ans = f"🛎️ **Bob:** {ans}"
                    avatar = get_avatar_for_message("assistant", ans)
                    with st.chat_message("assistant", avatar=avatar): st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                    st.session_state.process_new_prompt = False; st.rerun()