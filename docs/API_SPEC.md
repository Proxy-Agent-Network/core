# Proxy Agent Network (PAN) | Fleet API Specification (v2026.2)

**Status:** Active — Mesa Pilot (Vanguard 50)
**Base URL (Production):** \`https://api.proxyagent.network/\`
**Base URL (Sandbox):** \`http://localhost:8000/\`
**Content-Type:** \`application/json\` (all endpoints)
**Last Revised:** April 2026

> This document defines the RESTful endpoints for the PAN Fleet Gateway and Agent API. All requests require authentication — Ed25519 signatures for Fleet Partners, TPM-bound JWT for Vanguard Agents. See [Section 2 — Authentication](#2-authentication) before integrating.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [OSM Color Taxonomy](#3-osm-color-taxonomy)
4. [Fleet API — Ingestion](#4-fleet-api--ingestion)
5. [Agent API — Mission Lifecycle](#5-agent-api--mission-lifecycle)
6. [Agent API — Status](#6-agent-api--status)
7. [Gesture & Multi-Agent Bonus System](#7-gesture--multi-agent-bonus-system)
8. [SB 1417 Compliance Auto-Logging](#8-sb-1417-compliance-auto-logging)
9. [Surge Pricing](#9-surge-pricing)
10. [Error Reference](#10-error-reference)
11. [Data Models](#11-data-models)

---

## 1. Overview

PAN routes physical AV incident response through a two-sided API:

- **Fleet Partners** (Waymo, Zoox, etc.) send authenticated distress signals when an AV encounters a physical edge case it cannot self-resolve. PAN locks a bounty in escrow, dispatches the nearest qualified Vanguard Agent, and returns a sealed SB 1417 Optical Health Report on completion.

- **Vanguard Agents** authenticate via hardware-bound TPM keys and poll for assigned missions. They acknowledge dispatch, complete the physical task, and submit evidence. Settlement is immediate via Lightning Network L402 HODL invoices — agents receive 90% of the settled bounty.

### Key Architectural Notes

- **Deduplication:** Duplicate distress signals for the same VIN + fault code within 300 seconds are rejected with \`409 Conflict\`. This prevents double-dispatch from AV retry loops.
- **Replay Protection:** Fleet webhook requests older than 300 seconds are rejected regardless of signature validity.
- **IDOR Protection:** All mission completion and acknowledgement endpoints verify that the requesting agent ID matches the agent assigned to the mission. Cross-agent access returns \`403 Forbidden\`.
- **Settlement:** Bounty is stated in USD. Agent net payout = \`bounty_usd × 0.90\`. The PAN network retains 10% for operational costs.

---

## 2. Authentication

### Fleet Partners — Ed25519 Signatures

All fleet-to-network requests must be signed with the fleet's registered Ed25519 private key. PAN verifies the signature server-side against the public key registered during fleet onboarding.

**Required Headers:**

| Header | Value |
|---|---|
| \`X-Fleet-Id\` | Your registered fleet identifier (e.g., \`WAYMO_MESA_01\`) |
| \`X-Fleet-Signature\` | Ed25519 signature over the raw request body, hex-encoded |

**Signature computation (Python):**
```python
import nacl.signing

