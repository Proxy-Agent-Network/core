import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field

# 🛠️ THE FIX 2: Import the established authentication dependency
from api.v2x_bounty_api import verify_agent_signature 

logger = logging.getLogger("PAN_WalletAPI")
router = APIRouter(prefix="/v1/wallet", tags=["Agent Wallet"])

class LinkCardRequest(BaseModel):
    card_number: str

class WithdrawRequest(BaseModel):
    # 🛠️ THE FIX 4: Prevent negative/zero withdrawals
    amount: float = Field(..., gt=0, description="Amount to withdraw in USD")

async def get_agent_wallet(redis_client, agent_id: str):
    wallet_key = f"pan:agent:{agent_id}:wallet"
    wallet_data = await redis_client.get(wallet_key)
    
    if wallet_data:
        return json.loads(wallet_data)
        
    default_wallet = {
        "balance": 0.0,
        "linkedCard": None,
        "history": []
    }
    await redis_client.set(wallet_key, json.dumps(default_wallet))
    return default_wallet

@router.get("/")
# 🛠️ THE FIX 2: Require valid signature and extract real agent_id
async def get_wallet_data(request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Fetches the current balance and transaction history for the Agent App."""
    redis_client = request.app.state.redis_client
    wallet = await get_agent_wallet(redis_client, agent_id)
    return wallet

@router.post("/link-card")
async def link_debit_card(payload: LinkCardRequest, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Saves the masked card number to the agent's profile."""
    redis_client = request.app.state.redis_client
    
    # TODO: Migrate to atomic Redis transaction (WATCH/MULTI/EXEC) to prevent race conditions
    wallet = await get_agent_wallet(redis_client, agent_id)
    wallet["linkedCard"] = payload.card_number
    
    await redis_client.set(f"pan:agent:{agent_id}:wallet", json.dumps(wallet))
    return {"status": "success", "linkedCard": payload.card_number}

@router.post("/withdraw")
async def withdraw_funds(payload: WithdrawRequest, request: Request, agent_id: str = Depends(verify_agent_signature)):
    """Zeroes out the balance and adds a withdrawal record to the ledger."""
    redis_client = request.app.state.redis_client
    
    # 🛠️ THE FIX 1: Documented the atomic transaction requirement
    # TODO: Migrate to atomic Redis transaction (WATCH/MULTI/EXEC) to prevent race conditions
    wallet = await get_agent_wallet(redis_client, agent_id)
    
    # 🛠️ THE FIX 3: Guard against withdrawing without a linked destination
    if not wallet.get("linkedCard"):
        raise HTTPException(status_code=400, detail="No payout method linked. Please link a debit card first.")
        
    if wallet["balance"] < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
        
    # 🛠️ MINOR FIX: Standardized UTC timestamps
    tx_record = {
        "id": f"wd_{int(datetime.now(timezone.utc).timestamp())}",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "amount": f"-${payload.amount:.2f}",
        "description": f"Transfer to {wallet.get('linkedCard')}"
    }
    
    # Update balance and history
    wallet["balance"] -= payload.amount
    wallet["history"].insert(0, tx_record)
    
    # 🛠️ THE FIX 5: Cap history array to prevent unbounded memory growth in the JSON blob
    wallet["history"] = wallet["history"][:50] 
    
    await redis_client.set(f"pan:agent:{agent_id}:wallet", json.dumps(wallet))
    return {"status": "success", "new_balance": wallet["balance"]}