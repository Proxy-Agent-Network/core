# Changelog

All notable changes to the Proxy Agent Network (PAN) Core Infrastructure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2026.2.0-beta] - 2026-04-23 (Vanguard Field System)

### Added
- **Wingman BLE Module:** Two-stage BLE-to-UWB homing handshake for "Last 15 Meters" precision routing to stranded AVs. The Wingman BLE service feeds spatial data to the UwbHomingCompass on the Vanguard mobile app.
- **Biometric Device Transfer (KYC):** Automated device transfer flow allowing agents to recover their identity on a new phone after hardware loss. Enforces a 409 Conflict check when a new hardware key attempts to bind to an agent ID that already has one registered.
- **Agent API:** Dedicated `/agent/*` endpoint namespace for mission lifecycle, FCM token registration, evidence upload, presence management, and payout-floor configuration. Split out from v2x_bounty_api to match responsibility boundaries.
- **Evidence Pipeline:** Secure S3 evidence upload with cryptographic ownership tracking via Redis index. Mission completion now validates that submitted evidence URLs belong to the completing agent.
- **Reputation Engine:** SB 1417-compliant feedback API. Buyer/seller feedback is submitted per completed mission and contributes to the Vanguard Trust Score routing weight.
- **Two-Phase Ack:** Mission acceptance now requires both a TPM-signed ACCEPT and a post-render ACK, enabling the SLA watchdog to distinguish "received dispatch" from "actively en route."
- **FCM Dispatch:** Firebase Cloud Messaging integration for mission dispatch push notifications, with secure FCM token registration bound to hardware-attested agent identity.
- **Partner Dispatch API:** Bearer-token-authenticated webhook (`POST /api/v1/dispatch/request`) for legacy non-V2X fleet integrations. Uses `PARTNER_API_KEY` env var.
- **Offline Sync Engine:** Store-and-forward evidence engine for agents operating in low-connectivity zones.

### Changed
- **KMP Network Migration:** Migrated the mobile network layer from PanApiClient (Android-only) to PanWalletClient (Kotlin Multiplatform). WalletNetworkClient interfaces now bridge Android and iOS code paths.
- **JWT Audience Claim:** Vanguard Agent StrongBox JWTs now require the `"aud": "pan_dispatch_gateway"` claim. Tokens missing the claim are rejected at the gateway.
- **Gateway Hardening:** Hard imports for required routers (telemetry, wallet, agent) replace the prior fallback-to-mock pattern. Silent ImportError on load-bearing routes is no longer possible.
- **Webhook Authentication:** Zero-trust webhook authentication via Ed25519 per-fleet keys for V2X distress signals. DEV-FLEET-01 bypass now rejects in production.
- **Dispatch Engine:** Migrated dispatch routing to OSRM (Open Source Routing Machine) for deterministic street-grid routing. Dynamic L402 surge pricing tied to OSM color taxonomy.
- **Content Security Policy:** Hardened CSP on the Ops Hub dashboard with per-request nonces.
- **Redis Transactions:** Atomic wallet mutations via WATCH/MULTI transactions prevent payout double-counting under concurrent mission completions.

### User Interface
- **Ops Hub React Migration:** Migrated the Tactical Mission Control Dashboard from the legacy static UI to a React + Vite architecture. Live tactical map now driven by full-duplex telemetry WebSockets.
- **Mobile Tactical App:** Unified context grid and tactical boot sequence, agent feedback screen with wallet client integration, rank dossier and store screen for in-app progression, UWB homing radar UI, and rendered hardware guard overlay.
- **Executive Reporting:** New executive reports and fleet portals under the Ops Hub for compliance, operations, financial, and vendor SLA views.

### Fixed
- **Evidence Ownership Spoofing:** Mission completion's evidence ownership check now uses an anchored regex plus Redis index lookup, replacing the prior vulnerable substring match on URL paths.
- **Routing Double-Prefix Bug:** Fixed `/api/v1/v1/...` path shadowing caused by routers using internal `/v1/` path prefixes. All agent-facing routes now resolve correctly.
- **Fallback Mock Removed:** Removed the `/api/v1/{path:path}` fallback mock in the FastAPI gateway that was returning fabricated wallet balances for unrouted requests.
- **Race Conditions:** Patched race conditions in agent matching, mutex protection on USED_SIGNATURES set to prevent thread collision on replay-protection cache.

