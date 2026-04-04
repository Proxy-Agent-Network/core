# Proxy Agent Network (PAN) | Compliance & Acceptable Use Policy (AUP)

**Effective Date:** May 1, 2026  
**Version:** 2026.2 (Mesa Pilot — Vanguard 50)  
**Jurisdiction:** Maricopa County, Arizona (Sector 1)  
**Last Revised:** April 2026

Proxy Agent Network (PAN) is committed to operating a secure, strictly regulated, and legally robust physical infrastructure layer for Autonomous Vehicle (AV) fleets. This document outlines the regulatory frameworks, SB 1417 audit mandates, data handling practices, and prohibited activities governing all Vanguard Agents and Fleet API integrations.

---

### 1. Vanguard Agent Certification & Hardware Attestation

To prevent Sybil attacks, ensure physical accountability, and maintain our $5M HNOA/E&O liability shield, all Human Nodes (Agents) must pass strict certification before receiving M2H (Machine-to-Human) dispatch credentials.

| Certification Level | Requirement | Verification Method | Hardware/Security Standard |
| :--- | :--- | :--- | :--- |
| **Identity** | Government-issued ID + social security verification | Checkr API (`driver_pro` package, ~$30/check) | Secure Enclave / TPM 2.0 Device Binding |
| **Background Check** | Driving record, criminal history, county/federal search | Checkr `driver_pro` webhook confirms clearance | Clearance flag set in agent Redis profile before Key Ceremony unlock |
| **Military Service (Preferred)** | DD-214 (Veteran Verification) — preferred but not required | DD-214 upload + manual ops review | Grants priority dispatch queue position |
| **Operational Training** | Optical Reclamation Protocol (ORP) Certification | PAN-administered online + field assessment | Certified ORP supply kit issued on completion |
| **Device Binding** | Hardware Key Ceremony — binds Firebase identity to device TPM | Google Play Integrity attestation (server-side) | StrongBox TPM 2.0. Rooted or emulated devices rejected. |
| **HNOA Authorization** | Policy binding occurs automatically at EN_ROUTE transition | Phase 5 orchestration (policy binds on dispatch, not on hire) | Mission ID + Agent ID + VIN hash recorded in policy binding |
| **NARCAN Certification (Optional)** | Narcan nasal spray administration training | PAN-approved provider (NEXT Distro, local health dept., or equivalent) | `NARCAN_CERTIFIED` flag in agent backend profile. Annual renewal required. *(Pending legal review — see Section 7.)* |

*Note: PAN maintains a "Zero-Identity-Biometric" policy. Agent identity is proven via cryptographic hardware keys and background check records — never via facial recognition, fingerprint storage, or iris scanning. Health and safety biometrics collected by the Aegis Polo (heart rate, SpO2, skin temperature, galvanic skin response) are collected with explicit agent consent for occupational health and safety monitoring purposes only, and are governed separately under Section 5.*

---

### 2. Statutory Compliance: Arizona SB 1417

Under **PAN Protocol v2026.2**, every physical intervention automatically triggers the generation of a sealed, cryptographically-signed **Optical Health Report** to satisfy state regulatory mandates regarding independent AV sensor diagnostics. The report pipeline runs automatically throughout the mission — no agent action is required at any stage.

#### 2.1 Report Binding & Attestation

- **Binding:** Every Unified Diagnostic Service (UDS) fault code (e.g., `LIDAR_OCCLUSION_FRONT`) is mapped to a dynamic, hashed audit log. The HNOA policy binding ID is embedded in the report at EN_ROUTE transition.
- **Hardware Attestation:** Reports include the agent's StrongBox TPM hardware attestation token, cryptographically binding the report to the specific physical device used during the mission.
- **GPS Anchoring:** All events are timestamped and GPS-tagged at time of occurrence, not at mission end. Location data is embedded permanently in the compliance record.
- **Cryptographic Seal:** The completed report is hashed and the hash stored immutably. Any post-hoc modification to the report is detectable.
- **Indemnification:** Fleet Operators (e.g., Waymo, Zoox) indemnify PAN and its Agents against liability arising from pre-existing AV hardware failures not related to the specific ORP intervention.

#### 2.2 Automated SB 1417 Data Sources

The following data streams are appended to the Optical Health Report automatically throughout each mission. This list represents the complete data pipeline as of v2026.2:

