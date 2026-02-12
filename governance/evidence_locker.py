import os
import json
import base64
from typing import Dict, List, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# PROXY PROTOCOL - JURY EVIDENCE LOCKER (v1.0)
# "Confidential evidence delivery for High Court jurors."
# ----------------------------------------------------

class EvidenceLocker:
    """
    The Locker handles the multi-party encryption of dispute evidence.
    It ensures that only the 7 jurors selected by the AppellateVRF
    can access the sanitized task payload.
    """
    def __init__(self, storage_path: str = "/app/data/evidence_locker/"):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def seal_evidence(self, case_id: str, payload: Dict, juror_pubkeys: Dict[str, str]) -> bool:
        """
        Encrypts the evidence payload for each juror using their unique Public Key.
        
        Args:
            case_id: The unique ID of the dispute.
            payload: The sanitized data (OCR results, TPM quotes, task logs).
            juror_pubkeys: Dict mapping node_id to PEM-encoded Public Key.
        """
        print(f"[*] Sealing evidence for Case {case_id} across {len(juror_pubkeys)} jurors...")
        
        try:
            raw_data = json.dumps(payload).encode('utf-8')
            case_dir = os.path.join(self.storage_path, case_id)
            if not os.path.exists(case_dir):
                os.makedirs(case_dir)

            for node_id, pem_key in juror_pubkeys.items():
                # Load Juror's Hardware-Bound Public Key
                public_key = serialization.load_pem_public_key(pem_key.encode('utf-8'))
                
                # RSA-OAEP Encryption
                ciphertext = public_key.encrypt(
                    raw_data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                # Store the encrypted shard for this specific node
                shard_path = os.path.join(case_dir, f"{node_id}.shard")
                with open(shard_path, "wb") as f:
                    f.write(ciphertext)
                
            return True
        except Exception as e:
            print(f"[Locker] 🚨 Encryption Error: {str(e)}")
            return False

    def fetch_shard(self, case_id: str, node_id: str) -> Optional[str]:
        """
        Retrieves the encrypted blob for a specific juror.
        """
        shard_path = os.path.join(self.storage_path, case_id, f"{node_id}.shard")
        if not os.path.exists(shard_path):
            return None
            
        with open(shard_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def purge_case(self, case_id: str):
        """
        Scorched Earth: Wipes the evidence directory for a case after finality.
        """
        import shutil
        case_dir = os.path.join(self.storage_path, case_id)
        if os.path.exists(case_dir):
            shutil.rmtree(case_dir)
            print(f"[*] Case {case_id} purged from Evidence Locker.")

# --- Protocol Integration Test ---
if __name__ == "__main__":
    locker = EvidenceLocker()
    
    # Mock Data
    case_id = "CASE_992_DISPUTE"
    sanitized_evidence = {
        "task_id": "T-882",
        "human_proof_hash": "e3b0c442...",
        "ocr_redacted_text": "DEED OF TRUST: [REDACTED]",
        "tpm_attestation_status": "VERIFIED"
    }
    
    # In a real flow, these come from the Node Registry for the selected jurors
    mock_jurors = {
        "NODE_ELITE_X29": "PEM_PUBLIC_KEY_DATA_HERE...",
        "NODE_ALPHA_001": "PEM_PUBLIC_KEY_DATA_HERE..."
    }
    
    # Simulation
    print("--- EVIDENCE LOCKER CEREMONY ---")
    # Note: This will fail in CLI without real PEM strings, but illustrates the logic.
