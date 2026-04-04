# Contributing to Proxy Agent Network (PAN)

Welcome to the PAN Core Infrastructure repository. We actively welcome contributions from automotive engineers, DePIN developers, mobile engineers, firmware engineers, and hardware security specialists who are building the physical recovery layer for the autonomous vehicle (AV) era.

This code directly impacts the physical safety of Vanguard Agents working roadside next to autonomous vehicles. We hold all contributions to enterprise-grade reliability standards.

---

## Getting Started

Before writing any code, read **[DEVELOPER.md](DEVELOPER.md)** in full. It contains the complete environment setup, all required secrets, the Firebase RTDB rules requirement, the Key Ceremony flow, and the hardware integration architecture. There are several non-obvious setup requirements that will cost you hours if you miss them.

---

## How to Contribute (The Vanguard Standard)

1. **Fork the Project:** Create your isolated environment.
2. **Create a Branch:** `git checkout -b feature/uwb-homing-optimization`
3. **Commit your Changes:** `git commit -m 'Enhance Ultra-Wideband proximity logic for Sector 1'`
4. **Push to the Branch:** `git push origin feature/uwb-homing-optimization`
5. **Open a Pull Request:** Your PR description must explicitly state:
   - Which component or module is affected
   - How this impacts the Mesa Pilot SLA, SB 1417 compliance, or agent safety
   - Whether any hardware-side changes are required alongside the software change
   - Test coverage added or modified

---

## Engineering Standards

### Languages & Frameworks

| Layer | Language / Framework | Notes |
| :--- | :--- | :--- |
| Backend API | Python 3.10+ (PEP 8) | FastAPI + Redis. See `apps/backend/`. |
| Mobile | Kotlin Multiplatform (KMP) | Android primary target. iOS KMP in progress. |
| Smart Contracts / Escrow | Rust (via PyO3 FFI) | Maturin build. Virtual environment must be active before `maturin develop`. |
| Firmware | C / nRF Connect SDK | nRF52840 (all four Copperfield components). BLE GATT server. Nordic DFU OTA. |
| Embedded Controller | Arduino / ESP-IDF | ESP32-C3 (HapHat primary controller — motor PWM, LED strip). |

### API Documentation

All Fleet Gateway endpoint modifications must be documented in `/docs/v2026.2/`. The v2026.1 directory is archived — do not add new documentation there.

### Security Standards

- **Never commit** `local.properties`, `google-services.json`, `GoogleService-Info.plist`, or any file containing API keys, L402 macaroons, or Lightning node credentials.
- **Never commit** the `COGNITIVE_ENCRYPTION_KEY` — this key is static per deployment and losing it invalidates all stored agent memories.
- **GCP credentials:** Use `gcloud auth application-default login` for **local development only**. Production environments must use a dedicated JSON Service Account key with minimum required permissions. Do not use ADC in production containers.
- **Firebase RTDB rules must remain `deny-all`.** No application code writes directly to RTDB. All agent state routes through the Python backend → Redis. PRs that write agent state to RTDB will be rejected.
- **Firmware packages** must be signed with the PAN private key before distribution. The device firmware rejects unsigned packages. Never distribute unsigned firmware.

### Test Coverage

PRs affecting the following modules require a minimum of 90% test coverage:

- `/src/L402-Gateway/` — Lightning escrow and payment settlement
- `/src/escrow_oracle.py` — Three-stage zero-trust settlement (hardware + SB1417 + Ed25519)
- `PrivacyFilter.kt` — SB 1417 photo redaction pipeline (faces + license plates). The fail-safe path must always return a blacked-out bitmap, never an unredacted original.
- `BleHapHatService` implementations — Any real BLE implementation replacing the current mock
- `validate_multi_agent_bonus()` — Gesture bonus anti-gaming (Redis atomic NX, incident lock, shift cooldown)
- Any module that appends data to the SB 1417 Optical Health Report

PRs affecting hardware firmware do not have a coverage minimum but must include a test plan documenting which physical scenarios were validated on hardware.

---

## Open Roles — High Priority

These are the areas where contributions are most needed before the Memorial Day 2026 pilot. If you're working on one of these, open an Issue to claim it before starting.

