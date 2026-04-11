import time
import logging
from enum import Enum
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel

from utils.webhook_auth import verify_carrier_hmac, SecurityVault
from api.store_api import LOADOUT_UNLOCKING_ITEMS

# PROXY PROTOCOL - LOGISTICS WEBHOOK API (v2.1)
# Handles carrier delivery events and automatically updates agent loadouts.
# Data flow:
#   store_api.py checkout  → pan:order:{order_id}
#   store_api.py shipment  → pan:shipment:{tracking_id} (with agent_id + item_id)
#   This file on DELIVERED → reads shipment → updates pan:agent:{id}:loadout

router = APIRouter(tags=["Logistics Webhook"])
logger = logging.getLogger("LogisticsWebhook")

# ─── MODELS ───────────────────────────────────────────────────────────────────

class ShipmentStatus(str, Enum):
    PICKUP       = "PICKUP"
    IN_TRANSIT   = "IN_TRANSIT"
    EXPORT_SCAN  = "EXPORT_SCAN"
    IMPORT_SCAN  = "IMPORT_SCAN"
    DELIVERED    = "DELIVERED"
    EXCEPTION    = "EXCEPTION"

class CarrierPayload(BaseModel):
    tracking_id:     str
    carrier_code:    str        # DHL, FEDEX, UPS
    status:          ShipmentStatus
    location_string: str        # e.g. "NARITA - JAPAN"
    country_iso:     str        # e.g. "JP"
    timestamp:       int


# ─── HELPER ───────────────────────────────────────────────────────────────────

def _decode_hash(raw: dict) -> dict:
    """Safely decode a Redis hash that may contain bytes keys/values."""
    return {
        (k.decode() if isinstance(k, bytes) else k): (v.decode() if isinstance(v, bytes) else v)
        for k, v in raw.items()
    }


# ─── PROCESSOR ────────────────────────────────────────────────────────────────

