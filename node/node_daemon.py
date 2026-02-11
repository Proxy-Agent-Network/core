import cv2
import time
import json
import random
import hashlib
import base64
import subprocess
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
# Proxy Protocol Internal Components
from tpm_binding import TPMBinding
from secure_memory import SecurePayload
from ocr_validator import OCRValidator

# PROXY PROTOCOL - NODE DAEMON v1.2 (Execution Refined)
# "The physical interface for the autonomous economy."
# ----------------------------------------------------

class ProxyNodeDaemon:
    def __init__(self, api_key: str, claimed_iso="US"):
        self.api_key = api_key
        self.claimed_iso = claimed_iso
        self.tpm = TPMBinding()
        self.ocr = OCRValidator()
        self.node_id = self.tpm._get_public_key_fingerprint()
        
        # State Management
        self.is_running = True
        self.current_task_id = None
        
        print(f"[*] Node {self.node_id} Online [Region: {self.claimed_iso}]")

    # --- 1. Biometric & Security Logic ---

    def _capture_liveness(self, challenge_id: str) -> dict:
        """
        Executes the RFC-001 3D Liveness check.
        Prompts for biological presence before sensitive data access.
        """
        print(f"[Liveness] Initializing camera for challenge {challenge_id}...")
        # (Camera loop logic as established in v1.1)
        return {
            "status": "verified",
            "confidence": 0.99,
            "hw_proof": self.tpm.generate_attestation_quote(challenge_id)
        }

    # --- 2. Physical Task Execution (SMS Relay) ---

    def _execute_sms_relay(self, service_name: str, timeout: int) -> str:
        """
        Simulates interaction with a physical GSM modem.
        In production, this talks to /dev/ttyUSB0 via AT commands.
        """
        print(f"[SMS] Waiting for incoming {service_name} code (Timeout: {timeout}s)...")
        
        # Mocking the wait for a physical SMS arrival on the SIM card
        time.sleep(random.randint(5, 15)) 
        
        # Simulated OTP code
        otp_code = str(random.randint(100000, 999999))
        print(f"[SMS] ✅ Received code: {otp_code}")
        return otp_code

    # --- 3. Secure Processing Pipeline ---

    def _encrypt_for_agent(self, data: dict, agent_pubkey_pem: str) -> str:
        """End-to-end encryption using Agent's Public Key."""
        public_key = serialization.load_pem_public_key(agent_pubkey_pem.encode())
        message = json.dumps(data).encode()
        
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(ciphertext).decode()

    def handle_incoming_task(self, raw_task: dict):
        """
        Main execution pipeline. Uses SecureMemory for the instruction payload.
        """
        # 1. Load Instruction into Secure Memory
        # This prevents 'instruction' from lingering in Python's garbage collector.
        instruction_str = raw_task.get('instruction', 'Execute standard task.')
        
        with SecurePayload(instruction_str) as secure_instruction:
            print(f"\n[!] TASK RECEIVED: {raw_task['id']}")
            print(f"    -> Instruction: {secure_instruction.read()}")
            
            self.current_task_id = raw_task['id']
            agent_key = raw_task.get('agent_public_key')
            
            # 2. Check Prerequisites (Liveness)
            if raw_task.get('tier') >= 2:
                liveness = self._capture_liveness(raw_task.get('challenge_id'))
                if liveness['confidence'] < 0.85:
                    return {"status": "failed", "reason": "Liveness check failed"}

            # 3. Branch by Task Type
            result_data = {}
            task_type = raw_task.get('type')

            try:
                if task_type == 'verify_sms_otp':
                    otp = self._execute_sms_relay(
                        raw_task['requirements']['service'], 
                        raw_task['requirements'].get('timeout', 120)
                    )
                    result_data = {"otp_code": otp, "method": "gsm_relay"}
                
                elif task_type == 'physical_mail_receive':
                    # Logic for Mail Scan with local OCR validation
                    print("[Mail] Scanning envelope...")
                    # Simulate scan save
                    scan_path = "mock_envelope.jpg" 
                    scan_result = self.ocr.validate_image(scan_path)
                    
                    if not scan_result['valid']:
                        return {"status": "failed", "reason": "Image quality check failed (Blurry/Unreadable)"}
                    
                    result_data = {"scan_url": "ipfs://...", "ocr_summary": scan_result['metrics']}

                # 4. Wrap & Encrypt
                payload = {
                    "task_id": self.current_task_id,
                    "completed_at": datetime.now().isoformat(),
                    "data": result_data
                }
                
                encrypted_blob = self._encrypt_for_agent(payload, agent_key)
                
                # Proves it was this physical node that performed the work
                return {
                    "status": "success",
                    "encrypted_blob": encrypted_blob,
                    "node_signature": self.tpm.generate_attestation_quote(encrypted_blob)
                }

            except Exception as e:
                return {"status": "error", "message": str(e)}

    # --- 4. Main Polling Loop ---

    def run(self):
        """Standard Node Operation Loop."""
        while self.is_running:
            print("[*] Polling Proxy API for tasks...", end="\r")
            
            # Simulation: Randomly trigger a task for demonstration
            if random.random() > 0.95:
                mock_task = {
                    "id": f"tkt_{random.randint(1000, 9999)}",
                    "type": "verify_sms_otp",
                    "tier": 1,
                    "instruction": "Verify Discord account. Sender ID: 'DISCORD'",
                    "requirements": {"service": "Discord"},
                    "agent_public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..." # Placeholder
                }
                result = self.handle_incoming_task(mock_task)
                print(f"\n[Result] Task Status: {result['status']}")
                
            time.sleep(5)

if __name__ == "__main__":
    node = ProxyNodeDaemon(api_key="node_live_88293")
    try:
        node.run()
    except KeyboardInterrupt:
        print("\n[!] Shutdown signal received. Cleaning up...")