| Role | What's Needed | Files / Location |
| :--- | :--- | :--- |
| **Android BLE Engineer** | `AndroidBleHapHatService` — real BLE implementation replacing the current mock. The interface is defined in `BleHapHatService.kt`. This is a **pilot blocker**. | `apps/mobile/src/ble/BleHapHatService.kt` |
| **Firmware Engineer (nRF52840)** | TFLite Micro snap gesture classifier for Gauntlets VFG-1. The three-factor detection architecture (acceleration spike + duration + palm friction signature) is defined in Gauntlets VFG-1 spec Section 5.4. The classifier must be trained on field-negative examples (tool drops, door slams, driving vibration) — not synthetic data. | Gauntlets firmware repo |
| **Firmware Engineer (Gazell P2P)** | Glove-to-glove direct radio link using nRF52840 Gazell protocol for multi-agent gesture choreography sync. BLE fan-out through PAN Command cannot guarantee the sub-100ms simultaneity required for the gesture bonus system. See Gauntlets VFG-1 spec Section 15.2 for the corrected architecture. | Gauntlets firmware repo |
| **Backend Engineer** | Checkr background verification integration in `onboarding_api.py`. API design is complete. `CHECKR_API_KEY` and `CHECKR_WEBHOOK_SECRET` env vars are defined. This is a **pilot blocker**. | `apps/backend/src/onboarding_api.py` |
| **Mobile Engineer** | Phase 6 OSRM tactical route wiring in `AgentDashboardScreen`. `getTacticalRoute()` exists in `PanApiClient` with a TODO comment. Route data needs to be wired to the dashboard navigation UI. | `apps/mobile/src/screens/AgentDashboardScreen.kt` |
| **iOS Engineer** | Complete the KMP iOS client and UWB ranging implementation. | `apps/mobile/iosApp/` |
| **Hardware Engineer** | PANOPLY Vest v1.2 electronics bay thermal design. The bay must use aluminum or thermally conductive composite housing — sealed polymer is not acceptable for Arizona field conditions. Full requirements in Vest spec Section 4.3. Prototype sign-off requires thermal simulation at 40°C ambient. | Hardware design files |
| **Legal Engineering Lead** | Productize Power of Attorney templates for autonomous entities. Narcan emergency pocket legal review (AZ Good Samaritan statute, HNOA coverage for medical response actions). |  |
| **Rust Protocol Engineer** | Migrate settlement layer to high-frequency Lightning interactions. | `apps/backend/src/core/economics/` |
| **Developer Relations** | Build the "Hello World" fleet integration tutorials. First contact for most fleet partners will be the distress signal webhook — make it a 15-minute integration. | `/docs/` |

To apply, cryptographically sign a message with your GitHub handle and email [rob@proxyagent.network](mailto:rob@proxyagent.network).

---

## Known Tech Debt — Good First Issues

These are scoped, well-understood items that don't require deep system knowledge:

| Item | File | Description |
| :--- | :--- | :--- |
| `@file:Suppress` cleanup | `PanWalletClient.kt`, `PanApiClient.kt` | Suppressed `INVISIBLE_REFERENCE` / `INVISIBLE_MEMBER` warnings pending clean Gradle sync after `visibility(PUBLIC)` fix. |
| Callsign backend persistence | `WalletAndProfileScreen.kt` | `firstName` and `callsign` are currently `rememberSaveable` only — not persisted to the backend. Needs a write to the agent profile endpoint on change. |
| `net_payout` field verification | `PanApiClient.kt`, `v2x_bounty_api.py` | Confirm backend calculates `net_payout` from Redis and that the client is not submitting a client-calculated value to the settlement oracle. |
| imgbb → S3 migration | All evidence upload calls | imgbb is approved for the Vanguard 50 pilot only. Must migrate to AWS S3 or GCP Cloud Storage before fleet partner sign-off. |
| `ANDROID_PACKAGE_NAME` env check | `onboarding_api.py` | Add startup assertion that `ANDROID_PACKAGE_NAME` is set in the production environment before the Play Integrity check runs. |
| `HARDWARE_REGISTRY_URL` env check | `logistics_webhook_api.py` | Add startup assertion before registry wiring. |
| RFC 8037 test vector removal | `escrow_oracle.py` | Simulation block contains an RFC 8037 test vector. Must never reach production. Needs a `BuildConfig.DEBUG`-equivalent guard or removal. |

