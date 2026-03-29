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
Every mission automatically generates a sealed, immutable Optical Health Report — cryptographically signed and stored to satisfy California's autonomous vehicle incident documentation mandates.

### 📈 Dynamic Surge Pricing
The network automatically raises bounties when agent utilization exceeds 75%, ensuring critical incidents are always staffed. Bounties are anchored to the OSM color taxonomy and capped at 3x the base rate.

### 🧠 AI-Assisted Dispatch (Proxy-Alpha)
Vanguard Agents have access to Proxy-Alpha, a tactical AI engine powered by Gemini 2.5 Flash. Proxy-Alpha can query live AV telemetry, check SB 1417 compliance requirements, and provide field guidance — all secured behind a semantic prompt injection firewall.

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

## Fleet Partner Integration

Integrating your AV fleet with PAN takes minutes. Send a signed distress signal and we handle the rest.

### 1. Request Fleet Access

Contact us at [rob@proxyagent.network](mailto:rob@proxyagent.network) to register your fleet and receive your Ed25519 keypair and fleet credentials.

### 2. Send a Distress Signal

```bash
POST https://api.proxy-protocol.com/api/v1/v2x/distress
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
- Background check clearance
- Based in or near Mesa, AZ (Gilbert, Chandler, Tempe sectors welcome)

### What You Earn
- **Tier 1 tasks** (door securing, validation): $14.00 base
- **Tier 2 tasks** (sensor faults, calibrations): $45.00 base
- **Tier 3 tasks** (bio remediation, defleeting): $65.00 base
- **Surge multiplier** up to 3x during high-demand periods
- **Instant Lightning payout** — funds in your wallet within seconds of mission completion

### Apply
[Request Access →](https://www.proxyagent.network/)

---

## SDK & Developer Tools

Official client libraries for fleet integration:

| Language | Package | Install |
|---|---|---|
| **Python** | `proxy-agent` | `pip install proxy-agent` |
| **Node.js** | `@proxy-protocol/node` | `npm install @proxy-protocol/node` |

Full API reference and integration guides are available in the [`/docs`](docs/) directory.

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

- **SB 1417 (California):** Every mission generates a sealed Optical Health Report with timestamped photographic evidence, hardware attestation token, and cryptographic hash stored immutably.
- **CPUC AV Incident Reporting:** Compliance export API bundles and signs reports for state regulators.
- **Zero-Knowledge Agent Privacy:** Vanguard Agents' personal data is stored with AES-256 encryption. Fleet partners see only task outcomes, never agent identities.
- **IDOR Protection:** All mission assignments are cryptographically bound — agents can only complete missions assigned to them.

See [COMPLIANCE.md](COMPLIANCE.md) for full details.

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

Full architecture documentation is available in [`/docs/architecture`](docs/architecture/).

---

## Contributing

We are building the bridge between digital intelligence and physical reality. We are looking for mission-driven engineers to help define the standard for 2030.

**Open Roles (Remote / Async):**

- **Rust Protocol Engineer** — Migrate settlement layer to high-frequency Lightning interactions
- **Legal Engineering Lead** — Productize Power of Attorney templates for autonomous entities
- **Developer Relations** — Build the "Hello World" tutorials that 10,000 AI developers will use
- **iOS Engineer** — Complete the KMP iOS client and UWB ranging implementation

To apply, cryptographically sign a message with your GitHub handle and email [rob@proxyagent.network](mailto:rob@proxyagent.network).

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## Status

🚧 **Private Beta** — Mesa, AZ Sector 1 | Vanguard 50 Pilot | Go-Live: Memorial Day 2026

[Request Early Access →](https://www.proxyagent.network/)

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*The human infrastructure for the autonomous era. Built with veterans, for the future.*
