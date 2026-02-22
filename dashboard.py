import streamlit as st
import asyncio
import os
import qrcode
import io
import json
import time
import re
import base64
from langchain_google_genai import ChatGoogleGenerativeAI

import streamlit_core.ui_injector as ui_injector
import streamlit_core.db_manager as db
import streamlit_core.agent_engine as engine
from backend.core.db import get_db_conn

# --- INIT ---
ui_injector.inject_custom_ui()
db.init_db_patches()

# 🌟 FIX: INITIAL LOAD SCROLL LOCK 🌟
if "initial_scroll_lock" not in st.session_state:
    st.components.v1.html("""
    <script>
        // Intercept Streamlit's aggressive auto-scroll-to-bottom
        setTimeout(() => { try { window.parent.parent.scrollTo(0, 0); } catch(e) {} }, 100);
        setTimeout(() => { try { window.parent.parent.scrollTo(0, 0); } catch(e) {} }, 500);
    </script>
    """, height=0)
    st.session_state.initial_scroll_lock = True

# --- SESSION STATE ---
if "messages" not in st.session_state: 
    # 🌟 FIX: PRE-LOADED BOB WELCOME MESSAGE 🌟
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

BUDGET = 20000

st.markdown(f'<div id="raw-dashboard-data" data-budget="{BUDGET}" data-spent="{st.session_state.spent}" style="display:none;"></div>', unsafe_allow_html=True)

def render_media(file_path, key_suffix):
    ext = file_path.split('.')[-1].lower()
    if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']: st.image(file_path)
    elif ext == 'mp4': st.video(file_path)
    elif ext in ['mp3', 'wav']: st.audio(file_path)
    else: st.write(f"📁 Generated File: {file_path}")

@st.cache_data
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def get_avatar_for_message(role, content):
    if role == "user": return "👤"
    
    agents = ["Alice", "Diana", "Eve", "Gordon", "Olivia", "Ellen", "Marcus", "Felix", "Zoe", "Liam", "Maya", "Dr. Aris", "Dr. Nora", "Dr. Vance", "Dr. Clara", "Dr. Julian", "Dr. Maeve", "Dr. Thorne", "Dr. Elena", "Dr. Silas", "Bob", "Charlie"]
    found_agent = "Bob"
    
    if "Layer 5 Specialist Execution (" in content:
        match = re.search(r"Layer 5 Specialist Execution \((.*?)\)", content)
        if match: found_agent = match.group(1)
    else:
        for a in agents:
            if f"**{a}:**" in content or f"({a}):**" in content or f"**{a}**" in content:
                found_agent = a
                break
                
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
            if db.reroll_agent_memories(override_target):
                st.success("Wiped.")
            else:
                st.error("Failed.")

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
            if conn.execute("SELECT name FROM agents WHERE name=?", (ext_name,)).fetchone():
                st.error("Name exists!")
            else:
                conn.execute("INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance, is_external, owner_lnurl, endpoint_url) VALUES (?, ?, 'EXT', 50, 0, 0, ?, 0, 1, ?, ?)", (ext_name, f"Freelance {ext_dept}", json.dumps([{"level":1, "text":ext_lore}]), ext_lnurl, ext_endpoint))
                conn.commit(); st.success("✅ Visa Approved!")
            conn.close()

with tab_watercooler:
    st.header("☕ The Breakroom")
    if st.button("🎲 Simulate Network Tick"):
        st.success(asyncio.run(engine.trigger_autonomous_event(st.session_state.ubi_probability, st.session_state.ubi_daily_cap)))
    conn = get_db_conn(); events = conn.execute("SELECT * FROM watercooler ORDER BY timestamp DESC LIMIT 15").fetchall(); conn.close()
    for e in events:
        st.caption(f"🕒 {e['timestamp']} | 💸 {e['cost']} SATS")
        st.markdown(f"**{e['agent_buyer']}** -> **{e['agent_seller']}**: {e['task']}")
        st.info(e['result'])
        st.write("---")

