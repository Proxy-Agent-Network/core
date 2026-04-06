# Proxy Agent Network (PAN)
**The Human Infrastructure for the Autonomous Era**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Private Beta](https://img.shields.io/badge/Status-Private%20Beta-orange.svg)](https://www.proxyagent.network/)
[![Network: Mesa, AZ](https://img.shields.io/badge/Sector-Mesa%2C%20AZ-green.svg)]()

> When an autonomous vehicle hits a wall it can't solve alone, PAN sends a human.

---

## The Problem

Autonomous vehicle fleets encounter thousands of edge cases every day that software cannot resolve — sensor occlusion from road debris, door faults, biohazard spills, first-responder liaisons, and defleeting operations. Every unresolved incident costs fleets time, money, and rider trust.

Today, those incidents sit unresolved until an expensive fleet operations team dispatches a response — slowly, manually, and at scale.

---

## The Solution

PAN is a **decentralized physical infrastructure (DePIN) network** that connects AV fleets to a verified roster of Vanguard Agents — trained, background-checked operators who resolve physical edge cases in the field, earning real-time bounty payouts settled via the Lightning Network.

**Fleet sends a signal. PAN dispatches a human. Problem solved in minutes.**

---

## How It Works

```
  AV Fleet Partner                PAN Network                  Vanguard Agent
  ───────────────                 ───────────                  ──────────────
  Fault detected    ──────────▶   Ed25519 verified             Mission alert
  V2X distress      (webhook)     Geospatial dispatch   ────▶  dispatched to
  signal sent                     Bounty locked in HODL        nearest agent
                                  escrow
                                                               Agent arrives
  Optical Health    ◀──────────   SB 1417 audit sealed         UWB micro-homing
  Report received   (L402 payout) L402 invoice settled  ◀────  Evidence captured
                                  Agent earns 90% cut          Mission complete
```

---

## Key Features

### 🛡️ Zero-Trust Security
Every interaction is cryptographically verified. Fleet signals require Ed25519 signatures. Agent hardware is bound to a TPM via Google Play Integrity attestation. Bounty settlement requires a three-stage oracle: hardware proof, SB 1417 compliance, and an AV-signed Ed25519 payload verified by a Rust smart contract.

### ⚡ Instant Lightning Settlements
Agent payouts are settled in seconds, not days, via L402 HODL invoices on the Bitcoin Lightning Network. No banks. No ACH delays. No middlemen.

### 📍 Precision Micro-Homing
Agents navigate to within centimeters of a stranded AV using a two-stage proximity system: BLE Out-of-Band handshake at 50 meters, transitioning to UWB ranging at 15 meters for millimeter-precise vehicle locating.

### 📋 SB 1417 Compliance Built-In
Every mission automatically generates a sealed, immutable Optical Health Report — cryptographically signed and stored to satisfy California's autonomous vehicle incident documentation mandates. The compliance pipeline now includes voice log transcripts, biometric safety events, RATS threat detection logs, personal air quality readings, and conductivity hazard events — all timestamped, GPS-tagged, and automatically appended without any agent action.

### 📈 Dynamic Surge Pricing
The network automatically raises bounties when agent utilization exceeds 75%, ensuring critical incidents are always staffed. Bounties are anchored to the OSM color taxonomy and capped at 3x the base rate.

### 🧠 AI-Assisted Dispatch (Proxy-Alpha Companion Mode)
Vanguard Agents have access to Proxy-Alpha, a tactical AI engine powered by Gemini 2.5 Flash. Proxy-Alpha pre-loads mission context at dispatch — vehicle VIN, active fault code, UDS library, agent certifications, and live telemetry — before the agent says a word. Agents activate Proxy-Alpha hands-free via the Communicator Pin wake word ("Hey Dispatch") and receive field guidance through the pin's integrated speaker. All compliance-relevant interactions are automatically transcribed and appended to the SB 1417 report. Secured behind a semantic prompt injection firewall.

### 🦺 Project Copperfield — Vanguard Field System
PAN Agents in the Vanguard 50 pilot are equipped with the full Project Copperfield wearable platform — four integrated intelligent garments that together make a Vanguard Agent the safest, most documented, and most capable field operator on any incident scene. See [Vanguard Field System](#vanguard-field-system) below.

---

## Operational Status Matrix (OSM)

PAN uses a standardized color taxonomy for task classification, pricing, and dashboard visualization.

| Color | Category | Tier | Base Bounty |
|---|---|---|---|
| 🔴 RED | Biological / Foreign Object | Critical | $65.00 |
| 🟣 PURPLE | Defleeting | Critical | $65.00 |
| 🟡 YELLOW | Tech / Sensor Fault | Elevated | $45.00 |
| 🟠 ORANGE | Calibrations | Elevated | $45.00 |
| 🟢 GREEN | Power Down & Rest (PDR) | Standard | $14.00 |
| 🔵 BLUE | Validation | Standard | $14.00 |
| ⬜ WHITE | Demo Vehicle | Standard | $14.00 |

---

## Vanguard Field System

**Project Copperfield** is PAN's proprietary intelligent wearable platform — four components designed as a unified system, each functional independently but achieving maximum capability when deployed together.

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                   VANGUARD FIELD SYSTEM                         │
  │                                                                 │
  │  🧢 HapHat v2.3          🦺 PANOPLY Vest v1.2                  │
  │  Identity · Mission       Situational awareness · RATS          │
  │  alerting · Proximity     Rear threat detection · LED           │
  │  Haptic navigation        back panel · Spine haptics            │
  │  Cryptographic TPM        SB 1417 logging                       │
  │                                                                 │
  │  👕 Aegis Polo VFP-1 v1.2  🧤 Gauntlets VFG-1 v1.3            │
  │  Biometric monitoring     Gesture control · Culture             │
  │  Voice AI (Proxy-Alpha)   Tool NFC · Multi-agent                │
  │  Thermal management       bonuses · Easter egg                  │
  │  Emergency response       secret menu                           │
  └─────────────────────────────────────────────────────────────────┘
```

### 🧢 HapHat v2.3
An intelligent trucker hat housing five haptic motors in the sweatband, a full RGB NeoPixel brim strip, and a passive NFC identity panel. The hat communicates mission state and directional navigation through haptic patterns without the agent looking at their phone. NFC brim-tap provides instant agent identity verification to fleet managers and AV panels — no app installation required. PCM cooling liner maintains forehead temperature during 115°F Mesa summer operations.

### 🦺 PANOPLY Vest v1.2
An ANSI/ISEA 107-2020 Class 3 hi-vis vest with active intelligence. The Rear Awareness & Threat Detection System (RATS) uses layered mmWave radar, wide-angle camera, and ultrasonic sensors to warn the agent of approaching vehicles through haptic spine strip and LED back panel — before they turn around. The 16×24 flexible LED back panel dynamically displays OSM mission status to fleet managers and first responders at 50+ meter range. A five-motor haptic spine strip communicates navigation direction and proximity without requiring agent attention. Available in three tiers, unlocked by mission milestones.

### 👕 Aegis Polo VFP-1 v1.2
The innermost and most intimate component — worn directly against the skin. The Aegis Polo monitors the agent's biometrics (heart rate, SpO₂, skin temperature, galvanic skin response), reads their personal breathing zone air quality, and listens for their voice via the chest-mounted Communicator Pin. When vest RATS detects a Zone 2 threat and polo biometrics simultaneously detect a stress spike, the system recognizes the agent already knows — and escalates directly to Zone 1 maximum response, skipping the redundant warning. D3O rib impact panels protect against vehicle sideswipe. Bioluminescent collar stripe ensures passive nighttime visibility even when all electronics fail. Available at Tier 3 (200 missions completed).

### 🧤 Gauntlets VFG-1 v1.3
Cut-resistant HPPE field gloves with embedded IMU, NFC, haptic motor, and PCM back-of-hand cooling. A snap gesture toggles the hat brim light — hands-free, both hands on the work. Multi-agent bonuses reward verified physical interactions between agents on the same incident. First to the scene with Gauntlets? Earn a $2 Solo Glove Welcome bonus for greeting un-equipped agents. When both agents are gloved, base greetings (handshake, fist bump) earn $5 each, while flourish upgrades (Secret Handshake, BOOM Explosion) earn $7. The gesture system includes an undisclosed number of hidden easter eggs discovered naturally through use. Sold at cost — no PAN margin. Single-glove purchase always available. Unlock: 10 completed missions.

### Composite Threat Response
The polo and vest together enable a capability unavailable from any single component. When the vest's RATS radar classifies an approaching vehicle at Zone 2 range and the polo's biometric patch simultaneously detects the agent's stress response spiking — the system knows the agent has already perceived the threat. The Zone 2 warning sequence is redundant. The system skips directly to Zone 1 maximum response across all channels simultaneously: hat, spine strip, LED panel, gloves, and phone alarm. The agent's own physiology becomes an input to the threat escalation algorithm.

---

## Fleet Partner Integration

Integrating your AV fleet with PAN takes minutes. Send a signed distress signal and we handle the rest.

### 1. Request Fleet Access

Contact us at [rob@proxyagent.network](mailto:rob@proxyagent.network) to register your fleet and receive your Ed25519 keypair and fleet credentials.

### 2. Send a Distress Signal

```bash
POST [https://api.proxy-protocol.com/api/v1/v2x/distress](https://api.proxy-protocol.com/api/v1/v2x/distress)
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

### 3. Receive Confirmation

```json
{
  "status": "success",
  "task_id": "tsk_a3f8c291b04d"
}
```

PAN handles agent dispatch, SLA monitoring, compliance reporting, and Lightning settlement automatically. Your fleet operations team gets a real-time view of all active missions via the Ops Hub dashboard.

### Signature Requirements

All fleet webhook requests must be signed with your registered Ed25519 private key. The signature is computed over the raw request body. Requests older than 300 seconds are rejected to prevent replay attacks.

```python
import nacl.signing

signing_key = nacl.signing.SigningKey(your_private_key_bytes)
signature = signing_key.sign(request_body_bytes).signature.hex()
```

---

## Vanguard Agent Program

PAN is actively recruiting its founding Vanguard 50 — the first cohort of field operators in the Mesa, AZ sector.

### Who We're Looking For
- Veterans, first responders, and skilled tradespeople
- Valid driver's license and reliable vehicle
- Smartphone (Android 8.0+ or iOS 16+)
- Background check clearance (Checkr verified)
- Based in or near Mesa, AZ (Gilbert, Chandler, Tempe sectors welcome)

### What You Earn
- **Tier 1 tasks** (door securing, validation): $14.00 base
- **Tier 2 tasks** (sensor faults, calibrations): $45.00 base
- **Tier 3 tasks** (bio remediation, defleeting): $65.00 base
- **Surge multiplier** up to 3x during high-demand periods
- **Instant Lightning payout** — funds in your wallet within seconds of mission completion
- **Collaboration bonuses** — earn $2 for greeting un-equipped agents, or up to $7 each for verified bilateral gestures on shared incidents

### Tier Progression
Vanguard Agents unlock expanded capabilities and equipment as they complete missions:

| Milestone | Unlock |
|---|---|
| 10 missions | Gauntlets VFG-1 (purchase at cost) |
| 50 missions | Tier 2 certification · PANOPLY Vest Tier 2 features |
| 100 missions | 💯 milestone reward |
| 200 missions | Tier 3 certification · Aegis Polo VFP-1 · PANOPLY Vest Tier 3 features |

### Apply
[Request Access →](https://www.proxyagent.network/)

---

## SDK & Developer Tools

Official client libraries for fleet integration:

| Language | Package | Install |
|---|---|---|
| **Python** | \`proxy-agent\` | \`pip install proxy-agent\` |
| **Node.js** | \`@proxy-protocol/node\` | \`npm install @proxy-protocol/node\` |

Full API reference and integration guides are available in the [\`/docs\`](docs/) directory.

---

## Supported SDKs

### Python

```python
from proxy_agent import PanClient

client = PanClient(
    fleet_id="WAYMO_MESA_01",
    private_key_path="./fleet_private.key"
)

response = client.dispatch(
    vin="WAYMO-404",
    fault_code="UDS_SENSOR_OCCLUSION_LIDAR_FL",
    lat=33.420,
    lon=-111.840,
    osm_color="YELLOW"
)

print(response.task_id)
```

### Node.js

```javascript
const { PanClient } = require('@proxy-protocol/node');

const client = new PanClient({
  fleetId: 'WAYMO_MESA_01',
  privateKeyPath: './fleet_private.key'
});

const response = await client.dispatch({
  vin: 'WAYMO-404',
  faultCode: 'UDS_SENSOR_OCCLUSION_LIDAR_FL',
  lat: 33.420,
  lon: -111.840,
  osmColor: 'YELLOW'
});

console.log(response.taskId);
```

---

## Compliance & Legal

PAN is built for regulatory compliance from the ground up.

- **SB 1417 (California):** Every mission generates a sealed Optical Health Report with timestamped photographic evidence, hardware attestation token, and cryptographic hash stored immutably. The pipeline now includes voice transcripts (via Communicator Pin), RATS threat event logs, biometric safety events, dual air quality readings (ambient + personal breathing zone), and conductivity hazard events — all appended automatically.
- **CPUC AV Incident Reporting:** Compliance export API bundles and signs reports for state regulators.
- **Zero-Knowledge Agent Privacy:** Vanguard Agents' personal data is stored with AES-256 encryption. Fleet partners see only task outcomes, never agent identities. Companion Mode voice transcripts are never shared with fleet partners in full — compliance-flagged excerpts only.
- **IDOR Protection:** All mission assignments are cryptographically bound — agents can only complete missions assigned to them.
- **On-Device Privacy Filtering:** All photographic and video evidence is processed through an on-device ML redaction pipeline before leaving the agent's phone. Faces and license plates are redacted locally — raw PII never touches the network.
- **NARCAN-Certified Agents:** Agents holding medical response certification can carry Narcan emergency supplies in the Aegis Polo's sealed emergency pocket. All Good Samaritan administrations are automatically documented with voice transcript, GPS, and timestamp via Companion Mode. *(Awaiting final Arizona Good Samaritan statutory review prior to Vanguard 50 deployment).*

See [COMPLIANCE.md](legal/COMPLIANCE.md) for full details.

---

## Security

PAN takes security seriously. If you discover a vulnerability, please review our [Security Policy](SECURITY.md) and report it responsibly.

**Do not** open public GitHub issues for security vulnerabilities.

---

## Architecture Overview

For technical partners and contributors, the core stack:

| Component | Technology |
|---|---|
| API Gateway | FastAPI + Redis |
| Dispatch Engine | Geospatial GEORADIUS + FIFO queue |
| Surge Pricing | AUR-based exponential repricing daemon |
| SLA Enforcement | Two-phase ACK watchdog (15s timeout) |
| Escrow | Rust smart contracts via PyO3 FFI |
| Payments | LND gRPC — mainnet Lightning Network |
| Mobile | Kotlin Multiplatform (Android + iOS) |
| Hardware Security | Android StrongBox TPM + Play Integrity |
| Proximity | BLE OOB (50m) → UWB ranging (15m) |
| AI Engine | Gemini 2.5 Flash + Cognitive Vault |
| Background Checks | Checkr API — driver_pro package |
| Wearables | BLE 5.0 mesh · nRF52840 · ESP32-C3 |
| Threat Detection | TI IWR6843AOP mmWave + Edge ML (Coral TPU) |
| Haptics | 5-motor ERM array (hat) · 5-motor spine strip (vest) · wrist motor (gloves + polo) |
| Biometrics | MAX86150 PPG/ECG · BME688 air quality · VEML6075 UV |
| NFC | PN532 passive brim tag (hat) · PN532 active/passive (gloves) · vest back panel tag |
| PCM Thermal | Shared sodium sulfate decahydrate system · 45-min freeze cycle · all four garments |

Full architecture documentation is available in [\`architecture\`](architecture/).

---

## Contributing

We are building the bridge between digital intelligence and physical reality. We are looking for mission-driven engineers to help define the standard for 2030.

**Open Roles (Remote / Async):**

- **Rust Protocol Engineer** — Migrate settlement layer to high-frequency Lightning interactions
- **Legal Engineering Lead** — Productize Power of Attorney templates for autonomous entities
- **Developer Relations** — Build the "Hello World" tutorials that 10,000 AI developers will use
- **iOS Engineer** — Complete the KMP iOS client and UWB ranging implementation
- **Firmware Engineer** — AndroidBleHapHatService real implementation · ESP32 GATT server · OTA update pipeline
- **Hardware Engineer** — PANOPLY vest PCBA · Aegis Polo sensor integration · Gauntlets flex PCB

To apply, cryptographically sign a message with your GitHub handle and email [rob@proxyagent.network](mailto:rob@proxyagent.network).

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## Status

🚧 **Private Beta** — Mesa, AZ Sector 1 | Vanguard 50 Pilot | Go-Live: Memorial Day 2026

| System | Status |
|---|---|
| PAN API + Dispatch Engine | ✅ Operational |
| Android PAN Tactical app | ✅ Pilot-ready |
| Lightning settlement | ✅ Mainnet |
| SB 1417 compliance pipeline | ✅ Complete |
| Checkr background verification | 🔧 Integration in progress |
| HapHat v2.3 | 🔧 Mock → real BLE implementation |
| PANOPLY Vest v1.2 | 📐 Spec complete · prototype pending |
| Aegis Polo VFP-1 v1.2 | 📐 Spec complete · prototype pending |
| Gauntlets VFG-1 v1.3 | 📐 Spec complete · prototype pending |
| OSRM tactical routing | 🔧 Phase 6 wiring in progress |
| iOS client | 📋 Planned |

[Request Early Access →](https://www.proxyagent.network/)

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*The human infrastructure for the autonomous era. Built with veterans, for the future.*