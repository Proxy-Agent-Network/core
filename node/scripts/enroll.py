import subprocess
import json
import base64
import os
import requests
import sys

class ProxyNodeEnrollment:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.ek_pub_file = "ek.pub"
        self.ak_pub_file = "ak.pub"
        self.ak_priv_file = "ak.priv"
        self.quote_msg_file = "quote_msg.bin"
        self.quote_sig_file = "quote_sig.bin"

    def _read_file_b64(self, filepath):
        """Helper to read binary files and return base64 string"""
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None

    def generate_hardware_identity(self):
        """Step 1: Create the Endorsement and Attestation Keys inside the TPM"""
        print("[*] Generating Hardware Identity (EK/AK)...")
        try:
            # Create Endorsement Key (EK)
            subprocess.run(["tpm2_createek", "-c", "ek.ctx", "-u", self.ek_pub_file], check=True, capture_output=True)
            
            # Create Attestation Key (AK) bound to the EK
            subprocess.run([
                "tpm2_createak", 
                "-C", "ek.ctx", 
                "-c", "ak.ctx", 
                "-u", self.ak_pub_file, 
                "-r", self.ak_priv_file
            ], check=True, capture_output=True)
            
            print("[+] Keys cryptographically bound to physical silicon.")
        except subprocess.CalledProcessError as e:
            print(f"[-] TPM Error: {e.stderr.decode()}")
            sys.exit(1)

    def get_attestation_quote(self, nonce):
        """Step 2: Generate a PCR quote signed by the AK using the server nonce"""
        print(f"[*] Challenging TPM with Nonce: {nonce}")
        try:
            # Quoting PCR 7 (Secure Boot / Platform State)
            subprocess.run([
                "tpm2_quote", 
                "-c", "ak.ctx", 
                "-l", "sha256:7", 
                "-q", nonce, 
                "-m", self.quote_msg_file, 
                "-s", self.quote_sig_file
            ], check=True, capture_output=True)
            
            return {
                "message": self._read_file_b64(self.quote_msg_file),
                "signature": self._read_file_b64(self.quote_sig_file)
            }
        except subprocess.CalledProcessError as e:
            print(f"[-] Quote Error: {e.stderr.decode()}")
            sys.exit(1)

    def run(self):
        print("--- PROXY PROTOCOL NODE ENROLLMENT v1.6.0 ---")
        
        # 1. Fetch Challenge Nonce from Registry
        try:
            print(f"[*] Fetching challenge from {self.server_url}...")
            challenge_req = requests.get(f"{self.server_url}/api/v1/auth/challenge", timeout=10)
            challenge_req.raise_for_status()
            nonce = challenge_req.json().get("nonce")
            print(f"[+] Received Nonce: {nonce}")
        except Exception as e:
            print(f"[-] Connection Error: Could not reach Registry. {e}")
            return

        # 2. Hardware Operation
        self.generate_hardware_identity()
        quote_data = self.get_attestation_quote(nonce)

        # 3. Compile Manifest
        payload = {
            "node_id": "PENDING",
            "hardware_manifest": {
                "ek_public": self._read_file_b64(self.ek_pub_file),
                "ak_public": self._read_file_b64(self.ak_pub_file),
                "pcr_quote": quote_data,
                "nonce": nonce
            }
        }

        # 4. Submit for Final Verification
        try:
            print("[*] Submitting Hardware Proof of Silicon...")
            response = requests.post(
                f"{self.server_url}/api/v1/nodes/enroll", 
                json=payload, 
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                print("\n[SUCCESS] Node Verified and Enrolled.")
                print(f"ASSIGNED NODE_ID: {data['node_id']}")
                print(f"ENROLLED AT: {data['manifest']['enrolled_at']}")
            else:
                print(f"\n[REJECTED] Enrollment Failed: {response.json().get('reason')}")
        except Exception as e:
            print(f"[-] Submission Error: {e}")

if __name__ == "__main__":
    # If running on the same machine for testing, use localhost. 
    # If running on the Pi, replace with your server's IP.
    REGISTRY_URL = "http://localhost:5000"
    
    node = ProxyNodeEnrollment(REGISTRY_URL)
    node.run()
