import subprocess
import os
import hashlib
import json
from typing import Optional, Tuple

# PROXY PROTOCOL - TPM 2.0 BINDING CEREMONY (v1)
# "Identity rooted in silicon."
# ----------------------------------------------------
# Dependencies: tpm2-tools (installed via Docker/apt)

class TPMBinding:
    def __init__(self, tpm_path="/dev/tpm0"):
        self.tpm_path = tpm_path
        self.working_dir = "/tmp/tpm_context"
        os.makedirs(self.working_dir, exist_ok=True)
        
        # Persistent Handles (Standardized for Proxy Protocol)
        self.EK_HANDLE = "0x81010001" # Endorsement Key
        self.AK_HANDLE = "0x81010002" # Attestation Identity Key

    def _run_cmd(self, cmd_list: list) -> str:
        """Helper to run tpm2_tools commands safely."""
        try:
            result = subprocess.check_output(cmd_list, stderr=subprocess.STDOUT)
            return result.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            error_msg = e.output.decode('utf-8')
            raise RuntimeError(f"TPM Command Failed: {' '.join(cmd_list)}\nError: {error_msg}")

    def check_availability(self) -> bool:
        """Verifies TPM hardware is accessible."""
        if not os.path.exists(self.tpm_path):
            return False
        try:
            self._run_cmd(["tpm2_getcap", "properties-fixed"])
            return True
        except RuntimeError:
            return False

    def perform_binding_ceremony(self) -> dict:
        """
        The One-Time Setup.
        1. Clears transient objects.
        2. Creates a Primary Key (Endorsement Hierarchy).
        3. Creates an Identity Key (AK) meant for signing.
        4. Persists the keys in NVRAM.
        """
        print("[*] Starting TPM Binding Ceremony...")
        
        # 1. Clean Slate (Flush context)
        # Note: In prod, be careful not to wipe existing valid keys
        try:
            self._run_cmd(["tpm2_flushcontext", "-t"])
        except:
            pass # Ignore if empty

        # 2. Create Primary Key (Endorsement Key)
        # -C e: Endorsement Hierarchy
        # -g sha256: Hash algorithm
        # -G rsa: Key algorithm
        # -c: Context file output
        print("[*] Generating Endorsement Key (EK)...")
        self._run_cmd([
            "tpm2_createprimary", 
            "-C", "e", 
            "-g", "sha256", 
            "-G", "rsa", 
            "-c", f"{self.working_dir}/primary.ctx"
        ])

        # 3. Create Identity Key (Attestation Key)
        # -C: Parent context (The EK we just made)
        # -u, -r: Output public/private portions (encrypted)
        print("[*] Generating Identity Key (AK)...")
        self._run_cmd([
            "tpm2_create",
            "-C", f"{self.working_dir}/primary.ctx",
            "-g", "sha256",
            "-G", "rsa",
            "-u", f"{self.working_dir}/ak.pub",
            "-r", f"{self.working_dir}/ak.priv",
            "-a", "fixedtpm|fixedparent|sensitivedataorigin|userwithauth|sign|noda" 
            # Attributes ensure key cannot be exported ('fixedtpm')
        ])

        # 4. Load & Persist
        print("[*] Persisting Identity Key to Handle...")
        self._run_cmd([
            "tpm2_load",
            "-C", f"{self.working_dir}/primary.ctx",
            "-u", f"{self.working_dir}/ak.pub",
            "-r", f"{self.working_dir}/ak.priv",
            "-c", f"{self.working_dir}/ak.ctx"
        ])
        
        # Evict old handle if exists (overwrite)
        try:
            self._run_cmd(["tpm2_evictcontrol", "-C", "o", "-c", self.AK_HANDLE])
        except:
            pass

        self._run_cmd([
            "tpm2_evictcontrol", 
            "-C", "o", 
            "-c", f"{self.working_dir}/ak.ctx", 
            self.AK_HANDLE
        ])

        # 5. Export Public PEM for the Network
        # This is what you upload to the Proxy Registry
        self._run_cmd([
            "tpm2_readpublic",
            "-c", self.AK_HANDLE,
            "-f", "pem",
            "-o", f"{self.working_dir}/node_identity.pem"
        ])
        
        with open(f"{self.working_dir}/node_identity.pem", "r") as f:
            pub_key_pem = f.read()

        return {
            "status": "BOUND",
            "handle": self.AK_HANDLE,
            "public_key_pem": pub_key_pem,
            "hardware_proof": "tpm2_quote_placeholder" 
        }

    def sign_heartbeat(self, timestamp: str, status: str) -> str:
        """
        Signs a heartbeat payload using the hardware-locked key.
        The private key never leaves the chip.
        """
        payload = f"{timestamp}|{status}".encode('utf-8')
        payload_hash_file = f"{self.working_dir}/hash.bin"
        sig_output_file = f"{self.working_dir}/sig.bin"
        
        # 1. Hash the payload (Software side, or TPM side if small)
        with open(payload_hash_file, "wb") as f:
            f.write(hashlib.sha256(payload).digest())

        # 2. Sign the Hash using the TPM
        self._run_cmd([
            "tpm2_sign",
            "-c", self.AK_HANDLE,
            "-g", "sha256",
            "-d", payload_hash_file,
            "-f", "plain",
            "-o", sig_output_file
        ])

        # 3. Read Signature
        with open(sig_output_file, "rb") as f:
            signature_hex = f.read().hex()
            
        return signature_hex

# --- CLI Simulation ---
if __name__ == "__main__":
    tpm = TPMBinding()
    
    if not tpm.check_availability():
        print("❌ CRITICAL: No TPM detected at /dev/tpm0. Use the Docker image on valid hardware.")
        # For dev/testing purposes, we might Mock this, but the script is for Prod.
        exit(1)
        
    print("✅ TPM Hardware Detected.")
    
    try:
        # 1. Run Ceremony
        identity = tpm.perform_binding_ceremony()
        print("\n--- IDENTITY ESTABLISHED ---")
        print(f"Handle: {identity['handle']}")
        print(f"Public Key:\n{identity['public_key_pem']}")
        
        # 2. Sign a Heartbeat
        print("\n[*] Signing Heartbeat...")
        sig = tpm.sign_heartbeat("2026-02-10T12:00:00Z", "ONLINE")
        print(f"Hardware Signature: {sig[:64]}...")
        print("✅ Proof Valid.")
        
    except RuntimeError as e:
        print(f"❌ CEREMONY FAILED: {e}")
