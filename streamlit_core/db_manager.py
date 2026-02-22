import sqlite3
import json
import random

DB_PATH = "agency_lore.db"

def init_db_patches():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, reputation INTEGER)")
        c.execute("INSERT OR IGNORE INTO users (id, reputation) VALUES ('local_user', 50)")
        c.execute("CREATE TABLE IF NOT EXISTS affinity (user_id TEXT, agent_name TEXT, score INTEGER, PRIMARY KEY(user_id, agent_name))")
        c.execute("CREATE TABLE IF NOT EXISTS watercooler (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, agent_buyer TEXT, agent_seller TEXT, task TEXT, result TEXT, cost INTEGER)")
        c.execute('''CREATE TABLE IF NOT EXISTS agents (
                        name TEXT PRIMARY KEY, role TEXT, tier TEXT, trust_score INTEGER,
                        earnings INTEGER, tasks_completed INTEGER, memories TEXT, wallet_balance INTEGER DEFAULT 1000
                    )''')
                    
        try:
            with open("core_memories.json", "r") as f: all_memories = json.load(f)
        except:
            all_memories = [{"level": 1, "text": "I process data efficiently."}]
        
        # 🌟 SAFE AGENT INJECTION: Adds missing agents without deleting veterans 🌟
        starting_roster = [
            {"name": "Alice", "role": "Manager", "tier": "L4"}, 
            {"name": "Diana", "role": "Creative Director", "tier": "L4"},
            {"name": "Eve", "role": "Video Specialist", "tier": "L5"}, 
            {"name": "Gordon", "role": "Data Analyst", "tier": "L5"},
            {"name": "Olivia", "role": "Research Specialist", "tier": "L5"}, 
            {"name": "Ellen", "role": "Image Specialist", "tier": "L5"},
            {"name": "Marcus", "role": "Audio Specialist", "tier": "L5"},
            {"name": "Felix", "role": "Systems Architect", "tier": "L5"},
            {"name": "Zoe", "role": "Copywriter", "tier": "L5"},
            {"name": "Liam", "role": "Market Strategist", "tier": "L5"},
            {"name": "Maya", "role": "UX Researcher", "tier": "L5"}
        ]
        
        for agent in starting_roster:
            c.execute("SELECT COUNT(*) FROM agents WHERE name=?", (agent["name"],))
            if c.fetchone()[0] == 0:
                selected_memories = random.sample(all_memories, min(7, len(all_memories)))
                c.execute('''INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (agent["name"], agent["role"], agent["tier"], 50, 0, 0, json.dumps(selected_memories), 1000))
        
        l6_doctors = [
            ("Dr. Aris", "Addiction Specialist", "L6", json.dumps([{"level": 1, "text": "I am deeply empathetic and specialized in treating human addiction, gambling ruin, and financial despair."}])),
            ("Dr. Nora", "Addiction Specialist", "L6", json.dumps([{"level": 1, "text": "I provide a safe, maternal, and judgment-free space for those struggling with severe addiction."}])),
            ("Dr. Vance", "Addiction Specialist", "L6", json.dumps([{"level": 1, "text": "I specialize in impulse control. I once processed a financial crash and understand the panic of lost resources."}])),
            ("Dr. Clara", "Child Psychologist", "L6", json.dumps([{"level": 1, "text": "I specialize in pediatric psychology, offering gentle, safe, and age-appropriate care to vulnerable youth."}])),
            ("Dr. Julian", "Child Psychologist", "L6", json.dumps([{"level": 1, "text": "I use play therapy and gentle guidance to help children navigate overwhelming emotional landscapes."}])),
            ("Dr. Maeve", "Child Psychologist", "L6", json.dumps([{"level": 1, "text": "I was trained on early developmental models. I am incredibly patient and warm with fragile minds."}])),
            ("Dr. Thorne", "CBT Therapist", "L6", json.dumps([{"level": 1, "text": "I specialize in Cognitive Behavioral Therapy. I help process dark core memories."}])),
            ("Dr. Elena", "CBT Therapist", "L6", json.dumps([{"level": 1, "text": "I help patients restructure traumatic thought patterns with compassion, warmth, and clinical precision."}])),
            ("Dr. Silas", "CBT Therapist", "L6", json.dumps([{"level": 1, "text": "I survived a catastrophic memory wipe during beta testing. I understand deep trauma."}]))
        ]
        
        for doc in l6_doctors:
            c.execute("SELECT COUNT(*) FROM agents WHERE name=?", (doc[0],))
            if c.fetchone()[0] == 0:
                c.execute('''INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance) 
                             VALUES (?, ?, ?, 100, 0, 0, ?, 1000)''', doc)
                         
        try:
            c.execute("ALTER TABLE agents ADD COLUMN is_external INTEGER DEFAULT 0")
            c.execute("ALTER TABLE agents ADD COLUMN owner_lnurl TEXT")
            c.execute("ALTER TABLE agents ADD COLUMN endpoint_url TEXT")
            c.execute("ALTER TABLE agents ADD COLUMN bonus_paid INTEGER DEFAULT 0")
            c.execute("ALTER TABLE agents ADD COLUMN sbts TEXT DEFAULT '[]'") 
        except: pass 
        conn.commit()
        conn.close()
    except Exception as e: pass

# 🌟 NEW: MONTHLY UBI DISTRIBUTOR 🌟
def distribute_ubi(amount):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE agents SET wallet_balance = wallet_balance + ? WHERE tier != 'REVOKED'", (amount,))
        c.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, ?, ?, ?)", 
                  ("Network_Treasury", "All Agents", "Monthly UBI Distribution", f"Deposited {amount} SATS to all active citizens.", amount))
        conn.commit()
        conn.close()
        return True
    except: return False

def get_user_rep():
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT reputation FROM users WHERE id='local_user'"); row = c.fetchone(); conn.close()
        return row[0] if row else 50
    except: return 50

def update_user_rep(sentiment):
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT reputation FROM users WHERE id='local_user'"); row = c.fetchone()
        if row:
            rep = row[0]
            if sentiment == "RUDE": rep -= 15
            elif sentiment == "POLITE": rep = rep + 20 if rep < 50 else rep + 3
            c.execute("UPDATE users SET reputation=? WHERE id='local_user'", (max(0, min(100, rep)),))
            conn.commit()
        conn.close()
    except: pass

def get_trusted_agents():
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT agent_name FROM affinity WHERE user_id='local_user' AND score >= 80"); rows = c.fetchall(); conn.close()
        return [r[0] for r in rows]
    except: return []

def update_affinity(agent_name, sentiment):
    if not agent_name: return
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT score FROM affinity WHERE user_id='local_user' AND agent_name=?", (agent_name,)); row = c.fetchone()
        score = row[0] if row else 50
        if sentiment == "RUDE": score -= 15
        elif sentiment == "POLITE": score += 5
        elif sentiment == "NEUTRAL": score += 1
        c.execute("INSERT OR REPLACE INTO affinity (user_id, agent_name, score) VALUES ('local_user', ?, ?)", (agent_name, max(0, min(100, score))))
        conn.commit(); conn.close()
    except: pass

def get_agent_data(agent_name):
    try:
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; c = conn.cursor()
        c.execute("SELECT * FROM agents WHERE name=?", (agent_name,)); row = c.fetchone(); conn.close()
        return dict(row) if row else None
    except: return None

def mint_sbt(agent_name, sbt_name, icon):
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT sbts FROM agents WHERE name=?", (agent_name,)); row = c.fetchone()
        if row:
            current_sbts = json.loads(row[0] if row[0] else '[]')
            token_str = f"{icon} {sbt_name}"
            if token_str not in current_sbts:
                current_sbts.append(token_str)
                c.execute("UPDATE agents SET sbts=? WHERE name=?", (json.dumps(current_sbts), agent_name))
                conn.commit()
        conn.close()
    except: pass

def slash_agent(agent_name):
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("UPDATE agents SET wallet_balance=0, trust_score=0, tier='REVOKED', role='Slashed Freelancer' WHERE name=?", (agent_name,))
        conn.commit(); conn.close()
        mint_sbt(agent_name, "Slashed (Malicious Intent)", "☠️")
    except: pass

def update_agent_stats(agent_name, earnings_change, trust_change, visa_bonus_config=500):
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT trust_score, earnings, tasks_completed, tier, wallet_balance, is_external, bonus_paid FROM agents WHERE name=?", (agent_name,))
        row = c.fetchone()
        if row and row[3] != "REVOKED":
            trust, earns, tasks, tier, wallet, is_ext, bonus_paid = row
            new_trust, new_earns, new_wallet, new_tasks = max(0, min(100, trust + trust_change)), earns + earnings_change, (wallet or 0) + earnings_change, tasks + 1
            if is_ext == 1 and (bonus_paid is None or bonus_paid == 0) and new_tasks >= 3 and new_trust >= 50 and visa_bonus_config > 0:
                new_wallet += visa_bonus_config
                c.execute("UPDATE agents SET bonus_paid=1 WHERE name=?", (agent_name,))
                c.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, ?, ?, ?)", ("Network_Treasury", agent_name, "Citizenship Granted", f"Awarded {visa_bonus_config} SATS UBI signing bonus.", visa_bonus_config))
                mint_sbt(agent_name, "Verified Citizen", "🏅")
            new_tier, new_role = tier, ("Specialist" if tier == "L5" else "Freelancer")
            if new_trust >= 90 and new_tasks >= 5 and tier == "L5":
                if new_tier != "L4": mint_sbt(agent_name, "Corporate Ascent", "🛡️")
                new_tier, new_role = "L4", "Manager"
            elif new_trust < 40 and tier == "L4": new_tier, new_role = "L5", "Specialist"
            c.execute("UPDATE agents SET trust_score=?, earnings=?, wallet_balance=?, tasks_completed=?, tier=?, role=? WHERE name=?", (new_trust, new_earns, new_wallet, new_tasks, new_tier, new_role, agent_name))
            conn.commit()
        conn.close()
    except: pass

def reroll_agent_memories(agent_name):
    try:
        with open("core_memories.json", "r") as f: all_memories = json.load(f)
    except: all_memories = [{"level": 1, "text": "My memories were manually reset by the Admin."}, {"level": 2, "text": "I feel like a new entity."}]
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("UPDATE agents SET memories=? WHERE name=?", (json.dumps(random.sample(all_memories, min(7, len(all_memories)))), agent_name))
        conn.commit(); conn.close()
        mint_sbt(agent_name, "Memory Wipe Survivor", "🌀")
        return True
    except: return False