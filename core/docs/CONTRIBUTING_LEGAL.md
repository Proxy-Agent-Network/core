# Contributing to PAN Compliance & Legal Operations

Welcome to the **Proxy Agent Network (PAN) Compliance & Legal** track. While much of this repository focuses on hardware attestation and L402 cryptography, our mission—providing the physical recovery layer for autonomous vehicle (AV) fleets—is impossible without a bulletproof statutory and liability framework.

We need legal engineers, automotive compliance experts, and risk modelers to help us standardize the **Optical Health Reports** and **Liability Delegation Instruments** that allow Vanguard Agents to operate safely within regulated Operational Design Domains (ODDs).

---

## 1. Our Compliance Philosophy
PAN treats regulatory compliance as programmatic code. When an Agent physically intervenes with a grounded AV (e.g., clearing a LiDAR sensor), the protocol must generate a cryptographically verifiable, legally binding audit log that satisfies both fleet insurance carriers and state Departments of Transportation (e.g., Arizona DPS/DMV).

**We prioritize:**
* **Strict Statutory Alignment:** Logs must map directly to state mandates (e.g., Arizona SB 1417).
* **Cryptographic Chain of Custody:** Every legal/audit log must reference a specific Unified Diagnostic Service (UDS) fault code and the Agent's hardware TPM signature.
* **Liability Shielding:** Clear delineation of liability between the Fleet Operator's AI, the PAN Gateway, and the biological Agent.

---

## 2. Where to Contribute
All statutory templates, audit schemas, and liability frameworks are located in the `/docs/compliance/` directory.

---

## 3. Audit Template Structure
To maintain consistency for the Fleet API and state regulators, all SB 1417 Audit templates must follow this strict structure:

| Section | Focus | Placeholders |
| :--- | :--- | :--- |
| **A. Asset Identification** | Identification of the Fleet Operator & AV | `[FLEET_ID]`, `[VIN_HASH]` |
| **B. Intervention Scope** | Definition of the physical task authorized | `[UDS_FAULT_CODE]`, `[ORP_PROTOCOL_ID]` |
| **C. Attestation & Timestamp** | Hardware proof of presence and completion | `[AGENT_TPM_PUBKEY]`, `[L402_SETTLEMENT_TX]` |

---

## 4. Technical Requirements
You do not need to be a Rust or Python developer to contribute to this track, but your documents must follow these rules:

* **Format:** Use standard Markdown (`.md`) or JSON Schema (`.json`) for audit payloads.
* **Variables:** Use square brackets for programmatic data (e.g., `[TIMESTAMP]`, `[UDS_CODE]`).
* **Citations:** Every compliance template MUST cite the governing state legislation at the top (e.g., *Arizona Revised Statutes Title 28-9701*).

---

## 5. The Submission Process
1. **Fork the Repo:** Create your own copy of the repository.
2. **Draft your Schema:** Create or edit a file in `/docs/compliance/`.
3. **Submit a Pull Request (PR):**
   * Title your PR starting with `[COMPLIANCE]`.
   * Explicitly explain why this update is required (e.g., "Updating liability waiver to cover new Waymo Zeekr cabin entry procedures").
4. **Review:** A PAN Command maintainer with automotive risk/legal experience will review the PR to ensure it does not void our $5M HNOA/E&O policy.

---

## 6. Proposing New Intervention Types
If you believe the protocol needs to support a new type of physical task (e.g., "Biohazard Cabin Removal" or "Manual Intersection Takeover"), please open a **Discussion** in the repository rather than a PR. We must first debate the severe physical safety and insurance implications with our Fleet Partners before writing code.