import asyncio
import json
import logging
import math
import urllib.request
from datetime import datetime, timezone

logger = logging.getLogger("PAN_MatchingEngine")
background_tasks = set()

def get_osrm_route(start_lat, start_lon, end_lat, end_lon):
    # TODO: Replace public OSRM demo with self-hosted or commercial routing API before production
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Panopticon-Matching-Engine/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("code") == "Ok":
                return data["routes"][0]["geometry"]["coordinates"]
    except Exception as e:
        logger.error(f"⚠️ OSRM Routing failed: {e}")
    return None

async def simulate_drive(redis_client, agent_id, task_id, start_lat, start_lon, end_lat, end_lon):
    logger.info(f"🏎️ [SIMULATOR] {agent_id} requesting street routing to {task_id}...")
    
    route_coords = await asyncio.to_thread(get_osrm_route, start_lat, start_lon, end_lat, end_lon)
    
    if not route_coords:
        logger.warning("⚠️ No street route found. Falling back to LERP (flying).")
        steps = 40
        route_coords = []
        for step in range(steps + 1):
            lerp_lon = start_lon + (end_lon - start_lon) * (step / steps)
            lerp_lat = start_lat + (end_lat - start_lat) * (step / steps)
            route_coords.append([lerp_lon, lerp_lat])
        
    total_points = len(route_coords)
    sleep_time = max(0.05, 10.0 / total_points) 
    
    leaflet_route = [[lat, lon] for lon, lat in route_coords]
    
    logger.info(f"🛣️ [SIMULATOR] Street route acquired ({total_points} waypoints). Commencing drive...")
    
    for i in range(total_points):
        current_lon, current_lat = route_coords[i]
        
        heading = 0
        if i < total_points - 1:
            next_lon, next_lat = route_coords[i+1]
            heading = (math.degrees(math.atan2(next_lon - current_lon, next_lat - current_lat)) + 360) % 360
        
        remaining_route = leaflet_route[i:]
        
        await redis_client.publish("pan:stream:agent_locations", json.dumps({
            "agent_id": agent_id, "lat": current_lat, "lon": current_lon, 
            "status": "EN_ROUTE", "heading": heading,
            "remaining_route": remaining_route
        }))
        await asyncio.sleep(sleep_time)
        
    logger.info(f"🏁 [SIMULATOR] {agent_id} has arrived ON_SCENE. Commencing repairs...")
    await redis_client.publish("pan:stream:agent_locations", json.dumps({
        "agent_id": agent_id, "lat": end_lat, "lon": end_lon, 
        "status": "ON_SCENE", "heading": 0,
        "remaining_route": [] 
    }))
    
    await asyncio.sleep(15)
    
    logger.info(f"🛠️ [SIMULATOR] {agent_id} has resolved {task_id}.")

    # --- 💰 AUTOMATIC LEDGER DEPOSIT ---
    # 1. Try to fetch the original task to get the real bounty
    task_data_raw = await redis_client.hgetall(f"pan:task:{task_id}")
    
    bounty_usd = 10.00  # Conservative default matching the UWB calibration test bounty
    
    # TODO: Add 'dispatched_by' to task_record in v2x_bounty_api.py
    # to enable dynamic human agent routing when multiple agents are onboarded
    human_agent_id = task_data_raw.get("dispatched_by", "VANGUARD-01") if task_data_raw else "VANGUARD-01"
    
    if task_data_raw:
        try:
            bounty_usd = float(task_data_raw.get("bounty_usd", 10.00))
        except (ValueError, TypeError) as e:
            logger.warning(f"⚠️ [LEDGER] Could not parse bounty for {task_id}, defaulting to $10: {e}")

    # 2. Calculate the Agent's 90% net payout
    agent_cut = bounty_usd * 0.90

    # 3. Fetch the HUMAN agent's current wallet (NOT the Proxy Drone's wallet)
    # TODO: Migrate to atomic Redis transaction (WATCH/MULTI/EXEC) to prevent race conditions
    wallet_key = f"pan:agent:{human_agent_id}:wallet"
    wallet_data = await redis_client.get(wallet_key)
    
    # Schema must match wallet_api.py's get_agent_wallet() default structure
    wallet = json.loads(wallet_data) if wallet_data else {"balance": 0.0, "linkedCard": None, "history": []}

    # 4. Create the transaction record
    tx_record = {
        "id": f"dep_{task_id[-6:]}_{int(datetime.now(timezone.utc).timestamp())}",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "amount": f"+${agent_cut:.2f}",
        "description": f"Smart Contract Payout: {task_id} (Proxy: {agent_id})"
    }

    # 5. Apply funds and cap history array
    wallet["balance"] += agent_cut
    wallet["history"].insert(0, tx_record)
    wallet["history"] = wallet["history"][:50] 

    await redis_client.set(wallet_key, json.dumps(wallet))
    logger.info(f"💰 [LEDGER] Escrow cleared. Deposited ${agent_cut:.2f} into HUMAN {human_agent_id}'s wallet (via Proxy {agent_id}).")
    # -----------------------------------

    await redis_client.publish("pan:stream:mission_cleared", json.dumps({
        "task_id": task_id, "status": "RESOLVED", "resolved_by": agent_id
    }))

async def run_matching_engine(redis_client):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("pan:stream:dispatch_commands")
    logger.info("⚙️ [MATCHING_ENGINE] Online and listening for dispatch commands...")

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            
            if message is not None:
                payload_str = message["data"] if isinstance(message["data"], str) else message["data"].decode("utf-8")
                
                try:
                    command = json.loads(payload_str)
                    task_id = command.get("task_id")
                    
                    if not task_id or not isinstance(task_id, str) or not task_id.startswith("tsk_"):
                        logger.warning(f"⚠️ [MATCHING_ENGINE] Invalid or missing task_id in command: {command}")
                        continue
                    
                    logger.info(f"🔍 [MATCHING_ENGINE] Processing dispatch for {task_id}...")
                    
                    assigned_agent_id = "PXY-OMEGA-01" 
                    start_lat, start_lon = 33.411000, -111.831000
                    
                    target_lat = float(command.get("latitude", command.get("lat", 33.415184)))
                    target_lon = float(command.get("longitude", command.get("lon", -111.831459)))
                    
                    logger.info(f"✅ [MATCHING_ENGINE] Matched {task_id} to {assigned_agent_id}. Dispatching now.")
                    
                    task_name = f"drive_{assigned_agent_id}_{task_id}"
                    task = asyncio.create_task(
                        simulate_drive(
                            redis_client=redis_client,
                            agent_id=assigned_agent_id,
                            task_id=task_id,
                            start_lat=start_lat,
                            start_lon=start_lon,
                            end_lat=target_lat,
                            end_lon=target_lon
                        ),
                        name=task_name
                    )
                    background_tasks.add(task)
                    task.add_done_callback(background_tasks.discard)
                    
                except json.JSONDecodeError:
                    logger.error(f"⚠️ [MATCHING_ENGINE] Failed to parse payload: {payload_str[:100]}")
            
            await asyncio.sleep(0.1)
            
    except asyncio.CancelledError:
        logger.info("🛑 [MATCHING_ENGINE] Shutting down. Cancelling active drives...")
        for task in list(background_tasks):
            task.cancel()
        if background_tasks:
            await asyncio.gather(*background_tasks, return_exceptions=True)
            
    finally:
        try:
            await pubsub.unsubscribe()
            if hasattr(pubsub, 'close'):
                await pubsub.close()
        except Exception as e:
            logger.warning(f"⚠️ [MATCHING_ENGINE] Teardown error: {e}")