signing_key = nacl.signing.SigningKey(your_private_key_bytes)
signature = signing_key.sign(request_body_bytes).signature.hex()
```

**Replay protection:** The signature must accompany a request with a \`timestamp\` field no more than 300 seconds old. Older requests are rejected with \`401 Unauthorized\`.

**Key registration:** Contact [rob@proxyagent.network](mailto:rob@proxyagent.network) to register your fleet and receive your Ed25519 keypair. Public keys are stored server-side as \`PUBKEY_{FLEET_ID}\` environment variables.

---

### Vanguard Agents — TPM-Bound JWT

Agent API requests require a JWT issued during the Key Ceremony — the one-time hardware binding that ties the agent's Firebase identity to their device's StrongBox TPM via Google Play Integrity attestation.

**Required Header:**

| Header | Value |
|---|---|
| \`Authorization\` | \`Bearer {agent_jwt}\` |

Agent JWTs are issued at Key Ceremony completion and are device-bound. A JWT from one device cannot be used on another. If an agent loses their device, the \`/ops/hardware-reset\` workflow must be used — re-running the Key Ceremony on a new device without this step will return \`409 Conflict\` (key already registered).

---

## 3. OSM Color Taxonomy

PAN uses the Operational Status Matrix (OSM) color taxonomy for task classification, priority, and bounty anchoring. Pass \`osm_color\` in all distress signals.

| \`osm_color\` | Category | Tier | Default Bounty | Min Fleet Bid |
|---|---|---|---|---|
| \`RED\` | Biological / Foreign Object | 3 (Critical) | $65.00 | $50.00 |
| \`PURPLE\` | Defleeting | 3 (Critical) | $65.00 | $50.00 |
| \`YELLOW\` | Tech / Sensor Fault | 2 (Elevated) | $45.00 | $30.00 |
| \`ORANGE\` | Calibrations | 2 (Elevated) | $45.00 | $30.00 |
| \`GREEN\` | Power Down & Rest (PDR) | 1 (Standard) | $14.00 | $10.00 |
| \`BLUE\` | Validation | 1 (Standard) | $14.00 | $10.00 |
| \`WHITE\` | Demo Vehicle | 1 (Standard) | $14.00 | $10.00 |

Bounties are dynamically adjusted by the Surge Pricing Engine when Agent Utilization Ratio (AUR) exceeds 75%. See [Section 9 — Surge Pricing](#9-surge-pricing).

---

## 4. Fleet API — Ingestion

### Dispatch Vanguard Agent

**\`POST /api/v1/v2x/distress\`**

Triggers dispatch of the nearest qualified Vanguard Agent. Locks the bounty in Lightning Escrow. Optionally queues a secondary Tier 1 sentry agent for traffic direction and scene support.

**Auth:** Ed25519 fleet signature required (\`X-Fleet-Id\`, \`X-Fleet-Signature\`).

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| \`vin\` | \`string\` | ✅ | Vehicle VIN. Plain text — not hashed. |
| \`fault_code\` | \`string\` | ✅ | UDS fault code (e.g., \`UDS_SENSOR_OCCLUSION_LIDAR_FL\`). |
| \`latitude\` | \`float\` | ✅ | WGS-84 decimal degrees. |
| \`longitude\` | \`float\` | ✅ | WGS-84 decimal degrees. |
| \`bounty_usd\` | \`float\` | — | Opening bid in USD. Defaults to \`25.00\`. Must meet minimum for \`osm_color\` tier (see Section 3). |
| \`osm_color\` | \`string\` | — | OSM task classification. Defaults to \`"GREEN"\`. Case-insensitive. |
| \`request_secondary\` | \`bool\` | — | Set \`true\` to simultaneously queue a T1 sentry agent. Defaults to \`false\`. Only valid for T2/T3 incidents. |
| \`secondary_start_bid_usd\` | \`float\` | — | Secondary agent opening bid. Defaults to \`14.00\` (T1 balanced default). Ignored if \`request_secondary\` is \`false\`. |
| \`secondary_max_bid_usd\` | \`float\` | — | Secondary agent maximum bid. Defaults to \`24.00\`. |
| \`secondary_escalation_usd_per_min\` | \`float\` | — | Secondary bid escalation rate. Defaults to \`2.00\`. |

**Example Request:**
```bash
POST /api/v1/v2x/distress
X-Fleet-Id: WAYMO_MESA_01
X-Fleet-Signature: <ed25519_hex_signature>
Content-Type: application/json

