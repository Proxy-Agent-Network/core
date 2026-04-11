import uuid
import time
import json
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from redis.exceptions import WatchError
from utils.auth import verify_agent_signature
from datetime import datetime, timezone

logger = logging.getLogger("PAN_Store_API")
router = APIRouter()

# ─── ITEM CATALOG ─────────────────────────────────────────────────────────────
ITEM_CATALOG = {
    "gear_vest_01":  {"name": "Vanguard Class-2 Hi-Vis Vest",     "price_usd": 45.00},
    "gear_flare_01": {"name": "LED Roadside Flare Kit",            "price_usd": 25.00},
    "gear_hat_01":   {"name": "Standard Field Hat",                "price_usd": 18.00},
    "gear_visor_01": {"name": "PAN Window Visor",                  "price_usd": 22.00},
    "gear_decal_01": {"name": "PAN Magnetic Vehicle Decals",       "price_usd": 15.00},
    "hw_gauntlets":  {"name": "VFG-1 Gauntlets",                   "price_usd": 60.00},
}

# 🛡️ THE FIX: Export the set required by logistics_webhook_api.py
# This defines which store items grant new tactical capabilities upon delivery.
LOADOUT_UNLOCKING_ITEMS = {
    "gear_vest_01",
    "hw_gauntlets",
    "gear_flare_01"
}

# ─── REQUEST MODELS ───────────────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    item_id: str
    quantity: int = 1
    shipping_address: str 

class ShipmentRegistrationRequest(BaseModel):
    tracking_id: str
    carrier_code: str

