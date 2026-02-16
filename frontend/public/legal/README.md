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

### Automation (Python Example)

You can programmatically generate these instruments using standard string replacement.

```python
# utils/generate_poa.py mock usage
import datetime

def fill_template(template_path, agent_key, principal_name, limit_usd):
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Dynamic Replacement
    filled = content.replace("[PRINCIPAL NAME]", principal_name)
    filled = filled.replace("[AGENT_PUBLIC_KEY]", agent_key)
    filled = filled.replace("[MAX_LIMIT]", str(limit_usd))
    filled = filled.replace("[TIMESTAMP]", datetime.datetime.now().isoformat())
    
    return filled

# Example: Generate a Delaware POA
poa_text = fill_template("ai_power_of_attorney.md", "pk_agent_8829...", "John Doe", 500)
print(poa_text)
```

---

> [!IMPORTANT]
> **⚠️ Disclaimer:** These templates are provided for informational purposes and do not constitute legal advice. We recommend having your specific counsel review these instruments before mainnet deployment.
