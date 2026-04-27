"""
Partner dispatch endpoint for B2B fleet integrations.

Migrated from Flask app.py /api/v1/dispatch/request route (Stage 1d-3-d).

This is the legacy webhook path used by non-V2X fleet partners to inject
distress signals into the PAN dispatch queue. The preferred path for
Waymo/Zoox-class integrations is /v2x/distress (Ed25519 signatures via
verify_v2x_signature in api/v2x_bounty_api.py). This endpoint uses a
single shared bearer token (PARTNER_API_KEY) and is intended for partners
not yet integrated with the V2X cryptographic webhook protocol.

Authentication: Bearer token in the Authorization header, compared to
the PARTNER_API_KEY environment variable using constant-time comparison.
Fail-closed: if PARTNER_API_KEY is unset, every request returns 401.

Behavioral note vs the legacy Flask handler: the FastAPI version now
publishes the synthesized mission record to pan:stream:distress_alerts
so the Ops Hub command-center map lights up when a partner posts a
dispatch. The legacy Flask handler built this payload (the local
`map_payload` dict) but never published it, leaving the map blind to
partner-originated dispatches. Wired during this migration because the
downstream subscriber (api/telemetry_socket.py) was already in place.

Payload validation note: this endpoint uses manual dict validation
rather than a Pydantic model. The legacy Flask contract returns HTTP 400
with a specific error message format for missing fields and only checks
field presence (not types). Pydantic's default 422 with structured error
output would be a partner contract change. When all current partners
migrate to the V2X path, switch this to a Pydantic model and pick up the
auto-generated OpenAPI schema for free.

Multi-tenant note: the single-tenant bearer scheme is documented in
TODO.md as a future migration target. When fleet partners exceed two,
either namespace the env var (PARTNER_API_KEY_WAYMO, PARTNER_API_KEY_ZOOX)
or migrate the partner to the V2X Ed25519 path. The verify_partner_api_key
return value is the seam for that future rewrite.
"""

import json
import logging
import os
import random
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

logger = logging.getLogger("PAN_Dispatch")
router = APIRouter()


# ---------------------------------------------------------------------------
# Tiering constants
# ---------------------------------------------------------------------------
# Mirrors the inline tier tables from the legacy Flask handler. Centralized
# here so adding a new fault code has a single edit point. Tier 1 is the
# default for any unrecognized error_code.

TIER_2_FAULTS = {"spill_remediation", "tire_pressure"}
TIER_3_FAULTS = {"manual_override", "scene_securement"}

TIER_BOUNTY_USD = {
    1: 15.00,
    2: 25.00,
    3: 85.00,
}

MAX_BID_OFFSET_USD = 20.00

REQUIRED_FIELDS = ("asset_id", "latitude", "longitude", "error_code")


def classify_fault(error_code: str) -> tuple[int, float]:
    """Returns (tier, base_bounty_usd) for the supplied fault code."""
    if error_code in TIER_3_FAULTS:
        return 3, TIER_BOUNTY_USD[3]
    if error_code in TIER_2_FAULTS:
        return 2, TIER_BOUNTY_USD[2]
    return 1, TIER_BOUNTY_USD[1]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def verify_partner_api_key(authorization: str = Header(default=None)) -> str:
    """FastAPI dependency that authenticates partner dispatch requests.

    Validates the Authorization header against PARTNER_API_KEY env var via
    constant-time comparison. Fail-closed: returns 401 if either the env
    var is missing or the supplied bearer does not match.

    Returns a partner identifier string on success. Currently this is the
    static value "PARTNER_API_KEY_DEFAULT" because the bearer scheme is
    single-tenant. The return value exists as the seam for a future
    multi-tenant namespacing rewrite (see TODO.md) without breaking the
    handler's signature.
    """
    expected_key = os.environ.get("PARTNER_API_KEY")

    if not expected_key:
        logger.error("CRITICAL: PARTNER_API_KEY missing; partner dispatch disabled.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Partner API Key.",
        )

    if not authorization or not secrets.compare_digest(
        authorization, f"Bearer {expected_key}"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Partner API Key.",
        )

    return "PARTNER_API_KEY_DEFAULT"


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/dispatch/request", status_code=status.HTTP_201_CREATED)
async def partner_dispatch_request(
    request: Request,
    partner_id: str = Depends(verify_partner_api_key),
):
    """Receive a partner-originated dispatch request.

    Manually validates the JSON body to preserve the legacy 400 contract,
    builds a synthetic mission_id, classifies the fault into a tier,
    publishes the resulting record to pan:stream:distress_alerts so the
    Ops Hub map lights up, and returns a 201 to the partner.

    Mission ID format note: FLT-NNNNN with 5 random digits is preserved
    from the legacy Flask handler for partner contract compatibility. The
    underlying ID space (90,000 values, no collision detection) is fragile
    at scale. A future revision should switch to UUID-based IDs (see the
    pan:task:tsk_<uuid> pattern in v2x_bounty_api.py for the canonical
    form) once partner contracts can absorb the change.
    """
    # --- Manual payload validation (preserves legacy 400 contract) ---
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload.",
        )

    if not data or not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload.",
        )

    for field in REQUIRED_FIELDS:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}",
            )

    asset_id = data["asset_id"]
    latitude = data["latitude"]
    longitude = data["longitude"]
    error_code = data["error_code"]

    # --- Mission classification ---
    mission_id = f"FLT-{random.randint(10000, 99999)}"
    tier, base_bounty = classify_fault(error_code)

    # --- Publish to Ops Hub map stream ---
    # The pan:stream:distress_alerts channel is read by api/telemetry_socket.py
    # which fans messages out over WebSocket to all connected command-center
    # clients. The legacy Flask handler built this payload but never
    # published it; this is a behavior addition during the migration.
    map_payload = {
        "id": mission_id,
        "asset_id": asset_id,
        "lat": latitude,
        "lng": longitude,
        "fault_code": error_code,
        "bounty": f"${base_bounty:.2f}",
        "tier": tier,
    }

    redis_client = request.app.state.redis_client
    try:
        await redis_client.publish(
            "pan:stream:distress_alerts",
            json.dumps(map_payload),
        )
    except Exception as e:
        # Publish failure is logged but does not fail the partner request.
        # The partner contract is "we accepted your dispatch"; the Ops Hub
        # map update is a best-effort downstream concern.
        logger.error(
            f"Failed to publish dispatch {mission_id} to distress_alerts stream: {e}"
        )

    logger.info(
        f"Partner dispatch accepted: mission_id={mission_id} "
        f"asset_id={asset_id} tier={tier} bounty=${base_bounty:.2f}"
    )

    # --- Response (shape preserved from legacy Flask handler exactly) ---
    return {
        "status": "accepted",
        "mission_id": mission_id,
        "asset": asset_id,
        "tier": tier,
        "financials": {
            "escrow_locked": f"${base_bounty:.2f}",
            "bidding_mode": "auto_escalate",
            "max_cap": f"${base_bounty + MAX_BID_OFFSET_USD:.2f}",
        },
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "message": "Reverse-auction dispatch initiated. Webhooks will fire on status changes.",
    }