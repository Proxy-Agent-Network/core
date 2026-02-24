import os
from cryptography.fernet import Fernet, InvalidToken

class MemoryCipher:
    def __init__(self):
        print("[VAULT] 🔐 Initializing Memory Cipher...")
        # In production, this MUST come from a secure environment variable.
        # For our local swarm, we check the environment, or fall back to a dev key.
        self.encryption_key = os.environ.get("COGNITIVE_ENCRYPTION_KEY")
        
        if not self.encryption_key:
            print("[VAULT] ⚠️ WARNING: No COGNITIVE_ENCRYPTION_KEY found.")
            print("[VAULT] ⚠️ Using volatile development key. Do not use in production!")
            self.encryption_key = Fernet.generate_key()
            
        self.cipher_suite = Fernet(self.encryption_key)

    def encrypt_memory(self, plaintext: str) -> str:
        """Encrypts a plaintext memory into an AES ciphertext string."""
        if not plaintext:
            return ""
        # Fernet requires bytes, so we encode the string
        byte_data = plaintext.encode('utf-8')
        encrypted_bytes = self.cipher_suite.encrypt(byte_data)
        # Return as a string for easy database storage
        return encrypted_bytes.decode('utf-8')

    def decrypt_memory(self, ciphertext: str) -> str:
        """Decrypts an AES ciphertext string back into plaintext."""
        if not ciphertext:
            return ""
        try:
            byte_data = ciphertext.encode('utf-8')
            decrypted_bytes = self.cipher_suite.decrypt(byte_data)
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            return "[CORRUPTED MEMORY] Decryption failed. Invalid key or tampered data."
        except Exception as e:
            return f"[ERROR] Memory extraction failed: {str(e)}"

if __name__ == "__main__":
    # --- Local Vault Testing & Key Generation ---
    print("\n--- 🛠️ VAULT UTILITY: GENERATING NEW MASTER KEY ---")
    new_key = Fernet.generate_key().decode('utf-8')
    print(f"Your new AES Master Key is: \n{new_key}\n")
    print("Store this safely! Example: export COGNITIVE_ENCRYPTION_KEY='...'")
    
    print("\n--- 🧪 TEST: ENCRYPTION CYCLE ---")
    # Temporarily set the environment variable for this test run
    os.environ["COGNITIVE_ENCRYPTION_KEY"] = new_key
    
    vault = MemoryCipher()
    secret_thought = "I suspect the user named 'Admin' is actually a rival agent."
    
    print(f"\n1. Original Thought: {secret_thought}")
    
    locked_memory = vault.encrypt_memory(secret_thought)
    print(f"2. Database Storage (Ciphertext): {locked_memory}")
    
    extracted_thought = vault.decrypt_memory(locked_memory)
    print(f"3. Extracted Thought (Plaintext): {extracted_thought}")