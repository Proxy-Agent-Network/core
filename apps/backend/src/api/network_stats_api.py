"""
Network stats endpoint for the command_center dashboard.

Migrated from Flask app.py /api/v1/network/stats route (Stage 1d-3-b-2).

Returns a small JSON payload with the count of active nodes (nodes with a
last_seen timestamp within the last 5 minutes) plus a few static fields.
The Flask version is preserved during the parallel period; both Flask and
FastAPI versions execute the same query against the same nodes table.
"""

import logging
import time

from fastapi import APIRouter, Depends

from utils.db import DBWrapper, get_db_dep

logger = logging.getLogger("PAN_NetworkStats")
router = APIRouter()


@router.get("/network/stats")
def get_network_stats(db: DBWrapper = Depends(get_db_dep)):
    """Active-node count plus protocol metadata.

    Note: this is a sync `def` route, NOT `async def`. FastAPI runs sync
    routes in a threadpool, which is the supported pattern for blocking
    database libraries like psycopg2. See utils/db.py docstring for the
    rationale.
    """
    cutoff = time.time() - 300  # 5 minutes
    cur = db.execute(
        "SELECT COUNT(*) AS cnt FROM nodes WHERE last_seen > %s",
        (cutoff,),
    )
    row = cur.fetchone()
    active_nodes = row["cnt"] if row else 0

    return {
        "total_volume": "ENCRYPTED",
        "active_nodes": active_nodes,
        "peers": active_nodes,
        "protocol_v": "1.6.0",
        "status": "STABLE",
    }
