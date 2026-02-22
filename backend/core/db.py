import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_URL = os.environ.get("DATABASE_URL", "postgresql://proxy_admin:proxy_secure_password@db:5432/proxy_network")

class DBWrapper:
    def __init__(self):
        self.conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        
    def execute(self, query, params=None):
        # Auto-translate SQLite param syntax to Postgres syntax
        q = query.replace("?", "%s")
        c = self.conn.cursor()
        c.execute(q, params)
        return c
        
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()

def get_db_conn():
    return DBWrapper()