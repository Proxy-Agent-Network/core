# **Proxy Agent Network (PAN) | Legal & Compliance Endpoints**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet Legal Counsel & Compliance Teams

## **1\. The Statutory Requirement**

The Proxy Agent Network (PAN) acts as a legally binding, independent third-party auditor for autonomous vehicle sensor interventions. Fleet Operators utilize these specific endpoints to satisfy state regulatory requirements (e.g., Arizona SB 1417\) and to initiate hardware damage claims under PAN's $5,000,000 E\&O liability shield.

## **2\. Fetch SB 1417 Audit Log (OHR)**

**Endpoint:** GET /v2026.1/fleet/compliance/audit/{mission\_id}

Retrieves the immutable, cryptographically signed **Optical Health Report (OHR)** for a completed intervention. This payload is pre-formatted for direct appending to your monthly Arizona Department of Public Safety (DPS) compliance filings.

### **Request Headers**

X-PAN-Timestamp: 1780541400  
X-PAN-Signature: a8f5f167f44f4964e6c998dee827110c...

### **Success Response (200 OK)**

Returns the complete TPM-signed audit log.

{  
  "audit\_id": "AUD-MSN-88A9-4B2C",  
  "fleet\_operator": "WAYMO\_LLC",  
  "vehicle\_vin\_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  
  "uds\_fault\_code": "LIDAR\_MUD\_OCCLUSION",  
  "agent\_attestation": {  
    "vanguard\_id": "VANGUARD-042",  
    "tpm\_pubkey\_hash": "7d8a9b2c...",  
    "uwb\_proximity\_cm": 124.5,  
    "signature": "3045022100b..."  
  },  
  "l402\_settlement": {  
    "invoice\_hash": "lnbc250n1...",  
    "preimage\_revealed": true,  
    "settled\_sats": 25000  
  },  
  "gps\_location": "33.3214,-111.6608",  
  "timestamp\_cleared": "2026-05-22T14:32:15Z"  
}

## **3\. File E\&O Liability Dispute**

**Endpoint:** POST /v2026.1/fleet/mission/{mission\_id}/dispute

If an Autonomous Vehicle registers permanent hardware damage (e.g., a scratched LiDAR dome) immediately following a PAN intervention, Fleet Operators must invoke this endpoint within 24 hours to freeze the Agent's account and initiate a Tech E\&O insurance claim.

### **Request Payload**

{  
  "incident\_type": "HARDWARE\_DAMAGE",  
  "description": "Severe micro-abrasions detected on Front-Left LiDAR dome immediately following ORP completion. Suspected SOP violation (reused microfiber cloth).",  
  "evidence": {  
    "fleet\_telemetry\_url": "\[https://secure-storage.waymo.com/logs/v123\_sensor\_degradation.json\](https://secure-storage.waymo.com/logs/v123\_sensor\_degradation.json)",  
    "exterior\_cam\_url": "\[https://secure-storage.waymo.com/vid/v123\_cam\_fl\_1430.mp4\](https://secure-storage.waymo.com/vid/v123\_cam\_fl\_1430.mp4)"  
  }  
}

### **Success Response (201 Created)**

Returns the Dispute ID and confirms the asset freeze.

{  
  "dispute\_id": "DSP-88A9-4B2C",  
  "status": "ASSET\_FROZEN",  
  "message": "Vanguard Agent account suspended. SB 1417 OHR and edge-vision artifacts successfully locked for forensic review. A PAN Compliance Officer has been assigned."  
}

## **4\. Async Dispute Resolution (Webhook)**

Because hardware forensics require human review (cross-referencing Agent edge-vision photos with Fleet telemetry), E\&O disputes are resolved asynchronously. Once a verdict is reached, PAN pushes the resolution to your registered Fleet Callback URL.

### **Webhook Event (dispute.resolution)**

{  
  "event\_id": "evt\_77665544",  
  "event\_type": "dispute.resolution",  
  "dispute\_id": "DSP-88A9-4B2C",  
  "mission\_id": "MSN-88A9-4B2C",  
  "timestamp": "2026-05-24T09:15:00Z",  
  "result": {  
    "verdict": "AGENT\_AT\_FAULT",  
    "liability\_coverage": "APPROVED",  
    "insurance\_claim\_id": "CLM-PAN-2026-0042",  
    "message": "Forensics confirm Agent violated HP Potion SOP. Vanguard Agent permanently revoked. PAN's $5M E\&O policy engaged to cover full hardware replacement costs."  
  }  
}  
