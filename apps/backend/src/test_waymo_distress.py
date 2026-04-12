import requests
import json
import time
import redis

def fire_distress_signal():
    print("🚨 TRANSMITTING V2X DISTRESS SIGNAL TO PANOPTICON GATEWAY...")
    
    # 1. Connect to Redis and find the agent's EXACT live GPS coordinates
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        agent_data = r.hgetall("pan:agent:VNG-50-PILOT")
        
        lat = float(agent_data.get("lat", 33.4150))
        lon = float(agent_data.get("lon", -111.8310))
        print(f"📍 Agent located at Lat: {lat}, Lon: {lon}. Spawning AV at this exact location...")
    except Exception as e:
        print("⚠️ Could not reach Redis for live tracking. Falling back to default coordinates.")
        lat, lon = 33.4150, -111.8310

    # 2. Fire a Tier 1 distress signal with a dynamic VIN to bypass deduplication
    url = "http://127.0.0.1:5001/api/v1/v2x/distress"
    headers = {
        "Authorization": "Bearer sk_test_mock_waymo_token_123",
        "Content-Type": "application/json",
        "X-Fleet-Id": "DEV-FLEET-01"
    }
    
    dynamic_vin = f"WAYMO-AZ-{int(time.time()) % 10000}"
    
    payload = {
        "vin": dynamic_vin,
        "fault_code": "door_securing", # 🟢 Tier 1 Task: No special loadout required
        "latitude": lat,
        "longitude": lon,
        "bounty_usd": 25.00,
        "timestamp": int(time.time())
    }

    print(f"Targeting: {url}")
    print(f"Asset (VIN): {payload['vin']} | Fault: {payload['fault_code']}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"\nResponse HTTP Status: {response.status_code}")
        
        try:
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Body: {response.text}")
            
        if response.status_code in [200, 201]:
            print("\n✅ SUCCESS: Distress signal ingested! Check your Android map.")
        else:
            print("\n❌ FAILED: Backend rejected the signal.")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR: Could not reach the backend.")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")

if __name__ == "__main__":
    fire_distress_signal()