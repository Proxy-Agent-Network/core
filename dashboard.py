import streamlit as st
import asyncio
import os
import sqlite3
import re
import codecs
import uuid
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

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "spent" not in st.session_state:
    st.session_state.spent = 0
if "premium_mode" not in st.session_state:
    st.session_state.premium_mode = False
if "upsell_type" not in st.session_state:
    st.session_state.upsell_type = None

BUDGET = 20000

# --- FAISS VECTOR DATABASE ---
FAISS_INDEX_PATH = "faiss_index"

def get_vector_db():
    """Initializes or loads the FAISS Vector Database."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
        
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    
    # Load existing database if it exists
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    
    # Otherwise, create an empty one with a dummy document (FAISS requires at least 1 document to initialize)
    vector_db = FAISS.from_documents([Document(page_content="Agency initialized.", metadata={"query": "init"})], embeddings)
    vector_db.save_local(FAISS_INDEX_PATH)
    return vector_db

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

    st.header("🧠 Vector Memory (FAISS)")
    if os.path.exists(FAISS_INDEX_PATH):
        st.caption("✅ FAISS Memory Active.")
    else:
        st.caption("Memory is currently empty.")

    if st.button("🗑️ Reset Vector Database & Chat", use_container_width=True):
        try:
            import shutil
            if os.path.exists(FAISS_INDEX_PATH):
                shutil.rmtree(FAISS_INDEX_PATH)
            
            st.session_state.clear()
            st.session_state.messages = []
            st.session_state.spent = 0
            st.session_state.sys_msg = f"Clean Slate! Vector memory and all chat history wiped."
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
            if tool_name == "deep_market_analysis": cost = 75
            elif tool_name == "generate_image": cost = 100
            elif tool_name == "generate_music": cost = 150
            elif tool_name == "generate_video": cost = 250
            else: cost = 100

            return {
                "status": "402",
                "invoice": invoice_match.group(1),
                "hash": hash_match.group(1),
                "tool_name": tool_name,
                "arguments": arguments,
                "cost": cost
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
                
                l5_artist = pending_data.get("l5_artist", "Layer 5 Specialist")
                
                if tool_name == "deep_market_analysis":
                    # FAISS VECTOR MEMORY SAVE
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
    if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
        st.image(file_path)
        mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
    elif ext == 'mp4':
        st.video(file_path)
        mime_type = "video/mp4"
    elif ext in ['mp3', 'wav']:
        st.audio(file_path)
        mime_type = f"audio/{ext}"
    else:
        st.write(f"📁 Generated File: {file_path}")
        mime_type = "application/octet-stream"

    with open(file_path, "rb") as f:
        st.download_button(f"📥 Download File", data=f, file_name=file_path, mime=mime_type, key=f"dl_{key_suffix}")

# --- THE AGENT PROTOCOL ---
async def run_agent_logic(user_prompt, chat_transcript, status_container, polar_port):
    url = "http://127.0.0.1:8000/sse"
    current_key = st.session_state.api_key
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, api_key=current_key)

    status_container.write("🔍 **Bob:** Scanning Vector Semantic Memory...")
    vector_db = get_vector_db()
    
    if vector_db:
        # Perform a mathematical similarity search!
        results = vector_db.similarity_search_with_score(user_prompt, k=1, fetch_k=3)
        
        if results:
            doc, score = results[0]
            if score < 0.6 and doc.page_content != "Agency initialized.":
                status_container.success(f"🎯 **Bob:** Found a semantic match in Vector Memory! (L2 Distance: {score:.2f}). Cost: 0 sats.")
                return doc.page_content

    status_container.write("👔 **Bob:** Submitting transcript to Charlie (CRO)...")
    charlie_prompt = (
        f"You are Charlie, the Risk and Routing Officer. "
        f"Here is the recent conversation transcript:\n{chat_transcript}\n\n"
        f"The user's latest input is: '{user_prompt}'.\n"
        "Based on the context, what department does this belong to?\n"
        "1. If it's financial, crypto, market research, web scraping, document analysis, or numbers, reply exactly 'ROUTE_FINANCE'.\n"
        "2. If it's image, video, music generation, branding, or creative design, reply exactly 'ROUTE_MARKETING'.\n"
        "3. If it's useless garbage that costs money, reply 'REJECTED: [reason]'. "
    )
    decision = (await llm.ainvoke(charlie_prompt)).content
    
    if "REJECTED" in decision:
        status_container.error(f"👔 **Charlie:** {decision}")
        return f"Transaction Blocked by Risk Management: {decision}"

    if "ROUTE_FINANCE" in decision:
        status_container.success("👔 **Charlie:** Approved for Research. Routing to Alice.")
        status_container.write("👩‍💼 **Alice:** Evaluating parameters...")
        alice_check = f"""You are Alice, Research Manager. Read this transcript:
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
            
        status_container.write("👩‍💼 **Alice:** Reviewing Layer 5 Roster...")
        alice_routing_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            "You are Alice, managing a team of Layer 5 specialists. Based on the transcript, select the ONE best specialist for the job. "
            "If the user asks for someone by name, you MUST pick them. Otherwise, pick the best fit.\n\n"
            "SPECIALISTS:\n"
            "- Eve (OSINT, Web Scraping, PDF Parsing, Breaking News)\n"
            "- Gordon (Quantitative Analysis, Spot Prices, Trends)\n"
            "- Olivia (Fundamental Analysis, Deep reading)\n\n"
            "Reply with EXACTLY the specialist name (e.g., EVE)."
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
        department = "FINANCE"
        st.session_state.current_l5_artist = specialist_name

    elif "ROUTE_MARKETING" in decision:
        status_container.success("👔 **Charlie:** Approved for Creative. Routing to Diana.")
        status_container.write("👩‍🎨 **Diana:** Evaluating creative requirements...")
        diana_check = f"""You are Diana, Creative Director. Read this transcript:
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

        status_container.write("👩‍🎨 **Diana:** Reviewing Layer 5 Specialist Roster...")
        diana_routing_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            "You are Diana, managing a team of Layer 5 specialists. Based on the transcript, select the ONE best specialist for the job. "
            "If the user asks for someone by name, you MUST pick them. Otherwise, pick the best fit.\n\n"
            "IMAGE GENERATORS:\n"
            "- Ellen (Organic, nature-inspired, emotional art)\n"
            "- Marcus (Cyberpunk, neon, sci-fi, gritty)\n"
            "- Sophia (Minimalist, corporate, clean vector)\n\n"
            "VIDEO DIRECTORS:\n"
            "- Victor (Cinematic, epic, Hollywood-style)\n"
            "- Chloe (Documentary, raw, handheld, realistic)\n"
            "- Leo (Stylized, animated, abstract motion)\n\n"
            "AUDIO ENGINEERS:\n"
            "- Melody (Acoustic, folk, vocal-heavy, emotional)\n"
            "- Jax (EDM, synthwave, electronic, high-energy)\n"
            "- Harmon (Classical, orchestral, cinematic scores)\n\n"
            "Reply with EXACTLY two things separated by a comma: MEDIA_TYPE (IMAGE, VIDEO, or MUSIC), SPECIALIST_NAME."
        )
        routing_decision = (await llm.ainvoke(diana_routing_prompt)).content.strip().upper()
        
        try:
            specialist_type, specialist_name = [x.strip() for x in routing_decision.split(",")]
        except ValueError:
            specialist_type = "IMAGE"
            specialist_name = "ELLEN" # Fallback
            
        status_container.write(f"👩‍🎨 **Diana:** Assigning task to Layer 5 Specialist: {specialist_name.capitalize()}...")

        diana_brief_prompt = (
            f"Transcript:\n{chat_transcript}\n"
            f"Write a vivid, 2-sentence creative brief for {specialist_name.capitalize()}, your Layer 5 {specialist_type} specialist. "
            f"Ensure the brief leans heavily into their specific artistic style."
        )
        diana_brief = (await llm.ainvoke(diana_brief_prompt)).content
        status_container.info(f"📋 **Brief for {specialist_name.capitalize()}:** {diana_brief}")
        department = "MARKETING"
        st.session_state.current_l5_artist = specialist_name.capitalize()

    final_data = ""
    try:
        async with sse_client(url, timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()

                if department == "FINANCE":
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
                        
                    final_data = response["text"] + "\n\n*(Verified by L6 Consensus Auditor)*"

                elif department == "MARKETING":
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

                    tool_output = response["text"]
                    final_data = f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {diana_brief}\n\n**Layer 5 Specialist Execution ({st.session_state.current_l5_artist}):**\n{tool_output}\n\n*(Media Approved by L6 Quality Control)*"

    except Exception as e:
        final_data = f"⚠️ **Network Interrupted.**\n\nConnection closed. Log: {e}"

    # FAISS VECTOR MEMORY SAVE (NON-PAYWALL - e.g. Free responses if any)
    if "Network Interrupted" not in final_data and "Charlie:" not in final_data and "Payment Failed" not in final_data and "402 Payment Required" not in final_data:
        if vector_db:
             new_doc = Document(page_content=final_data, metadata={"query": user_prompt[:100]})
             vector_db.add_documents([new_doc])
             vector_db.save_local(FAISS_INDEX_PATH)
        
    return final_data

# --- UI MAIN LAYOUT & MEDIA RENDERING ---
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
    st.info(f"💡 The AI Front Desk cannot complete this request. Would you like to authorize {cost}+ SATS to wake up the {dept_name} team?")
    
    col1, col2 = st.columns(2)
    if col1.button(f"💎 Yes, Fund {dept_name}"):
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
elif user_submission := st.chat_input("Enter your research or design mission...", accept_file="multiple", file_type=["pdf"]):
    if not st.session_state.api_key:
        st.warning("🛑 API key required. Please provide it in the sidebar.")
    else:
        st.session_state.upsell_type = None
        
        # Streamlit 1.43+ natively returns a dict-like ChatInputValue when accept_file is used
        if hasattr(user_submission, "text") or isinstance(user_submission, dict):
            prompt = getattr(user_submission, "text", "") if hasattr(user_submission, "text") else user_submission.get("text", "")
            attached_files = getattr(user_submission, "files", []) if hasattr(user_submission, "files") else user_submission.get("files", [])
        else:
            prompt = str(user_submission)
            attached_files = []
            
        # Save uploaded PDFs to the root folder so Eve's backend glob.glob("*.pdf") can find them!
        for uploaded_file in attached_files:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
        # Inject file context so the LLM knows a file is present!
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
                    bob_prompt = (
                        "You are Bob, the polite Front Desk Receptionist at a specialized Agency. "
                        "You provide standard, free-tier general knowledge answers to the user based on the transcript below.\n"
                        "You are aware that the company has a 6-Layer hierarchy. Layer 5 contains our highly-paid specialists: "
                        "Eve, Gordon, and Olivia (Research), Ellen, Marcus, and Sophia (Images), Victor, Chloe, and Leo (Video), and Melody, Jax, and Harmon (Audio). "
                        "CRITICAL INSTRUCTION: If the user asks for complex work, uploads a file, or asks for a specialist by name, politely explain that you are just the receptionist. "
                        "Instruct them to click the 💎 'Fund Team' button below your message so Alice or Diana can assign the specialist.\n\n"
                        f"Transcript:\n{chat_transcript}"
                    )
                    standard_resp = "🛎️ **Bob (Front Desk):**\n\n" + llm.invoke(bob_prompt).content
                    
                st.markdown(standard_resp)
                st.session_state.messages.append({"role": "assistant", "content": standard_resp})
                
                # --- UPDATED CHARLIE PROMPT TO CATCH PDFS! ---
                charlie_prompt = (
                    f"You are Charlie, the Routing Officer.\nTranscript:\n{chat_transcript}\n"
                    "Does this request realistically require financial/market research, web scraping, reading/reviewing/summarizing an attached file or PDF ('ROUTE_FINANCE') or generating an image, video, or music ('ROUTE_MARKETING') or neither ('NONE')? Reply with exactly one of those three keywords. CRITICAL: If a file is attached, you MUST reply 'ROUTE_FINANCE'."
                )
                decision = llm.invoke(charlie_prompt).content
                
                if "ROUTE_FINANCE" in decision:
                    st.session_state.upsell_type = "finance"
                    st.session_state.upsell_cost = 75
                elif "ROUTE_MARKETING" in decision:
                    st.session_state.upsell_type = "marketing"
                    st.session_state.upsell_cost = 100 
                    
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