{
  "vin": "WAYMO-404",
  "fault_code": "UDS_SENSOR_OCCLUSION_LIDAR_FL",
  "latitude": 33.420,
  "longitude": -111.840,
  "bounty_usd": 45.00,
  "osm_color": "YELLOW"
}
```

**Example Request — With Secondary Agent:**
```bash
POST /api/v1/v2x/distress
X-Fleet-Id: WAYMO_MESA_01
X-Fleet-Signature: <ed25519_hex_signature>
Content-Type: application/json

{
  "vin": "WAYMO-404",
  "fault_code": "UDS_BIOHAZARD_SPILL_CABIN",
  "latitude": 33.420,
  "longitude": -111.840,
  "bounty_usd": 65.00,
  "osm_color": "RED",
  "request_secondary": true,
  "secondary_start_bid_usd": 14.00,
  "secondary_max_bid_usd": 24.00,
  "secondary_escalation_usd_per_min": 2.00
}
```

**Response \`201 Created\`:**

```json
{
  "status": "success",
  "task_id": "tsk_a3f8c291b04d",
  "incident_id": "inc_3f8c291b04"
}
```

**Response \`201 Created\` — With Secondary:**

```json
{
  "status": "success",
  "task_id": "tsk_a3f8c291b04d",
  "incident_id": "inc_3f8c291b04",
  "sentry_task_id": "tsk_b5e9d102c13e"
}
```

\`incident_id\` links the primary and secondary tasks under a single incident. Both tasks will share the same SB 1417 Optical Health Report scope. Both agents will be excluded from being assigned to each other's task.

**Error Responses:**

| Code | Condition |
|---|---|
| \`401 Unauthorized\` | Invalid or missing Ed25519 signature, or request timestamp > 300s old. |
| \`409 Conflict\` | Duplicate active task for this VIN + fault code (300s dedup window). |
| \`500 Internal Server Error\` | Routing failure — safe to retry after 2 seconds. |

---

## 5. Agent API — Mission Lifecycle

All agent endpoints require \`Authorization: Bearer {agent_jwt}\`.

---

### Poll for Assigned Missions

**\`GET /v1/agent/missions\`**

Polled by the PAN Command mobile app to retrieve missions assigned to the authenticated agent. Called on app foreground and at a configured polling interval.

**Response \`200 OK\`:**

```json
[
  {
    "task_id": "tsk_a3f8c291b04d",
    "incident_id": "inc_3f8c291b04",
    "lat": 33.42,
    "lon": -111.84,
    "error_code": "UDS_SENSOR_OCCLUSION_LIDAR_FL",
    "bounty_usd": 45.0,
    "intersection": "WAYMO-404",
    "role": "PRIMARY",
    "status": "ASSIGNED"
  }
]
```

Returns an empty array \`[]\` if no missions are currently assigned. The \`role\` field will be \`"PRIMARY"\` for standard dispatch or \`"SENTRY"\` for secondary agent assignment. Sentry missions display \`fault_code: "SENTRY_TRAFFIC_DIRECTION"\`.

---

### Acknowledge Mission

**\`POST /v1/agent/missions/{task_id}/ack\`**

Fired silently by PAN Command the moment the mission UI renders on the agent's screen. Confirms the agent has received and seen the mission. Required before the 15-second SLA watchdog considers the dispatch secure.

**Response \`200 OK\`:**

```json
{
  "status": "success",
  "message": "Mission acknowledged."
}
```

| Code | Condition |
|---|---|
| \`403 Forbidden\` | Mission is not assigned to this agent (IDOR protection). |
| \`404 Not Found\` | Mission not found or already revoked (re-dispatched after timeout). |

---

### Complete Mission

**\`POST /v1/agent/missions/{task_id}/complete\`**

Fired when the agent has physically resolved the incident. Triggers the three-stage settlement oracle: hardware attestation → SB 1417 compliance seal → AV-signed Ed25519 payload verified by Rust smart contract. On success, agent receives 90% of \`bounty_usd\` in their wallet immediately.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| \`agent_id\` | \`string\` | ✅ | Must match the authenticated agent's ID. |
| \`net_payout\` | \`float\` | ✅ | Agent's expected payout. Server verifies this equals \`bounty_usd × 0.90\` — client-submitted values are not trusted for settlement calculations. |
| \`evidence_urls\` | \`array[string]\` | — | URLs of redacted photographic evidence (processed through \`PrivacyFilter.sanitizeImage()\` before upload — faces and license plates redacted on-device). |
| \`hardware_attestation_token\` | \`string\` | — | StrongBox TPM attestation JWT binding the report to the agent's physical device. |
| \`av_signature_hex\` | \`string\` | — | Ed25519 signature from the AV confirming the agent was physically present and the fault code cleared. |

**Example Request:**
```json
{
  "agent_id": "VNG-A3F8C2-ALPHA",
  "net_payout": 40.50,
  "evidence_urls": [
    "[https://cdn.proxyagent.network/evidence/redacted_frame_001.jpg](https://cdn.proxyagent.network/evidence/redacted_frame_001.jpg)",
    "[https://cdn.proxyagent.network/evidence/redacted_frame_002.jpg](https://cdn.proxyagent.network/evidence/redacted_frame_002.jpg)"
  ],
  "hardware_attestation_token": "<strongbox_jwt>",
  "av_signature_hex": "<ed25519_hex>"
}
```

**Response \`200 OK\`:**

```json
{
  "status": "success"
}
```

On success, the SB 1417 Optical Health Report is sealed, the mission is removed from the active queue, and the agent's status returns to \`ONLINE\` for re-dispatch.

| Code | Condition |
|---|---|
| \`403 Forbidden\` | Mission assigned to a different agent (IDOR protection). |
| \`404 Not Found\` | Task or mission not found. |
| \`503 Service Unavailable\` | Wallet pipeline temporarily unavailable after 10 retry attempts. Payout is queued — agent will receive funds. Safe to display "payout pending" to agent. |

---

### Decline Mission

**\`POST /v1/agent/missions/{task_id}/decline\`**

Agent rejects the assigned mission. Places a 15-minute price-sensitive cooldown on this agent for this task — if the agent declined at a given bounty level, they won't receive it again at the same price during the cooldown window. The task re-enters the dispatch queue for reassignment.

**Response \`200 OK\`:**

```json
{
  "status": "success",
  "message": "Mission declined."
}
```

No request body required. The agent's status automatically returns to \`ONLINE\`.

---

### Extend Sentry Mission

**\`POST /v1/agent/missions/{task_id}/extend\`**

Accepts a fleet-offered time extension for an active \`SENTRY\` role mission. Only valid for agents holding a \`SENTRY\` role assignment. Adds incremental bounty to the sentry task up to the fleet manager's configured \`max_bounty_usd\` ceiling.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| \`task_id\` | \`string\` | ✅ | Must match the \`{task_id}\` path parameter. |
| \`extension_minutes\` | \`int\` | ✅ | Number of minutes the sentry is extending their on-scene commitment. |
| \`accepted_bounty_usd\` | \`float\` | ✅ | Additional bounty accepted for the extension period. Must not cause the total bounty to exceed \`max_bounty_usd\`. |

**Example Request:**
```json
{
  "task_id": "tsk_b5e9d102c13e",
  "extension_minutes": 15,
  "accepted_bounty_usd": 5.00
}
```

**Response \`200 OK\`:**

```json
{
  "status": "success",
  "new_bounty_usd": 19.00
}
```

| Code | Condition |
|---|---|
| \`400 Bad Request\` | Extension would cause total bounty to exceed the fleet manager's configured \`max_bounty_usd\` for this task. |
| \`403 Forbidden\` | Agent does not hold this mission, or the mission role is not \`SENTRY\`. |

---

## 6. Agent API — Status

### Update Agent Status

**\`POST /api/v1/agent/status\`**

Updates the agent's geospatial position and availability status in the Redis dispatch index. This is the **only** mechanism by which the matching engine detects available agents — agents who write status to Firebase RTDB (legacy path) will be invisible to dispatch.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| \`agent_id\` | \`string\` | ✅ | Authenticated agent's ID. |
| \`status\` | \`string\` | ✅ | One of: \`ONLINE\`, \`EN_ROUTE\`, \`ON_SCENE\`, \`OFFLINE\`. |
| \`latitude\` | \`float\` | ✅ | Current position. |
| \`longitude\` | \`float\` | ✅ | Current position. |
| \`patrol_mode\` | \`string\` | — | \`"car"\` (default) or \`"foot"\`. Affects OSRM routing profile used for ETA calculation. |

**Response \`200 OK\`:**

```json
{
  "status": "success"
}
```

**Important:** GPS coordinates written via this endpoint are stored permanently in the SB 1417 Optical Health Report alongside all safety events. This is a regulatory requirement — agent location data within compliance reports is not ephemeral.

---

## 7. Gesture & Multi-Agent Bonus System

Multi-agent bonuses are validated server-side when two Gauntlets VFG-1 report a verified physical contact gesture on the same incident, or when one Gauntlet reports a contact interaction and the gloveless partner confirms via app.

### Bonus Amounts

| Gesture | Type | Amount (each agent) | Requirements |
|---|---|---|---|
| Solo Glove Welcome | Base (One-Sided) | $2.00 | 1 Gauntlet. Partner must confirm via PAN Command push notification within 5 mins. |
| Handshake | Base (Bilateral) | $5.00 | 2 Gauntlets + NFC confirmation |
| Fist Bump | Base (Bilateral) | $5.00 | 2 Gauntlets + NFC confirmation |
| High Five | Base (Bilateral) | $5.00 | 2 Gauntlets + NFC confirmation |
| Secret Handshake | Flourish upgrade | $7.00 | 2 Gauntlets + NFC confirmation |
| BOOM Explosion | Flourish upgrade | $7.00 | 2 Gauntlets + NFC confirmation |
| Double Down | Flourish upgrade | $7.00 | 2 Gauntlets + NFC confirmation |

### Gesture Event Payload

Gesture events are submitted by the Gauntlets firmware via PAN Command. The backend validates eligibility before crediting wallets.

```kotlin
data class GauntletGestureEvent(
    val gloveId: String,            // Unique registered glove ID
    val agentId: String,            // Bound agent from Key Ceremony
    val gestureType: GestureType,   // See enum below
    val confidence: Float,          // 0.0–1.0, must be ≥ 0.85
    val partnerGloveId: String?,    // Non-null if bilateral NFC partner confirmed
    val partnerAgentId: String?,    // Non-null for Solo Welcome (gloveless partner ID)
    val timestamp: Long,
    val missionId: String?,         // Active mission context
    val toolNfcId: String?          // Tool in hand at time of gesture (for SB 1417 context)
)

