# Changelog

All notable changes to the Proxy Agent Network (PAN) Core Infrastructure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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