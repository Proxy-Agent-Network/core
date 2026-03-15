# Contributing to Proxy Agent Network (PAN)

Welcome to the PAN Core Infrastructure repository. We actively welcome contributions from automotive engineers, DePIN developers, and hardware security specialists who are building the physical recovery layer for the autonomous vehicle (AV) era.

## How to Contribute (The Vanguard Standard)

All contributions to the PAN M2H (Machine-to-Human) gateway must meet enterprise-grade reliability standards, as this code directly impacts the physical safety of high-value fleet assets and our Veteran workforce.

1.  **Fork the Project:** Create your isolated environment.
2.  **Create a Branch:** `git checkout -b feature/UWB_Homing_Optimization`
3.  **Commit your Changes:** `git commit -m 'Enhance Ultra-Wideband proximity logic for Sector 1'`
4.  **Push to the Branch:** `git push origin feature/UWB_Homing_Optimization`
5.  **Open a Pull Request:** Ensure your PR description explicitly states how this impacts the Mesa Pilot SLA or SB 1417 compliance.

## Engineering Standards

* **Language:** Python (PEP 8) and Rust (for Secure Enclave/TPM 2.0 bindings).
* **API Specs:** All Fleet Gateway endpoint modifications must be documented in `/docs/v2026.1/`.
* **Zero-Trust Security:** Never commit API keys, L402 Macaroons, or testnet Lightning node credentials.
* **Testing:** All PRs affecting the `/src/L402-Gateway/` or the `/hardware-node/` modules require a minimum of 90% test coverage simulating AV diagnostic fault ingestion.

## Governance & Protocol Upgrades

Major changes to the PAN protocol—such as altering the dynamic L402 surge pricing logic, modifying the 15-minute SLA enforcement parameters, or expanding the Operational Design Domain (ODD)—require formal consensus. Please open an Issue tagged `[RFC]` (Request for Comment) to initiate discussion with Fleet Partners and PAN Command before writing code.

## Hardware & Compliance Contributions

We actively welcome contributions that enhance our physical security and statutory reporting capabilities:

### 1. SB 1417 Audit Enhancements
* **Requirement:** Must map directly to Arizona Revised Statutes Title 28, Chapter 24 (Autonomous Vehicles).
* **Focus:** Improving the cryptographic hashing and immutability of the "Optical Health Reports."

### 2. Optical Reclamation Protocol (ORP)
* **Requirement:** Proposed changes to physical cleaning procedures (e.g., new microfiber standards or chemical solvent limits) must cite current LiDAR/Camera OEM manufacturer specifications (e.g., Waymo, Luminar, Hesai).
* **Review:** Physical protocol changes require sign-off from PAN Command to ensure they do not void the $5M HNOA/E&O Liability Shield.

Thank you for building the critical physical infrastructure required to scale L4 Autonomy.