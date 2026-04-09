import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from redis.exceptions import WatchError

from utils.auth import verify_agent_signature 

logger = logging.getLogger("PAN_WalletAPI")
router = APIRouter(prefix="/v1/wallet", tags=["Agent Wallet"])

class LinkCardRequest(BaseModel):
    card_number: str

class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to withdraw in USD")

class WaitlistPayload(BaseModel):
    item_id: str
    email: str

async def get_agent_wallet(redis_client, agent_id: str):
    """
    Helper for standard reads. 
    Fetches the fiat balance and piggybacks the Vanguard Trust Score data.
    """
    wallet_key = f"pan:agent:{agent_id}:wallet"
    
    missions_key = f"pan:agent:{agent_id}:missions_completed"
    
    # 🟢 FINDING 2 FIXED: Fetch seller_score (how fleets evaluate the agent)
    rep_score_key = f"pan:entity:{agent_id}:rep:seller_score"
    
    # Execute as a pipeline for speed
    async with redis_client.pipeline() as pipe:
        pipe.get(wallet_key)
        pipe.get(missions_key)
        pipe.get(rep_score_key)
        results = await pipe.execute()
        
    wallet_data, raw_missions, raw_score = results

    # Parse Vanguard Dossier safely
    missions_completed = int(raw_missions) if raw_missions else 0
    vanguard_trust_score = float(raw_score) if raw_score else 100.0
    
    if wallet_data:
        wallet = json.loads(wallet_data)
        wallet["missions_completed"] = missions_completed
        wallet["vanguard_trust_score"] = vanguard_trust_score
        return wallet
        
    return {
        "balance": 0.0,
        "linkedCard": None,
        "history": [],
        "missions_completed": missions_completed,
        "vanguard_trust_score": vanguard_trust_score
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
        for attempt in range(10):
            try:
                await pipe.watch(wallet_key)
                
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
        for attempt in range(10):
            try:
                await pipe.watch(wallet_key)
                
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

@router.post("/waitlist")
async def join_gear_waitlist(payload: WaitlistPayload, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """
    Records agent interest in a specific piece of Q3 pre-production hardware.
    Data is utilized by PAN Supply Chain to prioritize manufacturing runs.
    """
    redis_client = request.app.state.redis_client
    waitlist_key = f"pan:agent:{agent_id}:gear_interest:{payload.item_id}"
    
    # Store the email value with no TTL so it survives until fulfillment operations pulls the queue
    await redis_client.set(waitlist_key, payload.email)
    
    logger.info(f"📦 [SUPPLY CHAIN] Agent {agent_id} joined waitlist for {payload.item_id}")
    return {"status": "success"}