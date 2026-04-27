import os
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request

from utils.db import get_db_dep, DBWrapper

router = APIRouter()

@router.post("/seed-dvr")
def seed_dvr(request: Request, db: DBWrapper = Depends(get_db_dep)):
    """Generates realistic street-grid data using Manhattan Distance routing."""
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(status_code=403, detail="This debugging endpoint is permanently disabled in production environments.")
        
    # Security: Ensure only authorized admins/ops can trigger this (using the ops hub token)
    auth_header = request.headers.get("Authorization")
    expected_token = os.getenv("OPS_HUB_TOKEN", "dev-token-777")
    if not auth_header or auth_header != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    agents = [f"VAN-DEMO-{str(i).zfill(3)}" for i in range(1, 16)]
    base_lat, base_lon = 33.415, -111.831 # Mesa, AZ
    
    now = datetime.utcnow()
    start_time = now - timedelta(minutes=60)
    
    agent_states = {}
    for a in agents:
        start_lat = base_lat + random.uniform(-0.06, 0.06)
        start_lon = base_lon + random.uniform(-0.06, 0.06)
        agent_states[a] = {
            "lat": start_lat, "lon": start_lon,
            "state": "ONLINE", "mission_id": None,
            "timer": random.randint(5, 15),
            "target_lat": start_lat + random.uniform(-0.02, 0.02),
            "target_lon": start_lon + random.uniform(-0.02, 0.02)
        }
    
    count = 0
    for step in range(360):
        step_time = start_time + timedelta(seconds=step * 10)
        for a in agents:
            st = agent_states[a]
            
            if st["timer"] <= 0:
                if st["state"] == "ONLINE":
                    st["state"] = "BUSY_ON_WAY"
                    st["mission_id"] = f"FLT-{random.randint(1000, 9999)}"
                    st["target_lat"] = st["lat"] + random.uniform(-0.04, 0.04)
                    st["target_lon"] = st["lon"] + random.uniform(-0.04, 0.04)
                    st["timer"] = 9999 
                elif st["state"] == "BUSY_ON_WAY":
                    st["state"] = "BUSY_ON_SITE"
                    st["timer"] = random.randint(10, 20) 
                else:
                    st["state"] = "ONLINE"
                    st["mission_id"] = None
                    st["target_lat"] = st["lat"] + random.uniform(-0.02, 0.02)
                    st["target_lon"] = st["lon"] + random.uniform(-0.02, 0.02)
                    st["timer"] = 9999
            else:
                st["timer"] -= 1

            step_size = 0.001 
            if st["state"] != "BUSY_ON_SITE":
                lat_dist = st["target_lat"] - st["lat"]
                lon_dist = st["target_lon"] - st["lon"]
                
                if abs(lon_dist) > step_size:
                    st["lon"] += step_size if lon_dist > 0 else -step_size
                elif abs(lat_dist) > step_size:
                    st["lat"] += step_size if lat_dist > 0 else -step_size
                else:
                    st["lat"] = st["target_lat"]
                    st["lon"] = st["target_lon"]
                    if st["state"] == "BUSY_ON_WAY":
                        st["timer"] = 0 
                    elif st["state"] == "ONLINE":
                        st["target_lat"] = st["lat"] + random.uniform(-0.02, 0.02)
                        st["target_lon"] = st["lon"] + random.uniform(-0.02, 0.02)
            
            db.execute('''
                INSERT INTO agent_telemetry_history 
                (agent_id, latitude, longitude, status, current_mission_id, event_type, recorded_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (a, st["lat"], st["lon"], st["state"], st["mission_id"], "PING", step_time))
            count += 1
            
    db.commit()
    return {"status": "success", "message": f"Injected {count} Manhattan street-grid GPS pings!"}