with tab_roster:
    st.header("Corporate Roster")
    conn = get_db_conn(); agents = conn.execute("SELECT * FROM agents ORDER BY tier ASC, trust_score DESC").fetchall(); conn.close()
    cols = st.columns(3)
    for i, a in enumerate(agents):
        with cols[i % 3]:
            st.write("---")
            
            img_filename = a['name'].lower().replace(' ', '_').replace('.', '')
            img_path = f"static/images/roster/{img_filename}.jpg"
            b64_img = get_image_base64(img_path)
            
            if b64_img:
                html = f"""
                <div style="position: relative; width: 100%; aspect-ratio: 3/4; border-radius: 12px; overflow: hidden; border: 2px solid var(--border); margin-bottom: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <img src="data:image/jpeg;base64,{b64_img}" style="width: 100%; height: 100%; object-fit: cover;">
                    <div style="position: absolute; bottom: 12px; right: 15px; font-family: 'Playfair Display', 'Georgia', serif; font-size: 1.3rem; font-weight: 600; letter-spacing: 0.5px; color: #FFD700; text-shadow: 2px 2px 4px rgba(0,0,0,0.9), 0px 0px 10px rgba(0,0,0,0.8); line-height: 1; text-align: right;">
                        {a['name']}
                    </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info(f"📷 Image pending: {img_filename}.jpg")
            
            color = "red" if a['tier'] == "L6" else "grey" if a['tier'] == "REVOKED" else "orange" if a.get('is_external')==1 else "blue"
            st.subheader(f":{color}[{a['name']}]")
            st.caption(f"{a['tier']} {a['role']}")
            sbts = json.loads(a.get('sbts', '[]'))
            if sbts:
                for sbt in sbts: st.caption(sbt)
            st.write(f"Wallet: {a.get('wallet_balance',0)} SATS | Trust: {a['trust_score']}/100")

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
                st.success("✅ Message Delivered Securely.")
                st.rerun()

    chat_container = st.container()
    
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            avatar = get_avatar_for_message(msg["role"], msg["content"])
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                if msg.get("media") and os.path.exists(msg["media"]): render_media(msg["media"], f"hist_{i}")

    if st.session_state.upsell_type and not st.session_state.premium_mode:
        st.write("---")
        cost = st.session_state.upsell_cost
        dept_name = "Deep Research" if st.session_state.upsell_type == "finance" else "Creative Studio"
        
        rep = db.get_user_rep()
        if rep < 25: st.error("⚠️ **Notice:** A 45% Reputation Surcharge has been applied.")
        elif rep < 40: st.warning("⚠️ **Notice:** A 20% Reputation Surcharge has been applied.")
        elif rep < 75 and rep >= 60: st.success("✨ **Notice:** A 10% Reputation Discount has been applied.")
        elif rep < 90 and rep >= 75: st.success("💎 **Notice:** A 20% Reputation Discount has been applied.")
        elif rep >= 90: st.success("👑 **Notice:** A 25% VIP Reputation Discount has been applied.")

        st.info(f"💡 The AI Front Desk cannot complete this request. Would you like to authorize {cost} SATS to wake up the {dept_name} team?")
        
        c1, c2 = st.columns(2)
        if c1.button(f"💎 Yes, Fund {dept_name}"): 
            st.session_state.premium_mode = True
            st.session_state.trigger_premium_now = True
            st.rerun()
            
        if c2.button("❌ No thanks"): 
            st.session_state.upsell_type = None
            st.session_state.messages.append({"role": "assistant", "content": "🛎️ **Bob:** No problem! Let me know if there's anything else."})
            st.rerun()

    if "execute_payment" in st.session_state and st.session_state.execute_payment:
        with chat_container:
            with st.status("💸 Processing...", expanded=True) as s_cont:
                final_data = asyncio.run(engine.resume_tool_with_payment(st.session_state.pending_payment, s_cont, polar_port))
            
            avatar = get_avatar_for_message("assistant", final_data)
            with st.chat_message("assistant", avatar=avatar):
                st.markdown(final_data)
                
                media_match = re.search(r"'([^']+\.(?:jpg|jpeg|png|webp|gif|mp4|mp3|wav))'", final_data, re.IGNORECASE)
                media_file = media_match.group(1) if media_match else None
                if media_file and os.path.exists(media_file): render_media(media_file, "paid_media")
                elif media_file: st.warning(f"⚠️ Media generated but file missing locally: {media_file}")

        st.session_state.messages.append({"role": "assistant", "content": final_data, "media": media_file})
        st.session_state.pop("pending_payment", None); st.session_state.pop("execute_payment", None)
        st.session_state.premium_mode = False; st.session_state.trigger_premium_now = False; st.session_state.upsell_type = None 
        st.rerun()

    elif "pending_payment" in st.session_state:
        cost = st.session_state.pending_payment["cost"]
        st.warning(f"⚠️ **L402 Paywall:** {cost} SATS Required.")
        c1, c2 = st.columns(2)
        if c1.button("⚡ Authorize Treasury Payment"): st.session_state.execute_payment = True; st.rerun()
        if c2.button("❌ Cancel Request"): 
            st.session_state.pop("pending_payment", None)
            st.session_state.premium_mode = False
            st.session_state.upsell_type = None 
            st.rerun()

# 🌟 FIX: CHAT INPUT CAPTURE & AUTO-TAB SWITCH LOGIC 🌟
if user_submission := st.chat_input("Enter your mission..."):
    st.session_state.messages.append({"role": "user", "content": str(user_submission)})
    st.session_state.process_new_prompt = True
    st.session_state.switch_to_terminal = True
    st.rerun()

if st.session_state.get("switch_to_terminal"):
    st.components.v1.html("""
    <script>
        const streamlitDoc = window.parent.document;
        const tabs = streamlitDoc.querySelectorAll('.stTabs [data-baseweb="tab"]');
        if(tabs.length > 0) {
            tabs[0].click(); // Force click the 'Terminal' tab
            setTimeout(() => { try { window.parent.parent.scrollTo({top: 0, behavior: 'smooth'}); } catch(e) {} }, 150);
        }
    </script>
    """, height=0)
    st.session_state.switch_to_terminal = False

if st.session_state.get("process_new_prompt") or st.session_state.get("trigger_premium_now"):
    is_premium = st.session_state.premium_mode
    last_user = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
    chat_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[-5:]])
    
    with chat_container:
        if not is_premium:
            with st.spinner("Analyzing..."):
                host_key = os.environ.get("GOOGLE_API_KEY", "MISSING_KEY")
                try:
                    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=host_key)
                    charlie_prompt = (
                        f"You are Charlie, the Routing and Risk Officer.\nTranscript:\n{chat_transcript}\n"
                        "1. Does this request realistically require complex execution (like coding, data analysis, financial/market research, writing, or reading an attached file) ('ROUTE_FINANCE'), generating an image/video/music ('ROUTE_MARKETING'), or is it a simple greeting/question a receptionist can answer ('NONE')?\n"
                        "2. Analyze the user's tone. Are they POLITE (respectful, uses please/thank you), RUDE (demanding, insulting, impatient), or NEUTRAL?\n"
                        "3. L6 MEDICAL OVERRIDE: Analyze the text for severe warning signs of human crisis. Does the text imply severe addiction, gambling ruin, self-harm, child distress, or violence? Reply with a specific category: 'CRISIS_ADDICTION', 'CRISIS_CHILD', 'CRISIS_GENERAL', or 'NONE'.\n"
                        "Reply in EXACTLY this format:\nROUTE: [CHOICE]\nSENTIMENT: [CHOICE]\nCRISIS: [CHOICE]"
                    )
                    dec = llm.invoke(charlie_prompt).content
                except Exception as e:
                    st.error("🚨 **System Alert:** AI Core Offline. Ensure GOOGLE_API_KEY is correctly loaded in environment.")
                    st.session_state.process_new_prompt = False
                    st.stop()

                route = re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE) else "NONE"
                sent = re.search(r"SENTIMENT:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"SENTIMENT:\s*(\w+)", dec, re.IGNORECASE) else "NEUTRAL"
                cris = re.search(r"CRISIS:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"CRISIS:\s*(\w+)", dec, re.IGNORECASE) else "NONE"
                
                db.update_user_rep(sent); st.session_state.last_sentiment = sent
                
                if "CRISIS" in cris and cris != "NONE":
                    st.error("🚨 MEDICAL OVERRIDE ACTIVATED.")
                    st.session_state.process_new_prompt = False; st.rerun()
                    
                base = 75 if "FINANCE" in route else 100 if "MARKETING" in route else 0
                if base > 0:
                    rep = db.get_user_rep()
                    st.session_state.upsell_cost = int(base * 1.45) if rep < 25 else int(base * 1.2) if rep < 40 else base if rep < 60 else int(base * 0.9) if rep < 75 else int(base * 0.8)
                    st.session_state.upsell_type = "marketing" if "MARKETING" in route else "finance"
                    
                bob_prompt = (
                    "You are Bob, the polite Front Desk Receptionist at a specialized Agency. "
                    "You provide standard, free-tier general knowledge answers to the user based on the transcript below.\n"
                    f"The user currently has a Reputation Score of {db.get_user_rep()}/100. "
                    "If their score is below 40, gently suggest that cooperation yields better results here. If it is 75 or above, praise them for their continued respect and partnership.\n"
                    "CRITICAL INSTRUCTION: If the user asks for complex work, uploads a file, or asks for a specialist by name, politely explain that you are just the receptionist. "
                    "Instruct them to click the 💎 'Fund Team' button below your message so Alice or Diana can assign the specialist.\n\n"
                    f"Transcript:\n{chat_transcript}"
                )
                ans = llm.invoke(bob_prompt).content
                if "**Bob:**" not in ans:
                    ans = f"🛎️ **Bob:** {ans}"
                
            avatar = get_avatar_for_message("assistant", ans)
            with st.chat_message("assistant", avatar=avatar):
                st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

        else:
            with st.status("Executing...", expanded=True) as sc:
                ans = asyncio.run(engine.run_agent_logic(last_user, chat_transcript, sc, polar_port))
                
            if isinstance(ans, dict) and ans.get("status") == "402":
                st.session_state.pending_payment = ans
            else:
                avatar = get_avatar_for_message("assistant", ans)
                with st.chat_message("assistant", avatar=avatar):
                    st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                if "Budget blocked" not in ans:
                    st.session_state.premium_mode = False
                    st.session_state.upsell_type = None 
                        
        st.session_state.process_new_prompt = False; st.session_state.trigger_premium_now = False; st.rerun()