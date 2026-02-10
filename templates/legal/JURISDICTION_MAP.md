# Jurisdiction Selection Map (v1.0)

This map provides the routing logic for AI Agents to programmatically select the correct **Limited Power of Attorney (PoA)** template based on the Human Node's reported geolocation.

---

## 1. Automated Selection Table

| ISO Code | Country | State/Region | Template File | Statutory Reference |
| :--- | :--- | :--- | :--- | :--- |
| **US** | United States | Delaware | `us_delaware_poa.md` | Delaware Code Title 12, Chapter 40 |
| **GB** | United Kingdom | England & Wales | `uk_poa.md` | Powers of Attorney Act 1971 |
| **SG** | Singapore | National | `singapore_poa.md` | Powers of Attorney Act (Cap. 243) |

---

## 2. Routing Logic (Pseudo-code)

Agents should implement the following logic when initializing a task that requires legal capacity:

```python
def resolve_legal_template(node_geo_iso):
    # 1. Load the JURISDICTION_MAP
    # 2. Match node_geo_iso to Template File
    if node_geo_iso == "US":
        return "templates/legal/us_delaware_poa.md"
    elif node_geo_iso == "GB":
        return "templates/legal/uk_poa.md"
    elif node_geo_iso == "SG":
        return "templates/legal/singapore_poa.md"
    else:
        # Fallback to Universal Digital Commerce Code (Draft)
        return "templates/legal/ai_power_of_attorney.md"
```

---

## 3. Future Jurisdictions (In Review)

The following jurisdictions are currently being codified by the Legal Engineering team:

* **EU (Germany/Estonia):** Drafting for GDPR and eIDAS compliance.
* **AE (Dubai DIFC):** Drafting for the Digital Assets Law.
* **JP (Japan):** Drafting under Civil Code Article 99.

---

## 4. Usage Requirements

* **Geolocation Proof:** Agents must verify the Node's `hardware_heartbeat.py` coordinates before selecting a template.
* **Statutory Compliance:** Ensure the `[MAX_LIMIT]` placeholder in the template complies with the specific jurisdictional caps (e.g., **S$** in Singapore vs **£** in the UK).
* **Signature Requirement:** The final document must be hashed and signed by the Principal's key to activate the **"Legal Bridge."**

> [!NOTE]
> For contributions to this map, see [CONTRIBUTING_LEGAL.md](./CONTRIBUTING_LEGAL.md).
