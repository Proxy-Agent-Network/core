import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor

# 🛑 THE FIX #1: Strict Database URL Enforcement (Fail-Closed)
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL or "proxy_secure_password" in DB_URL:
    print(" [SECURITY] 🚨 CRITICAL: DATABASE_URL is missing or uses the insecure default!")
    raise ValueError("Application halted. You must provide a secure DATABASE_URL in the environment.")

class DBWrapper:
    def __init__(self):
        self.conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        
    def quote_identifier(self, identifier: str) -> str:
        """
        🛡️ PHASE 6 FIX: Safely quote SQL identifiers (tables/columns) to prevent injection.
        Policy: Strictly enforces alphanumeric and underscore formats.
        """
        if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
            raise ValueError(f"Invalid SQL identifier format detected: {identifier}")
        return f'"{identifier}"'
        
    def execute(self, query, params=None):
        # 🛑 SECURITY FIX: Pure native parameterization
        c = self.conn.cursor()
        c.execute(query, params)
        return c
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()

def get_db_conn():
    return DBWrapper()