# Proxy Agent Network (PAN) | Fleet API Specification (v2026.1)

**Status:** Active (Mesa Pilot)
**Base URL (Production):** `https://api.proxyagent.network/v2026.1/`
**Base URL (Sandbox):** `http://localhost:5000/`

This document defines the RESTful endpoints for the PAN Fleet Gateway. All payloads utilize `application/json` and require strict HMAC-SHA256 request signatures from registered Fleet Partners (e.g., Waymo, Zoox) or TPM 2.0 attestations from Vanguard Agents.

---

## 1. Fleet-to-Network (Ingestion)

### Dispatch Vanguard Agent
**Endpoint:** `POST /fleet/dispatch`  
**Description:** The AV's onboard diagnostic system triggers this webhook when a physical edge-case (e.g., sensor occlusion) grounds the vehicle. The API locks the L402 bounty and routes the mission to the nearest active Agent in Sector 1.

**Request Body:**
```json
{
  "fleet_id": "WAYMO_CORP",
  "vehicle_vin_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "uds_fault_code": "LIDAR_OCCLUSION_FRONT_LEFT",
  "telemetry": {
    "lat": 33.3214,
    "lng": -111.6608,
    "heading": 184.2
  },
  "l402_bounty_sats": 25000,
  "priority": "CRITICAL"
}