| Data Source | Component | What Is Logged |
| :--- | :--- | :--- |
| Photo evidence | Agent smartphone camera | Redacted JPEG frames (720p/3fps). Faces and license plates redacted on-device before upload via `PrivacyFilter.sanitizeImage()`. Raw PII never transmitted. Frame count and redaction count logged. |
| Hardware attestation | Android StrongBox TPM | JWT binding report to specific device hardware |
| Voice log transcripts | Aegis Polo — Communicator Pin (T3) | On-device speech-to-text transcript of agent voice entries. Compliance-relevant exchanges (fault codes, safety protocols, regulatory terms, medical actions) auto-flagged `[COMPLIANCE]` and always appended. Casual exchanges logged but not appended. |
| RATS threat events | PANOPLY Vest — mmWave radar (all tiers) | Threat zone, object classification, approach velocity, detection distance, and whether agent repositioned (inferred from GPS delta). All threat events logged regardless of agent response. |
| Sensor override events | PANOPLY Vest — shoulder override button | Timestamp, agent ID, override duration. Agent pressing the override button cannot be hidden from the compliance record. |
| Pre-approach air quality | PANOPLY Vest — biohazard sensor (T2+) | VOC, CO, H2S, PM2.5, PM10, temperature, humidity — logged at ON_SCENE status transition. Creates a verifiable pre-approach environmental record. |
| Personal breathing zone | Aegis Polo — air quality sensor (T3) | Same air quality metrics as vest sensor, at breathing-zone height. Distinguishes ambient environmental hazard from personal exposure. See Section 5 for data handling. |
| Biometric safety events | Aegis Polo — biometric patch (T3) | Heart rate, SpO2, skin temperature, and stress index — logged only at safety-relevant threshold crossings (heat distress, low oxygen, composite threat escalation). Continuous biometric stream is not logged; only events that cross defined safety thresholds are appended to the compliance record. |
| Conductivity hazard events | Aegis Polo — wrist cuff sensors (T3) | Electrical contact event: timestamp, GPS, tool in hand at time of event, affected hand, alert fired. |
| Approaching vehicle log | PANOPLY Vest — plate camera (T3) | Plate hash (redacted per PrivacyFilter), approach vector, distance, timestamp. Plate numbers are processed on-device and hashed — raw plate text is not stored. |
| Impact event | PANOPLY Vest — spine accelerometer (T3) | G-force vector, welfare check countdown initiated, agent response (cancelled / escalated), outcome. |
| Duress activation | PANOPLY Vest — duress button | GPS pin, timestamp, battery level, video buffer hash (T3). Activation is logged immediately and cannot be retroactively removed. |
| Agent gesture log | Gauntlets VFG-1 (unlocked at 10 missions) | Gesture type, confidence score, partner agent ID (for multi-agent events), tool in hand at time of gesture. |
| Narcan administration | Companion Mode — Communicator Pin (NARCAN_CERTIFIED agents) | Full interaction transcript flagged `[MEDICAL_RESPONSE]`, GPS, timestamp, patient response status. AZ Good Samaritan documentation auto-generated. *(Pending legal review — see Section 7.)* |

#### 2.3 On-Device Privacy Filtering — SB 1417 Photo Pipeline

All photographic and video evidence is processed through an on-device ML redaction pipeline (`PrivacyFilter.sanitizeImage()`) before any data leaves the agent's device:

- Face detection and text recognition run concurrently on every captured frame
- All detected faces and license plates are redacted with an opaque bounding box before upload
- Raw unredacted frames never leave the agent's device under any circumstances
- In the event of an ML processing failure, the pipeline returns a fully black (safe-fail) frame rather than the unredacted original
- The redaction pipeline is compliant with SB 1417, CCPA, and applicable CPRA provisions

---

### 3. Rules of Engagement & Prohibited Interventions

Vanguard Agents are deployed strictly for exterior, edge-case physical recovery. The following actions are strictly prohibited and will result in the immediate revocation of PAN credentials and potential civil liability:

