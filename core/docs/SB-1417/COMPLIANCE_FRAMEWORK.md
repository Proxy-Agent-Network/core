# **Proxy Agent Network (PAN) | Arizona SB 1417 Compliance Framework**

**Jurisdiction:** Arizona Department of Public Safety (DPS)

**Statute:** AZ Rev Stat § 28-9701 (SB 1417 \- "Autonomous Vehicle Physical Redundancy Act")

**Status:** Active (Mesa Pilot)

## **1\. The Regulatory Mandate**

Passed in response to the scaling of Level 4 autonomous fleets in Maricopa County, Arizona SB 1417 strictly prohibits Fleet Operators (e.g., Waymo, Zoox) from self-certifying the physical resolution of critical sensor occlusions.

If a vehicle's primary optical, LiDAR, or radar arrays register a critical fault code that grounds the vehicle, the physical clearing of that fault *must* be executed and cryptographically logged by an independent, certified third party.

PAN serves as this independent third-party layer.

## **2\. The Optical Health Report (OHR)**

To satisfy the DPS audit requirements, PAN generates an immutable **Optical Health Report (OHR)** for every physical intervention. The OHR mathematically binds the digital intent of the vehicle to the physical identity of the human agent.

The OHR is generated only after:

1. The Vanguard Agent's mobile hardware (TPM 2.0 / Secure Enclave) signs the presence attestation via Ultra-Wideband (UWB).  
2. The Agent executes the Optical Reclamation Protocol (ORP).  
3. The AV's onboard diagnostic system clears the UDS fault code.  
4. The L402 Lightning network settles the transaction.

## **3\. Audit Log Schema (JSON)**

Fleet partners can query these cryptographically signed logs via the PAN API to append to their mandatory monthly DPS compliance filings.

{  
  "$schema": "\[http://json-schema.org/draft-07/schema\#\](http://json-schema.org/draft-07/schema\#)",  
  "title": "SB1417\_Optical\_Health\_Report",  
  "type": "object",  
  "properties": {  
    "audit\_id": {  
      "type": "string",  
      "description": "Unique PAN identifier for the physical intervention."  
    },  
    "fleet\_operator": {  
      "type": "string",  
      "description": "Registered name of the AV Fleet (e.g., WAYMO\_LLC)."  
    },  
    "vehicle\_vin\_hash": {  
      "type": "string",  
      "description": "SHA-256 hash of the AV's Vehicle Identification Number."  
    },  
    "uds\_fault\_code": {  
      "type": "string",  
      "description": "The exact diagnostic code that grounded the asset (e.g., LIDAR\_MUD\_OCCLUSION\_FL)."  
    },  
    "agent\_attestation": {  
      "type": "object",  
      "properties": {  
        "vanguard\_id": { "type": "string" },  
        "tpm\_pubkey\_hash": { "type": "string" },  
        "uwb\_proximity\_cm": { "type": "number" },  
        "signature": { "type": "string" }  
      }  
    },  
    "l402\_settlement": {  
      "type": "object",  
      "properties": {  
        "invoice\_hash": { "type": "string" },  
        "preimage\_revealed": { "type": "boolean" },  
        "settled\_sats": { "type": "integer" }  
      }  
    },  
    "gps\_location": {  
      "type": "string",  
      "description": "Coordinates of the intervention."  
    },  
    "timestamp\_cleared": {  
      "type": "string",  
      "format": "date-time"  
    }  
  },  
  "required": \[  
    "audit\_id", "vehicle\_vin\_hash", "uds\_fault\_code",   
    "agent\_attestation", "l402\_settlement", "timestamp\_cleared"  
  \]  
}

## **4\. Liability Shielding & Indemnification**

By utilizing the PAN network and the OHR schema, Fleet Operators successfully transfer the liability of the physical intervention.

* **Fleet Indemnification:** During the exact timestamp window between the Agent's UWB proximity lock and the clearing of the UDS fault code, PAN assumes liability for the physical state of the sensor array, backed by our $5M HNOA/E\&O Insurance Umbrella.  
* **Agent Protections:** Vanguard Agents are protected against false claims of damage by the AV's own internal hardware logs. If the AV registers a "cleared" state and releases the L402 preimage, the AV has legally accepted the quality of the Agent's work.

## **5\. Data Retention**

To comply with SB 1417, PAN retains the cryptographic hashes of all Optical Health Reports for **7 years** on immutable ledger storage. PAN does *not* retain raw interior cabin video, passenger telemetry, or proprietary routing algorithms belonging to the Fleet Operator.