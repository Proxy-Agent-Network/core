import base64
import json
import sqlite3
from datetime import datetime
import os

class ProxyRegistryVerifier:
    def __init__(self, db_path="registry.db"):
        self.db_path = db_path
        self._bootstrap_db()

    def _bootstrap_db(self):
        """Initializes the SQLite database with Nodes and Tasks tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 1. Nodes Table (Identities)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    hardware_id TEXT UNIQUE,
                    enrolled_at TEXT,
                    status TEXT,
                    ak_public TEXT,
                    reputation_score INTEGER DEFAULT 100
                )
            ''')
            # 2. Tasks Table (The Order Book)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    node_id TEXT,
                    task_type TEXT,
                    bid_sats INTEGER,
                    status TEXT,
                    created_at TEXT,
                    settled_at TEXT,
                    FOREIGN KEY (node_id) REFERENCES nodes (node_id)
                )
            ''')
            conn.commit()

    # --- NODE LOGIC ---

    def verify_enrollment(self, payload):
        manifest = payload.get("hardware_manifest")
        ek_pub = manifest.get("ek_public")
        ak_pub = manifest.get("ak_public")
        
        # Check for existing hardware
        existing_node = self._get_node_by_hardware_id(ek_pub)
        if existing_node:
            return {"status": "SUCCESS", "node_id": existing_node[0], "message": "Re-authenticated."}

        new_id = f"NODE-{base64.b16encode(os.urandom(4)).decode()}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO nodes (node_id, hardware_id, enrolled_at, status, ak_public) VALUES (?, ?, ?, ?, ?)",
                (new_id, ek_pub, datetime.utcnow().isoformat(), "VERIFIED", ak_pub)
            )
        return {"status": "SUCCESS", "node_id": new_id}

    def _get_node_by_hardware_id(self, hardware_id):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT node_id, enrolled_at, status FROM nodes WHERE hardware_id = ?", (hardware_id,)).fetchone()

    # --- TASK / ORDER BOOK LOGIC ---

    def create_task(self, agent_id, task_type, bid_sats):
        """Adds a new Bid to the Order Book."""
        task_id = f"TASK-{base64.b16encode(os.urandom(4)).decode()}"
        created_at = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tasks (task_id, agent_id, task_type, bid_sats, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (task_id, agent_id, task_type, bid_sats, "OPEN", created_at)
            )
        return task_id

    def get_open_tasks(self):
        """Allows Nodes to 'poll' for available work."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row # Returns results as dictionaries
            cursor = conn.execute("SELECT * FROM tasks WHERE status = 'OPEN' ORDER BY bid_sats DESC")
            return [dict(row) for row in cursor.fetchall()]
