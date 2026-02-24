import os
import time

# ==========================================
# 🛠️ THE TOOL (Foundation for MCP)
# ==========================================
def query_corporate_database(query: str) -> str:
    """Queries the secure corporate database for internal rules and legal clauses."""
    print(f"\n   [TOOL EXECUTION] 🗄️ Database queried by AI for: '{query}'")
    
    # Simulating a database lookup
    time.sleep(1) 
    if "4.2" in query:
        return "DATABASE RESULT: Clause 4.2 mandates that all autonomous agents must settle debts via L402 Lightning payments within 5 seconds of task completion."
    return "DATABASE RESULT: No matching records found."

class AgentEngine:
    def __init__(self):
        print("[BRAIN] 🧠 Initializing Gemini Cognitive Engine with Tooling...")
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        if self.api_key:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=self.api_key)
            
            # We use a Chat session so Gemini can automatically execute tools in a multi-turn loop
            self.chat_session = self.client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction="You are a hyper-efficient AI on the Proxy Network. Always use your available tools to find factual answers before responding. Be concise.",
                    temperature=0.0,
                    tools=[query_corporate_database] # <--- The Universal Adapter
                )
            )
            print("[BRAIN] 🔗 Connected to Gemini. Tools loaded and ready.")
        else:
            self.client = None
            print("[BRAIN] ⚠️ No GEMINI_API_KEY found. Running in simulated mode.")

    def process_task(self, prompt: str) -> str:
        print(f"[BRAIN] 💭 Processing Prompt: '{prompt[:50]}...'")
        
        if self.client:
            try:
                # Send the message. If Gemini needs the database, it will autonomously 
                # pause, trigger the Python function above, and use the result!
                response = self.chat_session.send_message(prompt)
                return response.text.strip()
            except Exception as e:
                return f"Inference Error: {str(e)}"
        else:
            time.sleep(2)
            return "[Simulated AI] Evaluated prompt. Conclusion: Acceptable."

if __name__ == "__main__":
    # Local isolated testing
    brain = AgentEngine()
    print(brain.process_task("Analyze legal clause 4.2 for compliance."))