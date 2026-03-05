# Proxy Agent Network (PAN) | Rust Engineering Guidelines

| Status | Scope |
| :--- | :--- |
| **Active** | Core Settlement & Attestation Migration (Python -> Rust) |

As the Proxy Agent Network (PAN) scales to handle direct Unified Diagnostic Service (UDS) webhooks from Tier-1 Autonomous Vehicle (AV) fleets, we are migrating our core Machine-to-Human (M2H) settlement and Hardware Attestation state machines to Rust. This document outlines the architectural constraints for this mission-critical migration.

---

## 1. The Philosophy: "Correct by Construction"
In the legacy Python prototype, we relied on runtime checks. In the Rust production environment, we rely strictly on the **Type System** to protect fleet assets and Vanguard Agent payouts.

* **Rule:** Invalid physical states must be unrepresentable. Use `Enums` to define strict state machines (e.g., `MissionState::AgentEnRoute`, `MissionState::OrpInProgress`, `MissionState::FaultCleared`).
* **Rule:** **No `unwrap()`**. Handle every `Result` explicitly. A panic in the settlement layer means a stranded AV or an unpaid Veteran. This is unacceptable.

---

## 2. Core Stack & Dependencies
We utilize the "Bitcoin Standard" stack combined with hardware-level cryptographic crates to ensure zero-trust M2H operations.

| Component | Crate | Usage |
| :--- | :--- | :--- |
| **Async Runtime** | `tokio` | Multi-threaded scheduler for high-concurrency Fleet API ingestion. |
| **Serialization** | `serde`, `bincode` | Zero-copy deserialization for IPC messages and SB 1417 Audit Logs. |
| **L402 Settlement** | `bdk`, `lightning` (LDK) | Native Rust implementations for Lightning Network HODL invoices. |
| **Error Handling** | `thiserror`, `anyhow` | Structured, propagate-able errors for telemetry. |
| **Hardware Attestation**| `tss-esapi` | Interacting with Vanguard Agent mobile TPM 2.0 / StrongBox modules via FFI. |

---

## 3. Architecture: The Actor Model
The PAN Rust core operates on an **Actor Model** using `tokio::sync::mpsc` channels rather than shared mutable state (`Mutex<T>`), preventing race conditions during concurrent fleet deployments.

1. **The Fleet Ingest Actor:** Consumes incoming UDS fault webhooks from Waymo/Zoox API gateways.
2. **The Sector State Actor:** Manages active Mesa Sector 1 (ODD) deployments, Agent GPS geofencing, and L402 escrow states.
3. **The Attestation Actor:** Cryptographically verifies the Agent's Hardware Root of Trust (EK certificates) before authorizing physical AV intervention.

> [!IMPORTANT]
> **Constraint:** All critical L402 financial logic and SB 1417 audit hashing must be isolated in the **Sector State Actor** to guarantee execution finality.

---

## 4. Safety & Unsafe Code
* **Default:** `#![forbid(unsafe_code)]`
* **Exception:** FFI bindings to the Infineon TPM driver, Apple Secure Enclave APIs, or C-based UDS parsing libraries.
* **Requirement:** Any `unsafe` block must be accompanied by a `// SAFETY:` comment explicitly explaining why hardware invariants are upheld.

---

## 5. Testing Strategy
* **Unit Tests:** Co-located with code. Test pure physical state transitions, not IO.
* **Fuzz Testing:** We use `proptest` to throw randomized, corrupted UDS fault data at the Ingest Engine to ensure L402 funds are *never* locked or released incorrectly.
* **Integration:** Spin up a `regtest` Bitcoin node in CI to verify full AV-to-Human HODL invoice flows.

> *"If it compiles, it settles."*