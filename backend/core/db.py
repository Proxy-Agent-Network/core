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
        
    def execute(self, query, params=None):
        # 🛑 THE FIX #2: Smart Parameter Replacement
        # This regex looks for either a single-quoted string OR a question mark.
        # If it finds a question mark outside of quotes, it replaces it with %s.
        # If it finds a quoted string (like '?id=5'), it leaves it completely untouched.
        safe_query = re.sub(r"(('[^']*')|(\?))", lambda m: '%s' if m.group(3) else m.group(1), query)
        
        c = self.conn.cursor()
        c.execute(safe_query, params)
        return c
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()

def get_db_conn():
    return DBWrapper()