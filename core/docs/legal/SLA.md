# Proxy Agent Network (PAN) | Service Level Agreement

**Document Version:** 2026.1
**Jurisdiction / ODD:** Mesa, AZ (Sector 1)
**Effective Date:** May 22, 2026

This Service Level Agreement (SLA) dictates the operational commitments, response times, and financial remedies between Proxy Agent Network ("PAN") and integrated Autonomous Vehicle (AV) Fleet Operators.

---

## 1. Network Availability & API Uptime
PAN guarantees a **99.99% uptime** for the Fleet Gateway API and L402 Settlement Engine.
* **Scheduled Maintenance:** Conducted between 0200 - 0400 MST. Fleets will be notified 72 hours in advance.
* **Redundancy:** Distributed master nodes ensure seamless M2H (Machine-to-Human) webhook ingestion even during regional AWS/GCP outages.

## 2. The Vanguard Response Guarantee (Time-to-Site)
Within the designated Mesa Sector 1 Operational Design Domain (ODD), PAN guarantees the following response metrics for "Priority" L402 bounties:

* **Dispatch Latency:** < 5 seconds from UDS fault ingestion to Agent alert.
* **Target Arrival (ETA):** < 12 minutes.
* **Maximum SLA Boundary:** 15 minutes.
* **Remedy for Breach:** If a Proxy Agent fails to arrive within the 15-minute SLA, the Fleet Operator's smart contract escrow is instantly refunded, the task is re-routed to a secondary Agent at PAN's expense, and the at-fault Agent suffers a Reputation Slash.

## 3. Intervention Resolution Standards
Proxy Agents are deployed strictly for physical edge-case resolution. PAN guarantees:
* **Hardware Attestation:** Every arriving Agent is cryptographically verified via device Secure Enclave / TPM 2.0 prior to intervention.
* **Optical Reclamation Protocol (ORP):** Agents will exclusively utilize certified "HP Potion" supplies (MIL-SPEC microfiber, sensor-safe solvents) to prevent damage to $150k+ LIDAR/Camera arrays.
* **Zero-Tampering:** Agents will not access the vehicle cabin unless explicitly requested by the Fleet API for interior biohazard/debris removal.

## 4. Settlement & L402 Escrow Finality
PAN operates a zero-trust, conditional payment architecture:
* Bounties are locked in Lightning Network smart contracts upon task dispatch.
* **Condition of Release:** Funds are ONLY released to the Agent when the AV's onboard AI (UDS) confirms the fault code is physically cleared.
* If an Agent arrives but fails to clear the hardware fault, the bounty is returned to the Fleet Treasury. You only pay for successful resolution.

## 5. Regulatory Audit Compliance (SB 1417)
For every completed mission, PAN guarantees the generation of a cryptographic "Optical Health Report" within 60 seconds of task resolution. These logs are retained and made available to Fleet Operators to satisfy Arizona SB 1417 mandates for independent system diagnostic audits.

---
*For SLA escalations or API integration support, contact: command@proxyagent.network*