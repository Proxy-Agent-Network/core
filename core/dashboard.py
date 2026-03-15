import streamlit as st
import asyncio
import os
import io
import json
import time
import re
import codecs
import httpx

# BUG 3: Only import lightweight local modules at top level.
import streamlit_core.ui_injector as ui_injector
import streamlit_core.db_manager as db
import streamlit_core.agent_engine as engine

# --- INIT ---
ui_injector.inject_custom_ui()
db.init_db_patches()

# --- SESSION STATE INITIALIZATION ---
if "pending_payment" not in st.session_state: st.session_state.pending_payment = None
if "execute_payment" not in st.session_state: st.session_state.execute_payment = False
if "messages" not in st.session_state: 
    st.session_state.messages =
if "spent" not in st.session_state: st.session_state.spent = 0

#... (Avatar and Sidebar logic remains consistent)

with tab_chat:
    # BUG 2 FIX: High-precedence rendering for pending payments.
    # This renders at the top of the chat whenever a payment is required.
    if st.session_state.pending_payment:
        p_data = st.session_state.pending_payment
        cost = p_data.get("cost", 100)
        st.success(f"🎨 **Proposal Ready!** Please authorize the {cost} SATS treasury payment.")
        
        c1, c2, c3 = st.columns(3)
        if c1.button("⚡ Pay & Generate", use_container_width=True):
            st.session_state.execute_payment = True
            st.rerun() # Immediate rerun to start the 'execute_payment' block
        if c2.button("🗣️ Discuss Further", use_container_width=True): 
            st.session_state.pending_payment = None
            st.rerun()
        if c3.button("❌ Cancel", use_container_width=True): 
            st.session_state.pending_payment = None
            st.rerun()

    chat_container = st.container()
    
    # Render historical messages
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # BUG 2: Handle active payment execution
    if st.session_state.execute_payment:
        with chat_container:
            with st.status("💸 Processing Transaction...", expanded=True) as s_cont:
                pending_data = st.session_state.pending_payment
                
                async def process_override(p_data):
                    # (SSE Client and logic imports moved inside function for Bug 3)
                    from mcp.client.sse import sse_client
                    from mcp.client.session import ClientSession
                    
                    s_cont.write("Verifying Lightning Node...")
                    #... (Payment verification logic)
                    
                    async with sse_client("http://proxy_agent_v1:8000/sse", timeout=600.0) as streams:
                        async with ClientSession(streams, streams) as session:
                            await session.initialize()
                            res = await session.call_tool(p_data["tool_name"], arguments=p_data["arguments"])
                            return res.content.text

                try:
                    final_data = asyncio.run(process_override(pending_data))
                    st.session_state.spent += pending_data.get("cost", 100)
                    st.session_state.messages.append({"role": "assistant", "content": final_data})
                except Exception as e:
                    st.error(f"L5 Engine Failed: {e}")
                
                # Cleanup state and refresh UI
                st.session_state.pending_payment = None
                st.session_state.execute_payment = False
                st.rerun()

    # User Input Handling
    if user_submission := st.chat_input("Enter mission..."):
        st.session_state.messages.append({"role": "user", "content": user_submission})
        st.session_state.process_new_prompt = True
        st.rerun()

    # BUG 2 FIX: Processing logic loop
    if st.session_state.get("process_new_prompt"):
        with st.spinner("Analyzing mission..."):
            last_user = st.session_state.messages[-1]["content"]
            chat_transcript = str(st.session_state.messages[-5:])
            
            # Run engine logic
            ans = asyncio.run(engine.run_agent_logic(last_user, chat_transcript, None, "8082"))
            
            # BUG 2 FIX: Immediately check for 402 and rerun
            if isinstance(ans, dict) and ans.get("status") == "402":
                st.session_state.pending_payment = ans
                st.session_state.process_new_prompt = False
                st.rerun() # Forces display of the Pay buttons
            else:
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.session_state.process_new_prompt = False
                st.rerun()