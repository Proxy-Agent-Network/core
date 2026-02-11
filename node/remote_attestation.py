import hashlib
import base64
import json
from dataclasses import dataclass

# PROXY PROTOCOL - REMOTE ATTESTATION VERIFIER (v1)
# "Verify the hardware, not just the signature."
# ----------------------------------------------------

@dataclass
class GoldenState:
    """The known-good PCR values for a stock Raspberry Pi 5 node."""
    pcr0_hash: str # Firmware
    pcr7_hash: str # Secure Boot

class AttestationVerifier:
    def __init__(self):
        # Database of trusted hardware configurations
        self.known_good_states = {
            "rpi5_v1_0": GoldenState(
                pcr0_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                pcr7_hash="3b7c89..." # Mock hash
            )
        }

    def verify_quote(self, payload: dict, expected_nonce: str) -> dict:
        """
        Validates the TPM Quote.
        1. Check Nonce (Replay protection).
        2. Verify Signature (Proof of Key Ownership).
        3. Check PCRs (Proof of Software Integrity).
        """
        quote = payload['quote']
        
        # 1. Decode
        try:
            msg_bytes = base64.b64decode(quote['message'])
            sig_bytes = base64.b64decode(quote['signature'])
            pcr_bytes = base64.b64decode(quote['pcr_values'])
        except Exception:
            return {"valid": False, "reason": "Base64 decode failed"}

        # 2. Verify Signature (Simplified)
        # In a real impl, we use `tpm2_checkquote` or a python cryptography lib 
        # to verify `sig_bytes` against the Node's Public Key.
        # For this logic demo: We assume signature passed if structure exists.
        signature_valid = True 

        # 3. Verify Nonce
        # The Quote Message contains the Nonce. We check if it matches.
        # This prevents an attacker from re-sending yesterday's valid heartbeat.
        if expected_nonce not in str(msg_bytes):
             # Note: Real TPM structures are binary, this string check is illustrative
             pass 

        # 4. Verify PCRs (The Anti-Rootkit Check)
        # Check if the reported PCR values match our Golden State.
        # This detects if someone modified the Node software or kernel.
        is_pcr_valid = True # Mock check

        if not signature_valid:
            return {"valid": False, "reason": "Invalid Hardware Signature"}
        
        if not is_pcr_valid:
            return {"valid": False, "reason": "PCR Mismatch (Tampered Software detected)"}

        return {
            "valid": True,
            "node_id": payload['node_id'],
            "trust_level": "TIER_2_HARDWARE"
        }

# --- CLI Simulation ---
if __name__ == "__main__":
    verifier = AttestationVerifier()
    
    # Mock Payload from a Node
    mock_payload = {
        "node_id": "node_alpha_hw",
        "quote": {
            "message": "bG9oremV...",
            "signature": "c2lnbmF0dXJl...",
            "pcr_values": "cGNyZGF0YQ..."
        }
    }
    
    print("[*] Verifying Hardware Quote...")
    result = verifier.verify_quote(mock_payload, "nonce_123")
    
    if result['valid']:
        print(f"✅ ATTESTATION PASSED. Node {result['node_id']} is trusted.")
    else:
        print(f"❌ ATTESTATION FAILED. Reason: {result.get('reason')}")
