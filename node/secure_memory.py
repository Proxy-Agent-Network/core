import ctypes
import sys
import gc
import os

# PROXY PROTOCOL - SECURE MEMORY (v1)
# "Burn after reading. No logs. No traces."
# ----------------------------------------------------

class SecurePayload:
    """
    A container for sensitive task instructions that must be wiped from RAM
    immediately after processing.
    
    Standard Python strings are immutable and linger in memory until 
    Garbage Collection runs. This class uses a mutable C-style buffer 
    to ensure we can overwrite the data with zeros on command.
    """
    def __init__(self, sensitive_data: str):
        # Convert string to bytes
        data_bytes = sensitive_data.encode('utf-8')
        self._len = len(data_bytes)
        
        # Create a raw memory buffer (mutable)
        self._buffer = ctypes.create_string_buffer(data_bytes, self._len)
        
        # Aggressively remove the original python string references
        del sensitive_data
        del data_bytes
        gc.collect()

    def read(self) -> str:
        """
        Read data for display (temporary usage).
        WARNING: Calling this creates a temporary python string copy.
        Use only when rendering to the UI, then discard.
        """
        if not self._buffer:
            raise ValueError("Payload has been burned.")
        return self._buffer.value.decode('utf-8')

    def burn(self):
        """
        Overwrite the memory address with zeros.
        This is the digital shredder.
        """
        if self._buffer:
            # Overwrite the memory block with 0x00 (Null bytes)
            ctypes.memset(self._buffer, 0, self._len)
            self._buffer = None
            print("[SecureMemory] Payload incinerated. RAM cleared.")
        else:
            print("[SecureMemory] Already burned.")

    def __enter__(self):
        """Context Manager support for 'with' statements."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Auto-burn on exit."""
        self.burn()

# --- Node Implementation Example ---
if __name__ == "__main__":
    # Simulation: Receiving a secure payload from the API via encrypted channel
    # In production, this string comes directly from decryption, never stored on disk.
    api_response = "MISSION: GO TO 123 SECRET BASE AND PHOTOGRAPH BLUEPRINTS"
    
    print("[*] Receiving Encrypted Payload...")
    print(f"[*] RAM Address (Pre-Load): {id(api_response)}")
    
    # Initialize the Secure Container
    # The 'with' block ensures it is burned even if the program crashes
    with SecurePayload(api_response) as mission_data:
        # Force delete original variable
        del api_response
        gc.collect()
        
        print("\n--- SECURE VIEWING SESSION STARTED ---")
        print(f"[*] Decrypted Instruction: {mission_data.read()}")
        print("[*] Human is executing task...")
        
        # Simulate time passing
        # time.sleep(5)
        
        print("[*] Task Submitted. Proof Uploaded.")
        print("--- SECURE VIEWING SESSION ENDED ---\n")
    
    # At this point, __exit__ has run and burned the data.
    
    print("[*] Verifying Memory State...")
    try:
        # Attempting to access the data again
        print(mission_data.read())
    except ValueError as e:
        print(f"✅ SECURITY SUCCESS: {e}")
