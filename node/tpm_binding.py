import os
import hashlib
import json
import base64
import time
from typing import Dict, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# PROXY PROTOCOL - TPM 2.0 NATIVE INTERFACE (v2.0.1)
# "Hardened hardware binding via direct libtss2 calls."
# ----------------------------------------------------
# Dependencies: 
#   apt install libtss2-dev
#   pip install tpm2-pytss

try:
    from tpm2_pytss import ESysContext, TCTI, constants, types
    LIBTSS_AVAILABLE = True
except ImportError:
    LIBTSS_AVAILABLE = False

class TPMBinding:
    """
    Refactored to use tpm2-pytss for direct hardware interaction.
    Removes reliance on shell-calling tpm2-tools for increased security.
    """
    def __init__(self, tpm_path="/dev/tpm0"):
        self.tpm_path = tpm_path
        # Standard Handles for Proxy Identity
        self.EK_HANDLE = 0x81010001 # Endorsement Key (Chip identity)
        self.AK_HANDLE = 0x81010002 # Attestation Key (Node signing identity)
        
        if not LIBTSS_AVAILABLE:
            print("⚠️  tpm2-pytss not found. Critical security features will run in SIMULATION.")

    def check_availability(self) -> bool:
        """Verifies access to the physical TPM device."""
        if not os.path.exists(self.tpm_path):
            return False
        if not LIBTSS_AVAILABLE:
            return False
            
        try:
            with ESysContext() as context:
                # Get TPM properties to verify it's responsive
                context.get_capability(constants.Capability.PROPERTIES_FIXED, 0, 1)
                return True
        except Exception:
            return False

    def generate_attestation_quote(self, nonce: str) -> Dict:
        """
        Generates a hardware-signed Quote of the PCRs using libtss2.
        Proves software integrity and hardware residency.
        """
        if not self.check_availability():
            return self._mock_quote(nonce)

        print(f"[*] Native TPM 2.0 Quote Requested. Nonce: {nonce[:8]}...")

        # Convert hex string nonce to bytes
        try:
            nonce_bytes = bytes.fromhex(nonce) if len(nonce) % 2 == 0 else nonce.encode()
        except ValueError:
            nonce_bytes = nonce.encode()

        try:
            with ESysContext() as ctx:
                # 1. Load the Attestation Key (AK) handle context
                # For persistent handles, we address the handle directly
                ak_handle = self.AK_HANDLE

                # 2. Define PCR selection (0, 1, 7 for boot/config integrity)
                pcr_selection = types.TPML_PCR_SELECTION(
                    count=1,
                    pcrSelections=[
                        types.TPMS_PCR_SELECTION(
                            hash=constants.Alg.SHA256,
                            sizeofSelect=3,
                            pcrSelect=[0, 1, 7]
                        )
                    ]
                )

                # 3. Request the Quote
                # ctx.quote returns (quoted_data, signature)
                quoted, signature = ctx.quote(
                    ak_handle,
                    pcr_selection,
                    nonce_bytes,
                    types.TPMT_SIG_SCHEME(scheme=constants.Alg.RSASSA)
                )

                # 4. Read PCR current values for verification audit
                _, _, pcr_values = ctx.pcr_read(pcr_selection)

                return {
                    "node_id": self._get_public_key_fingerprint(),
                    "timestamp": int(time.time()),
                    "quote": {
                        "message": base64.b64encode(quoted.marshal()).decode('utf-8'),
                        "signature": base64.b64encode(signature.marshal()).decode('utf-8'),
                        "pcr_values": base64.b64encode(pcr_values.marshal()).decode('utf-8')
                    },
                    "hw_secured": True
                }
        except Exception as e:
            print(f"❌ TPM Library Error: {e}")
            return self._mock_quote(nonce)

    def _get_public_key_fingerprint(self) -> str:
        """Extracts the public key from hardware and returns an ID."""
        if not self.check_availability():
            return "NODE_SIM_DEADBEEF"
            
        try:
            with ESysContext() as ctx:
                # Read Public area of AK_HANDLE to derive ID
                public_blob, _, _ = ctx.read_public(self.AK_HANDLE)
                # Hash the public area to create the unique Node ID
                return hashlib.sha256(public_blob.marshal()).hexdigest()[:16].upper()
        except Exception:
            return "NODE_ERR_HARDWARE"

    def _mock_quote(self, nonce: str) -> Dict:
        """Fallback for development environments without physical TPMs."""
        return {
            "node_id": "NODE_SIM_VIRTUAL",
            "timestamp": int(time.time()),
            "mock": True,
            "nonce_echo": nonce,
            "hw_secured": False
        }

# --- Internal Ceremony Logic (v2.0 Only) ---
if __name__ == "__main__":
    tpm = TPMBinding()
    if tpm.check_availability():
        print(f"✅ Native TPM 2.0 Uplink Active: {tpm._get_public_key_fingerprint()}")
        # Test Quote
        test_quote = tpm.generate_attestation_quote("test_nonce")
        print(f"[*] Attestation structure generated: {list(test_quote.keys())}")
    else:
        print("❌ Physical TPM not detected. Running simulation.")