enum class GestureType {
    SNAP_SINGLE, SNAP_DOUBLE, SNAP_TRIPLE, SNAP_HOLD, SNAP_POINT,
    HANDSHAKE, HANDSHAKE_SECRET,
    FIST_BUMP, FIST_BUMP_BOOM,
    HIGH_FIVE, HIGH_FIVE_CONSECUTIVE,
    MIYAGI_TWO_HAND, MIYAGI_SURFACE,
    CONTACT_GENERIC
}
```

### Anti-Gaming Safeguards

All multi-agent bonus claims are validated against the following before wallet credit:

| Safeguard | Implementation |
|---|---|
| Physical contact verification | NFC bilateral read — both gloves must confirm contact at ≤4cm range. One agent cannot trigger a full $5/$7 multi-agent bonus alone. |
| Solo Glove App Confirmation | For the $2 Solo Glove Welcome bonus, the gloveless partner must tap the confirmation push notification in PAN Command within 5 minutes. If no confirmation occurs, the bonus lapses. |
| Mission state requirement | Both agents must be \`ON_SCENE\` with the same \`incident_id\`. Bonuses during \`IDLE\` or \`EN_ROUTE\` are rejected. |
| Per-incident bonus lock | Each bonus type is claimable once per \`incident_id\`. Atomic Redis \`SET NX\` prevents race conditions. |
| Shift cooldown | Same agent pair capped at 3 multi-agent bonuses per 8-hour shift across all incidents. |
| Confidence threshold | Gesture confidence must be ≥ 0.85. Lower-confidence events are discarded. |

### Choreography Architecture Note

Multi-agent gesture animations (simultaneous hat flash, spine shockwave) are triggered via direct nRF52840 Gazell peer-to-peer radio link between the partner gloves — **not** via PAN Command BLE fan-out. BLE fan-out cannot guarantee the sub-100ms simultaneity window required for the gesture feel. Wallet credit and SB 1417 logging route through PAN Command asynchronously after the animation has already fired.

---

## 8. SB 1417 Compliance Auto-Logging

Every mission automatically generates a sealed, immutable Optical Health Report. No agent action is required. The following data is appended automatically throughout each mission:

| Source | Component | Logged Data |
|---|---|---|
| Photo evidence | Agent smartphone | Redacted JPEG frames (720p/3fps). Faces and plates redacted on-device via \`PrivacyFilter.sanitizeImage()\` before upload. Raw PII never transmitted. |
| Hardware attestation | StrongBox TPM | JWT binding report to specific device hardware. |
| Voice transcripts | Aegis Polo — Communicator Pin (T3) | On-device speech-to-text. \`[COMPLIANCE]\`-flagged entries auto-appended. Non-compliance interactions logged but not appended. |
| RATS threat events | PANOPLY Vest — mmWave radar | Zone, object class, approach velocity, detection distance, agent repositioned flag. |
| Sensor override events | PANOPLY Vest — shoulder button | Timestamp, agent ID, override duration. Cannot be retroactively removed. |
| Pre-approach air quality | PANOPLY Vest — biohazard sensor (T2+) | VOC, CO, H2S, PM2.5, PM10, temperature, humidity at \`ON_SCENE\` transition. |
| Personal breathing zone | Aegis Polo — air quality sensor (T3) | Same metrics at breathing-zone height. Distinguishes ambient hazard from personal exposure. |
| Biometric safety events | Aegis Polo — biometric patch (T3) | HR, SpO2, skin temp, stress index — logged only at safety-threshold crossings. Continuous stream not logged. |
| Conductivity hazard events | Aegis Polo — wrist cuff sensors (T3) | Tool in hand, affected hand, timestamp, GPS. |
| Approaching vehicle log | PANOPLY Vest — plate camera (T3) | Plate hash (redacted), approach vector, distance, timestamp. |
| Impact event | PANOPLY Vest — spine accelerometer (T3) | G-force vector, welfare response time, outcome. |
| Duress events | PANOPLY Vest — duress button | GPS pin, timestamp, battery level. Cannot be retroactively removed. |
| Agent gesture log | Gauntlets VFG-1 | Gesture type, confidence, partner agent ID, tool in hand. |

Fleet partners receive only the sealed report hash and a compliance status indicator — never raw agent biometric data, voice transcripts, or PII.

---

## 9. Surge Pricing

The Surge Pricing Engine dynamically adjusts bounties when Agent Utilization Ratio (AUR) exceeds 75% in the active sector.

| AUR Threshold | Surge Multiplier |
|---|---|
| < 75% | 1.0× (no surge) |
| 75–85% | 1.5× |
| 85–95% | 2.0× |
| > 95% | 3.0× (maximum) |

Surge is applied to the \`bounty_usd\` value before the task enters the dispatch queue. Agents always receive 90% of the surged bounty. The \`3.0×\` cap is hard-coded and cannot be overridden by fleet partners.

Fleet partners configure their starting bid, escalation rate, and maximum bid via the Auto-Dispatch Rules panel in the Partner Integration Portal. The \`bounty_usd\` field in the distress signal should reflect the fleet's current bid at time of dispatch — escalation beyond the starting bid is managed by the fleet partner's bidding logic.

---

## 10. Error Reference

| Code | Meaning | Common Cause |
|---|---|---|
| \`400 Bad Request\` | Invalid request body or business rule violation | Extension would exceed \`max_bounty_usd\`; bounty below tier minimum |
| \`401 Unauthorized\` | Authentication failure | Invalid Ed25519 signature; expired agent JWT; request > 300s old |
| \`403 Forbidden\` | Authorization failure | IDOR — agent attempting to access another agent's mission; non-SENTRY agent calling \`/extend\` |
| \`404 Not Found\` | Resource not found | Task or mission already completed, declined, or timed out and re-dispatched |
| \`409 Conflict\` | Duplicate detection | Active task already exists for this VIN + fault code (300s dedup window); agent Key Ceremony already completed |
| \`500 Internal Server Error\` | Routing failure | Safe to retry after 2 seconds with exponential backoff |
| \`503 Service Unavailable\` | Transient service degradation | Wallet pipeline temporarily unavailable; payout is queued and will be delivered |

---

## 11. Data Models

### \`DistressPayload\`

```python
class DistressPayload(BaseModel):
    vin: str                                      # Vehicle VIN (plain text)
    fault_code: str                               # UDS fault code
    latitude: float                               # WGS-84
    longitude: float                              # WGS-84
    bounty_usd: float = 25.0                      # Opening bid in USD
    osm_color: str = "GREEN"                      # OSM classification (case-insensitive)
    request_secondary: bool = False               # Queue T1 sentry agent
    secondary_start_bid_usd: float = 14.0         # Secondary opening bid
    secondary_max_bid_usd: float = 24.0           # Secondary maximum bid
    secondary_escalation_usd_per_min: float = 2.0 # Secondary escalation rate
