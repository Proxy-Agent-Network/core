# Proxy Protocol Incident Response Playbook (v1.1)

**Status:** Active  
**Classification:** Operational Security (Internal/Partner)

This document defines the mandatory response protocols for "Scorched Earth" and "Protocol-Level" emergencies.

---

## 1. Severity Levels

| Level | Description | Example |
| :--- | :--- | :--- |
| **SEV-1 (Critical)** | Direct loss of funds, mass PII leak, or unverified hardware signing. | TPM bypass, Escrow logic bug. |
| **SEV-2 (High)** | Prolonged outage or systemic desync. | LN Partition, 30min+ API downtime. |
| **SEV-3 (Moderate)** | Degraded performance or UI latency. | Webhook delays, Reputation drift. |

---

## 2. SEV-1 Protocol: The "Kill Switch"

In the event of a catastrophic failure, the Core Team triggers the Circuit Breaker:

1.  **Bridge Freeze:** Broadcast a `PAUSE` signal to the LND Gateway. This prevents any new HODL invoices from being accepted.
2.  **State Snapshot:** Force a read-only state on the Task Mempool for forensic auditing.
3.  **Disclosure:** Immediate status update via `security@proxyagent.network` and the official Status Page.

---

## 3. Playbook: Protocol-Level Emergencies

### A. Lightning Network Split / Chain Partition
**Symptom:** Nodes report "Accepted" invoices that the API Gateway cannot see, or massive force-closure waves.

**Mitigation:**
* Transition all Escrow Logic to **Optimistic Local Mode**.
* Nodes are instructed to switch to `nostr_fallback.py` to broadcast preimages to the censorship-resistant layer.
* Agent SDKs will poll Nostr relays for proof hashes to manually release HTLCs once connectivity is restored.

### B. Jury Collusion (Mass-Collusion Attack)
**Symptom:** Verifiably correct proofs are being rejected by the Jury Tribunal (Schelling Point failure).

**Mitigation:**
1.  **Governance Freeze:** Temporarily suspend the automated Jury VRF selection.
2.  **Escalation:** Divert all disputed tasks above 50,000 Sats to the Appellate Court (7 manually verified Elite Jurors).
3.  **Slashing:** Identify the Sybil cluster (linked nodes/IPs) and perform a mass-burn of their staked BTC.

### C. Zero-Day Hardware Vulnerability (TPM Bypass)
**Symptom:** Discovery of a method to export "sealed" private keys from the Infineon OPTIGA™ chip.

**Mitigation:**
1.  **Node Invalidation:** Revoke the `AK_HANDLE` (Attestation Key) for all nodes running the affected firmware version.
2.  **Mandatory Re-Binding:** Force all Tier 2/3 nodes to perform a new Key Generation Ceremony with patched SDKs.
3.  **Reputation Snapshot:** Preserve operator scores but require a new hardware collateral lock.

---

## 4. Communication Matrix

* **SEV-1 Alert:** security@proxyagent.network
* **Public Status:** [status.proxyagent.network](https://status.proxyagent.network)
* **Encrypted Signal Line:** (Partner Access Only)

---

## 5. Post-Mortem Requirement

Every SEV-1 or SEV-2 event must be followed by a public Incident Report in the `security/audits` directory within **72 hours**, detailing the root cause and the "Anti-Fragile" remediation steps taken.

> *“Trust is hard-won and mathematically preserved.”*
