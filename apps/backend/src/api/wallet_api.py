import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from redis.exceptions import WatchError

# 🛠️ THE FIX 1: Addressed circular import risk by routing through our new utils module
from utils.auth import verify_agent_signature 

logger = logging.getLogger("PAN_WalletAPI")
router = APIRouter(prefix="/v1/wallet", tags=["Agent Wallet"])

class LinkCardRequest(BaseModel):
    card_number: str

class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to withdraw in USD")

async def get_agent_wallet(redis_client, agent_id: str):
    """
    Helper for standard reads. 
    🛠️ THE FIX 2: Removed the silent write side-effect. GETs should be purely idempotent.
    """
    wallet_key = f"pan:agent:{agent_id}:wallet"
    wallet_data = await redis_client.get(wallet_key)
    
    if wallet_data:
        return json.loads(wallet_data)
        
    return {
        "balance": 0.0,
        "linkedCard": None,
        "history": []
    }

@router.get("/")
async def get_wallet_data(request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Fetches the current balance and transaction history for the Agent App."""
    redis_client = request.app.state.redis_client
    wallet = await get_agent_wallet(redis_client, agent_id)
    return wallet

@router.post("/link-card")
async def link_debit_card(payload: LinkCardRequest, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Saves the masked card number to the agent's profile using atomic transactions."""
    redis_client = request.app.state.redis_client
    wallet_key = f"pan:agent:{agent_id}:wallet"
    
    async with redis_client.pipeline() as pipe:
        # 🛠️ THE FIX 3: Replaced infinite loop with a bounded 10-attempt retry mechanism
        for attempt in range(10):
            try:
                await pipe.watch(wallet_key)
                
                # 🛠️ THE FIX 4: Added architectural comment regarding async pipeline state
                # NOTE FOR FUTURE DEVS: Immediate-execution mode is active after watch().
                # pipe.get() executes directly and returns the value. Do NOT move this inside multi()!
                wallet_data = await pipe.get(wallet_key)
                if wallet_data:
                    wallet = json.loads(wallet_data)
                else:
                    wallet = {"balance": 0.0, "linkedCard": None, "history": []}
                    
                wallet["linkedCard"] = payload.card_number
                
                pipe.multi()
                pipe.set(wallet_key, json.dumps(wallet))
                await pipe.execute()
                break
            except WatchError:
                logger.warning(f"Concurrent modification detected linking card for {agent_id}. Retry {attempt + 1}/10...")
                if attempt == 9:
                    raise HTTPException(status_code=503, detail="Wallet temporarily unavailable. Please retry.")
                continue
                
    return {"status": "success", "linkedCard": payload.card_number}

@router.post("/withdraw")
async def withdraw_funds(payload: WithdrawRequest, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Zeroes out the balance and adds a withdrawal record to the ledger atomically."""
    redis_client = request.app.state.redis_client
    wallet_key = f"pan:agent:{agent_id}:wallet"
    
    async with redis_client.pipeline() as pipe:
        # 🛠️ THE FIX 3: Bounded retry mechanism
        for attempt in range(10):
            try:
                await pipe.watch(wallet_key)
                
                # 🛠️ THE FIX 4: Educational note
                # NOTE FOR FUTURE DEVS: Immediate-execution mode active after watch(). 
                # Do not place inside pipe.multi().
                wallet_data = await pipe.get(wallet_key)
                if wallet_data:
                    wallet = json.loads(wallet_data)
                else:
                    wallet = {"balance": 0.0, "linkedCard": None, "history": []}
                
                if not wallet.get("linkedCard"):
                    await pipe.unwatch()
                    raise HTTPException(status_code=400, detail="No payout method linked. Please link a debit card first.")
                    
                if wallet["balance"] < payload.amount:
                    await pipe.unwatch()
                    raise HTTPException(status_code=400, detail="Insufficient funds")
                    
                tx_record = {
                    "id": f"wd_{int(datetime.now(timezone.utc).timestamp())}",
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                    "amount": f"-${payload.amount:.2f}",
                    "description": f"Transfer to {wallet.get('linkedCard')}"
                }
                
                wallet["balance"] -= payload.amount
                wallet["history"].insert(0, tx_record)
                wallet["history"] = wallet["history"][:50] 
                
                pipe.multi()
                pipe.set(wallet_key, json.dumps(wallet))
                await pipe.execute()
                break
            except WatchError:
                logger.warning(f"Race condition detected for wallet {agent_id} during withdrawal. Retry {attempt + 1}/10...")
                if attempt == 9:
                    raise HTTPException(status_code=503, detail="Wallet temporarily unavailable due to high traffic. Please retry.")
                continue
                
    return {"status": "success", "new_balance": wallet["balance"]}