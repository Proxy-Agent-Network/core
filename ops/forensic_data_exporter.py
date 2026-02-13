import time
import json
import hashlib
import hmac
import base64
import logging
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from datetime import datetime

# PROXY PROTOCOL - FORENSIC DATA EXPORTER (v1.0)
# "Sealing the audit trail for institutional review."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Forensic Exporter",
    description="Authorized utility for packaging and signing forensic evidence bundles.",
    version="1.0.0"
)

# --- Configuration ---
# In production, this uses the Foundation HSM's master forensic key
FORENSIC_SIGNING_SECRET = "hsm_sec_88293_forensic_root"

class ForensicBundleRequest(BaseModel):
    investigation_id: str
    target_node_id: str
    evidence_items: List[Dict[str, Any]] # List of dHash matches, logs, and quotes
    auditor_id: str
    intended_recipient: str # e.g. "INSURANCE_PARTNER_A"

class ExportReceipt(BaseModel):
    export_id: str
    bundle_hash: str
    foundation_signature: str
    manifest_url: str
    timestamp: int
    retention_expiry: int

class ForensicExporter:
    """
    Service that aggregates forensic metadata and generates 
    a JWS-style signed archive for legal submission.
    """
    def __init__(self):
        self.RETENTION_DAYS = 30 # Forensic bundles are held longer than proofs
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ForensicExporter")

    def _generate_manifest_hash(self, data: Dict) -> str:
        """Deterministic SHA256 of the bundle content."""
        canonical = json.dumps(data, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _sign_bundle(self, bundle_hash: str) -> str:
        """Signs the bundle hash using the Foundation Forensic HSM secret."""
        return hmac.new(
            FORENSIC_SIGNING_SECRET.encode(),
            bundle_hash.encode(),
            hashlib.sha256
        ).hexdigest()

    async def package_evidence(self, request: ForensicBundleRequest) -> ExportReceipt:
        """
        Creates an immutable manifest of the investigation results.
        """
        self.logger.info(f"[*] Packaging Forensic Bundle for investigation: {request.investigation_id}")

        now = int(time.time())
        export_id = f"PXA-{request.investigation_id}-{now}"
        
        # 1. Construct the Manifest
        manifest = {
            "export_id": export_id,
            "version": "1.0",
            "protocol": "v3.4.3",
            "auditor": request.auditor_id,
            "target": request.target_node_id,
            "recipient": request.intended_recipient,
            "content_summary": {
                "item_count": len(request.evidence_items),
                "types": list(set([i.get('type', 'GENERIC') for i in request.evidence_items]))
            },
            "evidence_ledger": request.evidence_items,
            "timestamp": now
        }

        # 2. Cryptographic Binding
        bundle_hash = self._generate_manifest_hash(manifest)
        signature = self._sign_bundle(bundle_hash)
        
        expiry = now + (self.RETENTION_DAYS * 86400)

        # 3. Final Receipt
        receipt = ExportReceipt(
            export_id=export_id,
            bundle_hash=bundle_hash,
            foundation_signature=signature,
            manifest_url=f"https://forensics.proxyagent.network/v1/bundles/{export_id}.pxa",
            timestamp=now,
            retention_expiry=expiry
        )

        self.logger.info(f"✅ Forensic Bundle Sealed: {export_id} (Sig: {signature[:12]}...)")
        return receipt

# Initialize Exporter
exporter = ForensicExporter()

# --- API Endpoints ---

@app.post("/v1/forensics/export/package", response_model=ExportReceipt)
async def create_forensic_bundle(payload: ForensicBundleRequest):
    """
    Primary endpoint for the Forensic Portal.
    Bundles investigation data into a signed PXA file.
    """
    try:
        return await exporter.package_evidence(payload)
    except Exception as e:
        logging.error(f"Packaging failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal HSM signing error.")

@app.get("/v1/forensics/verify/{export_id}")
async def verify_bundle(export_id: str, bundle_hash: str, signature: str):
    """
    Public verification endpoint for recipients.
    Allows insurance partners to confirm the bundle hasn't been tampered with.
    """
    # Re-verify HMAC signature logic
    expected_sig = exporter._sign_bundle(bundle_hash)
    is_valid = hmac.compare_digest(expected_sig, signature)
    
    return {
        "export_id": export_id,
        "valid": is_valid,
        "trust_anchor": "PROXY_FOUNDATION_MASTER_HSM",
        "timestamp": int(time.time())
    }

@app.get("/health")
async def health():
    return {"status": "online", "hsm_link": "STABLE", "export_format": "PXA_V1"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8023 for forensic orchestration
    print("[*] Launching Protocol Forensic Exporter API on port 8023...")
    uvicorn.run(app, host="0.0.0.0", port=8023)
