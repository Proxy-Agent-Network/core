import os
import time

class AgentEngine:
    def __init__(self):
        print("[BRAIN] 🧠 Initializing Gemini Cognitive Engine...")
        
        # We look for the Gemini API key in the environment.
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        if self.api_key:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            print("[BRAIN] 🔗 Connected to Google Gemini via google-genai SDK.")
        else:
            self.client = None
            print("[BRAIN] ⚠️ No GEMINI_API_KEY found. Running in simulated inference mode.")

    def process_task(self, prompt: str) -> str:
        print(f"[BRAIN] 💭 Processing Prompt: '{prompt[:50]}...'")
        
        if self.client:
            from google.genai import types
            try:
                # 🛑 The Actual Gemini AI Inference Call
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="You are a hyper-efficient AI specialist on the Proxy Agent Network. Provide extremely concise, highly accurate answers. No fluff or conversational filler.",
                        max_output_tokens=150
                    )
                )
                return response.text.strip()
            except Exception as e:
                return f"Inference Error: {str(e)}"
        else:
            # Simulated "thinking" for local dev without a key
            time.sleep(2)
            return f"[Simulated AI Analysis] Evaluated prompt '{prompt}'. Conclusion: The parameters fall within acceptable legal bounds."

if __name__ == "__main__":
    # Local isolated testing
    brain = AgentEngine()
    print(brain.process_task("Analyze legal clause 4.2 for compliance."))