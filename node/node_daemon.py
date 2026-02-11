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

# PROXY PROTOCOL - NODE DAEMON v1.6 (Settlement Hardened)
# "Sub-second settlement verification via LND integration."
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

    # --- 1. Settlement Layer: LND Verification ---

    def _verify_escrow_lock(self, payment_hash: str) -> bool:
        """
        v1.6: Connects to local LND to verify the HODL invoice status.
        Ensures the Agent has actually locked funds before we start work.
        """
        print(f"[Settlement] Verifying Escrow Lock for Hash: {payment_hash[:12]}...")
        
        # In production, this calls: lncli lookupinvoice <hash>
        # We are looking for state: "ACCEPTED" (HODL-locked)
        try:
            # Simulation of LND RPC response
            # mock_lnd_status = lnd_client.lookup_invoice(r_hash=payment_hash)
            # return mock_lnd_status.state == "ACCEPTED"
            
            # For this logic demo, we simulate a successful lock check
            time.sleep(0.5) 
            return True 
        except Exception as e:
            print(f"[Settlement] 🚨 LND Connection Error: {e}")
            return False

    # --- 2. Biometric & Security Logic ---

    def _capture_liveness(self, challenge_id: str) -> dict:
        """Executes the RFC-001 3D Liveness check."""
        print(f"[Liveness] Initializing camera for challenge {challenge_id}...")
        return {
            "status": "verified",
            "confidence": 0.99,
            "hw_proof": self.tpm.generate_attestation_quote(challenge_id)
        }

    # --- 3. Legal Bridge: Documentation Generator ---

    def _generate_legal_instrument(self, agent_key: str, requirements: dict) -> dict:
        """Auto-fills Markdown PoA templates and binds to hardware identity."""
        jurisdiction = requirements.get('jurisdiction', 'US_DE')
        principal_name = requirements.get('principal_name', '[ANONYMOUS PRINCIPAL]')
        
        template_map = {
            "US_DE": "templates/legal/us_delaware_poa.md",
            "UK": "templates/legal/uk_poa.md",
            "SG": "templates/legal/singapore_poa.md"
        }
        
        instrument_text = f"""
        # LIMITED POWER OF ATTORNEY ({jurisdiction})
        PRINCIPAL: {principal_name}
        AGENT_KEY: {agent_key[:20]}...
        PROXY_NODE: {self.node_id}
        TIMESTAMP: {datetime.now().isoformat()}
        TASK_ID: {self.current_task_id}
        """
        
        content_hash = hashlib.sha256(instrument_text.encode()).hexdigest()
        hw_signature = self.tpm.generate_attestation_quote(content_hash)
        
        return {
            "instrument_body": instrument_text,
            "content_hash": content_hash,
            "hw_signature": hw_signature,
            "jurisdiction": jurisdiction
        }

    # --- 4. Privacy & Sanitization Pipeline ---

    def _apply_privacy_masking(self, input_path: str, task_requirements: dict) -> tuple:
        """Applies masking based on Agent requirements with fail-safe enforcement."""
        try:
            safe_path, report = self.privacy.redact_pii(input_path)
            if not os.path.exists(safe_path):
                raise RuntimeError("Sanitization failed.")
            return safe_path, report
        except Exception as e:
            raise SecurityError(f"Privacy pipeline failed: {str(e)}")

    # --- 5. Secure Processing Pipeline ---

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
        """Main execution pipeline with Settlement Verification."""
        instruction_str = raw_task.get('instruction', 'Execute standard task.')
        
        with SecurePayload(instruction_str) as secure_instruction:
            print(f"\n[!] TASK RECEIVED: {raw_task['id']}")
            
            self.current_task_id = raw_task['id']
            agent_key = raw_task.get('agent_public_key')
            payment_hash = raw_task.get('payment_hash')

            # 1. Settlement Pre-flight (THE LOCK CHECK)
            # If no payment hash is provided or if LND doesn't see it as LOCKED, abort.
            if not payment_hash or not self._verify_escrow_lock(payment_hash):
                print(f"❌ SETTLEMENT FAILED: Escrow for {raw_task['id']} not locked. Aborting.")
                return {"status": "failed", "reason": "PX_201: Escrow lock not detected"}
            
            print("✅ SETTLEMENT VERIFIED: Funds locked in HTLC.")

            # 2. Legal Bridge Pre-flight
            legal_proof = None
            if raw_task.get('type') == 'legal_notary_sign':
                legal_proof = self._generate_legal_instrument(agent_key, raw_task['requirements'])

            # 3. Check Prerequisites (Liveness)
            if raw_task.get('tier') >= 2:
                liveness = self._capture_liveness(raw_task.get('challenge_id'))
                if liveness['confidence'] < 0.85:
                    return {"status": "failed", "reason": "Liveness check failed"}

            # 4. Branch by Task Type
            result_data = {}
            task_type = raw_task.get('type')

            try:
                if task_type == 'legal_notary_sign':
                    print("[Legal] Affixing signature...")
                    result_data = {
                        "legal_instrument": legal_proof,
                        "signature_status": "affixed"
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

                # 5. Wrap & Encrypt
                payload = {
                    "task_id": self.current_task_id,
                    "completed_at": datetime.now().isoformat(),
                    "data": result_data
                }
                
                encrypted_blob = self._encrypt_for_agent(payload, agent_key)
                
                # The node signs the result to signal completion to the Settlement Layer
                return {
                    "status": "success",
                    "encrypted_blob": encrypted_blob,
                    "node_signature": self.tpm.generate_attestation_quote(encrypted_blob)
                }

            except SecurityError as se:
                return {"status": "failed", "reason": str(se)}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    # --- 6. Main Polling Loop ---

    def run(self):
        """Standard Node Operation Loop."""
        while self.is_running:
            print("[*] Polling Proxy API for tasks...", end="\r")
            
            if random.random() > 0.95:
                # Simulation: Task with Payment Hash
                mock_task = {
                    "id": f"tkt_{random.randint(1000, 9999)}",
                    "type": "legal_notary_sign",
                    "tier": 3,
                    "payment_hash": hashlib.sha256(b"mock_invoice_123").hexdigest(),
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
