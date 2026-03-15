# **Proxy Agent Network (PAN) | Sector Status & Surge Ticker**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0 (Supersedes v1 Market Ticker)

**Target:** Fleet API (V2X) & Routing Engine

## **1\. Localized Pricing & Telemetry**

In the Proxy Agent Network (PAN), pricing is not global. Because physical Vanguard Agents cannot teleport, supply and demand are strictly localized to specific Operational Design Domains (ODDs) or Geohashes.

To ensure fair L402 compensation for Vanguard Agents and to provide predictable OpEx for Fleet Partners, the PAN Gateway operates a real-time **Sector Status & Surge Ticker**. Fleet Operators should poll this endpoint to calculate expected costs before generating an L402 dispatch payload.

## **2\. The Endpoint**

GET /v2026.1/sector/{sector\_id}/status

### **Request Parameters**

* sector\_id (Path): The designated Level-6 Geohash or PAN Sector code (e.g., MESA\_AZ\_01).

### **Authentication**

Requires standard HMAC-SHA256 request signing using your Master Fleet Secret.

## **3\. Success Response (200 OK)**

Returns the current base rates for specific Unified Diagnostic Service (UDS) fault codes, alongside real-time physical network telemetry and the active Surge Multiplier.

{  
  "timestamp": "2026-05-22T14:30:00Z",  
  "sector\_id": "MESA\_AZ\_01",  
  "base\_currency": "SATS",  
  "base\_rates": {  
    "LIDAR\_MUD\_OCCLUSION": 25000,  
    "OPTICAL\_LENS\_OBSTRUCTED": 25000,  
    "CABIN\_DOOR\_AJAR": 20000,  
    "PERIMETER\_VANDALISM": 30000,  
    "KINETIC\_COLLISION": 50000  
  },  
  "network\_telemetry": {  
    "active\_agents": 42,  
    "agent\_utilization\_ratio": 0.82,  
    "surge\_multiplier": 1.7  
  },  
  "status": "ELEVATED",  
  "estimated\_sla\_secs": 540  
}

## **4\. Price Discovery & Surge Economics**

The actual L402 Satoshi bounty required to guarantee a 15-minute dispatch is calculated by multiplying the base\_rate for the specific UDS code by the surge\_multiplier.

* **Base Bounties:** Fixed rates representing nominal physical labor costs for the intervention (e.g., 25,000 Sats for an Optical Reclamation Protocol).  
* **Surge Multiplier:** When the **Agent Utilization Ratio (AUR)** exceeds 75% due to a mass-grounding event (e.g., a severe Arizona dust storm), the Surge Multiplier scales linearly (up to 5.0x). This financial incentive pulls "Off-Duty" Vanguard Agents into ACTIVE\_PATROL.  
* **SLA Estimation:** The estimated\_sla\_secs dynamically adjusts based on current traffic conditions and Agent density in the Sector.

## **5\. Bidding & Fleet Spend Caps**

Fleet Operators do not blindly accept surge pricing. When calling POST /fleet/dispatch, your backend must supply a max\_l402\_sats value.

* **Guaranteed Dispatch:** If your max\_l402\_sats is **higher** than the current calculated surge cost (Base \* Surge), your L402 HODL invoice is generated, and an Agent is dispatched immediately. You are only charged the *actual* calculated rate, not your maximum cap.  
* **Secondary Queue:** If your max\_l402\_sats is **lower** than the current surge cost, your Autonomous Vehicle is placed in a secondary queue. It will not be serviced until the mass-grounding event subsides and the Sector Surge drops below your specified cap.