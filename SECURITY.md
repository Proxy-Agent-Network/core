# Security Policy & Defense-in-Depth

We take the security of the Proxy Network seriously. Because our protocol interfaces with legal identities, physical access, and financial rails, we enforce a multi-layered defense strategy.

---

## 1. The Defense-in-Depth Architecture
Our security model relies on three independent pillars. Compromising one layer does not compromise the whole.

### A. Hardware Root of Trust (Physical Layer)
* **TPM 2.0:** All Tier 2+ Human Nodes must sign proofs using a non-exportable private key sealed inside an Infineon OPTIGA™ TPM.
* **Anti-Tamper:** Physical intrusion of the node chassis triggers a `TPM2_Clear`, instantly wiping the identity.
* **Reference:** [specs/hardware/security_architecture.md](./specs/hardware/security_architecture.md)

### B. Cryptographic Settlement (Financial Layer)
* **No Custody:** The Protocol never holds user funds.
* **HODL Invoices:** Funds are locked on the Lightning Network (LNV2) and only released upon revelation of a cryptographic preimage tied to a valid proof.
* **Reference:** [docs/economics/escrow_mechanics.md](./docs/economics/escrow_mechanics.md)

### C. Decentralized Adjudication (Governance Layer)
* **Jury Tribunals:** Disputes are not resolved by a central admin, but by a VRF-selected jury of high-reputation peers.
* **Schelling Point:** Incentives ensure honest adjudication without collusion.
* **Reference:** [specs/v1/jury_tribunal.md](./specs/v1/jury_tribunal.md)

---

## 2. Infrastructure Security

### Webhook Integrity
All real-time events are signed with **HMAC-SHA256**. We publish our egress IP ranges for firewall whitelisting.
* **Guide:** [docs/integration/WEBHOOK_SECURITY.md](./docs/integration/WEBHOOK_SECURITY.md)

### API Rate Limiting
To prevent denial-of-service (DoS), all endpoints are protected by token-bucket rate limiters.
* **Standard:** 10 RPS
* **Enterprise:** 100+ RPS

---

## 3. Supported Versions

| Version | Supported | End of Life |
| :--- | :--- | :--- |
| **1.0.x** | :white_check_mark: | LTS (2029) |
| **< 1.0** | :x: | Deprecated |

---

## 4. Vulnerability Disclosure
**Do not open public issues for security vulnerabilities.**

If you discover a vulnerability (specifically regarding ZK Circuits, TPM bypass, or Escrow logic), please follow the procedure below:

### Reporting
1. **Draft:** Use the template at [security/ADVISORY_TEMPLATE.md](./security/ADVISORY_TEMPLATE.md).
2. **Encrypt:** Use our PGP Key below.
3. **Send:** Email **security@rob-o-la.com**.

### Bug Bounty
We maintain a private bug bounty program for critical exploits:
* **Remote Code Execution:** Up to **$5,000**
* **Deanonymization of Proxies:** Up to **$2,000**

---

## 🔑 Secure Communication (PGP)
**Fingerprint:** `8829 3920 A1B2 C3D4 E5F6 7890 1234 5678 90AB CDEF`

```text
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: OpenPGP.js v4.10.10
Comment: [https://proxy.agent.network](https://proxy.agent.network)

xsBNBGM5+rUBCAC9/8k3j9... (Truncated for brevity) ...
... [Full key available on keyserver.ubuntu.com search: 0x99283] ...
-----END PGP PUBLIC KEY BLOCK-----
```
