"""
Synchronous Postgres connection helper for the FastAPI gateway.

This module provides a per-request DBWrapper using psycopg2-binary, mirroring
the pattern used by the legacy Flask app at apps/backend/entrypoints/app.py.
The Flask version lives at core/db.py (currently absent from the repo, but
referenced by app.py imports during the parallel period); this FastAPI copy
is intentionally self-contained so that retiring core/ in Stage 2 does not
require touching FastAPI code.

Why sync psycopg2 in a FastAPI codebase:
- FastAPI runs sync `def` route handlers in a threadpool automatically, so
  blocking psycopg2 calls do not stall the event loop for other requests.
- The query volume for the Vanguard 50 pilot is low; the throughput
  difference vs asyncpg only matters at scale far beyond pilot needs.
- The existing Flask handlers all use sync psycopg2; reusing the same
  pattern means we can translate handlers line-for-line during Stage 1d-3
  without simultaneously rewriting their SQL access.
- If a future scale-up requires async, swapping this single module to
  asyncpg is a contained refactor that does not ripple through every
  endpoint.

Usage in a FastAPI route:

    from fastapi import APIRouter, Depends
    from utils.db import get_db_dep, DBWrapper

    router = APIRouter()

    @router.get("/some/endpoint")
    def some_endpoint(db: DBWrapper = Depends(get_db_dep)):
        cur = db.execute("SELECT count(*) FROM nodes WHERE last_seen > %s",
                         (cutoff,))
        row = cur.fetchone()
        return {"count": row["count"]}

Note that the route is `def` (not `async def`). FastAPI's threadpool runs
the handler off the event loop, which is the supported pattern for sync
database libraries.
"""

import os
import re
import logging
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("PAN_DB")

# DATABASE_URL is required at module import time. The legacy core/db.py used
# the same fail-closed pattern: if the env var is missing or contains an
# obviously-insecure default, refuse to load the module rather than letting
# the app boot with broken DB access.
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise RuntimeError(
        "DATABASE_URL is not set in the environment. "
        "FastAPI gateway requires a Postgres connection string to start."
    )
if "proxy_secure_password" in DB_URL:
    raise RuntimeError(
        "DATABASE_URL contains the insecure default password. "
        "Set a real password before starting the gateway."
    )


class DBWrapper:
    """Per-request Postgres connection wrapper.

    Wraps a single psycopg2 connection with a RealDictCursor (so query
    results come back as dicts instead of tuples). Provides a small set of
    helpers: execute(), commit(), close(), and quote_identifier() for safe
    table/column name interpolation.

    Mirrors the behavior of the legacy Flask DBWrapper class so handlers
    written against either pattern work identically.
    """

    def __init__(self):
        self.conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

    def quote_identifier(self, identifier: str) -> str:
        """Safely quote a SQL identifier (table or column name).

        Identifiers cannot be parameterized with %s (psycopg2 only supports
        parameterization for values, not for table/column names). When you
        need to dynamically choose a table or column at query time, run the
        identifier through this method first to defend against SQL injection.

        Strict policy: only alphanumeric and underscore characters are
        allowed. Anything else raises ValueError.
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", identifier):
            raise ValueError(f"Invalid SQL identifier format: {identifier}")
        return f'"{identifier}"'

    def execute(self, query: str, params: Optional[tuple] = None):
        """Execute a parameterized query and return the cursor.

        Use %s placeholders in the query and pass values as a tuple in
        params. Never use string formatting to interpolate user input into
        a query - psycopg2's native parameterization is the only safe path.
        """
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        except Exception as e:
            logger.warning(f"Error closing DB connection: {e}")


def get_db_dep():
    """FastAPI dependency that yields a DBWrapper per request.

    Use as Depends(get_db_dep) in a route signature. The connection is
    opened when the route is invoked and closed after the response is sent,
    even if the route raises. The yield/finally pattern is FastAPI's
    standard contract for resource-managing dependencies.

    Each request gets its own connection. There is no connection pool at
    this layer - psycopg2.connect() creates a fresh connection per request.
    For pilot-scale traffic this is fine; if connection establishment
    overhead ever becomes a bottleneck, switch to psycopg2.pool.ThreadedConnectionPool
    or migrate this module to asyncpg.
    """
    db = DBWrapper()
    try:
        yield db
    finally:
        db.close()
