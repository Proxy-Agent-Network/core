# Proxy Agent Network (PAN) | Compliance & Acceptable Use Policy (AUP)

**Effective Date:** May 1, 2026 
**Version:** 2026.1 (Mesa Pilot)
**Jurisdiction:** Maricopa County, Arizona (Sector 1)

Proxy Agent Network (PAN) is committed to operating a secure, strictly regulated, and legally robust physical infrastructure layer for Autonomous Vehicle (AV) fleets. This document outlines the regulatory frameworks, SB 1417 audit mandates, and prohibited activities governing all Vanguard Agents and Fleet API integrations.

---

### 1. Vanguard Agent Certification & Hardware Attestation
To prevent Sybil attacks, ensure physical accountability, and maintain our $5M HNOA/E&O liability shield, all Human Nodes (Agents) must pass strict certification before receiving M2H (Machine-to-Human) dispatch credentials.

| Certification Level | Requirement | Hardware/Security Standard |
| :--- | :--- | :--- |
| **Identity/Background** | DD-214 (Veteran Verification) & AZ State Background Check | Secure Enclave / TPM 2.0 Device Binding |
| **Operational Training** | Optical Reclamation Protocol (ORP) Certification | Certified "HP Potion" ORP supply kit |
| **API Authorization** | L402 Wallet Setup & Geofence Validation | Sector 1 (85212) 15-Minute Radius limit |

*Note: PAN strictly adheres to a "Zero-Biometric" policy. Identity is proven via cryptographic hardware keys, not facial recognition or fingerprint storage.*

### 2. Statutory Compliance: Arizona SB 1417
Under **PAN Protocol v2026.1**, every physical intervention automatically triggers the generation of an **Optical Health Report** to satisfy state regulatory mandates regarding independent AV sensor diagnostics.
* **Binding:** Every Unified Diagnostic Service (UDS) fault code (e.g., `LIDAR_OCCLUSION_FRONT`) is mapped to a dynamic, hashed audit log.
* **Attestation:** Reports include the Agent's hardware ID, the GPS coordinates of the intervention, and a cryptographic execution hash.
* **Indemnification:** Fleet Operators (e.g., Waymo, Zoox) indemnify PAN and its Agents against liability arising from pre-existing AV hardware failures not related to the specific ORP intervention.

### 3. Rules of Engagement & Prohibited Interventions
Vanguard Agents are deployed strictly for exterior, edge-case physical recovery. The following actions are strictly prohibited and will result in the immediate revocation of PAN credentials and potential civil liability:
* **Unauthorized Cabin Entry:** Opening vehicle doors or interacting with passengers unless explicitly authorized by a specialized biohazard/debris Fleet webhook.
* **Internal Systems Tampering:** Opening the AV hood, accessing onboard compute units, or touching high-voltage EV systems.
* **Non-Compliant Chemicals:** Utilizing unapproved cleaning agents (e.g., standard glass cleaner or paper towels) on delicate, $20,000+ LiDAR or optical arrays, violating the ORP.
* **Traffic Disruption:** Intervening with a vehicle in an active, high-speed traffic lane without proper DOT-approved hazard signaling and securing the perimeter.

### 4. Settlement & Geofence Security
* **L402 HODL Invoices:** Intervention bounties are locked in Lightning Escrow upon AV task broadcast and only released when the AV clears its own fault code.
* **Strict SLA Geofencing:** Tasks are only dispatched to Agents within a highly restricted physical radius (e.g., < 3 miles) to mathematically guarantee our 15-minute response SLA.

### 5. Data Retention & Passenger Privacy
* **Zero PII Intercept:** PAN webhooks do not ingest, process, or store passenger personally identifiable information (PII), interior cabin video feeds, or fleet routing destinations.
* **Ephemeral Location:** Agent GPS/UWB telemetry is stored in volatile memory to facilitate routing and is wiped upon mission completion. 
* **Permanent Audit Data:** Only the cryptographic execution hashes (Optical Health Reports) and L402 transaction receipts are retained permanently to satisfy Arizona Department of Public Safety (DPS) audit requirements.

---
**CONFIDENTIAL // PROPRIETARY INFRASTRUCTURE**
*© 2026 PROXY AGENT NETWORK LLC. All Rights Reserved.*