# Changelog

All notable changes to the Proxy Protocol Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-02-09

### Added
- **Public Launch:** Repository made public for beta access.
- **Legal:** Added standard Delaware Power of Attorney templates (`templates/legal/`).
- **SDK:** Initial release of Python Client (`pip install proxy-agent-alpha`).
- **Pricing:** Dynamic Market Ticker endpoint (`GET /v1/market/ticker`) live.

---

## [0.9.2] - 2026-01-20 (Private Beta)

### Added
- **Escrow:** Integrated Lightning Network HODL invoices for sub-second escrow locking.
- **Webhooks:** Added `job.completed` and `job.failed` event signatures for agent callbacks.

### Fixed
- Fixed race condition in task dispatch queue when multiple agents bid on the same human node.

---

## [0.9.0] - 2026-01-05

### Added
- **Identity:** Implemented Tier 2 Video Authentication flow for Human Proxies.
- **Gov:** Initial "Triple-Lock" governance draft added to internal docs.

---

## [0.8.5] - 2025-12-15

### Changed
- Refactored `verify_sms_otp` payload to support international country codes (+44, +81).
- Increased default timeout for physical mail tasks to 24 hours.

---

## [0.1.0] - 2025-11-01

### Added
- Initial Proof of Concept (PoC) for "Human-in-the-loop" API.
- Basic "Hello World" task type for verifying simple captchas.
