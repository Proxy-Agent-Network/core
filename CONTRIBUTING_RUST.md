# Rust Protocol Engineering Guidelines

| Status | Scope |
| :--- | :--- |
| **Active** | Core Settlement Layer Migration (Python -> Rust) |

As Proxy Protocol scales to handle **10,000+ TPS** (Transactions Per Second) on the Lightning Network, we are migrating our core financial state machines to Rust. This document outlines the architectural constraints for this migration.

---

## 1. The Philosophy: "Correct by Construction"
In the Python implementation, we relied on runtime checks; in Rust, we rely on the **Type System**.

* **Rule:** Invalid states should be unrepresentable. Use `Enums` to define state machines (e.g., `EscrowState::Locked`, `EscrowState::Settled`).
* **Rule:** **No `unwrap()`**. Handle every `Result` explicitly. Panics in the settlement layer are unacceptable.

---

## 2. Core Stack & Dependencies
We utilize the "Bitcoin Standard" stack to ensure maximum compatibility with LND and LDK.

| Component | Crate | Usage |
| :--- | :--- | :--- |
| **Async Runtime** | `tokio` | Multi-threaded scheduler for high-concurrency IO. |
| **Serialization** | `serde`, `bincode` | Zero-copy deserialization for IPC messages. |
| **Bitcoin/LN** | `bdk`, `lightning` (LDK) | Native Rust implementations for HODL invoice logic. |
| **Error Handling** | `thiserror`, `anyhow` | Structured, propagate-able errors. |
| **Hardware** | `tss-esapi` | Interacting with the TPM 2.0 module via FFI. |

---

## 3. Architecture: The Actor Model
The Rust core operates on an **Actor Model** using `tokio::sync::mpsc` channels rather than shared mutable state (`Mutex<T>`).

1. **The Ingest Actor:** Consumes API requests from the Python Gateway.
2. **The State Actor:** Manages the in-memory order book and escrow states.
3. **The Settlement Actor:** Signs transactions via TPM and broadcasts to LND.

> [!IMPORTANT]
> **Constraint:** All critical financial logic must be isolated in the **State Actor** to prevent race conditions.

---

## 4. Safety & Unsafe Code
* **Default:** `#![forbid(unsafe_code)]`
* **Exception:** FFI bindings to the Infineon TPM driver or C-based computer vision libraries.
* **Requirement:** Any `unsafe` block must be accompanied by a `// SAFETY:` comment explaining why invariants are upheld.

---

## 5. Testing Strategy
* **Unit Tests:** Co-located with code. Test pure logic, not IO.
* **Fuzz Testing:** We use `proptest` to throw randomized data at the Settlement Engine to ensure funds are never released incorrectly.
* **Integration:** Spin up a `regtest` Bitcoin node in CI to verify full HODL invoice flows.

> *"If it compiles, it settles."*
