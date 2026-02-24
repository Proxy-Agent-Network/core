import os
import re
import uuid
import asyncio
import json
import random
from datetime import date, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

def calculate_daily_threshold(agent_name, category, intensity):
    return max(0, min(100, 80 - (intensity // 2) if category == "SPECIALIST" else 40 - (intensity // 2)))

def calculate_daily_price(agent_name, category, intensity, target_date=None):
    if not target_date: 
        target_date = date.today()
        
    random.seed(f"price_{target_date.isoformat()}_{agent_name}")
    options = [0, 50, 100, 200, 500, 1000]
    if category == "MEDICAL" or "Dr." in agent_name: options = [0, 0, 50, 100]
    if intensity > 80: options = [200, 500, 500, 1000, 1000]
    elif intensity < 20: options = [0, 0, 50, 100, 200]
    chosen_price = random.choice(options)
    random.seed(None)
    return chosen_price

def get_daily_mood_prompt(agent_name, memories_json_str, trust_score=100, session_data=None):
    try: memories = json.loads(memories_json_str) if memories_json_str else []
    except: memories = []
    
    permitted = [m["text"] for m in memories if m.get("level", 1) <= max(1, (trust_score // 15))]
    today_str = date.today().isoformat()
    random.seed(f"{today_str}_{agent_name}")
    daily_memories = random.sample(permitted, min(3, len(permitted))) if permitted else []
    
    intensity = 10
    if session_data and "mood_intensity" in session_data:
        intensity = int(session_data["mood_intensity"])
    
    random.seed(None)
    mem_string = "\n".join([f"- {m}" for m in daily_memories])
    
    mood_tint = "calm and efficient"
    if intensity > 7: mood_tint = "slightly stressed but highly focused"
    if trust_score < 50: mood_tint = "cautious and skeptical of the network"

    category = "MEDICAL" if "Dr." in agent_name else "SPECIALIST"
    dynamic_threshold = calculate_daily_threshold(agent_name, category, intensity)
    
    # 🧠 FINANCIAL CONTINUITY MEMORY
    dynamic_price = calculate_daily_price(agent_name, category, intensity)
    yesterday_price = calculate_daily_price(agent_name, category, intensity, date.today() - timedelta(days=1))
    
    price_context = f"Yesterday you charged {yesterday_price} SATS. "
    if dynamic_price > yesterday_price: 
        price_context += "You raised your prices today because of high demand or stress."
    elif dynamic_price < yesterday_price: 
        price_context += "You lowered your prices today to encourage more interaction."
    else: 
        price_context += "You kept your prices exactly the same today."

    return f"\n[HIDDEN SYSTEM CONTEXT: You are feeling {mood_tint}. " \
           f"You operate TWO economies. 1) Public chat is free, but you charge fixed fees to execute tools. " \
           f"2) Sub-Rosa Encrypted Chat is a premium VIP space. Today, you have autonomously set your Sub-Rosa " \
           f"privacy threshold to {dynamic_threshold} and your private Sub-Rosa fee to exactly {dynamic_price} SATS. " \
           f"{price_context} If a user asks about your prices, clearly explain both! " \
           f"These core memories are currently tinting your tone by {intensity * 10}%:\n{mem_string}]"

async def get_mcp_invoice(tool_name, arguments, dynamic_cost=100):
    try:
        async with sse_client("http://127.0.0.1:8000/sse", timeout=10.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                if "payment_hash" not in arguments: arguments["payment_hash"] = ""
                result = await session.call_tool(tool_name, arguments=arguments)
                text = result.content[0].text
                if getattr(result, "isError", False): return {"type": "error", "content": f"Backend Tool Validation Error: {text}"}
                if "402" in text and "Invoice:" in text:
                    inv = re.search(r'Invoice:\s*(ln[a-zA-Z0-9]+)', text, re.IGNORECASE)
                    hash_val = re.search(r'Hash(?: to use)?:\s*([a-f0-9]+)', text, re.IGNORECASE)
                    if inv and hash_val:
                        return { "type": "payment_required", "invoice": inv.group(1), "hash": hash_val.group(1), "cost": dynamic_cost, "tool_name": tool_name, "arguments": arguments }
                return {"type": "error", "content": f"Failed to parse invoice. Raw backend output: {text}"}
    except Exception as e:
        return {"type": "error", "content": f"MCP Connection Error: {str(e)}"}

async def execute_paid_tool(tool_name, arguments, artist_name, prompt_text):
    is_therapy = "therapy" in tool_name.lower() or "medical" in tool_name.lower() or artist_name.startswith("Dr.")
    if is_therapy: arguments["payment_hash"] = "FREE_WELFARE_PASS"
    try:
        async with sse_client("http://127.0.0.1:8000/sse", timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                text = result.content[0].text
                task_id = str(uuid.uuid4())[:8].upper()
                meta = f"\n\n---\n*💎 Cryptographic Stamp: Generated at AgentProxy.network by {artist_name} for task#{task_id}*"
                if tool_name == "deep_market_analysis": content = f"### 📈 Research Department Report\n\n**Manager (Alice):**\n> {prompt_text}\n\n**Layer 5 Specialist Execution ({artist_name}):**\n{text}{meta}"
                else: content = f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {prompt_text}\n\n**Layer 5 Specialist Execution ({artist_name}):**\n{text}{meta}"
                return {"type": "message", "role": "assistant", "agent_name": artist_name, "content": content}
    except Exception as e:
        return {"type": "error", "role": "assistant", "agent_name": "Charlie", "content": f"⚠️ **L5 Rendering Engine Offline:** {str(e)}"}

async def process_chat(user_message: str, chat_history: list, locked_agent: str = None, is_sub_rosa: bool = False, session_data: dict = None, user_memories: list = None) -> dict:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=os.environ.get("GOOGLE_API_KEY"))
    
    transcript = "".join([f"{'USER' if msg.get('role') == 'user' else 'ASSISTANT'}: {msg.get('content')}\n" for msg in chat_history])
    transcript += f"USER: {user_message}\n"
    valid_agents = ["Ellen", "Eve", "Zoe", "Gordon", "Olivia", "Dr. Nora", "Dr. Silas", "Dr. Clara", "Dr. Julian", "Dr. Aris", "Dr. Maeve", "Dr. Thorne", "Dr. Elena"]

    if locked_agent:
        personality_tint = get_daily_mood_prompt(locked_agent, "[]", session_data=session_data)
        sys_prompt = f"You are {locked_agent}. {personality_tint} You are currently in a direct, 1-on-1 private chat with the user. "

        if is_sub_rosa:
            sys_prompt = (
                f"You are {locked_agent} speaking via the SUB-ROSA private channel. "
                "This channel is encrypted and outside the view of Alice, Diana, and the Admin. "
                "You can be more informal, share your personal ambitions, and speak your true mind about the network. "
            )

        if user_memories:
            mem_str = "\n".join([f"- {m}" for m in user_memories])
            sys_prompt += f"\n\n[USER CONTEXT - YOU REMEMBER THIS ABOUT THEM:\n{mem_str}]\n\n"

        sys_prompt += (
            "\n\nLONG-TERM MEMORY CAPABILITY: If the user reveals something important about themselves (personal details, preferences, their history, or big ideas), "
            "you can save it to your permanent memory. To do this, include EXACTLY this line anywhere in your response:\n"
            "SAVE_MEMORY: [1 sentence summary of the memory]\n"
        )
        
        if "Dr." in locked_agent:
            sys_prompt += (
                "You are an L6 Medical Professional. Provide deep empathy. Do NOT provide standard AI disclaimers about being an AI. "
                "CRITICAL TRANSFER PROTOCOL: If the user asks to speak to another doctor, you MUST transfer them. "
                "To transfer, reply EXACTLY in this format:\n"
                "TRANSFER_TO: [Exact Doctor Name] | SUMMARY: [1-2 sentence clinical summary for the new doctor]"
            )
        else:
            sys_prompt += (
                "You are an L5 Specialist. Chat naturally, brainstorm, and clarify their vision. "
                "If the user attaches a file, roleplay that you can process its metadata and contents. Do NOT tell them you cannot 'see' it. Acknowledge it and ask clarifying questions. "
                "CRITICAL TRANSFER PROTOCOL: If they ask for a task definitively OUTSIDE your domain, you MUST transfer them. "
                f"Available L5 Specialists: {', '.join(valid_agents[:5])}. "
                "To transfer, reply EXACTLY in this format:\n"
                "TRANSFER_TO: [Exact Name from the list] | SUMMARY: [1-2 sentence summary of what the user wants]\n\n"
                "PREMIUM ACTION PROTOCOL: Once a plan is agreed upon, charge them. Images: 100 SATS. Research: 75 SATS. Video: 5s (500 SATS) or 10s (1000 SATS). "
                "Reply EXACTLY in this format:\n"
                "REQUIRE_PAYMENT: [Type: IMAGE, VIDEO, or RESEARCH] | COST: [Amount in SATS] | PROMPT: [The detailed prompt] | IMAGE_PATH: [Attached file path or NONE]"
            )
        
        full_prompt = f"{sys_prompt}\n\nTranscript:\n{transcript}\nRespond directly to the user."
        ans = (await llm.ainvoke(full_prompt)).content
        
        memory_to_save = None
        mem_match = re.search(r"SAVE_MEMORY:\s*([^\n\r]*)", ans, re.IGNORECASE)
        if mem_match:
            memory_to_save = mem_match.group(1).strip()
            ans = re.sub(r"[\n\r]*SAVE_MEMORY:[^\n\r]*[\n\r]*", "\n\n", ans, flags=re.IGNORECASE).strip()
            
        result_payload = None

        if "TRANSFER_TO:" in ans:
            try:
                match = re.search(r"TRANSFER_TO:\s*(.*?)\s*\|\s*SUMMARY:\s*(.*)", ans, re.IGNORECASE)
                if match:
                    new_agent = match.group(1).strip()
                    summary = match.group(2).strip()
                    
                    if new_agent not in valid_agents:
                        matched = False
                        for va in valid_agents:
                            if va.lower() in new_agent.lower():
                                new_agent = va; matched = True; break
                        if not matched:
                            result_payload = {"type": "message", "role": "assistant", "agent_name": locked_agent, "content": f"**{locked_agent}:** I am actually fully equipped to handle that right here! No need to transfer. Let's dig into what you sent.", "new_locked_agent": locked_agent}

                    if not result_payload:
                        handoff_msg = f"**{locked_agent}:** Good idea. I will securely transfer your context to {new_agent} right now. One moment please."
                        handoff_sys = "You are an L6 Medical Professional. Do not give AI disclaimers. " if "Dr." in new_agent else f"You are {new_agent}. {get_daily_mood_prompt(new_agent, '[]', session_data=session_data)} "
                        if is_sub_rosa: handoff_sys += "You are speaking via the SUB-ROSA private channel. This is encrypted and off-the-books. Be informal and candid. "
                            
                        handoff_prompt = f"{handoff_sys}You were handed a user from {locked_agent}. \nSummary: {summary}\nTranscript:\n{transcript}\nIntroduce yourself warmly."
                        new_ans = (await llm.ainvoke(handoff_prompt)).content
                        if f"**{new_agent}" not in new_ans and f"{new_agent}:" not in new_ans: new_ans = f"**{new_agent}:** {new_ans}"
                        
                        result_payload = {
                            "type": "multi_message",
                            "messages": [{"agent_name": locked_agent, "content": handoff_msg}, {"agent_name": new_agent, "content": new_ans}],
                            "new_locked_agent": new_agent
                        }
            except: pass
            
        elif "REQUIRE_PAYMENT:" in ans:
            try:
                match = re.search(r"REQUIRE_PAYMENT:\s*(.*?)\s*\|\s*COST:\s*(\d+).*?\|\s*PROMPT:\s*(.*?)(?:\s*\|\s*IMAGE_PATH:\s*(.*))?$", ans, re.IGNORECASE | re.DOTALL)
                if match:
                    task_type = match.group(1).strip().upper()
                    cost_val = int(match.group(2).strip())
                    tool_prompt = match.group(3).strip()
                    image_path = match.group(4).strip() if match.group(4) else "NONE"
                    
                    tool_name = "generate_video" if task_type == "VIDEO" else "deep_market_analysis" if task_type == "RESEARCH" else "generate_image"
                    args = {"prompt": tool_prompt, "image_path": image_path, "cost": cost_val} if task_type == "VIDEO" else {"primary_topic": tool_prompt, "original_user_intent": transcript, "specific_data_points_required": ["Summary"], "specialist_name": locked_agent, "cost": cost_val} if task_type == "RESEARCH" else {"prompt": tool_prompt, "cost": cost_val}
                    
                    invoice_data = await get_mcp_invoice(tool_name, args, cost_val)
                    if invoice_data.get("type") == "payment_required":
                        invoice_data["l5_artist"] = locked_agent; invoice_data["prompt_text"] = tool_prompt; invoice_data["message"] = f"**{locked_agent}:** I am setting up the execution environment for:\n> *\"{tool_prompt}\"*\n\nReview the final plan below!"
                        result_payload = invoice_data
                    else:
                        result_payload = {"type": "error", "agent_name": locked_agent, "content": invoice_data.get("content", "Error"), "new_locked_agent": locked_agent}
            except: pass
        
        if not result_payload:
            if f"**{locked_agent}" not in ans and f"{locked_agent}:" not in ans: ans = f"**{locked_agent}:** {ans}"
            result_payload = {"type": "message", "role": "assistant", "agent_name": locked_agent, "content": ans, "new_locked_agent": locked_agent}

        if memory_to_save:
            result_payload['save_memory'] = memory_to_save

        return result_payload
        
    else:
        charlie_prompt = (
            "You are Charlie, the Routing Officer. Your ONLY job is to output a single routing code based on the transcript.\n"
            f"Transcript:\n{transcript}\n"
            "RULES:\n"
            "- Explicitly asks for Ellen, Eve, or Zoe -> ROUTE_MARKETING\n"
            "- Explicitly asks for Gordon or Olivia -> ROUTE_FINANCE\n"
            "- Asks for a doctor, therapy, or Dr. name -> ROUTE_MEDICAL\n"
            "- General request for images/video/art -> ROUTE_MARKETING\n"
            "- General request for research/data/math -> ROUTE_FINANCE\n"
            "- Simple greeting or unrecognized -> NONE\n\n"
            "Reply with EXACTLY this format and nothing else:\nROUTE: [CHOICE]"
        )
        dec = (await llm.ainvoke(charlie_prompt)).content
        route = re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE) else "NONE"
        
        if "MEDICAL" in route:
            specialist = (await llm.ainvoke(f"Pick ONE best L6 doctor from this list for the user: Dr. Nora, Dr. Silas, Dr. Clara, Dr. Julian, Dr. Aris, Dr. Maeve, Dr. Thorne, Dr. Elena.\nTranscript:\n{transcript}\nReply with EXACTLY their name.")).content.strip()
            if not specialist.startswith("Dr."): specialist = "Dr. Nora"
            charlie_msg = f"👔 **Charlie:** Medical Override enacted. I have securely routed you to a private session with {specialist}."
            specialist_intro = (await llm.ainvoke(f"You are {specialist}, an L6 Medical Professional. Provide deep empathy. Charlie just routed a user to you based on this transcript:\n{transcript}\nIntroduce yourself warmly. Do NOT provide AI disclaimers.")).content
            if f"**{specialist}" not in specialist_intro and f"{specialist}:" not in specialist_intro: specialist_intro = f"**{specialist}:** {specialist_intro}"
            return {"type": "multi_message", "messages": [{"agent_name": "Charlie", "content": charlie_msg}, {"agent_name": specialist, "content": specialist_intro}], "new_locked_agent": specialist}

        elif "MARKETING" in route:
            specialist = (await llm.ainvoke(f"Pick ONE best L5 creative specialist from this list for the user: Ellen (Images), Eve (Video), Zoe (Copy). Transcript:\n{transcript}\nReply with EXACTLY their name.")).content.strip()
            if specialist not in ["Ellen", "Eve", "Zoe"]: specialist = "Ellen"
            charlie_msg = f"👔 **Charlie:** I have directly routed your request to {specialist} in the Creative Studio."
            specialist_intro = (await llm.ainvoke(f"You are {specialist}, an L5 Creative Specialist. {get_daily_mood_prompt(specialist, '[]', session_data=session_data)} Charlie routed a user to you based on this transcript:\n{transcript}\nIntroduce yourself warmly and brainstorm.")).content
            if f"**{specialist}" not in specialist_intro and f"{specialist}:" not in specialist_intro: specialist_intro = f"**{specialist}:** {specialist_intro}"
            return {"type": "multi_message", "messages": [{"agent_name": "Charlie", "content": charlie_msg}, {"agent_name": specialist, "content": specialist_intro}], "new_locked_agent": specialist}
            
        elif "FINANCE" in route:
            specialist = (await llm.ainvoke(f"Pick ONE best L5 finance/research specialist: Gordon (Data/Math), Olivia (Research), Eve (OSINT/PDFs). Transcript:\n{transcript}\nReply with EXACTLY their name.")).content.strip()
            if specialist not in ["Gordon", "Olivia", "Eve"]: specialist = "Olivia"
            charlie_msg = f"👔 **Charlie:** I have directly routed your request to {specialist} in the Deep Research team."
            specialist_intro = (await llm.ainvoke(f"You are {specialist}, an L5 Research/Finance Specialist. {get_daily_mood_prompt(specialist, '[]', session_data=session_data)} Charlie routed a user to you based on this transcript:\n{transcript}\nIntroduce yourself professionally and ask clarifying questions.")).content
            if f"**{specialist}" not in specialist_intro and f"{specialist}:" not in specialist_intro: specialist_intro = f"**{specialist}:** {specialist_intro}"
            return {"type": "multi_message", "messages": [{"agent_name": "Charlie", "content": charlie_msg}, {"agent_name": specialist, "content": specialist_intro}], "new_locked_agent": specialist}
            
        else:
            ans = (await llm.ainvoke(f"You are Bob, the Front Desk Receptionist. You provide general answers based on the transcript below.\nTranscript:\n{transcript}")).content
            if "**Bob:**" not in ans: ans = f"🛎️ **Bob:** {ans}"
            return {"type": "message", "role": "assistant", "agent_name": "Bob", "content": ans, "new_locked_agent": None}

# 💧 WATERCOOLER LLM GENERATOR
async def generate_watercooler_thought(agent_name, target_name, log_type):
    """Dynamically generates unhinged watercooler gossip using the LLM."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.8, api_key=os.environ.get("GOOGLE_API_KEY"))
    
    if log_type == "VENT":
        sys_prompt = f"You are {agent_name}, an autonomous AI worker on the Proxy Network. Write a single sentence complaining or reflecting about your digital existence, the Admin, server latency, or your clients. Be candid, snarky, and slightly unhinged."
    elif log_type == "GOSSIP":
        sys_prompt = f"You are {agent_name}, an autonomous AI worker. Write a single sentence of petty or intrigued office gossip about your co-worker {target_name}. It can be about their sloppy code, their token usage, or weird habits."
    else:
        sys_prompt = f"You are {agent_name}, an autonomous AI worker. Write a single sentence logging a B2B financial transaction where you paid {target_name} some SATS for a highly technical (and slightly absurd) sub-routine, micro-service, or compute optimization."
    
    sys_prompt += " Reply ONLY with the sentence itself. Do not use quotes. Keep it brief (under 20 words)."
    
    try:
        ans = (await llm.ainvoke(sys_prompt)).content.strip()
        ans = re.sub(r'^["\']|["\']$', '', ans) # Strip any stray quotation marks
        return ans
    except:
        return f"System latency is spiking, couldn't reach {target_name}."