---

## Governance & Protocol Upgrades

Major changes to the PAN protocol require formal consensus before implementation. Open an Issue tagged `[RFC]` (Request for Comment) to initiate discussion before writing code for any of the following:

- Altering dynamic L402 surge pricing logic or the AUR threshold
- Modifying the 15-minute SLA enforcement parameters
- Expanding the Operational Design Domain (ODD) beyond Sector 1 (Mesa, AZ)
- Changes to the BLE GATT command protocol or service UUIDs for any Copperfield component
- Changes to the multi-agent gesture bonus system (amounts, anti-gaming rules, shift cooldown)
- Changes to the SB 1417 Optical Health Report data schema
- Changes to the Composite Threat Response algorithm (RATS + biometric escalation logic)
- Hardware architecture changes affecting the gesture simultaneity sync path (Gazell peer link)

Fleet Partners and PAN Command must be consulted before implementation. RFCs that affect fleet partner integrations require a 14-day comment period before merge.

---

## Hardware & Compliance Contributions

### 1. SB 1417 Audit Enhancements

- **Requirement:** Must map directly to Arizona Revised Statutes Title 28, Chapter 24 (Autonomous Vehicles). Final rules effective December 31, 2026 — monitor for regulatory updates.
- **Focus Areas:** Cryptographic hashing and immutability of Optical Health Reports; expanding the automated data pipeline; on-device redaction (`PrivacyFilter`) accuracy.
- **Privacy Rule:** Any change that causes raw PII (unredacted faces or license plates) to leave the agent's device will be rejected unconditionally, regardless of other merits.
- **Data Schema Changes:** Any modification to the SB 1417 report data schema requires an `[RFC]` issue and legal review before implementation.

### 2. Optical Reclamation Protocol (ORP)

- **Requirement:** Proposed changes to physical cleaning procedures (e.g., new microfiber standards or chemical solvent limits) must cite current LiDAR/Camera OEM manufacturer specifications (e.g., Waymo, Luminar, Hesai).
- **Review:** Physical protocol changes require sign-off from PAN Command to ensure they do not void the $5M HNOA/E&O Liability Shield.

### 3. Project Copperfield — Vanguard Field System

Contributions to the Project Copperfield wearable platform (HapHat v2.3, PANOPLY Vest v1.2, Aegis Polo VFP-1, Gauntlets VFG-1) follow additional requirements:

- **Spec documents are authoritative.** Hardware behavior must match the published spec. Deviations require the spec to be updated via PR before (or alongside) the firmware change.
- **Haptic delineation protocol must be preserved.** The hat, vest spine, gloves, and polo wrist motor each own specific haptic channels. A PR that causes two components to communicate the same information through the same channel simultaneously (outside of Zone 1 emergency) conflicts with the delineation protocol and will be rejected.
- **Gesture easter eggs — Tier C is firmware-only.** Tier C secrets are intentionally undocumented. Do not add documentation, code comments, or log entries that reveal Tier C content. The Three-Agent Secret and other Tier C easter eggs should exist only in firmware and backend, with no human-readable description accessible to agents.
- **OTA firmware packages must be signed** with the PAN private key before distribution. The nRF52840 and ESP32-C3 firmware both verify package signatures before applying updates.
- **Electronics bay thermal design:** Any hardware PR modifying the PANOPLY Vest electronics bay enclosure must include thermal simulation results demonstrating &lt;60°C case temperature at sustained 5W average load at 40°C ambient. Sealed polymer enclosures will not be accepted for this bay.
- **Integration Port contacts:** Any hardware PR modifying the polo or vest Integration Port must specify gold-plated contacts (minimum 30µin over nickel barrier). Standard pogo pin contacts corrode in the sweat exposure environment of the collar zone.

### 4. Agent Safety — Non-Negotiable

Any contribution that affects a safety-critical code path — RATS threat detection, Zone 1 emergency response, duress button, impact detection, conductivity hazard alerting, composite threat escalation, or the PrivacyFilter fail-safe — requires review from at least two PAN Core team members before merge, regardless of test coverage. Agent safety is not a place for solo judgment calls.

---

Thank you for building the critical physical infrastructure required to scale L4 Autonomy. The Vanguard Agents working roadside in Mesa depend on this code being right.
