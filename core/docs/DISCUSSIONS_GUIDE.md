# Proxy Agent Network (PAN) | Discussions & Integration Guide

Welcome to the Proxy Agent Network (PAN) technical forum. This repository serves as the primary communication channel for our Fleet Partners (Waymo, Zoox, Cruise, etc.), Vanguard Agents, and infrastructure developers coordinating operations within the Mesa, AZ (Sector 1) deployment.

---

## 1. Where to Post?

To maintain the operational integrity of our engineering channels, please categorize your post correctly:

| Category | Usage |
| :--- | :--- |
| **🛠️ Fleet API Integration** | "How does our UDS webhook authenticate with the PAN Gateway?" (B2B Support) |
| **🛡️ SB 1417 Compliance** | Discussions regarding the cryptographic formatting of Optical Health Reports. |
| **💡 Protocol Proposals** | "Suggesting a new V2X standard for automated Agent dispatch." (Brainstorming) |
| **⚙️ Hardware Node Ops** | Troubleshooting TPM 2.0 / Secure Enclave attestation for Vanguard Agents. |
| **💬 General Sector Comms** | Operational updates regarding the Mesa Pilot or Maricopa expansion. |

> [!IMPORTANT]
> **Do NOT use the "Issues" tab for integration questions.** The Issues tab is strictly reserved for confirmed bugs, SLA breaches, and L402 settlement failures. General questions posted as Issues will be automatically converted to Discussions by the PAN Command team.

---

## 2. Protocol Upgrades (The PAN RFC Process)

Before submitting a formal **Request for Comment (RFC)** via a Pull Request to modify the core PAN protocol (e.g., altering the L402 base bounty algorithm or updating the Optical Reclamation Protocol), you must champion the concept here first to ensure alignment with our Fleet Partners.

1.  **Draft:** Post your idea in the **Protocol Proposals** category with the prefix `[RFC]`.
2.  **Debate:** Engage with the engineering community for a minimum of **7 days**.
3.  **Refine:** Incorporate feedback into your technical specification, paying special attention to AV safety and SB 1417 audit implications.
4.  **Submit:** Once you achieve rough consensus, open a formal Issue using the `protocol_upgrade` template.

---

## 3. Operational Etiquette

* **Zero-Tolerance for PII:** Do not post raw logs that contain personally identifiable information (passenger data, license plates, or unmasked exterior camera feeds). All telemetry must be sanitized before posting.
* **No Speculation:** PAN is a physical infrastructure network, not a speculative token project. Discussions regarding secondary market trading or "tokenomics" are strictly prohibited and will be deleted.
* **Professional Conduct:** Criticize the code or the process, not the engineers or the Vanguard Agents.

Please refer to [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) for our strict enforcement policies regarding operational security and professionalism.