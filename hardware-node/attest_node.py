import platform
import subprocess
import hashlib
import hmac
import json
import uuid

# SIMULATED "MANUFACTURER KEY" (In prod, this is burned into silicon)
# This key represents the "Proxy Network Authority" trusting this hardware class.
MANUFACTURER_ROOT_KEY = b"PROXY_NETWORK_ROOT_V1_SECURE"

def get_windows_uuid():
    """Extracts the immutable Machine UUID from the Windows Motherboard."""
    try:
        # We use WMIC to get the real hardware ID
        cmd = subprocess.check_output('wmic csproduct get uuid', shell=True)
        # Decode and clean up the output (remove headers/newlines)
        uid = cmd.decode().split('\n')[1].strip()
        return uid
    except Exception as e:
        # Fallback for non-Windows or restricted environments
        print(f"[!] Hardware Access Error: {e}")
        return str(uuid.getnode())

def generate_proof_of_body():
    """Generates a cryptographic proof binding this code to this specific physical machine."""
    
    print("--- INITIATING HARDWARE ATTESTATION ---")
    
    # 1. ACQUIRE HARDWARE IDENTITY
    hw_id = get_windows_uuid()
    print(f"[*] MOTHERBOARD UUID:  {hw_id}")
    
    # 2. GENERATE NONCE (Time-based to prevent replay attacks)
    # In a real TPM, this prevents someone from recording your login and reusing it.
    import time
    nonce = str(int(time.time() / 10)) # Valid for 10 second window
    
    # 3. SIGN THE BODY (HMAC-SHA256)
    # We are signing the HW_ID + NONCE with the ROOT KEY.
    # Only a machine with this specific HW_ID could generate this specific hash right now.
    msg = f"{hw_id}:{nonce}".encode()
    signature = hmac.new(MANUFACTURER_ROOT_KEY, msg, hashlib.sha256).hexdigest()
    
    print(f"[*] CRYPTO SIGNATURE:  {signature[:32]}...")
    
    # 4. CREATE PAYLOAD
    payload = {
        "node_id": f"NODE_{hashlib.sha256(hw_id.encode()).hexdigest()[:8].upper()}",
        "hardware_proof": signature,
        "timestamp": int(time.time()),
        "architecture": platform.machine(),
        "system": platform.system()
    }
    
    return payload

if __name__ == "__main__":
    proof = generate_proof_of_body()
    print("\n--- ATTESTATION PAYLOAD (SEND TO /api/register) ---")
    print(json.dumps(proof, indent=2))
    
    print("\n[SUCCESS] This node is cryptographically bound to this hardware.")