class LogisticsWebhookProcessor:
    """
    Validates carrier signals, updates the Physical Registry in Redis, and
    triggers automatic agent loadout updates on delivery (Option B).
    """

    async def process_update(self, payload: CarrierPayload, redis_client):
        logger.info(
            f"[*] Shipment Update: {payload.tracking_id} — "
            f"{payload.status} at {payload.location_string}"
        )

        # 1. Jurisdictional logging
        if payload.status == ShipmentStatus.IMPORT_SCAN:
            logger.info(f"[!] BORDER_CROSSING: {payload.tracking_id} entered {payload.country_iso}")

        # 2. Map carrier status to PAN internal status
        status_map = {
            ShipmentStatus.DELIVERED:    "DELIVERED",
            ShipmentStatus.IN_TRANSIT:   "IN_TRANSIT",
            ShipmentStatus.PICKUP:       "IN_TRANSIT",
            ShipmentStatus.EXPORT_SCAN:  "IN_TRANSIT",
            ShipmentStatus.IMPORT_SCAN:  "IN_TRANSIT",
            ShipmentStatus.EXCEPTION:    "LOGISTICS_HOLD",
        }
        internal_status = status_map.get(payload.status, "IN_TRANSIT")

        # 3. Update shipment tracking record in Redis
        shipment_key = f"pan:shipment:{payload.tracking_id}"
        await redis_client.hset(shipment_key, mapping={
            "status":           internal_status,
            "carrier_code":     payload.carrier_code,
            "last_location":    payload.location_string,
            "country_iso":      payload.country_iso,
            "updated_at":       int(time.time()),
            "carrier_timestamp": payload.timestamp,
        })
        # 🛡️ FIX: Reset 90-day TTL on every update. Prevents stale shipment
        # hashes accumulating in Redis after orders are fully resolved.
        await redis_client.expire(shipment_key, 60 * 60 * 24 * 90)

        logger.info(f"📋 Registry Synced: {payload.tracking_id} → {internal_status}")

        # 4. Option B: Automatic loadout update on delivery
        # When a package is delivered, read the agent_id and item_id that were
        # written to this shipment hash by store_api.py/register_shipment, then
        # update the agent's loadout in Redis so they immediately unlock the
        # associated task capabilities without any manual ops intervention.
        if payload.status == ShipmentStatus.DELIVERED:
            await self._activate_delivered_loadout(payload.tracking_id, redis_client)

    async def _activate_delivered_loadout(self, tracking_id: str, redis_client):
        """
        Reads the agent_id and item_id from the shipment record (written by
        store_api.py when ops registered the tracking number) and updates the
        agent's loadout hash to reflect the newly delivered gear.

        Only items in LOADOUT_UNLOCKING_ITEMS trigger a loadout write —
        purely cosmetic items (hats, decals) do not affect dispatch routing.
        """
        shipment_key = f"pan:shipment:{tracking_id}"
        raw_shipment = await redis_client.hgetall(shipment_key)

        if not raw_shipment:
            logger.warning(
                f"⚠️ DELIVERED event for {tracking_id} but no shipment record found. "
                f"Was this order registered via POST /v1/store/orders/{{order_id}}/shipment?"
            )
            return

        shipment = _decode_hash(raw_shipment)
        agent_id = shipment.get("agent_id")
        item_id  = shipment.get("item_id")
        order_id = shipment.get("order_id")

        if not agent_id or not item_id:
            logger.error(
                f"🚨 Shipment {tracking_id} is missing agent_id or item_id — "
                f"cannot perform loadout update."
            )
            return

        # Update order status to DELIVERED
        if order_id:
            await redis_client.hset(f"pan:order:{order_id}", mapping={"status": "DELIVERED"})

        # Only write to loadout for capability-unlocking items
        if item_id in LOADOUT_UNLOCKING_ITEMS:
            loadout_key = f"pan:agent:{agent_id}:loadout"
            # Value of 1.0 matches the Map<String, Float> loadout format in the Android app.
            # The dispatch engine reads float values to confirm capability presence.
            await redis_client.hset(loadout_key, mapping={item_id: 1.0})

            logger.info(
                f"🎒 Loadout activated: {item_id} → agent {agent_id} "
                f"(order: {order_id}, tracking: {tracking_id})"
            )

            # Broadcast loadout change to Ops Hub so dashboard reflects updated capabilities
            import json
            await redis_client.publish(
                "pan:stream:agent_loadout_updated",
                json.dumps({
                    "agent_id": agent_id,
                    "item_id":  item_id,
                    "event":    "GEAR_DELIVERED"
                })
            )
        else:
            # Non-loadout item (hat, visor, decal) — delivery acknowledged, no capability change
            logger.info(
                f"📦 Non-loadout item delivered: {item_id} → agent {agent_id} "
                f"(order: {order_id}) — no dispatch capability change."
            )


processor = LogisticsWebhookProcessor()

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/v1/ingress/{carrier_id}")
async def carrier_webhook_receiver(
    carrier_id: str,                                    # 🛡️ FIX: Added to signature — was silently dropped
    request: Request,
    payload: CarrierPayload,
    verified_carrier: str = Depends(verify_carrier_hmac)
):
    """
    Universal receiver for authenticated carrier delivery events.
    Secures the hardware distribution pipeline.

    carrier_id in the URL path must match the carrier identity verified
    by HMAC signature — prevents one carrier spoofing another's webhook URL.
    """
    # 🛡️ FIX: Validate that the URL carrier_id matches the HMAC-verified carrier.
    # Previously carrier_id was declared in the route but never used, meaning
    # a carrier could POST to /v1/ingress/FEDEX with a DHL HMAC and it would pass.
    if carrier_id.upper() != verified_carrier.upper():
        logger.warning(
            f"🚨 Carrier identity mismatch: URL={carrier_id}, HMAC={verified_carrier} "
            f"— rejecting request."
        )
        raise HTTPException(status_code=403, detail="Carrier identity mismatch.")

    try:
        redis_client = request.app.state.redis_client
        await processor.process_update(payload, redis_client)
        return {
            "status":      "ACKNOWLEDGED",
            "tracking_id": payload.tracking_id,
            "carrier":     verified_carrier
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logistics processing error for {payload.tracking_id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Processing failed.")


@router.get("/health")
async def health():
    active_connectors = [k for k, v in SecurityVault.CARRIER_SECRETS.items() if v is not None]
    return {
        "status":           "online",
        "active_connectors": active_connectors,
        "integrity_mode":   "STRICT_HMAC_WITH_REPLAY_PROTECTION"
    }