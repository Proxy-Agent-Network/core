import time
import logging
import json
import hashlib
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# PROXY PROTOCOL - PRECEDENT SEARCH API (v1.0)
# "Semantic discovery for the autonomous legal archive."
# ----------------------------------------------------

app = FastAPI(
    title="Proxy Protocol Precedent Search",
    description="Vector-assisted search engine for High Court historical verdicts.",
    version="1.0.0"
)

# --- Models ---

class SearchMatch(BaseModel):
    case_id: str
    title: str
    relevance_score: float # 0.0 to 1.0
    verdict: str
    region: str
    summary_snippet: str
    manifest_hash: str

class SearchResponse(BaseModel):
    query: str
    results_count: int
    matches: List[SearchMatch]
    search_time_ms: float

# --- Internal Search Logic ---

class PrecedentSearchEngine:
    """
    Implements mock vector embeddings and keyword-weighted search
    to find relevant 'Case Law' within the protocol archive.
    """
    def __init__(self):
        # Simulation: This would normally interface with a vector DB (Pinecone/Milvus)
        # and a local embedding model (all-MiniLM-L6-v2).
        self.archive_cache: List[Dict] = [
            {
                "id": "CASE-8829-APP",
                "title": "Protocol Breach: Metadata Forgery",
                "summary": "Suspicion of coordinated dHash collision across regional hubs.",
                "region": "ASIA_SE",
                "verdict": "REJECTED",
                "hash": "e3b0c442...",
                "keywords": ["dhash", "collision", "forgery", "metadata", "asia"]
            },
            {
                "id": "CASE-8772-APP",
                "title": "Dispute: Notary Seal Validity",
                "summary": "Determined that digital seals via RON hardware are equivalent to physical embossed seals.",
                "region": "GLOBAL",
                "verdict": "APPROVED",
                "hash": "3b7c89f...",
                "keywords": ["notary", "ron", "seal", "digital", "legal"]
            },
            {
                "id": "CASE-8421-APP",
                "title": "Task Contest: Geofence Drift",
                "summary": "Stationary nodes must maintain zero-drift locality proofs.",
                "region": "US_WEST",
                "verdict": "REJECTED",
                "hash": "8a2e1c...",
                "keywords": ["geofence", "drift", "gps", "locality", "stationary"]
            }
        ]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SearchAPI")

    def _calculate_mock_relevance(self, query: str, entry: Dict) -> float:
        """
        Simulates vector cosine similarity using keyword overlap.
        """
        query_words = set(query.lower().split())
        match_count = 0
        
        # Check title and summary
        combined_text = (entry['title'] + " " + entry['summary']).lower()
        for word in query_words:
            if word in combined_text:
                match_count += 2 # Weighted higher
            elif word in entry['keywords']:
                match_count += 1
                
        # Normalize score
        return min(0.99, match_count / (len(query_words) + 1))

    def execute_query(self, query: str, limit: int) -> List[SearchMatch]:
        """
        Runs the semantic search pipeline.
        """
        self.logger.info(f"[*] Executing Precedent Query: '{query}'")
        
        results = []
        for entry in self.archive_cache:
            score = self._calculate_mock_relevance(query, entry)
            if score > 0.1:
                results.append(SearchMatch(
                    case_id=entry['id'],
                    title=entry['title'],
                    relevance_score=score,
                    verdict=entry['verdict'],
                    region=entry['region'],
                    summary_snippet=entry['summary'],
                    manifest_hash=entry['hash']
                ))

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

# Initialize Engine
search_engine = PrecedentSearchEngine()

# --- API Endpoints ---

@app.get("/v1/forensics/search", response_model=SearchResponse)
async def search_archive(
    q: str = Query(..., min_length=3, description="Natural language search query"),
    limit: int = Query(5, ge=1, le=20),
    region: Optional[str] = None
):
    """
    Search endpoint for the Case Law Explorer.
    Powers the 'Semantic Precedent' lookups.
    """
    start_time = time.time()
    
    try:
        matches = search_engine.execute_query(q, limit)
        
        # Optional: Hard region filter (metadata filter)
        if region:
            matches = [m for m in matches if m.region.upper() == region.upper()]

        duration_ms = (time.time() - start_time) * 1000

        return SearchResponse(
            query=q,
            results_count=len(matches),
            matches=matches,
            search_time_ms=round(duration_ms, 2)
        )
    except Exception as e:
        # Fixed F821 error by referencing search_engine.logger instead of self.logger
        search_engine.logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="INTERNAL_SEARCH_ENGINE_ERROR")

@app.get("/v1/forensics/search/trending")
async def get_trending_disputes():
    """Returns categories seeing high dispute volumes."""
    return {
        "timestamp": int(time.time()),
        "trending_categories": ["DHASH_COLLISION", "GEOFENCE_DRIFT"],
        "total_active_audits": 14,
        "recommendation": "Increase regional actuary levy for ASIA_SE hub."
    }

@app.get("/health")
async def health():
    return {"status": "online", "engine": "SEMANTIC_V1", "index_synchronized": True}

if __name__ == "__main__":
    import uvicorn
    # Launched on internal port 8023 for legal engineering access
    print("[*] Launching Protocol Precedent Search API on port 8023...")
    uvicorn.run(app, host="0.0.0.0", port=8023)
