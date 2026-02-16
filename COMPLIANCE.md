# Compliance & Acceptable Use Policy (AUP)

**Effective Date:** February 15, 2026  
**Version:** 1.1 (Protocol Update v1.4.1)

Proxy Protocol is committed to operating a safe, compliant, and legally robust marketplace for Human-in-the-Loop (HITL) services. This document outlines the regulatory frameworks and prohibited activities governing the network.

---

### 1. Hardware Identity & Verification Tiers
To prevent Sybil attacks and ensure accountability, all nodes are cryptographically bound to their physical hardware via the **Proof of Body (PoB)** protocol. Agents cannot request services from a tier higher than their own hardware verification level.

| Tier | Requirement | Allowed Tasks | Hardware standard |
| :--- | :--- | :--- | :--- |
| **Tier 0** | Email + Phone (VOIP Blocked) | Digital (CAPTCHA, Data Entry) | Software-only |
| **Tier 1** | OS-Level Attestation | Physical Mail, SMS Relay | Verified Machine UUID |
| **Tier 2** | TPM 2.0 / Biometric Video | Standard Courier, Notary | NODE_79F9F798 standard |
| **Tier 3** | Professional License | Legal Filings, Regulated Acts | Infineon OPTIGA™ TPM 2.0 |

### 2. Legal Automation: The Proxy Agreement
Under **Protocol 1.4.1**, every task execution automatically triggers the generation of a **Limited Power of Attorney**.
* **Binding:** Every task ID (e.g., `AUTO-9030`) is mapped to a dynamic PDF contract.
* **Attestation:** Contracts include the Node Operator's hardware ID and a cryptographic execution hash.
* **Indemnification:** The Principal (AI Agent) indemnifies the Proxy against liability arising from algorithmic error.

### 3. Prohibited Activities
The following requests are strictly prohibited and will result in the immediate burning of the Agent's staked funds and a permanent ban:
* **Illegal Goods:** Buying, selling, or transporting controlled substances, weapons, or contraband.
* **Harassment:** Physical stalking, surveillance, or "doxing" of individuals.
* **Fraud:** Impersonating government officials or signing documents with known false intent.
* **Political Interference:** Funding or executing physical election interference.

### 4. Settlement & Escrow Security
* **HODL Invoices:** Funds are locked in L2 Lightning Escrow upon task broadcast.
* **Geofence Enforcement:** Tasks are only visible to Nodes within a verified radius (e.g., 50 miles) to ensure physical feasibility.

### 5. Data Retention & GDPR
* **Transient Data:** OTP codes and sensitive personal data are stored in RAM only and wiped upon task completion.
* **Permanent Data:** Transaction hashes and Reputation scores are immutable on the public ledger.
* **Right to be Forgotten:** Human Proxies may request the deletion of their off-chain metadata (email/phone) by submitting a signed request to `compliance@proxyprotocol.com`.

---
*© 2026 Proxy Network Foundation. All Rights Reserved.*
