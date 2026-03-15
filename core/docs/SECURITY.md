# Security Policy & Defense-in-Depth

We treat the security of the Proxy Agent Network (PAN) as mission-critical. Because our protocol interfaces directly with high-value Autonomous Vehicle (AV) hardware and financial settlement rails, we enforce a strict, zero-trust, multi-layered defense strategy.

---

## 1. The Defense-in-Depth Architecture
Our security model relies on three independent pillars to ensure the integrity of the Machine-to-Human (M2H) economy. Compromising one layer does not compromise the network.

### A. Hardware Root of Trust (Identity Layer)
* **Secure Enclave / StrongBox:** All Proxy Agents (Human Nodes) must cryptographically sign their interventions using a non-exportable private key sealed inside their mobile device's hardware security module (Apple Secure Enclave or Android TPM 2.0).
* **Biometric-Free Verification:** PAN does not store FaceID or TouchID data. The device hardware verifies the Agent locally and issues an unforgeable "Success" token.
* **Anti-Spoofing:** Any attempt to spoof GPS location or bypass the hardware-backed identity results in an immediate, permanent "Slash" of the Agent's network access.

### B. L402 Cryptographic Settlement (Financial Layer)
* **Zero Custody:** PAN is not a bank and never custodies fleet funds.
* **Atomic Bounties (Lightning Network):** Intervention bounties are locked in L402 HODL invoices. Funds are *only* released to the Agent upon the cryptographic revelation of a preimage, which is strictly tied to the AV's onboard AI confirming the successful clearing of the sensor fault code.

### C. Immutable Telemetry (Compliance Layer)
* **SB 1417 Audit Engine:** Every physical intervention generates a cryptographically signed "Optical Health Report."
* **Data Sovereignty:** These logs satisfy Arizona SB 1417 mandates for independent diagnostic audits and are tamper-proof, ensuring fleets have undeniable proof of third-party sensor reclamation.

---

## 2. API & Infrastructure Security

### Webhook Integrity (Fleet Gateways)
All real-time M2H dispatch events and state changes are signed with **HMAC-SHA256**. We publish our egress IP ranges for strict enterprise firewall whitelisting.

### API Rate Limiting
To prevent denial-of-service (DoS) attacks on the dispatch queue, all endpoints are protected by token-bucket rate limiters.
* **Standard Fleet API:** 100 RPS
* **Enterprise Direct Integration (V2X):** 1,000+ RPS

---

## 3. Supported Versions

| Version | ODD / Sector | Supported | End of Life |
| :--- | :--- | :--- | :--- |
| **2026.1 (Pilot)** | Mesa, AZ (Sector 1) | :white_check_mark: | Active |
| **< 2026.0** | Prototypes | :x: | Deprecated |

---

## 4. Vulnerability Disclosure
**Do not open public GitHub issues for security vulnerabilities.**

If you discover a vulnerability (specifically regarding Enclave bypass, L402 Escrow manipulation, or UWB location spoofing), please follow the procedure below:

### Reporting
1. **Encrypt:** Use our PGP Key below to encrypt your findings.
2. **Send:** Email **security@proxyagent.network**.

### Bug Bounty (Mesa Pilot)
We maintain a private bug bounty program for critical exploits affecting the M2H settlement layer or Agent Identity verification:
* **Remote Code Execution (Fleet Gateway):** Up to **$10,000**
* **Cryptographic Forgery of SB 1417 Audit Logs:** Up to **$5,000**
* **Bypass of Hardware Attestation (TPM/Enclave):** Up to **$2,500**

---

## 🔑 Secure Communication (PGP)
**Fingerprint:** `8829 3920 A1B2 C3D4 E5F6 7890 1234 5678 90AB CDEF`

-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: OpenPGP.js v4.10.10
Comment: https://proxyagent.network

xsBNBGM5+rUBCAC9/8k3j9... (Truncated for brevity) ...
... [Full key available on keyserver.ubuntu.com search: 0x99283] ...
-----END PGP PUBLIC KEY BLOCK-----