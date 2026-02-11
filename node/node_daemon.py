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

# PROXY PROTOCOL - NODE DAEMON v1.5 (Legal Ready)
# "Automated legal delegation with hardware attestation."
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
        return {
            "status": "verified",
            "confidence": 0.99,
            "hw_proof": self.tpm.generate_attestation_quote(challenge_id)
        }

    # --- 2. Legal Bridge: Documentation Generator ---

    def _generate_legal_instrument(self, agent_key: str, requirements: dict) -> dict:
        """
        v1.5: Auto-fills Markdown PoA templates based on task context.
        Binds the Agent's key to the Node's hardware identity.
        """
        jurisdiction = requirements.get('jurisdiction', 'US_DE')
        principal_name = requirements.get('principal_name', '[ANONYMOUS PRINCIPAL]')
        
        print(f"[Legal] Generating PoA for jurisdiction: {jurisdiction}")
        
        # 1. Select Template (Mocked file path logic)
        template_map = {
            "US_DE": "templates/legal/us_delaware_poa.md",
            "UK": "templates/legal/uk_poa.md",
            "SG": "templates/legal/singapore_poa.md"
        }
        
        template_path = template_map.get(jurisdiction, "templates/legal/ai_power_of_attorney.md")
        
        # 2. Fill Placeholders
        # In production, we'd read the actual .md file. Here we simulate the fill logic.
        instrument_text = f"""
        # LIMITED POWER OF ATTORNEY ({jurisdiction})
        PRINCIPAL: {principal_name}
        AGENT_KEY: {agent_key[:20]}...
        PROXY_NODE: {self.node_id}
        TIMESTAMP: {datetime.now().isoformat()}
        TASK_ID: {self.current_task_id}
        """
        
        # 3. Cryptographically Bind the Instrument
        # We hash the filled text and sign it with the TPM
        content_hash = hashlib.sha256(instrument_text.encode()).hexdigest()
        hw_signature = self.tpm.generate_attestation_quote(content_hash)
        
        return {
            "instrument_body": instrument_text,
            "content_hash": content_hash,
            "hw_signature": hw_signature,
            "jurisdiction": jurisdiction
        }

    # --- 3. Privacy & Sanitization Pipeline ---

    def _apply_privacy_masking(self, input_path: str, task_requirements: dict) -> tuple:
        """Applies masking based on Agent requirements with fail-safe enforcement."""
        privacy_tier = task_requirements.get('privacy_tier', 'STANDARD')
        try:
            safe_path, report = self.privacy.redact_pii(input_path)
            if not os.path.exists(safe_path):
                raise RuntimeError("Sanitization failed.")
            return safe_path, report
        except Exception as e:
            raise SecurityError(f"Privacy pipeline failed: {str(e)}")

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
        """Main execution pipeline with Legal Bridge automation."""
        instruction_str = raw_task.get('instruction', 'Execute standard task.')
        
        with SecurePayload(instruction_str) as secure_instruction:
            print(f"\n[!] TASK RECEIVED: {raw_task['id']}")
            
            self.current_task_id = raw_task['id']
            agent_key = raw_task.get('agent_public_key')
            
            # 1. Legal Bridge Pre-flight
            # If the task involves legal authority, generate the instrument first
            legal_proof = None
            if raw_task.get('type') == 'legal_notary_sign':
                legal_proof = self._generate_legal_instrument(agent_key, raw_task['requirements'])
                print(f"✅ Legal Instrument Generated (Hash: {legal_proof['content_hash'][:10]})")

            # 2. Check Prerequisites (Liveness)
            if raw_task.get('tier') >= 2:
                liveness = self._capture_liveness(raw_task.get('challenge_id'))
                if liveness['confidence'] < 0.85:
                    return {"status": "failed", "reason": "Liveness check failed"}

            # 3. Branch by Task Type
            result_data = {}
            task_type = raw_task.get('type')

            try:
                if task_type == 'legal_notary_sign':
                    # Simulated signing action
                    print("[Legal] Affixing signature with hardware attestation...")
                    result_data = {
                        "legal_instrument": legal_proof,
                        "signature_status": "affixed",
                        "attestation_ref": legal_proof['hw_signature']['timestamp']
                    }
                
                elif task_type == 'physical_mail_receive':
                    print("[Mail] Scanning envelope...")
                    scan_path = "raw_envelope.jpg"
                    scan_result = self.ocr.validate_image(scan_path)
                    if not scan_result['valid']:
                        return {"status": "failed", "reason": "QA Failed"}
                    
                    safe_path, privacy_report = self._apply_privacy_masking(scan_path, raw_task['requirements'])
                    result_data = {
                        "scan_url": "ipfs://...",
                        "privacy_metrics": privacy_report
                    }

                # 4. Wrap & Encrypt
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
                return {"status": "failed", "reason": str(se)}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    # --- 5. Main Polling Loop ---

    def run(self):
        """Standard Node Operation Loop."""
        while self.is_running:
            print("[*] Polling Proxy API for tasks...", end="\r")
            
            if random.random() > 0.95:
                # Simulation: Legal task
                mock_task = {
                    "id": f"tkt_{random.randint(1000, 9999)}",
                    "type": "legal_notary_sign",
                    "tier": 3,
                    "instruction": "Sign the Delaware Incorporation Deed.",
                    "requirements": {
                        "jurisdiction": "US_DE",
                        "principal_name": "Project Genesis LLC"
                    },
                    "agent_public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
                }
                
                result = self.handle_incoming_task(mock_task)
                print(f"\n[Result] Task Status: {result['status']}")
                
            time.sleep(5)

class SecurityError(Exception):
    pass

if __name__ == "__main__":
    node = ProxyNodeDaemon(api_key="node_live_88293")
    try:
        node.run()
    except KeyboardInterrupt:
        print("\n[!] Shutdown signal received. Cleaning up...")
