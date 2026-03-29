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
11. [Open Roadmap](#11-open-roadmap)
12. [Troubleshooting](#12-troubleshooting)
13. [Security Notes](#security-notes)

---

## 1. Project Overview

PAN Tactical dispatches verified Vanguard Agents to resolve physical AV edge cases that autonomous vehicles cannot handle alone — sensor occlusion, door faults, spill remediation, and first-responder liaison. Agents earn real bounty payouts settled via Lightning Network L402 micropayments.

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
           │ mission:active:{task_id}
           ▼
┌─────────────────────┐
│  Mobile App         │  Vanguard Agent receives mission
│  (KMP Android/iOS)  │  BLE OOB → UWB micro-homing → Evidence
└──────────┬──────────┘
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

### Mobile
- Android Studio Hedgehog or later
- Android SDK API 26+ (required for UWB)
- Kotlin 2.1.0
- Firebase project with Authentication and RTDB enabled
- Google Play Console app linked to GCP project

### Rust (Escrow Smart Contracts)
- Rust 1.70+
- PyO3 build toolchain

---

## 4. Environment Setup

### `local.properties` (Mobile — never commit this file)

```properties
# Google Maps
MAPS_API_KEY=your_android_maps_key
IOS_MAPS_API_KEY=your_ios_maps_key

# ImgBB (Evidence Upload — SB 1417 Compliance)
IMGBB_API_KEY=your_imgbb_key

# Firebase
FIREBASE_RTDB_URL=https://your-project-default-rtdb.firebaseio.com

# PAN Backend
PAN_API_BASE_URL=https://your-backend-url.com
AGENT_DEV_TOKEN=your_dev_token

# Google Play Integrity (GCP Project Number — from Play Console)
PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER=123456789012

# OSRM Routing Server (self-hosted — see Phase 4 roadmap)
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

# Hardware Registry (Container-safe)
HARDWARE_REGISTRY_URL=http://hardware-registry:8010

# Cognitive Vault (Memory Encryption)
# Generate with: python -m cognitive_vault.memory_cipher
COGNITIVE_ENCRYPTION_KEY=your_fernet_key_here

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
# In separate terminals:

# SLA Watchdog (Two-phase ACK enforcement)
python watchdog_worker.py

# Matching Engine (Geospatial dispatch)
python -c "import asyncio; from matching_engine import run_matching_engine; import redis.asyncio as r; asyncio.run(run_matching_engine(r.Redis()))"

# Surge Pricing Daemon
python -c "import asyncio; from core.economics.surge_pricing_engine import SurgePricingEngine; import redis.asyncio as r; asyncio.run(SurgePricingEngine(r.Redis()).run_loop())"
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

---

## 8. Key Ceremony

Every Vanguard Agent must complete the Key Ceremony before they can receive missions. This binds their Firebase identity to their device's hardware TPM using Google Play Integrity attestation.

### Prerequisites
- Agent device must have Google Play Services
- Device must not be rooted or an emulator
- Agent must be logged in via Firebase Authentication
- `PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER` must be set in `local.properties`

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

---

## 9. Running the Stack

### Full Local Development Stack

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Backend API
cd apps/backend/src
uvicorn main:app --reload

# Terminal 3: SLA Watchdog
python watchdog_worker.py

# Terminal 4: Matching Engine
python -c "import asyncio; from matching_engine import run_matching_engine; import redis.asyncio as r; asyncio.run(run_matching_engine(r.Redis()))"

# Terminal 5: Surge Pricing Daemon
python -c "import asyncio; from core.economics.surge_pricing_engine import SurgePricingEngine; import redis.asyncio as r; asyncio.run(SurgePricingEngine(r.Redis()).run_loop())"
```

> 💡 **Tip:** The inline `python -c` commands above are the authoritative way to start the workers until a `run_workers.py` convenience wrapper is built (tracked as a Phase 4 ops task). If you create one locally, it should import and `asyncio.gather()` the matching engine and surge pricing loops together.

### Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "online", "active_connectors": [...], "integrity_mode": "STRICT_HMAC_WITH_REPLAY_PROTECTION"}
```

### Inject a Test Mission (Dev Menu)

In the mobile app, long-press the PAN logo in the top-left corner of the dashboard to open the Dev Menu. Select a test location to inject a V2X distress signal into the dispatch queue.

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

## 11. Open Roadmap

### Pre-Go-Live (All blockers resolved ✅)
All three pre-Memorial Day blockers are closed.

### Phase 4: Platform Scale & Public Hardening

| # | Item | Status |
|---|---|---|
| 1 | Semantic Prompt Injection Defense (cosine similarity firewall) | ✅ Shipped |
| 2 | Async Data Wiring + Redis DI for Proxy-Alpha tools | ✅ Shipped |
| 3 | `cognitive_vault` containerization via `pyproject.toml` | ✅ Shipped |
| 4 | OSRM dedicated routing server migration | Open |
| 5 | MCP Platform Layer for external fleet partners | Open |
| 6 | Real BLE OOB handshake (replace simulation stub) | Q3 2026 |
| 7 | Ops Hub live dashboard (Leaflet + WebSocket) | Open |
| 8 | Aerial dispatch integration (drone visual verification) | Theoretical |

### Open Tech Debt

| File | Item |
|---|---|
| `PanWalletClient.kt` + `PanApiClient.kt` | `@file:Suppress` — pending clean Gradle sync |
| `onboarding_api.py` | Confirm `ANDROID_PACKAGE_NAME` env var set in production |
| `logistics_webhook_api.py` | Confirm `HARDWARE_REGISTRY_URL` env var set before registry wiring |
| `escrow_oracle.py` | RFC 8037 test vector in sim block — never use in production |
| `AndroidBleClient.kt` | `isScanning` AtomicBoolean + `close()` stub — replace with real BLE in Q3 |

---

## 12. Troubleshooting

### Redis

**`redis.exceptions.ConnectionError: Error connecting to localhost:6379`**
Redis isn't running. Start it with `redis-server` before launching any backend process.

**`WRONGTYPE Operation against a key holding the wrong kind of value`**
A Redis key has an unexpected type — usually caused by leftover data from a previous dev session. Flush the dev database with `redis-cli FLUSHDB` (never run this in production).

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
This is a known suppressed warning in `PanWalletClient.kt` and `PanApiClient.kt` related to BuildConfig visibility. It does not affect functionality. A clean Gradle sync after the `visibility(PUBLIC)` fix should resolve it.

**`google-services.json not found`**
The Firebase config file is missing. Download it from your Firebase project console and place it in `composeApp/`.

---

### Key Ceremony

**`Agent identity missing. Please log in.`**
The agent is not authenticated via Firebase. Ensure Firebase Auth is initialized and the agent has signed in before tapping INITIALIZE NODE.

**`Hardware key already registered for this identity.`** (HTTP 409)
The Key Ceremony has already been completed for this agent on this or another device. If the agent lost their device, use the `/ops/hardware-reset` workflow — do not attempt to re-run the ceremony directly.

**`Device failed hardware integrity checks`** (HTTP 401)
The device is rooted, running a custom ROM, or is an emulator. Play Integrity requires an unmodified device with certified bootloader.

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

---

## Security Notes

- **Never commit `local.properties`** — it contains all API keys and secrets
- **Never commit `google-services.json`** or `GoogleService-Info.plist`
- **The `COGNITIVE_ENCRYPTION_KEY` must be static** — rotating it invalidates all stored agent memories
- **Hardware Key Ceremony is irreversible** — use `/ops/hardware-reset` workflow if an agent loses their device
- **Play Integrity tokens are verified server-side** via Google ADC — ensure GCP credentials are configured on the backend host before go-live
- **All V2X fleet signals require Ed25519 signatures** — register fleet public keys via `PUBKEY_*` environment variables before a fleet partner goes live

---

## License

MIT — see `LICENSE` for details.

---

*Built with ❤️ for the Vanguard 50 — Veterans providing meaningful work in the autonomous era.*
