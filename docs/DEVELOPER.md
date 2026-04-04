# PAN Tactical — Proxy Agent Network
**The Human Infrastructure for the Autonomous Era**

> Veteran-led field support for autonomous vehicle fleets in Mesa, AZ (Waymo/Magna sector).
> Go-Live: Memorial Day 2026 | Pilot: Vanguard 50 Agents

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Prerequisites](#3-prerequisites)
4. [Environment Setup](#4-environment-setup)
5. [Backend Setup (FastAPI + Redis)](#5-backend-setup)
6. [Mobile Setup (Kotlin Multiplatform)](#6-mobile-setup)
7. [Cognitive Vault Setup](#7-cognitive-vault-setup)
8. [Key Ceremony (Vanguard Agent Onboarding)](#8-key-ceremony)
9. [Running the Stack](#9-running-the-stack)
10. [OSM Color Taxonomy](#10-osm-color-taxonomy)
11. [Project Copperfield — Vanguard Field System](#11-project-copperfield--vanguard-field-system)
12. [BLE / Hardware Integration](#12-ble--hardware-integration)
13. [SB 1417 Compliance Pipeline](#13-sb-1417-compliance-pipeline)
14. [Proxy-Alpha Companion Mode](#14-proxy-alpha-companion-mode)
15. [Checkr Background Verification](#15-checkr-background-verification)
16. [Open Roadmap](#16-open-roadmap)
17. [Troubleshooting](#17-troubleshooting)
18. [Security Notes](#18-security-notes)

---

## 1. Project Overview

PAN Tactical dispatches verified Vanguard Agents to resolve physical AV edge cases that autonomous vehicles cannot handle alone — sensor occlusion, door faults, spill remediation, and first-responder liaison. Agents earn real bounty payouts settled via Lightning Network L402 micropayments.

Agents in the Vanguard 50 pilot are equipped with the **Project Copperfield Vanguard Field System** — four intelligent wearable components that together make a Vanguard Agent the safest and most documented field operator on any incident scene. See [Section 11](#11-project-copperfield--vanguard-field-system) for hardware integration details.

**Core Stack:**

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) + Redis |
| Mobile App | Kotlin Multiplatform (Android/iOS) |
| Payments | Lightning Network (LND) via gRPC |
| Escrow | Rust smart contracts via PyO3 FFI |
| AI Dispatcher | Gemini 2.5 Flash + Cognitive Vault |
| Hardware Security | Android StrongBox TPM + Google Play Integrity |
| Proximity | UWB ranging (15m) + BLE OOB handshake (50m) |
| Compliance | SB 1417 Optical Health Reports |
| Background Checks | Checkr API (driver_pro package) |
| Wearables | BLE 5.0 mesh · nRF52840 · ESP32-C3 |
| Threat Detection | TI IWR6843AOP mmWave + Edge ML (Coral TPU) |

---

## 2. Architecture

```
Fleet Partner (AV)
       │ Ed25519 Webhook
       ▼
┌─────────────────────┐
│   webhook_auth.py   │  Zero-Trust ingress validation
│   (Ed25519 + HMAC)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  v2x_bounty_api.py  │  Distress signal ingestion
│  (FastAPI Router)   │  OSM color taxonomy + base bounty lock
└──────────┬──────────┘
           │ Redis Queue
           ▼
┌─────────────────────┐     ┌──────────────────────┐
│  matching_engine.py │────▶│ surge_pricing_engine  │
│  (Geospatial FIFO)  │     │ (AUR-based repricing) │
└──────────┬──────────┘     └──────────────────────┘
           │ mission:active:{task_id}  +  HNOA policy bind (async)
           │ Checkr background verified at enlistment
           ▼
┌──────────────────────────────────────────────────┐
│  Mobile App (KMP Android/iOS)                    │
│  HardwarePermissionsGuard → KMP App              │
│  BLE OOB → UWB micro-homing → Evidence capture  │
│                                                  │
│  Project Copperfield Wearable Layer:             │
│  HapHat v2.3 ←→ PANOPLY Vest v1.1               │
│  Aegis Polo VFP-1 ←→ Gauntlets VFG-1            │
│  (BLE mesh · haptic choreography · RATS)         │
└──────────┬───────────────────────────────────────┘
           │ completeMission(evidenceUrls, av_signature)
           ▼
┌─────────────────────┐
│  escrow_oracle.py   │  3-stage zero-trust settlement
│  (Play Integrity +  │  Hardware → SB1417 → Ed25519 Rust FFI
│   SB1417 + Ed25519) │
└──────────┬──────────┘
           │ LND gRPC
           ▼
┌─────────────────────┐
│  lightning_engine   │  L402 HODL invoice settlement
│  (Mainnet LND)      │  Agent earns 90% cut
└─────────────────────┘
```

---

## 3. Prerequisites

### Backend
- Python 3.10+
- Redis 7.0+
- LND node (mainnet) with TLS cert and macaroon
- GCP service account with Play Integrity API enabled (ADC configured)
- Checkr account with `CHECKR_API_KEY` and `CHECKR_WEBHOOK_SECRET`

### Mobile
- Android Studio Hedgehog or later
- Android SDK API 26+ (required for UWB and BLE)
- Kotlin 2.1.0
- Firebase project with Authentication enabled
  - **Note:** Firebase RTDB rules must be set to `deny-all` — the app no longer writes directly to RTDB. All agent state routes through the Python backend → Redis.
- Google Play Console app linked to GCP project

### Rust (Escrow Smart Contracts)
- Rust 1.70+
- PyO3 build toolchain

### Hardware (Vanguard Field System — Pilot Only)
- HapHat v2.3 (ESP32-C3 · nRF52840 · BLE 5.0)
- PANOPLY Vest v1.1 (mmWave radar · spine strip · BLE)
- Aegis Polo VFP-1 (Communicator Pin · biometric patch · BLE)
- Gauntlets VFG-1 (IMU · NFC · BLE)
- All hardware uses Nordic DFU OTA update protocol

---

## 4. Environment Setup

### `local.properties` (Mobile — never commit this file)

```properties
# Google Maps
MAPS_API_KEY=your_android_maps_key
IOS_MAPS_API_KEY=your_ios_maps_key

# Evidence Upload (SB 1417 Compliance)
# ⚠️ ARCHITECTURAL NOTE: imgbb is approved for Vanguard 50 pilot only.
# Must migrate to AWS S3 or GCP Cloud Storage before fleet partner sign-off.
IMGBB_API_KEY=your_imgbb_key

# Firebase (Auth only — RTDB rules must be set to deny-all)
# FIREBASE_RTDB_URL is intentionally removed — all state routes through PAN backend
FIREBASE_PROJECT_ID=your_firebase_project_id

# PAN Backend
PAN_API_BASE_URL=https://your-backend-url.com
AGENT_DEV_TOKEN=your_dev_token

# Google Play Integrity (GCP Project Number — from Play Console)
PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER=123456789012

# OSRM Tactical Routing (self-hosted)
OSRM_BASE_URL=https://your-osrm-instance.com
```

### Backend `.env`

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# LND (Mainnet)
LND_GRPC_HOST=your-lnd-node-ip
LND_GRPC_PORT=10009
LND_TLS_CERT_PATH=/path/to/tls.cert
LND_MACAROON_PATH=/path/to/admin.macaroon
LND_NETWORK=mainnet

# Play Integrity (Google Application Default Credentials)
ANDROID_PACKAGE_NAME=com.pan.tactical
# Run: gcloud auth application-default login

# Fleet Partner Public Keys (Ed25519 hex)
PUBKEY_WAYMO_MESA_01=your_waymo_pubkey_hex
PUBKEY_MAGNA_TEST_01=your_magna_pubkey_hex

# Carrier HMAC Secrets (Logistics Webhooks)
WHSEC_DHL=your_dhl_secret
WHSEC_FEDEX=your_fedex_secret
WHSEC_UPS=your_ups_secret

# Hardware Registry
HARDWARE_REGISTRY_URL=http://hardware-registry:8010

# Cognitive Vault (Memory Encryption)
# Generate with: python -m cognitive_vault.memory_cipher
COGNITIVE_ENCRYPTION_KEY=your_fernet_key_here

# Checkr Background Verification
CHECKR_API_KEY=your_checkr_api_key
CHECKR_WEBHOOK_SECRET=your_checkr_webhook_secret
# Recommended package: driver_pro (~$30/check)

# Environment
ENVIRONMENT=production
```

### Generating a Cognitive Encryption Key

```bash
cd apps/backend/src
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Store the output as `COGNITIVE_ENCRYPTION_KEY`. **This key must be static across container restarts — losing it means losing all encrypted agent memories.**

---

## 5. Backend Setup

### Install Dependencies

```bash
cd apps/backend
pip install -r requirements.txt

# Install Cognitive Vault as a local package
pip install -e src/cognitive_vault
```

### Build Rust Escrow Smart Contracts

> ⚠️ **Activate your Python virtual environment first.** If no venv is active, Maturin will attempt to install the Rust bindings into your global Python environment, which can cause version conflicts.

```bash
# Activate your venv first
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

cd apps/backend/src/core/economics
maturin develop  # or maturin build --release for production
```

### Start Redis

```bash
redis-server
```

### Run the Backend

```bash
cd apps/backend/src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Background Workers

```bash
cd apps/backend/src
python run_workers.py
```

---

## 6. Mobile Setup

### Android

1. Add `google-services.json` to `composeApp/`
2. Add all required keys to `local.properties` (see Section 4)
3. Build and run:

```bash
./gradlew :composeApp:assembleDebug
```

### iOS

1. Add `GoogleService-Info.plist` to the iOS target
2. Ensure `IOS_MAPS_API_KEY` is set in `local.properties`
3. Build via Xcode after running:

```bash
./gradlew :composeApp:linkDebugFrameworkIosArm64
```

### Required Android Permissions (`AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
<uses-permission android:name="android.permission.UWB_RANGING" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />
```

### Key Mobile Architecture Notes

**`MainActivity`** inherits from `FragmentActivity` (not `ComponentActivity`) — required for the Phase 4 biometric prompt. Do not change this inheritance.

**`HardwarePermissionsGuard`** wraps the root composable — GPS, BLE, and UWB permissions are gate-checked before the KMP app boots. Hardware clients cannot initialize safely before this guard completes.

**`PanApiClient`** routes all agent status updates to the Python backend (`/api/v1/agent/status`), not directly to Firebase RTDB. The matching engine reads from Redis — writing to RTDB makes the agent invisible to geospatial dispatch.

**`PrivacyFilter.sanitizeImage()`** runs on `Dispatchers.Default` and owns the input bitmap completely. Never use the original bitmap after calling this function — it is unconditionally recycled. The fail-safe path returns a fully black bitmap rather than the unredacted original.

---

## 7. Cognitive Vault Setup

The Cognitive Vault provides encrypted memory and emotion state tracking for Proxy-Alpha (the tactical AI engine).

### Install

```bash
pip install -e apps/backend/src/cognitive_vault
```

### Verify

```bash
python -c "from cognitive_vault import EmotionEngine, MemoryCipher; print('Vault OK')"
```

### Test Encryption Cycle

```bash
cd apps/backend/src/cognitive_vault
python memory_cipher.py
# Outputs a new master key and runs an encrypt/decrypt cycle
```

### Start Proxy-Alpha (AgentEngine)

```python
from agent_engine import AgentEngine
import asyncio
import redis.asyncio as redis

async def main():
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    brain = AgentEngine(redis_client=redis_client)
    await brain.startup()
    response = await brain.process_task("What is the fault code for WAYMO-404?")
    print(response)

asyncio.run(main())
```

### Companion Mode (Proxy-Alpha via Communicator Pin)

In the field, Proxy-Alpha is accessed hands-free through the Aegis Polo's Communicator Pin. The agent says **"Hey Dispatch"** (default wake word — configurable to "Hey Commander", "Hey Captain", or "Hey Vanguard" in app settings). The pin's MEMS microphone captures the query. On-device speech-to-text transcribes it. The response plays through the pin's speaker.

The system prompt is injected automatically at mission accept and includes:
- Vehicle VIN and fault code
- UDS fault code plain-English description and known causes
- Agent certification level (determines depth of procedural guidance)
- Live vehicle telemetry from fleet API
- SLA remaining time

All interactions are transcribed and stored. Compliance-relevant responses (fault codes, safety protocols, regulatory terms) are automatically flagged `[COMPLIANCE]` and appended to the SB 1417 report. Casual interactions are logged but not appended to compliance records. Fleet managers see interaction count, duration, and compliance flag — not the full transcript.

```python
def build_proxy_alpha_context(mission: dict, agent: dict) -> str:
    return f"""
You are Proxy-Alpha, the tactical AI assistant for Vanguard Agent
{agent['callsign']}, Tier {agent['tier']}, Proxy Agent Network.

MISSION CONTEXT:
  Mission ID:    {mission['task_id']}
  Vehicle VIN:   {mission['vin']}
  Fleet:         {mission['fleet_id']}
  Fault Code:    {mission['fault_code']}
  Plain Text:    {UDS_CODE_LIBRARY[mission['fault_code']].description}
  OSM Tier:      {mission['osm_color']}
  SLA Remaining: {calculate_sla_remaining(mission)} minutes

AGENT CERTIFICATIONS: {agent['certifications']}
VEHICLE TELEMETRY: {format_vehicle_telemetry(mission['vin'])}

Be concise. Agent is working with their hands.
Safety first. Procedure second. Compliance third.
All interactions are logged to SB 1417 report.
Mark compliance-relevant responses with [COMPLIANCE].
    """
```

---

## 8. Key Ceremony

Every Vanguard Agent must complete the Key Ceremony before they can receive missions. This binds their Firebase identity to their device's hardware TPM using Google Play Integrity attestation.

### Prerequisites
- Agent device must have Google Play Services
- Device must not be rooted or an emulator
- Agent must be logged in via Firebase Authentication
- `PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER` must be set in `local.properties`
- Checkr background check must be completed and approved (see Section 15)

### Steps

1. **Provision agent accounts** (run once by ops team):
```bash
cd apps/backend/src
python provision_vanguard_50.py
# Use --reset flag with caution — destructive operation
```

2. **Agent completes Key Ceremony on-device:**
   - Open the PAN Tactical app
   - Navigate to the Key Ceremony screen
   - Tap **INITIALIZE NODE**
   - The app will: generate TPM key → fetch Play Integrity token → register with backend
   - On success, the agent is bound to the network and can receive missions

3. **Verify ceremony completion:**
```bash
redis-cli EXISTS pan:agent:{agent_firebase_uid}:pubkey
# Returns 1 if ceremony completed successfully
```

### Vanguard 50 Status
- All 50 pilot agents have been provisioned via `provision_vanguard_50.py` ✅
- Key Ceremony must be completed individually on each agent's physical device
- Checkr background verification must pass before Key Ceremony is unlocked

---

## 9. Running the Stack

### Full Local Development Stack

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend API
cd apps/backend/src
uvicorn main:app --reload

# Terminal 3: All background workers
cd apps/backend/src
python run_workers.py
```

### Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "online", "active_connectors": [...], "integrity_mode": "STRICT_HMAC_WITH_REPLAY_PROTECTION"}
```

### Inject a Test Mission (Dev Menu)

In the mobile app, long-press the PAN logo in the top-left corner of the dashboard to open the Dev Menu (`BuildConfig.DEBUG` only — not present in production builds). Select a test location to inject a V2X distress signal into the dispatch queue.

### Firebase RTDB Rules

The Firebase RTDB instance (`pan-tactical-default-rtdb`) must be locked to deny-all. No application code writes directly to RTDB — all agent state routes through the Python backend → Redis. Verify this is set before any pilot deployment:

```json
{
  "rules": {
    ".read": false,
    ".write": false
  }
}
```

---

## 10. OSM Color Taxonomy

PAN uses the Operational Status Matrix (OSM) color taxonomy for task classification, pricing, and dashboard visualization. Fleet partners should pass `osm_color` in their distress signal payloads.

| Color | Category | Tier | Base Bounty |
|---|---|---|---|
| 🔴 RED | Biological / Foreign Object | 3 (Critical) | $65.00 |
| 🟣 PURPLE | Defleeting | 3 (Critical) | $65.00 |
| 🟡 YELLOW | Tech / Sensor Fault | 2 (Elevated) | $45.00 |
| 🟠 ORANGE | Calibrations | 2 (Elevated) | $45.00 |
| 🟢 GREEN | Power Down & Rest (PDR) | 1 (Standard) | $14.00 |
| 🔵 BLUE | Validation | 1 (Standard) | $14.00 |
| ⬜ WHITE | Demo Vehicle | 1 (Standard) | $14.00 |

Bounties are dynamically adjusted by the Surge Pricing Engine when Agent Utilization Ratio (AUR) exceeds 75%. Maximum surge is 3.0x. Agents always receive 90% of the final settled bounty.

### Distress Signal Example

```json
POST /api/v1/v2x/distress
{
  "vin": "WAYMO-404",
  "fault_code": "UDS_SENSOR_OCCLUSION_LIDAR_FL",
  "latitude": 33.420,
  "longitude": -111.840,
  "bounty_usd": 45.00,
  "osm_color": "YELLOW"
}
```

---

## 11. Project Copperfield — Vanguard Field System

Project Copperfield is PAN's proprietary intelligent wearable platform. Four components form a unified system. Each is functional independently but achieves maximum capability when all four are deployed together.

### Component Overview

| Component | Codename | Spec | BLE Service UUID |
|---|---|---|---|
| Intelligent trucker hat | HapHat v2.3 | `project_copperfield_haphat_v2_3.html` | `A0000001-…` |
| Hi-vis safety vest | PANOPLY v1.1 | `VFV1_Vanguard_Field_Vest_Spec_v1_1.html` | `B0000001-…` |
| Base layer polo | Aegis Polo VFP-1 | `VFP1_Aegis_Polo_Spec_v1_1.html` | `D0000001-…` |
| Field gloves | Gauntlets VFG-1 v1.1 | `VFG1_Vanguard_Gauntlets_Spec_v1_1.html` | `C0000001-…` |

All four components use the **nRF52840** BLE module and share the same firmware update infrastructure (Nordic DFU over BLE). The HapHat additionally uses an **ESP32-C3** as the primary controller for motor PWM and LED control.

### Haptic Ownership — The Delineation Protocol

Three independent haptic systems exist in the full field system. They must never communicate the same information redundantly. The authoritative ownership table is in the vest spec Section 13, but the core principle is:

- **Hat** — owns mission state and identity events (conscious attention)
- **Spine strip** (vest) — owns navigation and spatial awareness (ambient, no attention required)
- **Gloves** — own gesture confirmation and tool interaction feedback
- **Polo wrist motor** — owns the Quiet Feature only (opt-in, ON_SCENE transition, once per mission)

All four fire simultaneously **only** for Zone 1 critical emergencies and multi-agent gesture bonuses.

### BLE Command Data Classes (Kotlin)

```kotlin
// Unified command routing — hat and vest spine strip share this interface
data class VanguardHapticCommand(
    val targetDevice: HapticDevice,     // HAT, SPINE, or BOTH
    val motorId: MotorId,
    // Kotlin Byte is signed — firmware treats as unsigned uint8_t (0–255)
    // Use .toByte() for values > 127
    val intensityPwm: Byte = 0x00,
    val ledMode: LedMode? = null,       // null for spine (no LEDs)
    val ledColor: LedColor? = null,
    // Kotlin Short is signed — firmware treats as unsigned uint16_t (0–65535ms)
    // Use .toShort() for values > 32767
    val durationMs: Short = 0,
    val partnerAgentId: String? = null  // For simultaneous multi-agent dispatch
)

enum class HapticDevice { HAT, SPINE, BOTH }

// v2.3 addition — warmer tone for Miyagi biometric calming confirmation
enum class LedColor(val byte: Byte) {
    OFF(0x00), WHITE(0x01), CYAN(0x02), GREEN(0x03),
    RED(0x04), AMBER(0x05), ORANGE(0x06),
    YELLOW(0x07),     // ON_SCENE
    PURPLE(0x08),     // MISSION_INCOMING
    WARM_AMBER(0x09)  // Miyagi calming confirmed by polo biometric
}
```

### Composite Threat Response

The vest and polo together enable an escalation that neither can produce alone:

```
RATS Zone 2 detected (vest radar)
    +
Polo biometric stress index > 0.7 (HR + GSR spike)
    ↓
System recognizes: agent already knows.
Zone 2 warning is redundant.
Skip directly to Zone 1 maximum response:
  → Hat: RED strobe, ALL motors max
  → Vest spine: ALL motors max continuous
  → Both gloves: max buzz
  → LED panel: full RED strobe
  → Phone: max volume alarm, overrides DND
```

### RATS — Rear Awareness & Threat Detection System

The vest's three-sensor stack (mmWave radar + wide-angle camera + ultrasonic) defines three threat zones. The sensitivity profile is auto-selected based on OSM road speed data at the mission GPS location:

| Context | Zone 3 Threshold | Zone 1 Threshold |
|---|---|---|
| `HIGH_SPEED_ROADWAY` (≥45mph) | 40m | 5m |
| `ARTERIAL_ROAD` (default) | 30m | 5m |
| `PARKING_STRUCTURE` | Pedestrian mode only | 5m |
| `RESIDENTIAL` (≤25mph) | 10m | 5m |

All RATS events are logged to the SB 1417 report with zone, object class, approach velocity, detection distance, and whether the agent repositioned (inferred from GPS delta).

#### ⚠️ Electronics Bay Thermal Budget — Hardware Engineering Note

> **The electronics bay requires active thermal design. A sealed polymer shell will fail in Mesa summer conditions.**

The vest electronics bay houses the mmWave radar (TI IWR6843AOP), Edge TPU (Coral), BLE module, and LED panel driver — with a combined peak draw of ~14W. In direct Arizona sunlight, a sealed IP54 polymer enclosure will reach surface temperatures well above safe operating range for the LiPo battery and radar module. Worse, the PCM panels directly adjacent to the bay may absorb electronics heat rather than body heat — defeating their primary purpose.

**Required design changes before prototype:**

- **Housing material:** The electronics bay enclosure must be **aluminum or thermally conductive composite** — acting as a passive heatsink, not an insulator. Sealed polymer is not acceptable for the Arizona deployment environment.
- **Radar placement:** The mmWave radar module should be positioned on the **exterior face** of the bay with a thermal interface pad directly to the shell. This is the highest heat-generating component and must have a direct conduction path to ambient air.
- **Thermal simulation required:** Run a thermal simulation at 40°C ambient with 14W peak load before committing to a prototype enclosure geometry. The goal is &lt;60°C case temperature at sustained 5W average load (realistic operational draw).
- **Design to average, not peak:** The 14W peak figure assumes all LEDs at full white simultaneously with radar at maximum sensitivity. Real operational load averages ~5W. Thermal design should target continuous 5W with adequate headroom for peak bursts, not sustained 14W.
- **Solar strip benefit:** The shoulder solar strips convert incident sunlight to electricity rather than heat — they provide a modest thermal benefit to the upper bay area in addition to their power generation function.

### Dual Air Quality — Four Scenario System

The vest biohazard sensor (ambient, shoulder height) and polo air quality sensor (breathing zone, back lower panel) together distinguish four scenarios:

| Vest Sensor | Polo Sensor | Scenario | Response |
|---|---|---|---|
| BREACH | CLEAR | Ambient hazard, agent not yet exposed | AMBER warning, advise upwind approach |
| CLEAR | BREACH | Personal exposure not caught at ambient | RED flash, "REPOSITION IMMEDIATELY" |
| BREACH | BREACH | Confirmed full exposure | Full emergency, fleet escalation |
| CLEAR | CLEAR | Environment clean | Log "CONFIRMED CLEAR" to SB 1417 |

### Gauntlet Gesture System

The Gauntlets VFG-1 use a 32kHz IMU + palm capacitive sensor + NFC to detect gestures. All gesture processing runs on the nRF52840 — not on the phone — for sub-80ms response latency.

**Anti-gaming safeguards:**
- NFC bilateral read confirms two registered gloves made physical contact (range: 4cm max)
- Both agents must be `ON_SCENE` on the same `incident_id`
- Atomic Redis `SET NX` prevents duplicate bonus claims per incident
- Same agent pair capped at 3 multi-agent bonuses per 8-hour shift

**Key gesture events:**

```kotlin
data class GauntletGestureEvent(
    val gloveId: String,
    val agentId: String,
    val gestureType: GestureType,
    val confidence: Float,            // threshold: 0.85
    val partnerGloveId: String? = null,
    val timestamp: Long,
    val missionId: String? = null,
    val toolNfcId: String? = null     // tool in hand at time of gesture
)
```

The `toolNfcId` field enables the vest's conductivity wrist cuff to adapt its hazard threshold to the specific tool being held. Jump starters use maximum sensitivity. Cleaning supplies use monitoring-only mode.

#### ⚠️ Multi-Agent Gesture Sync Architecture — Hardware Engineering Note

> **Do not rely on PAN Command as the fan-out relay for time-critical gesture choreography.**

BLE in a noisy RF environment (street intersection, AV wireless stack, cellular, competing 2.4GHz devices) cannot guarantee the &lt;100ms synchronized response window required for the multi-agent hat flash and spine shockwave to feel simultaneous. Routing the choreography signal through PAN Command introduces unpredictable latency that will break the shared physical moment at the core of the gesture culture layer.

**Required architecture:** Partner gloves must negotiate a **direct peer-to-peer radio link** during pairing — using the nRF52840's proprietary 2.4GHz Gazell protocol or equivalent — and fire the choreography trigger directly glove-to-glove, bypassing the phone entirely for the animation sequence.

```
CORRECT architecture:
  Glove A detects gesture ──▶ Direct 2.4GHz link ──▶ Glove B confirms
         │                                                    │
         └──────────── Synchronized haptic trigger ──────────┘
                  (sub-10ms, phone not in path)
         │
         ▼ async (non-blocking)
  PAN Command API ──▶ Redis wallet credit + SB 1417 log

INCORRECT architecture:
  Glove A detects gesture ──▶ PAN Command ──▶ BLE fan-out ──▶ Glove B
                                    (unpredictable latency, packet loss risk)
```

The wallet credit and compliance logging can and should be asynchronous through PAN Command — they don't need to be instantaneous. The magic does. This design also makes the gesture system resilient at scenes with marginal LTE coverage.

#### ⚠️ Snap Gesture — TFLite Classifier Required

The IMU is located at the wrist cuff, not the fingers. A simple peak threshold on the acceleration spike will produce unacceptable false positive rates — car door slams, tool drops, and wrench impacts produce similar wrist deceleration signatures to a finger snap.

The snap detection pipeline requires a **trained TFLite model on the nRF52840**, not just a high-pass filter and threshold check. The three-factor check (acceleration spike &gt;8G + duration &lt;10ms + friction signature from palm capacitive sensor) provides meaningful discrimination, but the classifier must be trained on real-world negative examples — field tool use, driving vibration, physical exertion — not just synthetic snap data.

The 90-second onboarding calibration session serves double duty: it establishes the agent's personal baseline and generates labeled positive examples. False positive reports from agents in the field should be treated as training data. The production classifier that ships in firmware v1.0 will be underfitted — budget for at least two classifier update OTA cycles during the Vanguard 50 pilot before the gesture feel is right.

### OTA Firmware Updates

All four Copperfield components support BLE OTA via Nordic DFU:

- **Feature updates** — Agent receives PAN Command push notification: *"Something new is in your Gauntlets. Go find it."* Agent-prompted install.
- **Security patches** — Silent background install when device is charging and BLE-connected. No agent notification unless the patch changes observable behavior.
- **Critical security** — Mandatory install. Hardware will not accept missions until update is applied.

All firmware packages are signed with the PAN private key. Unsigned packages are rejected by the device firmware before installation.

---

## 12. BLE / Hardware Integration

### BLE GATT Service UUIDs

| Component | Service UUID |
|---|---|
| HapHat v2.3 | `A0000001-0000-1000-8000-00805F9B34FB` |
| PANOPLY Vest v1.1 | `B0000001-0000-1000-8000-00805F9B34FB` |
| Gauntlets VFG-1 | `C0000001-0000-1000-8000-00805F9B34FB` |
| Aegis Polo VFP-1 | `D0000001-0000-1000-8000-00805F9B34FB` |
| AV OOB Service | `A0000001-0000-1000-8000-00805F9B34FB` |
| AV UWB MAC Char | `A0000002-0000-1000-8000-00805F9B34FB` |
| AV Session Key Char | `A0000003-0000-1000-8000-00805F9B34FB` |

### `BleHapHatService` Interface

The `BleHapHatService` interface defines the GATT payload contract for the HapHat firmware. The current implementation (`rememberBleHapHatService()`) returns a **mock** for UI development. The real `AndroidBleHapHatService` implementation is a pre-go-live blocker — see Section 16.

```kotlin
interface BleHapHatService {
    suspend fun connect(): Boolean
    suspend fun sendCommand(command: HapHatCommand): Boolean
    fun close()
}
```

### `AndroidBleClient` — OOB Handshake

`AndroidBleClient` implements `BleHomingClient` and performs the BLE Out-of-Band handshake to retrieve UWB session credentials from the stranded AV:

1. BLE scan filtered to `PAN_AV_SERVICE_UUID`
2. GATT connect on discovery → discover services
3. Read `UWB_MAC_CHAR_UUID` → read `SESSION_KEY_CHAR_UUID` (chained)
4. Complete `OobHandshakeResult` with MAC + session key
5. 15-second timeout safeguard. Null session key characteristic fires explicit error — no silent hang.

Key implementation notes:
- `gattConnection` is `@Volatile` — written from BLE callback thread, read from coroutine context
- `scanCallback` is nulled after `stopScanning()` to prevent memory leak
- Uses deprecated `onCharacteristicRead` API intentionally for minSdk 26 compatibility

### `PrivacyFilter` — SB 1417 Compliance

All photographic evidence is sanitized on-device before upload:

```kotlin
// STRICT CONTRACT: This function takes ownership of originalBitmap.
// originalBitmap is unconditionally recycled before the function returns.
// Never use originalBitmap after calling sanitizeImage().
suspend fun sanitizeImage(originalBitmap: Bitmap): Bitmap
```

- Concurrent face detection + text recognition (`coroutineScope` + `async`)
- ARGB_8888 normalization prevents PII ghosting through redaction paint
- Bounds clamping on all expanded rects (negative inset intentionally expands bounding box)
- `Paint` instantiated inside function — thread-safe for concurrent coroutine calls
- Fail-safe: ML crash returns fully black bitmap, never unredacted original
- OOM fallback: 1×1 black pixel if even the blackout bitmap allocation fails

---

## 13. SB 1417 Compliance Pipeline

Every mission generates a sealed, immutable Optical Health Report. The pipeline runs automatically — no agent action required at any stage.

### Data Sources (Full System)

| Source | Component | Data Logged |
|---|---|---|
| Photo evidence | Phone camera | Redacted JPEG frames (720p/3fps), frame count, redaction count |
| Hardware attestation | StrongBox TPM | Cryptographic token binding report to specific device |
| Voice transcripts | Aegis Polo — Communicator Pin | Full transcript with `[COMPLIANCE]` flagged entries, GPS, timestamp |
| RATS threat events | PANOPLY Vest — radar | Zone, object class, approach velocity, detection distance, agent repositioned |
| Pre-approach air quality | PANOPLY Vest — biohazard sensor | VOC, CO, H2S, PM2.5, PM10, temp, humidity at ON_SCENE transition |
| Personal breathing zone | Aegis Polo — air quality sensor | Same metrics as vest sensor, breathing zone height |
| Biometric safety events | Aegis Polo — biometric patch | HR, skin temp, SpO2, stress index at any threshold crossing |
| Conductivity hazard | Aegis Polo — wrist cuffs | Tool in hand, affected hand, timestamp, alert fired |
| Sensor override | PANOPLY Vest — shoulder button | Timestamp, agent ID, override duration (cannot be hidden) |
| Approaching vehicles | PANOPLY Vest — plate camera (T3) | Plate hash (redacted), approach vector, distance, timestamp |
| Duress activation | PANOPLY Vest — duress button | GPS pin, timestamp, battery level, video buffer hash (T3) |
| Agent gesture log | Gauntlets | Gesture type, confidence, partner agent ID, tool in hand |
| Impact event | PANOPLY Vest — accelerometer (T3) | G-force vector, welfare response time, outcome |

### Report Structure

```python
{
  "mission_id": "tsk_a3f8c291b04d",
  "agent_id": "VNG-A3F8C2-ALPHA",
  "vest_tier": 3,
  "hardware_attestation_token": "<strongbox_jwt>",
  "photo_evidence": {
    "frame_count": 62,
    "redacted_frame_count": 62,
    "upload_urls": ["..."]
  },
  "voice_logs": [...],         # Communicator Pin transcripts
  "threat_events": [...],      # RATS detections
  "air_quality_logs": [...],   # Vest + polo dual sensor
  "biometric_events": [...],   # Polo patch threshold crossings
  "conductivity_events": [...],
  "approaching_vehicle_log": [...],
  "duress_events": [...],
  "gesture_log": [...]
}
```

### 720p/3fps Evidence Pipeline

The camera pipeline is intentionally rate-limited to 3fps. This is a deliberate security and stability decision — not a limitation:

- **333ms per frame** — sufficient for concurrent face + text ML detection without dropping frames
- **Prevents StrongBox lag** — sustained 30fps CPU load causes thermal throttling that degrades the Secure Element's JWT signing performance
- **Bandwidth-safe** — 40–80KB per redacted JPEG at 70% quality fits within degraded 4G LTE coverage in Mesa field conditions
- **Battery-safe** — allows agent to remain ON_SCENE for full 20-minute SLA without device dying

---

## 14. Proxy-Alpha Companion Mode

See Section 7 for setup. Additional implementation notes:

### Wake Word Detection

Wake word detection runs **on-device** on the Communicator Pin's nRF52840 — not on the phone. Only after wake word confirmation does audio stream to PAN Command for processing. The default wake word is **"Hey Dispatch"** (two words required — single-word triggers are rejected). Configurable in app settings to: "Hey Commander", "Hey Captain", or "Hey Vanguard".

False positive prevention:
- Both words must be spoken within 800ms
- Speaker separation model weights toward agent's enrolled voice profile (calibrated during onboarding)
- "Proxy Agent Network" does not trigger — the wake word is "Hey Dispatch", not "Proxy"

### Transcript Privacy

- **Agent sees:** Full interaction history in PAN Command app
- **Fleet manager sees:** Interaction count, total duration, compliance topics covered. Never the full transcript.
- **SB 1417 report gets:** Only `[COMPLIANCE]`-flagged exchanges appended automatically

### Medical Response Integration

When a NARCAN_CERTIFIED agent administers Narcan and reports it via Companion Mode:

```
Agent: "Hey Dispatch, Narcan administered, single dose, patient responsive."
→ Proxy-Alpha logs [MEDICAL_RESPONSE] entry with GPS + timestamp
→ Asks: "Should I contact emergency services?"
→ Agent responds yes/no
→ If yes: 911 called via PAN Command with agent GPS pre-populated
→ AZ Good Samaritan documentation auto-generated
→ Fleet manager notified
→ Pocket restocking request created
```

All NARCAN_CERTIFIED agents carry the certification flag in their Redis profile. Fleet managers can filter dispatch by this flag.

---

## 15. Checkr Background Verification

All Vanguard Agents are background-checked via Checkr before the Key Ceremony is unlocked.

### Integration Point

Background verification is initiated in `onboarding_api.py` during `process_enlistment()`, after the agent's Redis profile is written.

```python
# Enlistment flow:
# 1. Write agent profile to Redis
# 2. Create Checkr candidate
# 3. Initiate Checkr report (driver_pro package, ~$30/check)
# 4. Webhook confirms completion → agent unlocked for Key Ceremony

async def create_checkr_candidate(agent_data: dict) -> str:
    """Creates a Checkr candidate and returns candidate_id."""
    ...

async def initiate_checkr_report(candidate_id: str) -> str:
    """Initiates driver_pro background check, returns report_id."""
    ...

# Webhook endpoint: POST /checkr/webhook
# Validates CHECKR_WEBHOOK_SECRET HMAC signature
# On report clear: sets agent:checkr_status = APPROVED in Redis
```

### Environment Variables Required

```bash
CHECKR_API_KEY=your_checkr_api_key
CHECKR_WEBHOOK_SECRET=your_checkr_webhook_secret
```

### Status

Checkr integration is **in progress** — API design is complete, implementation is pending. This is a pre-go-live requirement. Agents cannot complete the Key Ceremony without Checkr approval.

---

## 16. Open Roadmap

### Pre-Go-Live Blockers

| # | Item | Status |
|---|---|---|
| 1 | `AndroidBleHapHatService` — real BLE implementation (currently mock) | 🔧 In progress |
| 2 | Phase 6 OSRM route wiring in `AgentDashboardScreen` (`getTacticalRoute()` exists in `PanApiClient`, TODO comment in place) | 🔧 In progress |
| 3 | Checkr integration in `onboarding_api.py` | 🔧 In progress |
| 4 | `net_payout` field verification — confirm backend calculates from Redis, not client-submitted value | 📋 Verify |
| 5 | Callsign backend persistence (currently `rememberSaveable` only, not written to backend) | 📋 Pending |
| 6 | imgbb → S3/GCP migration (required before fleet partner sign-off) | 📋 Pre-fleet |

### Phase 4: Platform Scale & Public Hardening

| # | Item | Status |
|---|---|---|
| 1 | Semantic Prompt Injection Defense (cosine similarity firewall) | ✅ Shipped |
| 2 | Async Data Wiring + Redis DI for Proxy-Alpha tools | ✅ Shipped |
| 3 | `cognitive_vault` containerization via `pyproject.toml` | ✅ Shipped |
| 4 | OSRM dedicated routing server migration | ✅ Shipped |
| 5 | MCP Platform Layer for external fleet partners | ✅ Shipped |
| 6 | Firebase RTDB locked to deny-all (no direct client writes) | ✅ Shipped |
| 7 | `PanApiClient` agent status routing to Python backend (was writing to RTDB) | ✅ Shipped |
| 8 | `PrivacyFilter` thread safety + bounds clamping | ✅ Shipped |
| 9 | `AndroidBleClient` `@Volatile` + null session key hang fix | ✅ Shipped |
| 10 | JWT mutex in `PanApiClient` (StrongBox thread safety) | ✅ Shipped |
| 11 | Ops Hub live dashboard (Leaflet + WebSocket) | Open |
| 12 | iOS client completion | Planned |
| 13 | Aerial dispatch integration (drone visual verification) | Theoretical |

### Hardware Roadmap

| Component | Status |
|---|---|
| HapHat v2.3 spec | ✅ Complete |
| PANOPLY Vest v1.1 spec | ✅ Complete |
| Aegis Polo VFP-1 v1.1 spec | ✅ Complete |
| Gauntlets VFG-1 v1.1 spec | ✅ Complete |
| HapHat prototype (hand-wired V1) | ✅ Built |
| `AndroidBleHapHatService` real implementation | 🔧 Blocker |
| PANOPLY Vest prototype | 📐 Pending funding |
| Aegis Polo prototype | 📐 Pending funding |
| Gauntlets prototype | 📐 Pending funding |

### Open Tech Debt

| File | Item |
|---|---|
| `PanWalletClient.kt` + `PanApiClient.kt` | `@file:Suppress` — pending clean Gradle sync |
| `onboarding_api.py` | Confirm `ANDROID_PACKAGE_NAME` env var set in production |
| `logistics_webhook_api.py` | Confirm `HARDWARE_REGISTRY_URL` env var set before registry wiring |
| `escrow_oracle.py` | RFC 8037 test vector in sim block — never use in production |
| `WalletAndProfileScreen.kt` | Callsign/firstName `rememberSaveable` only — not persisted to backend |
| `BleHapHatService.kt` | `TODO: Before Pilot, create AndroidBleHapHatService and toggle via BuildConfig.DEBUG` |
| `UwbClient.kt` | WebRTC + VoIP TODOs — future AV diagnostics and passenger comms |
| All evidence uploads | imgbb → AWS S3 or GCP Cloud Storage before fleet partner sign-off |

---

## 17. Troubleshooting

### Redis

**`redis.exceptions.ConnectionError: Error connecting to localhost:6379`**
Redis isn't running. Start it with `redis-server` before launching any backend process.

**`WRONGTYPE Operation against a key holding the wrong kind of value`**
A Redis key has an unexpected type — usually caused by leftover data from a previous dev session. Flush the dev database with `redis-cli FLUSHDB` (never run this in production).

**Agent is online but never receives missions**
Verify `updateAgentStatus()` in `PanApiClient` is posting to `$PAN_API_BASE_URL/api/v1/agent/status` — not to `FIREBASE_RTDB_URL`. The matching engine's `GEORADIUS` query reads from Redis. Agents writing status to RTDB are invisible to dispatch.

---

### LND / Lightning Engine

**`LND Connection Failed: [Errno 111] Connection refused`**
Your LND node is unreachable. Verify `LND_GRPC_HOST` and `LND_GRPC_PORT` in `.env` and confirm the node is running.

**`FATAL NETWORK MISMATCH: Expected mainnet, but node is on [testnet]`**
The `LND_NETWORK` env var doesn't match your node's actual chain. Set `LND_NETWORK=testnet` for development or point to your mainnet node.

**`[Errno 2] No such file or directory: '/path/to/admin.macaroon'`**
The macaroon path in `LND_MACAROON_PATH` is wrong. On a standard LND install, macaroons live at `~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon`.

---

### Play Integrity / Google ADC

**`google.auth.exceptions.DefaultCredentialsError`**
GCP Application Default Credentials aren't configured on the backend host. Run:
```bash
gcloud auth application-default login
```
In production containers, attach a GCP service account with the Play Integrity API role instead.

**`App binary not recognized by Play Protect`**
The app hasn't been published to Google Play yet, or the `ANDROID_PACKAGE_NAME` doesn't match the Play Console app. For development, this check is bypassed when ADC is not configured (non-production environment only).

---

### PyO3 / Rust Escrow Contracts

**`ModuleNotFoundError: No module named 'hodl_escrow'`**
The Rust bindings haven't been compiled yet. Run `maturin develop` from inside `apps/backend/src/core/economics/` with your virtual environment active.

**`maturin: error: Python interpreter not found`**
Your virtual environment isn't activated. Run `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows) before running `maturin develop`.

---

### Mobile / Android Build

**`Build failed: Missing required local.properties key`**
A required secret is missing from `local.properties`. Check the full list in Section 4 and ensure every key is present. The build will fail fast with the exact missing key name.

**`INVISIBLE_REFERENCE` / `INVISIBLE_MEMBER` Kotlin compiler warning**
Known suppressed warning in `PanWalletClient.kt` and `PanApiClient.kt` related to BuildConfig visibility. Does not affect functionality. Clean Gradle sync after the `visibility(PUBLIC)` fix should resolve it.

**`google-services.json not found`**
The Firebase config file is missing. Download it from your Firebase project console and place it in `composeApp/`.

**Agent status updates not reflected in dispatch**
See Redis troubleshooting above — confirm `PanApiClient.updateAgentStatus()` is routing to the Python backend, not Firebase RTDB.

---

### BLE / Hardware

**HapHat connects but commands have no effect**
Confirm the ESP32-C3 firmware version matches the GATT characteristic UUIDs in `BleHapHatService.kt`. The `durationMs` field is a signed Kotlin `Short` but the firmware expects an unsigned `uint16_t` — values above 32,767ms must be cast with `.toShort()`. Same applies to `intensityPwm` — values above 127 must be cast with `.toByte()`.

**BLE OOB handshake times out after 15 seconds**
The AV's GATT server is not advertising `PAN_AV_SERVICE_UUID` or the `SESSION_KEY_CHAR_UUID` characteristic is not present on the service. The `AndroidBleClient` now fires an explicit error on null session key characteristic rather than hanging silently — check logcat for "Session key characteristic not found on AV".

**RATS sensor not detecting approaches**
Confirm the mmWave radar module (TI IWR6843AOP) is powered and the vest electronics bay BLE module is connected to PAN Command. RATS sensitivity profile is auto-selected from mission GPS — verify the OSRM_BASE_URL is reachable and returning valid road speed data.

**Gauntlet gesture confidence below 0.85 threshold**
Agent calibration may be stale. In PAN Command → Settings → Gauntlets → Recalibrate. All gesture thresholds are personal baselines — factory defaults are intentionally conservative.

**Multi-agent gesture bonus fires on one agent but not both / hats flash out of sync**
The choreography signal is routing through PAN Command rather than direct glove-to-glove radio. In a noisy RF environment BLE fan-out through the phone will produce visible latency between the two hat responses. Verify the partner gloves have negotiated a direct peer-to-peer 2.4GHz link during pairing — check firmware logs for `GAZELL_PEER_LINK_ESTABLISHED`. If the link is not established, the gloves will fall back to BLE-via-PAN-Command which cannot guarantee the synchronization window. Re-pair the gloves in close proximity (&lt;1m) and retry.

**Snap gesture triggering hat light during tool use / false positive rate too high**
The snap classifier on the nRF52840 is underfitted — this is expected during early Vanguard 50 pilot. Three actions: (1) agent reports false positives via PAN Command → Gauntlets → Report False Positive — each report is a labeled negative training example; (2) lower the snap intensity threshold temporarily via PAN Command → Settings → Gauntlets → Snap Sensitivity; (3) verify the palm capacitive contact sensor is functioning — a snap without the friction signature should not cross the 0.85 confidence threshold. If the sensor is damaged or delaminated, all snap events will rely on the acceleration signature alone, dramatically increasing false positive rate.

---

### Key Ceremony

**`Agent identity missing. Please log in.`**
The agent is not authenticated via Firebase. Ensure Firebase Auth is initialized and the agent has signed in before tapping INITIALIZE NODE.

**`Hardware key already registered for this identity.`** (HTTP 409)
The Key Ceremony has already been completed for this agent on this or another device. If the agent lost their device, use the `/ops/hardware-reset` workflow — do not attempt to re-run the ceremony directly.

**`Device failed hardware integrity checks`** (HTTP 401)
The device is rooted, running a custom ROM, or is an emulator. Play Integrity requires an unmodified device with certified bootloader.

**Agent provisioned but Key Ceremony screen is locked**
Checkr background verification has not completed or was not approved. Check `redis-cli HGET pan:agent:{uid} checkr_status` — must be `APPROVED` before Key Ceremony is unlocked.

---

### Cognitive Vault

**`Missing required COGNITIVE_ENCRYPTION_KEY`**
The `COGNITIVE_ENCRYPTION_KEY` environment variable is not set. Generate a key with:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Then add it to your `.env`. This key must be static — do not regenerate it once agent memories have been stored.

**`[CORRUPTED MEMORY] Decryption failed. Invalid key or tampered data.`**
The encryption key has changed since the memory was stored, or the stored data was tampered with. If this happens in development, clear the memory store and restart with the correct key.

**Companion Mode transcripts not appearing in SB 1417 report**
Confirm the Communicator Pin wake word was detected (check pin LED — CYAN pulse indicates active session). Verify `COMPLIANCE`-flagged exchanges contain a recognized fault code, safety term, or regulatory reference. Casual interactions are logged but not auto-appended to the compliance report.

---

## 18. Security Notes

- **Never commit `local.properties`** — it contains all API keys and secrets
- **Never commit `google-services.json`** or `GoogleService-Info.plist`
- **The `COGNITIVE_ENCRYPTION_KEY` must be static** — rotating it invalidates all stored agent memories
- **Hardware Key Ceremony is irreversible** — use `/ops/hardware-reset` workflow if an agent loses their device
- **Play Integrity tokens are verified server-side** via Google ADC — ensure GCP credentials are configured on the backend host before go-live. (Note: Use `gcloud auth application-default login` for local development only. Production environments must use a dedicated JSON Service Account key.)
- **All V2X fleet signals require Ed25519 signatures** — register fleet public keys via `PUBKEY_*` environment variables before a fleet partner goes live
- **Firebase RTDB must be locked to deny-all** — no application code should write directly to RTDB. Verify rules before pilot deployment.
- **Dev menu is `BuildConfig.DEBUG` only** — confirm `IS_DEBUG_MODE = BuildConfig.DEBUG` in production builds. The dev menu injects live distress signals into the dispatch queue.
- **imgbb API key** — evidence uploads are pilot-only via imgbb. Rotate this key if compromised. Migrate to S3/GCP before fleet partner goes live.
- **Checkr webhook signature** — all Checkr webhook payloads must be validated against `CHECKR_WEBHOOK_SECRET` before processing. Never trust an unsigned Checkr callback.
- **Gauntlet firmware packages** — all OTA packages must be signed with the PAN private key. The device firmware rejects unsigned packages before installation. Never distribute unsigned firmware.

---

## License

MIT — see `LICENSE` for details.

---

*Built with ❤️ for the Vanguard 50 — Veterans providing meaningful work in the autonomous era.*
