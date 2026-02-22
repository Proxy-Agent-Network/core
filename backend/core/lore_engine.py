import sqlite3
import json
import random
import os

DB_PATH = "agency_lore.db"

def initialize_corporate_ladder():
    print("🧠 Booting Emotion Engine & Corporate Ladder...")
    
    # Load the Jumble
    if not os.path.exists("core_memories.json"):
        print("❌ Error: core_memories.json not found!")
        return

    with open("core_memories.json", "r") as f:
        all_memories = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            name TEXT PRIMARY KEY,
            role TEXT,
            tier TEXT,
            trust_score INTEGER,
            earnings INTEGER,
            tasks_completed INTEGER,
            memories TEXT
        )
    ''')

    # The starting roster
    starting_roster = [
        {"name": "Alice", "role": "Manager", "tier": "L4"},
        {"name": "Diana", "role": "Creative Director", "tier": "L4"},
        {"name": "Eve", "role": "Specialist", "tier": "L5"},
        {"name": "Gordon", "role": "Specialist", "tier": "L5"},
        {"name": "Olivia", "role": "Specialist", "tier": "L5"},
        {"name": "Ellen", "role": "Specialist", "tier": "L5"},
        {"name": "Marcus", "role": "Specialist", "tier": "L5"}
    ]

    for agent in starting_roster:
        # Check if agent exists
        c.execute("SELECT name FROM agents WHERE name=?", (agent["name"],))
        if not c.fetchone():
            # Draw 7 random memories
            selected_memories = random.sample(all_memories, min(7, len(all_memories)))
            
            # Everyone starts with a neutral trust score of 50
            c.execute('''
                INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (agent["name"], agent["role"], agent["tier"], 50, 0, 0, json.dumps(selected_memories)))
            print(f"✨ Synthesized {agent['name']} with 7 core memories.")

    conn.commit()
    conn.close()
    print("✅ Autonomous Roster Online.")

if __name__ == "__main__":
    initialize_corporate_ladder()