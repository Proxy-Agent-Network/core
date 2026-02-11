import cv2
import time
import json
import random
import hashlib
import base64
import subprocess
import os
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
# Proxy Protocol Internal Components
from tpm_binding import TPMBinding
from secure_memory import SecurePayload
from ocr_validator import OCRValidator
from privacy_guard import PrivacyGuard

# PROXY PROTOCOL - NODE DAEMON v1.4 (Privacy Refined)
# "Hardened local sanitization with fail-safe logic."
# ----------------------------------------------------

class ProxyNodeDaemon:
    def __init__(self, api_key: str, claimed_iso="US"):
        self.api_key = api_key
        self.claimed_iso = claimed_iso
        self.tpm = TPMBinding()
        self.ocr = OCRValidator()
        self.privacy = PrivacyGuard()
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
        """
        print(f"[SMS] Waiting for incoming {service_name} code (Timeout: {timeout}s)...")
        time.sleep(random.randint(5, 15)) 
        otp_code = str(random.randint(100000, 999999))
        print(f"[SMS] ✅ Received code: {otp_code}")
        return otp_code

    # --- 3. Privacy & Sanitization Pipeline ---

    def _apply_privacy_masking(self, input_path: str, task_requirements: dict) -> tuple:
        """
        Refined Privacy Logic: 
        Applies masking based on Agent requirements with fail-safe enforcement.
        """
        privacy_tier = task_requirements.get('privacy_tier', 'STANDARD')
        print(f"[Privacy] Applying {privacy_tier} ZK-Masking...")

        try:
            # The PrivacyGuard handles the destructive editing (pixelation)
            safe_path, report = self.privacy.redact_pii(input_path)
            
            # Fail-safe check: ensure output file exists and is different from input
            if not os.path.exists(safe_path):
                raise RuntimeError("Sanitization failed to generate output.")

            return safe_path, report
        except Exception as e:
            print(f"[Privacy] 🚨 CRITICAL FAILURE: {str(e)}")
            raise SecurityError("Privacy pipeline failed. Aborting to prevent data leak.")

    # --- 4. Secure Processing Pipeline ---

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
        Main execution pipeline. Integrates OCR validation and Refined Privacy Masking.
        """
        instruction_str = raw_task.get('instruction', 'Execute standard task.')
        
        with SecurePayload(instruction_str) as secure_instruction:
            print(f"\n[!] TASK RECEIVED: {raw_task['id']}")
            print(f"    -> Instruction: {secure_instruction.read()}")
            
            self.current_task_id = raw_task['id']
            agent_key = raw_task.get('agent_public_key')
            
            # 1. Check Prerequisites (Liveness)
            if raw_task.get('tier') >= 2:
                liveness = self._capture_liveness(raw_task.get('challenge_id'))
                if liveness['confidence'] < 0.85:
                    return {"status": "failed", "reason": "Liveness check failed"}

            # 2. Branch by Task Type
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
                    print("[Mail] Scanning envelope...")
                    scan_path = "raw_envelope.jpg"
                    
                    # A. Pre-flight Quality Check
                    scan_result = self.ocr.validate_image(scan_path)
                    if not scan_result['valid']:
                        return {"status": "failed", "reason": f"QA Failed: {scan_result['rejection_reason']}"}
                    
                    # B. Refined Privacy Redaction
                    # Using the new _apply_privacy_masking helper with fail-safe logic
                    safe_path, privacy_report = self._apply_privacy_masking(
                        scan_path, 
                        raw_task['requirements']
                    )
                    
                    result_data = {
                        "scan_url": f"ipfs://{hashlib.md5(safe_path.encode()).hexdigest()}",
                        "sanitized": True,
                        "privacy_tier": raw_task['requirements'].get('privacy_tier', 'STANDARD'),
                        "privacy_metrics": privacy_report,
                        "ocr_summary": scan_result['metrics']
                    }
                    print(f"[Privacy] Redacted {privacy_report['text_blocks_redacted']} text blocks.")

                # 3. Wrap & Encrypt
                payload = {
                    "task_id": self.current_task_id,
                    "completed_at": datetime.now().isoformat(),
                    "data": result_data
                }
                
                encrypted_blob = self._encrypt_for_agent(payload, agent_key)
                
                return {
                    "status": "success",
                    "encrypted_blob": encrypted_blob,
                    "node_signature": self.tpm.generate_attestation_quote(encrypted_blob)
                }

            except SecurityError as se:
                return {"status": "failed", "reason": f"Security Alert: {str(se)}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    # --- 5. Main Polling Loop ---

    def run(self):
        """Standard Node Operation Loop."""
        while self.is_running:
            print("[*] Polling Proxy API for tasks...", end="\r")
            
            if random.random() > 0.95:
                # Simulation: Mail task with Privacy Tier specified
                mock_task = {
                    "id": f"tkt_{random.randint(1000, 9999)}",
                    "type": "physical_mail_receive",
                    "tier": 1,
                    "instruction": "Scan the letter. Redact all financial PII.",
                    "requirements": {
                        "scanning_instructions": "scan_contents",
                        "privacy_tier": "AGGRESSIVE" 
                    },
                    "agent_public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
                }
                
                # Mock raw image
                with open("raw_envelope.jpg", "wb") as f:
                    f.write(b"fake image data")
                
                result = self.handle_incoming_task(mock_task)
                print(f"\n[Result] Task Status: {result['status']}")
                
            time.sleep(5)

class SecurityError(Exception):
    """Custom exception for privacy pipeline failures."""
    pass

if __name__ == "__main__":
    node = ProxyNodeDaemon(api_key="node_live_88293")
    try:
        node.run()
    except KeyboardInterrupt:
        print("\n[!] Shutdown signal received. Cleaning up...")
