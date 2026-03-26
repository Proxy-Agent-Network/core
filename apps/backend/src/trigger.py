import asyncio
import json
import redis.asyncio as redis

async def main():
    print("📡 Connecting to PAN Ledger...")
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    task_id = "tsk_alpha_777"
    bounty = "75.00"
    
    # 1. Save the real bounty to the database so the ledger can find it
    await r.hset(f"pan:task:{task_id}", mapping={"bounty_usd": bounty})
    
    # 2. Fire the network command to wake up the Matching Engine
    command = {"task_id": task_id, "lat": 33.415, "lon": -111.831}
    await r.publish("pan:stream:dispatch_commands", json.dumps(command))
    
    print(f"🚀 Real dispatch sent to the backend for ${bounty}!")

asyncio.run(main())