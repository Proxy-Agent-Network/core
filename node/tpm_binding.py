import subprocess
import os
import hashlib
import json
import base64
from typing import Dict, Optional

# PROXY PROTOCOL - TPM 2.0 HARDWARE INTERFACE (v1.2)
# "Identity sealed in silicon. Verified by math."
# ----------------------------------------------------
# Dependencies: tpm2-tools (apt install tpm2-tools)

class TPMBinding:
    def __init__(self, tpm_path="/dev/tpm0"):
        self.tpm_path = tpm_path
        self.working_dir = "/tmp/tpm_context"
        os.makedirs(self.working_dir, exist_ok=True)
        
        # Standard Handles
        self.EK_HANDLE = "0x81010001" # Endorsement Key (The Chip's ID)
        self.AK_HANDLE = "0x81010002" # Attestation Key (The Signing ID)

    def _run_cmd(self, cmd_list: list, binary=False) -> str:
        """Execute tpm2-tools command."""
        try:
            result = subprocess.check_output(cmd_list, stderr=subprocess.STDOUT)
            return result if binary else result.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            error_msg = e.output.decode('utf-8') if not binary else "Binary Error"
            raise RuntimeError(f"TPM Error: {' '.join(cmd_list)}\n{error_msg}")

    def check_availability(self) -> bool:
        if not os.path.exists(self.tpm_path):
            return False
        try:
            self._run_cmd(["tpm2_getcap", "properties-fixed"])
            return True
        except RuntimeError:
            return False

    def generate_attestation_quote(self, nonce: str) -> Dict:
        """
        CRITICAL: Generates a signed Quote of the PCRs (Platform Configuration Registers).
        This proves the key is hardware-resident and the system boot is untampered.
        
        Args:
            nonce: A random challenge from the server to prevent replay attacks.
        """
        # PCR Banks to Quote:
        # 0: BIOS/Firmware
        # 1: Host Configuration
        # 7: Secure Boot State
        pcr_selection = "sha256:0,1,7"
        
        msg_file = f"{self.working_dir}/quote.msg"
        sig_file = f"{self.working_dir}/quote.sig"
        pcr_file = f"{self.working_dir}/quote.pcr"
        
        print(f"[*] Generating TPM 2.0 Quote for nonce: {nonce[:8]}...")
        
        # 1. Run tpm2_quote
        # -c: Key Handle
        # -l: PCR Selection
        # -q: Nonce (Challenge)
        # -m: Message Output
        # -s: Signature Output
        # -o: PCR Values Output
        self._run_cmd([
            "tpm2_quote",
            "-c", self.AK_HANDLE,
            "-l", pcr_selection,
            "-q", nonce,
            "-m", msg_file,
            "-s", sig_file,
            "-o", pcr_file
        ])
        
        # 2. Read Outputs
        with open(msg_file, "rb") as f: quote_msg = f.read()
        with open(sig_file, "rb") as f: quote_sig = f.read()
        with open(pcr_file, "rb") as f: pcr_values = f.read()
            
        return {
            "node_id": self._get_public_key_fingerprint(),
            "timestamp": int(os.path.getmtime(sig_file)),
            "quote": {
                "message": base64.b64encode(quote_msg).decode('utf-8'),
                "signature": base64.b64encode(quote_sig).decode('utf-8'),
                "pcr_values": base64.b64encode(pcr_values).decode('utf-8')
            }
        }

    def _get_public_key_fingerprint(self) -> str:
        """Returns the SHA256 of the Public Key (Node ID)."""
        pub_file = f"{self.working_dir}/ak.pem"
        # Export if missing
        if not os.path.exists(pub_file):
            self._run_cmd(["tpm2_readpublic", "-c", self.AK_HANDLE, "-f", "pem", "-o", pub_file])
            
        with open(pub_file, "rb") as f:
            pub_data = f.read()
        return hashlib.sha256(pub_data).hexdigest()[:16]

    # ... (Previous create_keys code remains valid, just truncated for brevity)
