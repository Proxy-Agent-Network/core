# **Proxy Agent Network (PAN) | M2H Legal Mandates & Jurisdictions**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet Legal Counsel & PAN Compliance Engine

This directory contains standardized **Machine-to-Human (M2H) Physical Intervention Mandates**. Because Vanguard Agents physically interact with $150,000 autonomous assets on public roadways, explicit legal authorization is required to transfer liability and satisfy state-level Department of Transportation (DOT) and Department of Public Safety (DPS) regulations.

### **Template Mapping by Sector**

Unlike generic digital contracts, PAN M2H mandates are strictly mapped to the Operational Design Domain (ODD) where the Autonomous Vehicle (AV) is physically grounded.

| Sector ID | Active File | Key Legislation | Status |
| :---- | :---- | :---- | :---- |
| **MESA\_AZ\_01** | ai\_power\_of\_attorney.md\* | AZ Rev Stat § 28-9701 (SB 1417\) | Active Pilot |
| **AUSTIN\_TX\_01** | tx\_m2h\_mandate.md | TX Transp Code § 545.454 | Drafting (Q3 2026\) |
| **SF\_CA\_01** | ca\_cpuc\_mandate.md | CPUC AV Deployment Program | Drafting (Q4 2026\) |

*\*Note: The Mesa Pilot utilizes the legacy ai\_power\_of\_attorney.md filename for v2026.1.0 API backwards compatibility.*

### **Automated Execution Guide**

M2H Mandates are never printed or wet-signed. They are programmatically generated and cryptographically sealed by the PAN Gateway during an intervention.

1. **Geohash Resolution:** The Gateway matches the AV's GPS coordinates to the active Sector to select the correct statutory template.  
2. **Hydration:** The PAN engine dynamically replaces bracketed placeholders (e.g., \[VEHICLE\_VIN\_HASH\], \[AGENT\_TPM\_PUBKEY\]) at runtime.  
3. **Cryptographic Sealing:** The completed document hash is mathematically bound to the Vanguard Agent's hardware Secure Enclave signature and the AV's UDS Dispatch signature.  
4. **WORM Storage:** The resulting artifact is pushed to immutable Write-Once-Read-Many (WORM) storage for 7 years to satisfy mandatory DPS compliance audits.

### **Python Gateway Implementation (Example)**

The following pseudo-code demonstrates how the PAN Gateway programmatically hydrates the M2H Mandate prior to L402 escrow settlement.

\# utils/generate\_m2h\_mandate.py  
import datetime  
import hashlib

def hydrate\_mandate(template\_path, fleet\_id, vin\_hash, agent\_tpm, uds\_code):  
    with open(template\_path, 'r') as f:  
        content \= f.read()  
      
    \# Dynamic Placeholder Replacement  
    hydrated \= content.replace("\[FLEET\_ID\]", fleet\_id)  
    hydrated \= hydrated.replace("\[VEHICLE\_VIN\_HASH\]", vin\_hash)  
    hydrated \= hydrated.replace("\[AGENT\_TPM\_PUBKEY\]", agent\_tpm)  
    hydrated \= hydrated.replace("\[UDS\_FAULT\_CODE\]", uds\_code)  
    hydrated \= hydrated.replace("\[UTC\_TIMESTAMP\]", datetime.datetime.now(datetime.UTC).isoformat())  
      
    \# Generate the cryptographic hash of the final agreement  
    document\_hash \= hashlib.sha256(hydrated.encode('utf-8')).hexdigest()  
      
    return hydrated, document\_hash

\# Example: Generate a Mesa AZ-01 Mandate  
mandate\_text, doc\_hash \= hydrate\_mandate(  
    template\_path="ai\_power\_of\_attorney.md",   
    fleet\_id="WAYMO\_LLC",  
    vin\_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  
    agent\_tpm="041d8e9b2c...",  
    uds\_code="LIDAR\_MUD\_OCCLUSION"  
)

\[\!IMPORTANT\]

**⚠️ Legal Disclaimer:** The templates provided in this directory are integrated directly into the PAN $5,000,000 HNOA/E\&O liability shield. Any manual modifications to these templates by Fleet Operators without prior approval from PAN Command and retained mobility counsel will immediately void the liability transfer guarantees for that specific intervention.