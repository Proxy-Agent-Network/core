import time
import logging
import json
import hashlib
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

# PROXY PROTOCOL - ADJUDICATION ARCHIVIST API (v1.0)
# "Hardening the immutable record of decentralized justice."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Adjudication Archivist",
    description="Permanent storage and lookup service for High Court verdicts.",
    version="1.0.0"
)

# --- Models ---

class CaseLawEntry(BaseModel):
    case_id: str
    verdict: str # APPROVE, REJECT
    finalized_at: int
    consensus_stats: str # e.g. "6/7"
    manifest_hash: str
    economic_recap: Dict
    forensic_link: str # IPFS or internal storage URL

class ArchiveSearchResponse(BaseModel):
    total_results: int
    entries: List[CaseLawEntry]

# --- Internal Archiving Logic ---

class AdjudicationArchivist:
    """
    Maintains the permanent, auditable ledger of High Court decisions.
    Serves as the source of truth for 'Protocol Precedent'.
    """
    def __init__(self):
        # Format: { "case_id": CaseLawEntry }
        self.verdict_archive: Dict[str, CaseLawEntry] = {
            "CASE-8829-APP": CaseLawEntry(
                case_id="CASE-8829-APP",
                verdict="REJECTED",
                finalized_at=int(time.time() - 86400),
                consensus_stats="6/7",
                manifest_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                economic_recap={"payout": 0, "slash_count": 1, "slash_total": 600000},
                forensic_link="https://forensics.proxyagent.network/v1/bundles/PXA-8829.pxa"
            )
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ArchivistAPI")

    def archive_verdict(self, data: Dict) -> str:
        """
        Ingests a finalized consensus report and creates a permanent entry.
        """
        case_id = data.get('case_id')
        now = int(time.time())
        
        # Calculate unique manifest ID
        manifest_id = f"LAW-{hashlib.sha256(f'{case_id}:{now}'.encode()).hexdigest()[:8].upper()}"
        
        entry = CaseLawEntry(
            case_id=case_id,
            verdict=data.get('verdict'),
            finalized_at=now,
            consensus_stats=data.get('consensus'),
            manifest_hash=data.get('manifest_hash'),
            economic_recap=data.get('economic_report', {}),
            forensic_link=f"https://forensics.proxyagent.network/v1/archive/{case_id}.pxa"
        )
        
        self.verdict_archive[case_id] = entry
        self.logger.info(f"📜 CASE_ARCHIVED: {case_id} recorded as precedent.")
        
        return manifest_id

# Initialize Engine
archivist = AdjudicationArchivist()

# --- API Endpoints ---

@app.post("/v1/archivist/ingest", status_code=201)
async def ingest_new_verdict(payload: Dict):
    """
    Internal endpoint for the Verdict Publisher.
    Commits a finalized case to the permanent ledger.
    """
    try:
        manifest_id = archivist.archive_verdict(payload)
        return {"status": "ARCHIVED", "manifest_id": manifest_id}
    except Exception as e:
        logging.error(f"Archive failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal archival error.")

@app.get("/v1/archivist/lookup/{case_id}", response_model=CaseLawEntry)
async def get_verdict_record(case_id: str):
    """Retrieves the authoritative record for a specific case."""
    entry = archivist.verdict_archive.get(case_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Case record not found in archive.")
    return entry

@app.get("/v1/archivist/search", response_model=ArchiveSearchResponse)
async def search_archive(
    query: Optional[str] = Query(None),
    limit: int = 20
):
    """Searchable index of historical protocol decisions."""
    results = list(archivist.verdict_archive.values())
    
    if query:
        results = [e for e in results if query.lower() in e.case_id.lower() or query.lower() in e.verdict.lower()]
        
    return ArchiveSearchResponse(
        total_results=len(results),
        entries=results[:limit]
    )

@app.get("/health")
async def health():
    return {"status": "online", "persistence_layer": "READY"}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8028 for legal archival
    print("[*] Launching Protocol Adjudication Archivist API on port 8028...")
    uvicorn.run(app, host="0.0.0.0", port=8028)
