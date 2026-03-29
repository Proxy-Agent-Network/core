import os
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("PAN_MemoryCipher")

class MemoryCipher:
    def __init__(self):
        logger.info("🔐 [VAULT] Initializing Memory Cipher...")
        
        self.encryption_key = os.environ.get("COGNITIVE_ENCRYPTION_KEY")
        
        # 🟢 THE FIX: Fail-closed architecture for containerized deployments.
        # Generating a random key on startup causes permanent data loss of all 
        # stored memories whenever the Docker container restarts.
        if not self.encryption_key:
            logger.critical("🛑 [VAULT] FATAL: COGNITIVE_ENCRYPTION_KEY environment variable is missing.")
            logger.critical("🛑 [VAULT] Cannot initialize memory vault. A static Master Key is required to prevent data loss across container reboots.")
            raise EnvironmentError("Missing required COGNITIVE_ENCRYPTION_KEY.")
            
        try:
            # Ensure the key is properly encoded to bytes as required by Fernet
            key_bytes = self.encryption_key.encode('utf-8') if isinstance(self.encryption_key, str) else self.encryption_key
            self.cipher_suite = Fernet(key_bytes)
        except ValueError as e:
            logger.critical(f"🛑 [VAULT] FATAL: Invalid COGNITIVE_ENCRYPTION_KEY format. Must be 32 url-safe base64-encoded bytes. ({e})")
            raise

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
            logger.error("⚠️ [VAULT] CORRUPTED MEMORY: Decryption failed. Invalid key or tampered data.")
            return "[CORRUPTED MEMORY] Decryption failed. Invalid key or tampered data."
        except Exception as e:
            logger.error(f"⚠️ [VAULT] ERROR: Memory extraction failed: {str(e)}")
            return f"[ERROR] Memory extraction failed: {str(e)}"

if __name__ == "__main__":
    # --- Local Vault Testing & Key Generation ---
    # Standard print statements retained for CLI utility mode
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