# Legal Templates & Jurisdictions

This directory contains standardized "Power of Attorney" and "Delegation" instruments designed for Autonomous Agents. Select the template based on the jurisdiction of the Principal (the human/company owning the Agent).

---

### Template Comparison

| Region | File | Key Legislation | Best For |
| :--- | :--- | :--- | :--- |
| 🇺🇸 **United States** | `ai_power_of_attorney.md` | Delaware General Corp Law | Startups, DAOs, US Banking |
| 🇬🇧 **UK** | `uk_limited_power_attorney.md` | Powers of Attorney Act 1971 | UK/EU Correspondence, GDPR |
| 🇸🇬 **Singapore** | `singapore_poa.md` | Electronic Transactions Act 2010 | Asian Markets, ACRA Filings |

---

### Usage Guide

1.  **Select:** Choose the file matching your legal domicile.
2.  **Fill:** Replace the bracketed placeholders (e.g., `[AGENT_PUBLIC_KEY]`) dynamically at runtime.
3.  **Sign:** The Principal must cryptographically sign the hash of the filled document.
4.  **Store:** Upload the signed PDF/Markdown to IPFS or the Proxy Network Escrow.

> [!IMPORTANT]
> **⚠️ Disclaimer:** These templates are provided for informational purposes and do not constitute legal advice. We recommend having your specific counsel review these instruments before mainnet deployment.
