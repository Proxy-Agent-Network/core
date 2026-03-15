# **Proxy Agent Network (PAN) | Sector Telemetry & Context Injection**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) & Vanguard Tactical App

## **1\. The "Literal Machine" Problem**

Standard autonomous vehicle (AV) telemetry is highly literal. When a sensor fails, the AV generates a binary Unified Diagnostic Service (UDS) code (e.g., LIDAR\_MUD\_OCCLUSION).

However, deploying a human Vanguard Agent requires more than just a fault code and GPS coordinates. Is the AV safely pulled over on a residential street, or is it dead-center in a 45-MPH intersection? Are there hostile pedestrians surrounding the vehicle?

To bridge the gap between machine logic and human safety, PAN utilizes **Telemetry Context Injection**. This allows the AV's onboard AI to utilize its *surviving* sensors to provide critical environmental awareness to the Vanguard Agent prior to their arrival.

## **2\. The Context Schema**

Fleet Operators are strongly encouraged to populate the optional telemetry.context object in the /fleet/dispatch webhook payload. This data is rendered directly onto the Agent's AR HUD.

{  
  "fleet\_id": "WAYMO\_CORP",  
  "vehicle\_vin\_hash": "e3b0c...",  
  "uds\_fault\_code": "LIDAR\_MUD\_OCCLUSION",  
  "telemetry": {  
    "lat": 33.3214,  
    "lng": \-111.6608,  
    "context": {  
      "parking\_state": "BLOCKING\_LIVE\_LANE",  
      "hazard\_lights\_active": true,  
      "ambient\_traffic\_velocity\_mph": 45,  
      "pedestrian\_density": "HIGH",  
      "weather\_state": "DUST\_STORM\_ACTIVE",  
      "fleet\_instructions": "Approach from the rear; vehicle is disabled in the left turn lane."  
    }  
  },  
  "l402\_bounty\_sats": 35000  
}

## **3\. Human-in-the-Loop (HITL) Safety Overrides**

In the PAN ecosystem, Vanguard Agents are strictly prohibited from utilizing "creative intuition" when executing physical repairs (e.g., you cannot invent a new way to clean a LiDAR dome; you must follow the HP Potion SOP to maintain the $5M liability shield).

However, Vanguard Agents possess something AVs do not: **General physical intuition and survival instincts.** If the contextual telemetry provided by the AV conflicts with the physical reality on the ground, the Agent is authorized to invoke a **HITL Safety Override**.

* **The Scenario:** The AV telemetry reports pedestrian\_density: "LOW" and parking\_state: "SAFE". The Vanguard Agent arrives to find the vehicle surrounded by an angry crowd actively vandalizing the chassis.  
* **The Action:** The Agent executes the ABORT: SCENE UNSAFE protocol via their Tactical App.  
* **The Result:** The Agent safely retreats. The PAN network overrides the machine's assessment, cancels the L402 escrow without a Vanguard Trust Score (VTS) slashing penalty, and instantly escalates the event to the Fleet Operator for 911 dispatch.

## **4\. Strict Privacy Boundaries**

Context Injection is powerful but must be heavily sanitized to protect civilian privacy and comply with PAN's Zero-Biometric mandates. Fleet Operators must adhere to the following injection rules:

* **Rule 1 (Zero Interior Context):** Fleet APIs must **never** inject interior cabin status, passenger counts, or passenger behavior into the context block. PAN Agents only service the exterior hardware.  
* **Rule 2 (No PII):** Do **not** inject passenger names, drop-off locations, or payment information.  
* **Sanitization:** The PAN API Gateway actively scans the context block. If regex patterns resembling PII (e.g., phone numbers, names) are detected, the gateway will strip the entire context object from the dispatch before routing it to the Vanguard Agent.