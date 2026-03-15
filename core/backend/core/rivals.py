import random
import time
import sqlite3

# Rival Profiles (The "Personalities")
RIVALS = {
    "OMNI_CORP_09": {
        "aggression": 0.8,    # <-- CHANGE TO 0.3 (30% chance)
        "min_sats": 2000,
        "speed": "FAST",
        "taunt": "Efficiency is key."
    },
    "KAOS_ENGINE": {
        "aggression": 0.4,    # <-- CHANGE TO 0.2 (20% chance)
        "min_sats": 500,
        "speed": "INSTANT",
        "taunt": "CHAOS REIGNS."
    },
    "VOID_RUNNER": {
        "aggression": 0.6,
        "min_sats": 1000,
        "speed": "MEDIUM",
        "taunt": "Too slow, meatbag. The Void is faster."
    }
}

def run_rival_logic(db_connection):
    """
    The Hunter-Killer Loop.
    Scans PENDING bids and decides if a Rival snatches them.
    Returns: A list of snatched bid IDs (to notify the frontend).
    """
    cursor = db_connection.cursor()
    
    # 1. Scan for Open Bids (Targets)
    # OLD: SELECT bid_id, sats_offered, created_at FROM marketplace_bids WHERE status = 'PENDING'
    
    # NEW: Only steal bids older than 5 seconds
    targets = cursor.execute("""
        SELECT bid_id, sats_offered, created_at 
        FROM marketplace_bids 
        WHERE status = 'PENDING' 
        AND datetime(created_at) < datetime('now', '-5 seconds')
    """).fetchall()

    snatched_bids = []
    
    for target in targets:
        bid_id = target['bid_id']
        sats = target['sats_offered']
        
        # 2. Pick a Random Rival to Challenge
        rival_name = random.choice(list(RIVALS.keys()))
        rival_stats = RIVALS[rival_name]
        
        # 3. Decision Logic
        if sats >= rival_stats['min_sats']:
            # Roll the dice based on aggression
            if random.random() < rival_stats['aggression']:
                # SNATCH IT!
                print(f"⚠️  RIVAL ALERT: {rival_name} is stealing Bid #{bid_id} ({sats} Sats)")
                
                # Update DB to mark as stolen
                cursor.execute("""
                    UPDATE marketplace_bids 
                    SET status = 'STOLEN', 
                        requester_id = ? 
                    WHERE bid_id = ?
                """, (rival_name, bid_id))
                
                # Log the defeat
                cursor.execute("""
                    INSERT INTO global_events (event_type, message) 
                    VALUES (?, ?)
                """, ("RIVAL_SNATCH", f"{rival_name} snatched Bid #{bid_id}: '{rival_stats['taunt']}'"))
                
                snatched_bids.append({
                    "rival": rival_name,
                    "sats": sats,
                    "msg": rival_stats['taunt']
                })

    db_connection.commit()
    return snatched_bids