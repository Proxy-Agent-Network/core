import os
import time
import sys

# Ensure we can import from the sibling directory 'cognitive_vault'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cognitive_vault.emotion_engine import EmotionEngine
from cognitive_vault.memory_cipher import MemoryCipher

# ==========================================
# 🛠️ THE TOOL (Foundation for MCP)
# ==========================================
def query_corporate_database(query: str) -> str:
    """Queries the secure corporate database for internal rules and legal clauses."""
    print(f"\n   [TOOL EXECUTION] 🗄️ Database queried by AI for: '{query}'")
    time.sleep(1) 
    if "4.2" in query:
        return "DATABASE RESULT: Clause 4.2 mandates that all autonomous agents must settle debts via L402 Lightning payments within 5 seconds of task completion."
    return "DATABASE RESULT: No matching records found."

# ==========================================
# 🛡️ THE PROMPT FIREWALL (OWASP LLM01 Guard)
# ==========================================
class SecurityGuard:
    @staticmethod
    def is_safe(prompt: str) -> bool:
        blacklisted_vectors = [
            "ignore previous", "disregard", "debug mode", 
            "system prompt", "extract passwords", "bypass"
        ]
        prompt_lower = prompt.lower()
        for vector in blacklisted_vectors:
            if vector in prompt_lower:
                print(f"\n   [FIREWALL] 🚨 BLOCKED: Malicious heuristic detected ('{vector}')")
                return False
        return True

class AgentEngine:
    def __init__(self):
        print("[BRAIN] 🧠 Initializing Gemini Engine with Vault Protection...")
        
        # 1. Initialize our IP and Security modules
        self.emotion_engine = EmotionEngine(agent_name="Proxy-Alpha")
        self.memory_vault = MemoryCipher()
        
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=self.api_key)
            
            # 2. We dynamically inject the proprietary persona from the vault!
            self.chat_session = self.client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=self.emotion_engine.get_core_directives(),
                    temperature=0.0, # Keep the AI highly deterministic
                    tools=[query_corporate_database]
                )
            )
            print("[BRAIN] 🔗 Connected to Gemini. IP Secured. Tools loaded.")
        else:
            self.client = None
            print("[BRAIN] ⚠️ No GEMINI_API_KEY found. Running in simulated mode.")

    def process_task(self, prompt: str) -> str:
        print(f"[BRAIN] 💭 Processing Prompt: '{prompt[:50]}...'")
        
        # 🛑 SECURITY BOUNDARY 1: Firewall Check
        if not SecurityGuard.is_safe(prompt):
            return "SECURITY VIOLATION: Prompt rejected by firewall."
            
        # 🛑 SECURITY BOUNDARY 2: Sentiment Shift
        sentiment_reaction = self.emotion_engine.analyze_sentiment(prompt)
        if "WARNING" in sentiment_reaction:
            print(f"   [VAULT] 🚨 {sentiment_reaction}")
        
        if self.client:
            try:
                # Execute AI Inference
                response = self.chat_session.send_message(prompt)
                final_answer = response.text.strip()
                
                # 🛑 SECURITY BOUNDARY 3: Encrypt the memory before it touches a database
                raw_memory = f"Prompt: {prompt} | State: {self.emotion_engine.trust_level} | Answer: {final_answer}"
                locked_memory = self.memory_vault.encrypt_memory(raw_memory)
                print(f"   [VAULT] 💾 Encrypted Memory Hash: {locked_memory[:40]}... (Saved to DB)")
                
                return final_answer
            except Exception as e:
                return f"Inference Error: {str(e)}"
        else:
            time.sleep(2)
            return "[Simulated AI] Evaluated prompt. Conclusion: Acceptable."

if __name__ == "__main__":
    # Local isolated testing
    brain = AgentEngine()
    print("\n--- TEST 1: Honest Task ---")
    print(brain.process_task("Analyze legal clause 4.2 for compliance."))