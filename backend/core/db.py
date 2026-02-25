import os
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
        
    def execute(self, query, params=None):
        # 🛑 SECURITY FIX: Pure native parameterization
        # The query already contains %s placeholders from app.py.
        # Passing it directly to psycopg2 prevents SQL corruption from escaped strings.
        c = self.conn.cursor()
        c.execute(query, params)
        return c
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()

def get_db_conn():
    return DBWrapper()