```

### \`MissionCompletePayload\`

```python
class MissionCompletePayload(BaseModel):
    agent_id: str
    net_payout: float                    # Expected payout (server validates)
    evidence_urls: list = []             # Redacted frame URLs
    hardware_attestation_token: str = "" # StrongBox TPM JWT
    av_signature_hex: str = ""           # AV Ed25519 confirmation
```

### \`SentryExtensionPayload\`

```python
class SentryExtensionPayload(BaseModel):
    task_id: str             # Must match path parameter
    extension_minutes: int   # Duration of extension
    accepted_bounty_usd: float  # Additional bounty for extension
```

### \`AegisBiometricEvent\`

Published internally from the Aegis Polo via BLE → PAN Command → backend. Not a REST endpoint — documented here for fleet partner awareness of what feeds the SB 1417 compliance record.

```python
class AegisBiometricEvent:
    agent_id: str
    mission_id: str | None
    heart_rate_bpm: int
    skin_temp_c: float
    sp_o2_percent: float
    gsr_microsiemens: float
    stress_index: float        # 0.0–1.0 derived from HR + GSR combined
    timestamp: int
```

The \`stress_index\` field feeds the Composite Threat Response algorithm: if \`stress_index > 0.7\` while the vest RATS system is actively tracking a Zone 2 threat, the system escalates directly to Zone 1 maximum response, skipping the Zone 2 warning sequence.

### Mission Object (Agent-Facing)

```json
{
  "task_id": "tsk_a3f8c291b04d",
  "incident_id": "inc_3f8c291b04",
  "lat": 33.42,
  "lon": -111.84,
  "error_code": "UDS_SENSOR_OCCLUSION_LIDAR_FL",
  "bounty_usd": 45.0,
  "intersection": "WAYMO-404",
  "role": "PRIMARY",
  "status": "ASSIGNED"
}
```

\`role\` is one of \`"PRIMARY"\` or \`"SENTRY"\`. Sentry missions will always have \`error_code: "SENTRY_TRAFFIC_DIRECTION"\` regardless of the primary fault at the incident.

---

*Proxy Agent Network LLC · Mesa, AZ · proxyagent.network · v2026.2 · April 2026*