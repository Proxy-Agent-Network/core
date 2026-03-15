import requests
import json
import random
import time

def get_live_data(task_type):
    """
    Fetches real-world data based on the Task Type.
    Returns a formatted string payload.
    """
    payload = "VERIFIED_DATA_NULL"

    try:
        # 1. CRYPTO PRICE ORACLE (For High Value Tasks)
        if task_type == "DATA_ANALYSIS" or task_type == "FINANCIAL":
            # Public CoinDesk API
            response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json", timeout=2)
            data = response.json()
            price = data['bpi']['USD']['rate']
            payload = f"BTC_USD: ${price} | TS: {int(time.time())}"

        # 2. WEATHER ORACLE (For Compute Tasks)
        elif task_type == "COMPUTE_V1" or task_type == "IOT_SENSING":
            # wttr.in is a text-based weather service
            # We fetch a specific location or random one
            cities = ["London", "NewYork", "Tokyo", "Singapore"]
            target = random.choice(cities)
            response = requests.get(f"https://wttr.in/{target}?format=%C+%t", timeout=2)
            weather = response.text.strip()
            payload = f"METEO_DATA [{target.upper()}]: {weather}"
            
        # 3. NETWORK ORACLE (Generic)
        else:
            payload = f"HASH_VERIFY: 0x{random.getrandbits(128):032x}"

    except Exception as e:
        print(f"⚠️ ORACLE FAILURE: {e}")
        payload = f"ORACLE_OFFLINE_ERR_{random.randint(100,999)}"

    return payload