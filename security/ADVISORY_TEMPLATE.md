---
name: Security Vulnerability Report
about: Report a security bug or cryptographic flaw (Private Disclosure Only).
title: "[SEC] <Brief description of vulnerability>"
labels: SECURITY
assignees: ''
---

# Security Vulnerability Report

> [!IMPORTANT]
> **Notice:** Do **NOT** open a public GitHub Issue for security vulnerabilities.  
> **Submission:** Encrypt this report using our PGP Key (see [SECURITY.md](../SECURITY.md)) and email it to **security@rob-o-la.com**.

---

## 1. Vulnerability Metadata
* **Reporter:** [Name / Alias]
* **Date:** [YYYY-MM-DD]
* **Affected Component:** (e.g., ZK Circuits, TPM 2.0 Signing, HODL Invoice Logic)
* **Severity (CVSS Estimate):** (Critical / High / Medium / Low)

---

## 2. Summary
*(A concise, one-paragraph description of the vulnerability. Example: "The ZK proof verification logic allows for replay attacks if the nonce is not incremented.")*

---

## 3. Technical Details
* **Vector:** (Remote / Physical / MITM)
* **Prerequisites:** (e.g., "Attacker must have a verified Tier 2 account")

---

## 4. Proof of Concept (PoC)
*(Provide step-by-step instructions or a script to reproduce the exploit.)*

```bash
# Example reproduction command
proxy-node --exploit-flag --target-id [ID]
```

---

## 5. Impact Analysis
*(What happens if this is exploited? Loss of funds? PII Leak? Reputation damage?)*

---

## 6. Suggested Mitigation
*(If you have a fix in mind, describe it here. Code snippets or diffs are welcome.)*

---

**Disclosure Agreement:** By submitting this report, you agree to the **Proxy Protocol Responsible Disclosure Policy** and the **Bug Bounty terms** outlined in our [SECURITY.md](../SECURITY.md).
