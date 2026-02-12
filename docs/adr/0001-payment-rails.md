# ADR 001: Selecting Lightning Network for Micro-Settlements

**Date:** 2025-06-15  
**Status:** Accepted  
**Context:** Internal R&D Phase 1

---

## Context
The Proxy Protocol requires a settlement layer to transfer value from AI Agents (Principals) to Human Nodes (Proxies).

* **Constraint 1:** Transactions must be trustless (escrow capable).
* **Constraint 2:** Tasks may be low value (e.g., $0.50 for an SMS verification).
* **Constraint 3:** Settlement must be near-instant (human completes task -> gets paid).

## Options Considered

### 1. Traditional Fiat (Stripe Connect)
* **Pros:** Easy developer experience.
* **Cons:** High fees ($0.30 + 2.9%) make micro-tasks impossible. Requires Agents to have bank accounts (KYC friction).
* **Verdict:** Rejected.

### 2. Ethereum / L2s (Optimism/Base)
* **Pros:** Smart contract capability.
* **Cons:** Gas fees are unpredictable. Wallet UX is still high-friction for non-crypto natives.
* **Verdict:** Rejected for v1.

### 3. Bitcoin Lightning Network (LNV2)
* **Pros:** Sub-cent fees. Instant settlement. **HODL Invoices** allow for cryptographic escrow without a central custodian holding funds.
* **Cons:** Liquidity management requires running a specialized node.
* **Verdict:** **Selected.**

---

## Decision
We will use the **Bitcoin Lightning Network** utilizing HODL Invoices for the primary escrow mechanism.

## Consequences
* We must build a custom Python wrapper for LND (Lightning Network Daemon).
* Agents must hold BTC to transact (we will provide a fiat on-ramp partner later).
* This aligns with our **"Sovereign Agent"** philosophy.