class WaitlistRequest(BaseModel):
    item_id: str
    email: str

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/v1/store/checkout")
async def checkout(
    payload: CheckoutRequest,
    request: Request,
    agent_identity: dict = Depends(verify_agent_signature)
):
    agent_id = agent_identity.get("agent_id")
    redis_client = request.app.state.redis_client

    item = ITEM_CATALOG.get(payload.item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item '{payload.item_id}' not found.")

    if payload.quantity < 1 or payload.quantity > 10:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 10.")

    order_id = f"ord_{uuid.uuid4().hex[:12]}"
    total_usd = round(item["price_usd"] * payload.quantity, 2)
    wallet_key = f"pan:agent:{agent_id}:wallet"

    # 🛡️ FIXED: Deduct funds safely using a watched transaction pipeline
    async with redis_client.pipeline() as pipe:
        for attempt in range(10):
            try:
                await pipe.watch(wallet_key)
                wallet_raw = await pipe.get(wallet_key)
                wallet = json.loads(wallet_raw) if wallet_raw else {"balance": 0.0, "linkedCard": None, "history": []}
                
                if wallet["balance"] < total_usd:
                    raise HTTPException(status_code=402, detail="Insufficient funds in agent wallet.")
                
                # Deduct funds
                wallet["balance"] -= total_usd
                
                # Add transaction history
                tx_record = {
                    "id": f"tx_{int(time.time())}",
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                    "amount": f"-${total_usd:.2f}",
                    "description": f"Supply Depot: {item['name']} (x{payload.quantity})"
                }
                wallet["history"].insert(0, tx_record)
                wallet["history"] = wallet["history"][:50]
                
                pipe.multi()
                pipe.set(wallet_key, json.dumps(wallet))
                
                # Create the order record alongside the deduction
                order_key = f"pan:order:{order_id}"
                pipe.hset(order_key, mapping={
                    "order_id":         order_id,
                    "agent_id":         agent_id,
                    "item_id":          payload.item_id,
                    "item_name":        item["name"],
                    "quantity":         payload.quantity,
                    "price_usd":        item["price_usd"],
                    "total_usd":        total_usd,
                    "shipping_address": payload.shipping_address,
                    "status":           "PROCESSING",
                    "created_at":       int(time.time()),
                    "tracking_id":      "",
                    "carrier_code":     "",
                })
                pipe.expire(order_key, 60 * 60 * 24 * 730)
                pipe.rpush(f"pan:agent:{agent_id}:orders", order_id)
                
                await pipe.execute()
                break
            except WatchError:
                if attempt == 9:
                    raise HTTPException(status_code=503, detail="Wallet temporarily unavailable. Please retry.")
                continue

    logger.info(f"📦 Order created & funded: {order_id} — {payload.item_id} x{payload.quantity} for agent {agent_id}")

    return {
        "status":    "success",
        "order_id":  order_id,
        "item":      item["name"],
        "total_usd": total_usd,
        "message":   "Order received. Fulfillment confirmation will be sent to your registered email."
    }

@router.post("/v1/store/orders/{order_id}/shipment")
async def register_shipment(
    order_id: str,
    payload: ShipmentRegistrationRequest,
    request: Request
):
    redis_client = request.app.state.redis_client
    order_key = f"pan:order:{order_id}"
    
    raw_order = await redis_client.hgetall(order_key)
    if not raw_order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")

    order = {
        (k.decode() if isinstance(k, bytes) else k): (v.decode() if isinstance(v, bytes) else v)
        for k, v in raw_order.items()
    }

    agent_id = order.get("agent_id")
    item_id  = order.get("item_id")

    if not agent_id or not item_id:
        logger.error(f"Order {order_id} is malformed — missing agent_id or item_id")
        raise HTTPException(status_code=500, detail="Order record is malformed.")

    shipment_key = f"pan:shipment:{payload.tracking_id}"
    await redis_client.hset(shipment_key, mapping={
        "tracking_id":  payload.tracking_id,
        "carrier_code": payload.carrier_code,
        "order_id":     order_id,
        "agent_id":     agent_id,
        "item_id":      item_id,
        "status":       "IN_TRANSIT",
        "created_at":   int(time.time()),
    })
    await redis_client.expire(shipment_key, 60 * 60 * 24 * 90)

    await redis_client.hset(order_key, mapping={
        "tracking_id":  payload.tracking_id,
        "carrier_code": payload.carrier_code,
        "status":       "SHIPPED",
    })

    logger.info(f"🚚 Shipment registered: {payload.tracking_id} ({payload.carrier_code}) → order {order_id} for agent {agent_id} (item: {item_id})")

    return {
        "status":       "success",
        "tracking_id":  payload.tracking_id,
        "order_id":     order_id,
        "agent_id":     agent_id,
        "item_id":      item_id,
    }

@router.get("/v1/store/orders")
async def get_agent_orders(
    request: Request,
    agent_identity: dict = Depends(verify_agent_signature)
):
    agent_id = agent_identity.get("agent_id")
    redis_client = request.app.state.redis_client

    order_ids = await redis_client.lrange(f"pan:agent:{agent_id}:orders", 0, -1)
    orders = []

    for raw_id in order_ids:
        order_id_str = raw_id.decode() if isinstance(raw_id, bytes) else raw_id
        raw_order = await redis_client.hgetall(f"pan:order:{order_id_str}")
        if raw_order:
            order = {
                (k.decode() if isinstance(k, bytes) else k): (v.decode() if isinstance(v, bytes) else v)
                for k, v in raw_order.items()
            }
            orders.append(order)

    return {"orders": orders}

@router.post("/v1/store/waitlist")
async def join_waitlist(
    payload: WaitlistRequest,
    request: Request,
    agent_identity: dict = Depends(verify_agent_signature)
):
    agent_id = agent_identity.get("agent_id")
    redis_client = request.app.state.redis_client

    waitlist_key = f"pan:waitlist:{payload.item_id}"
    await redis_client.hset(waitlist_key, agent_id, payload.email)

    logger.info(f"📋 Waitlist: agent {agent_id} joined queue for {payload.item_id}")

    return {
        "status":  "success",
        "message": "You've been added to the priority waitlist."
    }