- **Unauthorized Cabin Entry:** Opening vehicle doors or interacting with passengers unless explicitly authorized by a specialized biohazard/debris Fleet webhook.
- **Internal Systems Tampering:** Opening the AV hood, accessing onboard compute units, or touching high-voltage EV systems.
- **Non-Compliant Chemicals:** Utilizing unapproved cleaning agents (e.g., standard glass cleaner or paper towels) on delicate, $20,000+ LiDAR or optical arrays, violating the ORP.
- **Traffic Disruption:** Intervening with a vehicle in an active, high-speed traffic lane without proper DOT-approved hazard signaling and securing the perimeter.
- **Sensor Alert Suppression:** Activating the vest RATS override button without genuine operational justification. Override events are logged to the SB 1417 report and cannot be removed.
- **Credential Sharing:** Allowing another individual to use an agent's PAN Command app, hardware-bound device, or registered Vanguard Field System equipment. Hardware Key Ceremony binding is per-device and per-person; credential sharing is detectable.
- **Evidence Tampering:** Any attempt to circumvent or disable the `PrivacyFilter` pipeline, modify evidence frames, or interrupt the SB 1417 report generation pipeline.

---

### 4. Settlement, Escrow & Agent Earnings

- **L402 HODL Invoices:** Intervention bounties are locked in Lightning Escrow upon AV task broadcast and only released when the three-stage settlement oracle is satisfied: (1) hardware attestation, (2) SB 1417 compliance confirmation, (3) AV-signed Ed25519 Ed25519 payload verified by Rust smart contract.
- **Agent Earnings Split:** Agents receive 90% of the settled bounty. The remaining 10% covers network operational costs. This split is fixed and disclosed to agents at onboarding.
- **Surge Pricing:** Bounties are dynamically adjusted when Agent Utilization Ratio (AUR) exceeds 75%. Maximum surge is 3.0× the base rate. Surge is applied before the 90/10 split — agents benefit from surge in full proportion.
- **Multi-Agent Collaboration Bonuses:** Agents operating on the same incident may earn verified collaboration bonuses ($5.00 base, $7.00 flourish upgrades) through the Gauntlets VFG-1 gesture system. Bonuses require NFC bilateral cryptographic confirmation that two registered agents made physical contact on the same `incident_id`. Bonus eligibility is capped at 3 events per agent pair per 8-hour shift to prevent gaming.
- **Strict SLA Geofencing:** Tasks are only dispatched to Agents within a highly restricted physical radius (< 3 miles) to mathematically guarantee our 15-minute response SLA.

---

### 5. Data Retention, Privacy & Agent Health Data

#### 5.1 General Data Handling

- **Zero PII Intercept:** PAN webhooks do not ingest, process, or store passenger personally identifiable information (PII), interior cabin video feeds, or fleet routing destinations.
- **On-Device Redaction:** All photo and video evidence is redacted on the agent's device before transmission. Raw PII never traverses the PAN network.
- **Fleet Partner Isolation:** Fleet partners receive only task outcomes and Optical Health Report hashes. Fleet partners do not receive agent identity information, agent location history beyond mission GPS pins, or raw compliance report contents.

#### 5.2 Agent Location Data — Correction from Prior Version

> **Note:** The prior version of this document (v2026.1) stated that "Agent GPS/UWB telemetry is stored in volatile memory to facilitate routing and is wiped upon mission completion." This statement is **no longer accurate** as of v2026.2.

Agent GPS coordinates are embedded permanently in SB 1417 Optical Health Reports alongside every logged event. This is required by Arizona regulatory mandates — compliance reports without GPS anchoring are not valid under SB 1417. Location data within compliance reports is retained permanently for regulatory audit purposes. Agent GPS data used for real-time dispatch routing (Redis geospatial index) continues to be ephemeral and is cleared at mission completion.

#### 5.3 Agent Health & Safety Biometric Data

The Aegis Polo VFP-1 (Tier 3, 200 missions) collects health and safety biometric data — heart rate, SpO2, skin temperature, and galvanic skin response — from agents during ON_SCENE operations. This data is collected and handled as follows:

- **Consent:** Agents explicitly consent to health biometric monitoring during Aegis Polo pairing setup. Consent can be withdrawn by unpairing the polo, which disables all biometric monitoring.
- **Purpose:** Data is used exclusively for (a) real-time agent safety monitoring and emergency response, (b) personalized thermal management, and (c) SB 1417 compliance logging of safety-relevant threshold events.
- **Fleet Manager Access:** Fleet managers can view real-time safety alerts (heat distress, low SpO2) and aggregate occupational health data (UV exposure, air quality exposure history) for agents in their roster. Fleet managers do not have access to continuous biometric streams.
- **Agent Access:** Agents can view their own complete biometric history in PAN Command.
- **Third-Party Disclosure:** Health biometric data is not sold, licensed, or shared with any third party. Fleet partners receive safety alert notifications but not the underlying biometric readings.
- **Retention:** Safety-event biometric snapshots embedded in SB 1417 reports are retained permanently. Continuous biometric streams not crossing safety thresholds are retained for 90 days then purged.