### Security
- **Hardware Attestation at Registration:** Public key registration now validates DER cert format at submission time. Play Integrity gating on key ceremony blocks emulators and rooted devices.
- **PII Storage Separation:** Migrated onboarding document uploads to dedicated S3 PII bucket with AES-256 SSE. Evidence uploads fall back to the PII bucket only in dev.
- **Dev Bypass Gating:** VNG-50-PILOT pilot bypasses, DEV-FLEET-01 webhook auth, mock Redis, and mock TPM all gated behind `ENVIRONMENT != production`. Production deployments now fail loudly rather than silently falling back.
- **Admin Portal Lockdown:** ADMIN_SECRET_TOKEN now strictly enforced. Login endpoint rate-limited and uses timing-safe comparison. Removed hardcoded "Panopticon Prime" RBAC bootstrap that auto-provisioned OWNER access at every startup.
- **FLASK_SECRET_KEY Enforcement:** App startup now hard-fails if FLASK_SECRET_KEY is missing or matches the known insecure default.

### Removed
- **AI Chatbot Subsystem:** Purged the deprecated AI marketplace/chatbot product (PowerChat, WaterCooler, Sub-Rosa, Market endpoints). 23 routes and associated imports removed.
- **v1 Judiciary Stubs:** Removed legacy jury tribunal, appellate VRF, evidence locker, and forensic data exporter modules from the pre-pivot architecture.
- **v1 Discovery/Slashing:** Removed deprecated hub_discovery_api, slashing_engine, and traffic_shaper middleware.
- **Duplicate Telemetry Ingest:** Removed the unauthenticated Flask `/api/v1/telemetry/ingest` that duplicated the authenticated FastAPI version. Single source of truth is now the hardware-JWT-authenticated path.
- **v1 Legacy Docs:** Purged `docs/architecture/specs/v1/` and assorted duplicate documentation (`architecture/security/THREAT_MODEL.md`, `architecture/media/BRAND.md`, `architecture/specs/openapi.yaml`, outdated assets).

---

## [2026.1.0-beta] - 2026-03-04 (Mesa Pilot Architecture)

### Added
- **Vanguard 50:** Integrated recruitment and onboarding endpoints for the Mesa AZ (Sector 1) Veteran pilot.
- **Compliance Engine:** Full implementation of the Arizona SB 1417 "Optical Health Report" cryptographic audit schema.
- **Geofencing:** Strict UWB (Ultra-Wideband) and GPS geofencing logic enforcing the 15-minute response SLA.

### Changed
- **Architectural Pivot:** Completely deprecated legacy "Digital Task" endpoints (e.g., CAPTCHA, SMS Relay, Legal Signatures) to focus 100% on physical Autonomous Vehicle (AV) recovery.
- **Documentation:** Complete overhaul of all repository guidelines to reflect enterprise Fleet API integration standards and physical OPSEC.

### Security
- **Zero-Trust Identity:** Deprecated all biometric/video authentication workflows. PAN now strictly relies on Hardware Attestation (TPM 2.0 / Apple Secure Enclave) to protect fleet assets and passenger privacy.

---

## [0.9.5] - 2026-02-09

### Added
- **Fleet Gateway:** Initial ingestion logic for Unified Diagnostic Service (UDS) fault codes (e.g., `LIDAR_OCCLUSION_FRONT`).
- **L402 Economy:** Migrated escrow architecture to Lightning Network HODL invoices for instant Machine-to-Human (M2H) micro-settlements.

### Changed
- Replaced the centralized "Jury Tribunal" dispute resolution with deterministic, AV-driven L402 smart contract execution.

---

## [0.9.2] - 2026-01-20 (Private Fleet Beta)

### Added
- **Ops Hub:** Launched the Tactical Mission Control Dashboard for real-time sector observability.
- **Webhooks:** Added `mission.dispatched`, `agent.en_route`, and `orp.completed` event signatures for Fleet Partner callbacks.

### Fixed
- Fixed race condition in the dispatch queue when multiple Vanguard Agents are equidistant to a grounded AV.

---

## [0.9.0] - 2026-01-05

### Added
- **Hardware Layer:** Initial Rust (`tss-esapi`) bindings for physical device identity.
- **Protocol:** Drafted the Optical Reclamation Protocol (ORP) establishing chemical/microfiber standards for LiDAR/Camera intervention.

---

## [0.8.5] - 2025-12-15

### Changed
- Refactored M2H task routing to support dynamic L402 Surge Pricing based on localized AV fleet demand and weather anomalies.

---

## [0.1.0] - 2025-11-01

### Added
- Initial Proof of Concept (PoC) for a localized "Human-in-the-Loop" API bridging digital intent with physical execution.