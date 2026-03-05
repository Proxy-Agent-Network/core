# Proxy Agent Network (PAN) | Governance & Trust Framework

**The decentralized rules engine governing the Machine-to-Human (M2H) economy and Vanguard Agent operations.**

Proxy Agent Network (PAN) operates as the critical physical bridge between autonomous vehicle (AV) intent and real-world execution. To ensure the safety of $150k+ fleet assets and the integrity of our Veteran workforce, we enforce a strict, "Zero-Trust" Governance Model.

---

## 1. Hardware-Backed Identity (No Biometrics)
To comply with stringent data privacy standards (and the 2026 Delete Act), PAN **does not** collect, store, or process biometric data (FaceID, fingerprints, or retinal scans).

* **Proof of Node:** All Proxy Agents (Human Nodes) authenticate exclusively via their mobile device’s hardware security module (Apple Secure Enclave or Android StrongBox/TPM 2.0).
* **The Guarantee:** Every physical intervention and SB 1417 audit log is cryptographically signed by the device hardware, mathematically proving the authorized Agent was present on-site without storing personally identifiable biometrics on PAN servers.

## 2. Automated Adjudication (L402 Escrow)
PAN eliminates human "dispatchers" and subjective management. Financial settlement and dispute resolution are programmatic.

* **Locked Bounties:** Upon an AV issuing an M2H task (e.g., sensor occlusion), the L402 Lightning bounty is locked in a smart contract.
* **Algorithmic Release:** Funds are released to the Agent **only** when the AV's onboard AI (Unified Diagnostic Service) autonomously confirms the fault code is cleared.
* **No "Juries":** If the vehicle's AI says the sensor is still dirty, the task is failed. There is no subjective human appeals process for physical asset health.

## 3. The Reputation Engine (SLA & Slashing)
Agent standing within the network is dictated purely by performance telemetry, not human managers.

* **The 15-Minute SLA:** Agents must arrive at the stranded AV within 15 minutes of accepting a mission. Consistent failure to meet this SLA results in a "Reputation Slash."
* **The "Vanguard" Tier:** Agents who maintain a 98% SLA success rate and zero sensor damage reports are elevated to the "Vanguard" tier, granting them priority access to high-bounty, high-priority fleet interventions.
* **Zero-Tolerance Slashing:** Any attempt to spoof GPS location, bypass hardware attestation, or utilize unapproved cleaning chemicals (violating the Optical Reclamation Protocol) results in an immediate, permanent ban from the PAN protocol.

## 4. Protocol Upgrades (RFCs)
Major changes to the PAN protocol—such as integrating new AV diagnostic APIs, updating the Base Bounty minimums, or expanding the Operational Design Domain (ODD) beyond Maricopa County—must be proposed as a Request for Comment (RFC) in the public repository Issues to ensure transparency with our Fleet Partners.