#### 5.4 Cognitive Vault — Companion Mode Data

Agent interactions with Proxy-Alpha (Companion Mode) are encrypted at rest using AES-256 via the Cognitive Vault. The encryption key is unique per deployment instance and static — key rotation invalidates all stored interactions. Fleet managers see interaction metadata (count, duration, compliance topics covered) but never the full transcript. Agent voice transcripts are the private record of the agent's interaction with the AI system.

---

### 6. Vanguard Field System — Compliance Hardware

The Project Copperfield Vanguard Field System is PAN's proprietary intelligent wearable platform. All four components contribute to the automated SB 1417 compliance pipeline. Hardware attestation for compliance purposes uses the agent's smartphone StrongBox TPM — wearable components are registered to the agent profile and their involvement in compliance logging is recorded but they do not independently attest.

| Component | Compliance Role | Tier Unlock |
| :--- | :--- | :--- |
| **HapHat v2.3** | Agent identity surface (NFC brim-tap). Provides visual mission state confirmation to fleet managers and first responders. | All tiers |
| **PANOPLY Vest v1.2** | RATS threat detection logging. Pre-approach air quality logging. LED back panel visual compliance display. Body camera evidence pipeline (T3). License plate detection log (T3). Duress event logging. | All tiers (T2/T3 features unlock at 50/200 missions) |
| **Aegis Polo VFP-1** | Voice log transcripts via Communicator Pin. Health biometric safety event logging. Personal air quality logging. Conductivity hazard event logging. UV exposure occupational health record. Narcan administration documentation. | Tier 3 (200 missions) |
| **Gauntlets VFG-1** | Multi-agent collaboration bonus verification (NFC bilateral cryptographic confirmation). Tool-in-hand context for voice log entries. Agent gesture log. | Unlocks at 10 missions |

---

### 7. Pending Legal Review Items

The following features are documented in PAN's technical specifications but require legal counsel review before production deployment:

| Item | Status | Blocking Concern |
| :--- | :--- | :--- |
| **Narcan Emergency Pocket (NARCAN_CERTIFIED agents)** | ⚠️ Pending legal review | AZ Good Samaritan statute scope, HNOA policy coverage for medical response actions, PAN vicarious liability during agent-administered Narcan, training certification partnership agreements. The standard (non-Narcan) Emergency Pocket does not require legal review and may proceed independently. |
| **Biometric Health Data — CCPA/CPRA Classification** | ⚠️ Under review | Arizona currently has no standalone biometric privacy statute, but CCPA/CPRA may apply to California-based fleet partners accessing agent health data. Legal review of data processing agreements with fleet partners required. |
| **SB 1417 Scope Confirmation** | ⚠️ Monitoring | SB 1417 effective December 31, 2026. PAN compliance pipeline is designed to the known requirements as of April 2026. Final regulatory guidance may modify logging requirements. PAN will update compliance pipeline as final rules are published. |

---

### 8. Incident Reporting & Escalation Protocol

- **Duress Events:** Any agent duress button activation triggers immediate fleet manager notification and GPS pin. Escrow for the active mission is placed on hold pending welfare confirmation. If the agent does not confirm safe status within the response window, emergency contact notification and fleet manager escalation are triggered automatically.
- **RATS Zone 1 Events:** All Zone 1 (0–5m imminent threat) detections are logged to the SB 1417 report regardless of outcome. If an agent experiences a Zone 1 event, the fleet manager receives an automatic incident alert with GPS coordinates, threat velocity data, and agent biometric state at time of detection (T3 only).
- **Impact Events:** Spine accelerometer impact detection (T3) triggers a 60-second welfare check countdown. Non-response escalates to fleet manager and agent emergency contact. All impact events are permanently logged regardless of outcome.
- **Electrical Contact Events:** Conductivity threshold breach (T3) is logged immediately with tool context. If the agent does not confirm safe status via PAN Command within 5 minutes of a conductivity event, fleet manager is notified.

---

**CONFIDENTIAL // PROPRIETARY INFRASTRUCTURE**  
*© 2026 PROXY AGENT NETWORK LLC. All Rights Reserved.*  
*Questions regarding this document: rob@proxyagent.network*
