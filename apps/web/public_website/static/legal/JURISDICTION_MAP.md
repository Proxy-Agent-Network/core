# **Proxy Agent Network (PAN) | Sector & Jurisdiction Map**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Routing Engine & Legal Operations

This map provides the routing logic for the PAN Gateway to programmatically select the correct **Machine-to-Human (M2H) Physical Intervention Mandate** and compliance reporting schema based on the stranded Autonomous Vehicle's (AV) physical location and Operational Design Domain (ODD).

## **1\. Active Sector Table**

Because physical AV interventions are bound by specific state-level Department of Transportation (DOT) and Department of Public Safety (DPS) regulations, the M2H Mandate varies by physical sector.

| Sector ID | Physical Region | Statutory Reference | M2H Mandate File |
| :---- | :---- | :---- | :---- |
| **MESA\_AZ\_01** | Maricopa County, Arizona (US) | AZ Rev Stat § 28-9701 (SB 1417\) | ai\_power\_of\_attorney.md |

*(Note: The M2H Mandate template retains the legacy ai\_power\_of\_attorney.md filename for v2026.1.0 API backwards compatibility).*

## **2\. Sector Routing Logic (Python Gateway)**

When an AV transmits a Unified Diagnostic Service (UDS) fault code via the Fleet API, the PAN Gateway resolves the GPS coordinates to a Level-6 Geohash and assigns the appropriate legal framework before locking the L402 escrow and dispatching a Vanguard Agent.

def resolve\_sector\_mandate(lat: float, lng: float) \-\> dict:  
    \# 1\. Convert AV coordinates to Level-6 Geohash  
    geohash \= encode\_geohash(lat, lng, precision=6)  
      
    \# 2\. Match Geohash to active PAN Sector  
    sector\_id \= lookup\_sector(geohash)  
      
    if sector\_id \== "MESA\_AZ\_01":  
        return {  
            "jurisdiction": "State of Arizona",  
            "statute": "SB 1417",  
            "mandate\_template": "templates/legal/ai\_power\_of\_attorney.md",  
            "audit\_schema": "sb1417\_optical\_health\_report",  
            "active": True  
        }  
    else:  
        \# Halt execution. We cannot legally dispatch Agents outside authorized ODDs.  
        raise OutOfBoundsError("AV coordinates fall outside active PAN Operational Design Domains.")

## **3\. Future Expansion Sectors (In Review)**

The PAN Legal Engineering team and retained mobility counsel are currently codifying the M2H Physical Intervention Mandates for the following upcoming Q3 2026 expansion sectors:

* **AUSTIN\_TX\_01 (Texas):** Drafting compliance mapping for TX Transp Code § 545.454 (Automated Motor Vehicles).  
* **SF\_CA\_01 (California):** Drafting compliance mapping for CPUC & DMV Autonomous Vehicle Deployment Program regulations (Requires additional municipal zoning sign-offs).  
* **VEGAS\_NV\_01 (Nevada):** Drafting compliance mapping for NRS Chapter 482A (Autonomous Vehicles).

## **4\. Usage & Liability Requirements**

* **Strict Geofencing:** Vanguard Agents are programmatically locked from accepting L402 contracts or executing the M2H Mandate if their mobile hardware detects they are outside their legally authorized Sector.  
* **Liability Shield Initialization:** The $5M HNOA/E\&O liability transfer is strictly contingent upon the Agent confirming their physical presence inside the valid statutory jurisdiction via an Ultra-Wideband (UWB) Time-of-Flight lock.  
* **Cryptographic Sealing:** The final M2H Mandate is never printed or wet-signed. It is mathematically generated, hashed with the AV's UDS Dispatch Signature and the Vanguard Agent's TPM Enclave Signature, and committed to WORM (Write-Once-Read-Many) storage for 7 years to satisfy state auditors.