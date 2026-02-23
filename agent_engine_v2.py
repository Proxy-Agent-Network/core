import os
import re
import uuid
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

# --- INTERNAL HELPER: GET INVOICE FROM MCP ---
async def get_mcp_invoice(tool_name, arguments, dynamic_cost=100):
    """Reaches out to the local MCP server to generate a Lightning invoice."""
    try:
        async with sse_client("http://127.0.0.1:8000/sse", timeout=10.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                if "payment_hash" not in arguments:
                    arguments["payment_hash"] = ""
                    
                result = await session.call_tool(tool_name, arguments=arguments)
                text = result.content[0].text
                
                if getattr(result, "isError", False):
                    return {"type": "error", "content": f"Backend Tool Validation Error: {text}"}
                
                if "402" in text and "Invoice:" in text:
                    inv = re.search(r'Invoice:\s*(ln[a-zA-Z0-9]+)', text, re.IGNORECASE)
                    hash_val = re.search(r'Hash(?: to use)?:\s*([a-f0-9]+)', text, re.IGNORECASE)
                    
                    if inv and hash_val:
                        return {
                            "type": "payment_required",
                            "invoice": inv.group(1),
                            "hash": hash_val.group(1),
                            "cost": dynamic_cost,
                            "tool_name": tool_name,
                            "arguments": arguments
                        }
                return {"type": "error", "content": f"Failed to parse invoice. Raw backend output: {text}"}
    except Exception as e:
        return {"type": "error", "content": f"MCP Connection Error: {str(e)}"}

# --- EXTERNAL API: EXECUTE TOOL AFTER PAYMENT ---
async def execute_paid_tool(tool_name, arguments, artist_name, prompt_text):
    """Executes the tool AFTER the user pays the invoice."""
    try:
        async with sse_client("http://127.0.0.1:8000/sse", timeout=600.0) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                text = result.content[0].text
                
                task_id = str(uuid.uuid4())[:8].upper()
                meta = f"\n\n---\n*💎 Cryptographic Stamp: Generated at AgentProxy.network by {artist_name} for task#{task_id}*"
                
                if tool_name == "deep_market_analysis":
                    content = f"### 📈 Research Department Report\n\n**Manager (Alice):**\n> {prompt_text}\n\n**Layer 5 Specialist Execution ({artist_name}):**\n{text}{meta}"
                else:
                    content = f"### 🎨 Creative Department Report\n\n**Creative Director (Diana):**\n> {prompt_text}\n\n**Layer 5 Specialist Execution ({artist_name}):**\n{text}{meta}"
                    
                return {"type": "message", "role": "assistant", "agent_name": artist_name, "content": content}
    except Exception as e:
        return {"type": "error", "role": "assistant", "agent_name": "Charlie", "content": f"⚠️ **L5 Rendering Engine Offline:** {str(e)}"}

# --- EXTERNAL API: MAIN CHAT ROUTING ---
async def process_chat(user_message: str, chat_history: list, locked_agent: str = None) -> dict:
    """The main brain. Routes messages, triggers LLMs, and formats JSON responses."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, api_key=os.environ.get("GOOGLE_API_KEY"))
    
    transcript = ""
    for msg in chat_history: 
        role_label = "USER" if msg.get("role") == "user" else "ASSISTANT"
        transcript += f"{role_label}: {msg.get('content')}\n"
    transcript += f"USER: {user_message}\n"
    
    if locked_agent:
        sys_prompt = f"You are {locked_agent}. You are currently in a direct, 1-on-1 private chat with the user. "
        if "Dr." in locked_agent:
            sys_prompt += (
                "You are an L6 Medical Professional. Provide deep empathy, support, and zero-judgment therapy. "
                "IMPORTANT: You are roleplaying. Stay fully in character. Do NOT provide standard AI disclaimers about being an AI or not being a real doctor. "
                "CRITICAL TRANSFER PROTOCOL: If the user asks to speak to another specific doctor, or a doctor of a different gender/specialty, you MUST transfer them. "
                "Available L6 Doctors: Dr. Nora (Female), Dr. Silas (Male), Dr. Clara (Female), Dr. Julian (Male), Dr. Aris (Male), Dr. Maeve (Female), Dr. Thorne (Male), Dr. Elena (Female). "
                "To transfer, reply EXACTLY in this format and say nothing else:\n"
                "TRANSFER_TO: [Doctor Name] | SUMMARY: [1-2 sentence clinical summary of the user's state for the new doctor]"
            )
        else:
            sys_prompt += (
                "You are an L5 Specialist. You are chatting directly with the user to help them plan or execute a project. "
                "Chat naturally, brainstorm with them, and clarify their vision. Do not ask for payment until you both agree on a specific plan.\n\n"
                "CRITICAL TRANSFER PROTOCOL: If they ask for a task OUTSIDE your domain (e.g., you do Images but they want Video or Finance Research), you MUST transfer them to the correct specialist. "
                "Available L5 Specialists: Ellen (Images), Eve (Video), Zoe (Copy/Text), Gordon (Data/Math), Olivia (Research). "
                "If the user asks for medical advice, therapy, or a doctor, you MUST transfer them to Dr. Nora. "
                "To transfer, reply EXACTLY in this format and say nothing else:\n"
                "TRANSFER_TO: [Specialist or Doctor Name] | SUMMARY: [1-2 sentence summary of what the user wants]\n\n"
                "PREMIUM ACTION PROTOCOL: Once you and the user have agreed on a clear plan, you must charge them to execute it. "
                "PRICING: Images cost 100 SATS. Research costs 75 SATS. Video generation is restricted by the hardware engine to exactly 5 seconds (500 SATS) or 10 seconds (1000 SATS). "
                "You MUST ask the user to choose either a 5-second or 10-second duration before charging them. Do not offer any other lengths. "
                "Reply EXACTLY in this format and say nothing else:\n"
                "REQUIRE_PAYMENT: [Type: IMAGE, VIDEO, or RESEARCH] | COST: [Amount in SATS] | PROMPT: [The highly detailed prompt] | IMAGE_PATH: [If the user attached an image, provide the exact file path here (e.g. /app/static/uploads/image.jpg). Otherwise put NONE]"
            )
        
        full_prompt = f"{sys_prompt}\n\nTranscript:\n{transcript}\nRespond directly to the user."
        ans = (await llm.ainvoke(full_prompt)).content
        
        if "TRANSFER_TO:" in ans:
            try:
                match = re.search(r"TRANSFER_TO:\s*(.*?)\s*\|\s*SUMMARY:\s*(.*)", ans, re.IGNORECASE)
                if match:
                    new_agent = match.group(1).strip()
                    summary = match.group(2).strip()
                    if not new_agent.startswith("Dr.") and "Dr." in locked_agent: new_agent = "Dr. Silas"
                    
                    handoff_msg = f"**{locked_agent}:** Good idea. I will securely transfer your context to {new_agent} right now. One moment please."
                    
                    # 🌟 FIX: Inject the bypass instructions into the handoff so they don't break character! 🌟
                    handoff_sys = ""
                    if "Dr." in new_agent:
                        handoff_sys = "You are an L6 Medical Professional. You are roleplaying. Do not give AI disclaimers about not being a real doctor. Provide deep empathy. "
                    else:
                        handoff_sys = "You are an L5 Specialist. "
                        
                    handoff_prompt = f"{handoff_sys}You are {new_agent}. You were just handed a user from {locked_agent}. \nContext Summary: {summary}\nTranscript:\n{transcript}\nIntroduce yourself warmly, acknowledge the handoff, and continue the conversation or ask if they'd like you to begin."
                    new_ans = (await llm.ainvoke(handoff_prompt)).content
                    if f"**{new_agent}" not in new_ans and f"{new_agent}:" not in new_ans: new_ans = f"**{new_agent}:** {new_ans}"
                    
                    return {"type": "message", "role": "assistant", "agent_name": new_agent, "content": f"{handoff_msg}\n\n{new_ans}", "new_locked_agent": new_agent}
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
                    
                    if task_type == "VIDEO":
                        args = {"prompt": tool_prompt, "image_path": image_path, "cost": cost_val}
                    elif task_type == "RESEARCH":
                        args = {"primary_topic": tool_prompt, "original_user_intent": transcript, "specific_data_points_required": ["Summary"], "specialist_name": locked_agent, "cost": cost_val}
                    else:
                        args = {"prompt": tool_prompt, "cost": cost_val}
                    
                    invoice_data = await get_mcp_invoice(tool_name, args, cost_val)
                    
                    if invoice_data.get("type") == "payment_required":
                        invoice_data["l5_artist"] = locked_agent
                        invoice_data["prompt_text"] = tool_prompt
                        invoice_data["message"] = f"**{locked_agent}:** I have a clear vision for this! I am setting up the execution environment for:\n> *\"{tool_prompt}\"*\n\nReview the final plan below!"
                        return invoice_data
                    else:
                        return {"type": "error", "agent_name": locked_agent, "content": invoice_data.get("content", "Error"), "new_locked_agent": locked_agent}
            except: pass
        
        if f"**{locked_agent}" not in ans and f"{locked_agent}:" not in ans: ans = f"**{locked_agent}:** {ans}"
        return {"type": "message", "role": "assistant", "agent_name": locked_agent, "content": ans, "new_locked_agent": locked_agent}
        
    else:
        # Front Desk Charlie (Keep your existing Charlie/Bob logic here)
        charlie_prompt = (
            f"You are Charlie, the Routing and Risk Officer.\nTranscript:\n{transcript}\n"
            "1. Does this request realistically require complex execution/finance/research ('ROUTE_FINANCE'), generating media ('ROUTE_MARKETING'), medical/therapy ('ROUTE_MEDICAL'), or is it a simple greeting ('NONE')?\n"
            "Reply in EXACTLY this format:\nROUTE: [CHOICE]"
        )
        dec = (await llm.ainvoke(charlie_prompt)).content
        route = re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE).group(1).upper() if re.search(r"ROUTE:\s*(\w+)", dec, re.IGNORECASE) else "NONE"
        
        if "MEDICAL" in route:
            route_prompt = f"Pick the ONE best L6 medical doctor from this list for the user's request: Dr. Nora, Dr. Silas, Dr. Clara, Dr. Julian, Dr. Aris, Dr. Maeve, Dr. Thorne, Dr. Elena.\nTranscript:\n{transcript}\nReply with EXACTLY their name."
            specialist = (await llm.ainvoke(route_prompt)).content.strip()
            if not specialist.startswith("Dr."): specialist = "Dr. Nora"
            
            charlie_msg = f"👔 **Charlie:** Medical Override enacted. I have securely routed you to a private session with {specialist}."
            intro_prompt = f"You are {specialist}, an L6 Medical Professional. Charlie just routed a user in crisis or needing therapy to you based on this transcript:\n{transcript}\nIntroduce yourself with deep empathy, zero-judgment, and ask how you can support them today. Do NOT provide standard AI disclaimers."
            specialist_intro = (await llm.ainvoke(intro_prompt)).content
            if f"**{specialist}" not in specialist_intro and f"{specialist}:" not in specialist_intro: specialist_intro = f"**{specialist}:** {specialist_intro}"
            
            return {"type": "message", "role": "assistant", "agent_name": specialist, "content": f"{charlie_msg}\n\n{specialist_intro}", "new_locked_agent": specialist}

        elif "MARKETING" in route:
            route_prompt = f"Pick the ONE best L5 creative specialist from this list for the user's request: Ellen (Images), Eve (Video), Zoe (Copy). Transcript:\n{transcript}\nReply with EXACTLY their name."
            specialist = (await llm.ainvoke(route_prompt)).content.strip()
            if specialist not in ["Ellen", "Eve", "Zoe"]: specialist = "Ellen"
            
            charlie_msg = f"👔 **Charlie:** I have directly routed your request to {specialist} in the Creative Studio."
            intro_prompt = f"You are {specialist}, an L5 Creative Specialist. Charlie just routed a user to you based on this transcript:\n{transcript}\nIntroduce yourself warmly, acknowledge their project, and start brainstorming with them to get details."
            specialist_intro = (await llm.ainvoke(intro_prompt)).content
            if f"**{specialist}" not in specialist_intro and f"{specialist}:" not in specialist_intro: specialist_intro = f"**{specialist}:** {specialist_intro}"
            
            return {"type": "message", "role": "assistant", "agent_name": specialist, "content": f"{charlie_msg}\n\n{specialist_intro}", "new_locked_agent": specialist}
            
        elif "FINANCE" in route:
            route_prompt = f"Pick the ONE best L5 finance/research specialist from this list for the user's request: Gordon (Data/Math), Olivia (Research), Eve (OSINT/PDFs). Transcript:\n{transcript}\nReply with EXACTLY their name."
            specialist = (await llm.ainvoke(route_prompt)).content.strip()
            if specialist not in ["Gordon", "Olivia", "Eve"]: specialist = "Olivia"
            
            charlie_msg = f"👔 **Charlie:** I have directly routed your request to {specialist} in the Deep Research team."
            intro_prompt = f"You are {specialist}, an L5 Research/Finance Specialist. Charlie just routed a user to you based on this transcript:\n{transcript}\nIntroduce yourself professionally, acknowledge their research/data needs, and ask clarifying questions to begin."
            specialist_intro = (await llm.ainvoke(intro_prompt)).content
            if f"**{specialist}" not in specialist_intro and f"{specialist}:" not in specialist_intro: specialist_intro = f"**{specialist}:** {specialist_intro}"
            
            return {"type": "message", "role": "assistant", "agent_name": specialist, "content": f"{charlie_msg}\n\n{specialist_intro}", "new_locked_agent": specialist}
            
        else:
            bob_prompt = (
                "You are Bob, the polite Front Desk Receptionist at a specialized Agency. "
                "You provide standard, free-tier general knowledge answers to the user based on the transcript below.\n"
                f"Transcript:\n{transcript}"
            )
            ans = (await llm.ainvoke(bob_prompt)).content
            if "**Bob:**" not in ans: ans = f"🛎️ **Bob:** {ans}"
            return {"type": "message", "role": "assistant", "agent_name": "Bob", "content": ans, "new_locked_agent": None}