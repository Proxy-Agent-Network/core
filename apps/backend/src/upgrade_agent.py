import redis
import time
import sys

# This is the exact ID we hardcoded in PanBootSequence.kt
AGENT_ID = "VNG-50-PILOT" 

def grant_god_mode():
    # Connect directly to the local Redis instance
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    now = int(time.time())
    
    # 1. Inject the profile with ALL required matching fields
    r.hset(f"pan:agent:{AGENT_ID}", mapping={
        "callsign": "PILOT-ALPHA",
        "status": "ONLINE",
        "tier": 3,
        "clearance": 3,
        "vehicle_class": "TACTICAL",
        "lat": 33.4150,
        "lon": -111.8310,
        "radius_miles": 500,
        "last_active": now
    })
    
    # 2. Add to the Geospatial Index (Longitude first for Redis GEOADD)
    r.geoadd("pan:agent_locations", [-111.8310, 33.4150, AGENT_ID])
    
    # 3. Seed the Loadout required for Tier 3 Scene Securement
    r.hset(f"pan:agent:{AGENT_ID}:loadout", mapping={
        "gear_vest_01": 1.0,
        "gear_flare_01": 1.0,
        "scene_securement": 1.0
    })
    
    # 4. Set 24-hour TTLs to keep the dev environment clean
    r.expire(f"pan:agent:{AGENT_ID}", 86400)
    r.expire(f"pan:agent:{AGENT_ID}:loadout", 86400)
    
    print(f"✅ SUCCESS: {AGENT_ID} granted Tier 3 God Mode!")
    print("   -> Profile, Geo-Index, and Loadout successfully seeded.")

def revoke_god_mode():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.delete(f"pan:agent:{AGENT_ID}")
    r.delete(f"pan:agent:{AGENT_ID}:loadout")
    r.zrem("pan:agent_locations", AGENT_ID)
    print(f"🗑️ CLEANUP: {AGENT_ID} state wiped from Redis.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--revoke":
        revoke_god_mode()
    else:
        grant_god_mode()