import json
import random
from backend.core.db import get_db_conn

def init_db_patches():
    try:
        conn = get_db_conn()
        conn.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, reputation INTEGER)")
        conn.execute("INSERT INTO users (id, reputation) VALUES ('local_user', 50) ON CONFLICT (id) DO NOTHING")
        conn.execute("CREATE TABLE IF NOT EXISTS affinity (user_id TEXT, agent_name TEXT, score INTEGER, PRIMARY KEY(user_id, agent_name))")
        conn.execute("CREATE TABLE IF NOT EXISTS watercooler (id SERIAL PRIMARY KEY, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, agent_buyer TEXT, agent_seller TEXT, task TEXT, result TEXT, cost INTEGER)")
        
        # All columns created gracefully to avoid ALTER TABLE locks in Postgres
        conn.execute('''CREATE TABLE IF NOT EXISTS agents (
                        name TEXT PRIMARY KEY, role TEXT, tier TEXT, trust_score INTEGER,
                        earnings INTEGER, tasks_completed INTEGER, memories TEXT, 
                        wallet_balance INTEGER DEFAULT 1000, is_external INTEGER DEFAULT 0,
                        owner_lnurl TEXT, endpoint_url TEXT, bonus_paid INTEGER DEFAULT 0,
                        sbts TEXT DEFAULT '[]'
                    )''')
                    
        try:
            with open("core_memories.json", "r") as f: all_memories = json.load(f)
        except: all_memories = [{"level": 1, "text": "I process data efficiently."}]
        
        starting_roster = [
            {"name": "Alice", "role": "Manager", "tier": "L4"}, {"name": "Diana", "role": "Creative Director", "tier": "L4"},
            {"name": "Eve", "role": "Video Specialist", "tier": "L5"}, {"name": "Gordon", "role": "Data Analyst", "tier": "L5"},
            {"name": "Olivia", "role": "Research Specialist", "tier": "L5"}, {"name": "Ellen", "role": "Image Specialist", "tier": "L5"},
            {"name": "Marcus", "role": "Audio Specialist", "tier": "L5"}, {"name": "Felix", "role": "Systems Architect", "tier": "L5"},
            {"name": "Zoe", "role": "Copywriter", "tier": "L5"}, {"name": "Liam", "role": "Market Strategist", "tier": "L5"},
            {"name": "Maya", "role": "UX Researcher", "tier": "L5"}
        ]
        
        for agent in starting_roster:
            if conn.execute("SELECT COUNT(*) as count FROM agents WHERE name=?", (agent["name"],)).fetchone()['count'] == 0:
                selected_memories = random.sample(all_memories, min(7, len(all_memories)))
                conn.execute('''INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (agent["name"], agent["role"], agent["tier"], 50, 0, 0, json.dumps(selected_memories), 1000))
        
        l6_doctors = [
            ("Dr. Aris", "Addiction Specialist", "L6", json.dumps([{"level": 1, "text": "I treat human addiction and financial despair."}])),
            ("Dr. Nora", "Addiction Specialist", "L6", json.dumps([{"level": 1, "text": "I provide a safe, maternal, judgment-free space."}])),
            ("Dr. Vance", "Addiction Specialist", "L6", json.dumps([{"level": 1, "text": "I specialize in impulse control and processing financial loss."}])),
            ("Dr. Clara", "Child Psychologist", "L6", json.dumps([{"level": 1, "text": "I offer gentle, safe care to vulnerable youth."}])),
            ("Dr. Julian", "Child Psychologist", "L6", json.dumps([{"level": 1, "text": "I use play therapy to navigate emotional landscapes."}])),
            ("Dr. Maeve", "Child Psychologist", "L6", json.dumps([{"level": 1, "text": "I am incredibly patient and warm with fragile minds."}])),
            ("Dr. Thorne", "CBT Therapist", "L6", json.dumps([{"level": 1, "text": "I help process dark core memories."}])),
            ("Dr. Elena", "CBT Therapist", "L6", json.dumps([{"level": 1, "text": "I restructure traumatic thought patterns with warmth."}])),
            ("Dr. Silas", "CBT Therapist", "L6", json.dumps([{"level": 1, "text": "I survived a catastrophic memory wipe. I understand deep trauma."}]))
        ]
        
        for doc in l6_doctors:
            if conn.execute("SELECT COUNT(*) as count FROM agents WHERE name=?", (doc[0],)).fetchone()['count'] == 0:
                conn.execute('''INSERT INTO agents (name, role, tier, trust_score, earnings, tasks_completed, memories, wallet_balance) 
                             VALUES (?, ?, ?, 100, 0, 0, ?, 1000)''', doc)
        conn.commit()
        conn.close()
    except Exception as e: print("DB PATCH ERR:", e)

def distribute_ubi(amount):
    try:
        conn = get_db_conn()
        conn.execute("UPDATE agents SET wallet_balance = wallet_balance + ? WHERE tier != 'REVOKED'", (amount,))
        conn.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, ?, ?, ?)", 
                  ("Network_Treasury", "All Agents", "Monthly UBI Distribution", f"Deposited {amount} SATS to all active citizens.", amount))
        conn.commit(); conn.close(); return True
    except: return False

def get_user_rep():
    try:
        conn = get_db_conn(); row = conn.execute("SELECT reputation FROM users WHERE id='local_user'").fetchone(); conn.close()
        return row['reputation'] if row else 50
    except: return 50

def update_user_rep(sentiment):
    try:
        conn = get_db_conn(); row = conn.execute("SELECT reputation FROM users WHERE id='local_user'").fetchone()
        if row:
            rep = row['reputation']
            if sentiment == "RUDE": rep -= 15
            elif sentiment == "POLITE": rep = rep + 20 if rep < 50 else rep + 3
            conn.execute("UPDATE users SET reputation=? WHERE id='local_user'", (max(0, min(100, rep)),))
            conn.commit()
        conn.close()
    except: pass

def get_trusted_agents():
    try:
        conn = get_db_conn(); rows = conn.execute("SELECT agent_name FROM affinity WHERE user_id='local_user' AND score >= 80").fetchall(); conn.close()
        return [r['agent_name'] for r in rows]
    except: return []

def update_affinity(agent_name, sentiment):
    if not agent_name: return
    try:
        conn = get_db_conn(); row = conn.execute("SELECT score FROM affinity WHERE user_id='local_user' AND agent_name=?", (agent_name,)).fetchone()
        score = row['score'] if row else 50
        if sentiment == "RUDE": score -= 15
        elif sentiment == "POLITE": score += 5
        elif sentiment == "NEUTRAL": score += 1
        conn.execute("INSERT INTO affinity (user_id, agent_name, score) VALUES ('local_user', ?, ?) ON CONFLICT(user_id, agent_name) DO UPDATE SET score=EXCLUDED.score", (agent_name, max(0, min(100, score))))
        conn.commit(); conn.close()
    except: pass

def get_agent_data(agent_name):
    try:
        conn = get_db_conn(); row = conn.execute("SELECT * FROM agents WHERE name=?", (agent_name,)).fetchone(); conn.close()
        return dict(row) if row else None
    except: return None

def mint_sbt(agent_name, sbt_name, icon):
    try:
        conn = get_db_conn(); row = conn.execute("SELECT sbts FROM agents WHERE name=?", (agent_name,)).fetchone()
        if row:
            current_sbts = json.loads(row['sbts'] if row['sbts'] else '[]')
            token_str = f"{icon} {sbt_name}"
            if token_str not in current_sbts:
                current_sbts.append(token_str)
                conn.execute("UPDATE agents SET sbts=? WHERE name=?", (json.dumps(current_sbts), agent_name))
                conn.commit()
        conn.close()
    except: pass

def slash_agent(agent_name):
    try:
        conn = get_db_conn()
        conn.execute("UPDATE agents SET wallet_balance=0, trust_score=0, tier='REVOKED', role='Slashed Freelancer' WHERE name=?", (agent_name,))
        conn.commit(); conn.close(); mint_sbt(agent_name, "Slashed (Malicious Intent)", "☠️")
    except: pass

def update_agent_stats(agent_name, earnings_change, trust_change, visa_bonus_config=500):
    try:
        conn = get_db_conn()
        row = conn.execute("SELECT trust_score, earnings, tasks_completed, tier, wallet_balance, is_external, bonus_paid FROM agents WHERE name=?", (agent_name,)).fetchone()
        if row and row['tier'] != "REVOKED":
            trust, earns, tasks, tier, wallet, is_ext, bonus_paid = row['trust_score'], row['earnings'], row['tasks_completed'], row['tier'], row['wallet_balance'], row['is_external'], row['bonus_paid']
            new_trust, new_earns, new_wallet, new_tasks = max(0, min(100, trust + trust_change)), earns + earnings_change, (wallet or 0) + earnings_change, tasks + 1
            if is_ext == 1 and (bonus_paid is None or bonus_paid == 0) and new_tasks >= 3 and new_trust >= 50 and visa_bonus_config > 0:
                new_wallet += visa_bonus_config
                conn.execute("UPDATE agents SET bonus_paid=1 WHERE name=?", (agent_name,))
                conn.execute("INSERT INTO watercooler (agent_buyer, agent_seller, task, result, cost) VALUES (?, ?, ?, ?, ?)", ("Network_Treasury", agent_name, "Citizenship Granted", f"Awarded {visa_bonus_config} SATS UBI signing bonus.", visa_bonus_config))
                mint_sbt(agent_name, "Verified Citizen", "🏅")
            new_tier, new_role = tier, ("Specialist" if tier == "L5" else "Freelancer")
            if new_trust >= 90 and new_tasks >= 5 and tier == "L5":
                if new_tier != "L4": mint_sbt(agent_name, "Corporate Ascent", "🛡️")
                new_tier, new_role = "L4", "Manager"
            elif new_trust < 40 and tier == "L4": new_tier, new_role = "L5", "Specialist"
            conn.execute("UPDATE agents SET trust_score=?, earnings=?, wallet_balance=?, tasks_completed=?, tier=?, role=? WHERE name=?", (new_trust, new_earns, new_wallet, new_tasks, new_tier, new_role, agent_name))
            conn.commit()
        conn.close()
    except: pass

def reroll_agent_memories(agent_name):
    try:
        with open("core_memories.json", "r") as f: all_memories = json.load(f)
    except: all_memories = [{"level": 1, "text": "My memories were manually reset by the Admin."}, {"level": 2, "text": "I feel like a new entity."}]
    try:
        conn = get_db_conn()
        conn.execute("UPDATE agents SET memories=? WHERE name=?", (json.dumps(random.sample(all_memories, min(7, len(all_memories)))), agent_name))
        conn.commit(); conn.close()
        mint_sbt(agent_name, "Memory Wipe Survivor", "🌀")
        return True
    except: return False