import os
import asyncio
import redis.asyncio as redis

async def main():
    # 🛡️ PHASE 6 FIX: Hard environment guard against financial manipulation in production
    if os.environ.get("ENVIRONMENT") != "development":
        print(" [SECURITY] 🚨 CRITICAL: check_wallets.py is a dev-only script. Aborting execution!")
        return

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Give everyone a cool $100 just to be safe
    await r.hset("pan:wallet:PXY-OMEGA-01", "balance", 67.50)
    await r.hset("pan:wallet:agent_1", "balance", 67.50)
    await r.hset("pan:wallet:proxy_007", "balance", 67.50)
    await r.hset("pan:wallet:default", "balance", 67.50)

    print("💰 Seeded all possible local test wallets with $67.50!")

asyncio.run(main())