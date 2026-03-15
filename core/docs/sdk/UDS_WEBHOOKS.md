# **Proxy Agent Network (PAN) | UDS Webhooks & Callbacks**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

## **1\. The Autonomous Trigger**

The Proxy Agent Network is an entirely machine-triggered infrastructure layer. When an Autonomous Vehicle (AV) detects a physical hardware impairment that it cannot resolve via software (e.g., wiping a camera, rebooting a compute node), its onboard AI generates a **Unified Diagnostic Service (UDS)** fault code.

Fleet Operators route these specific physical UDS codes directly to the PAN Gateway via asynchronous webhooks to instantly dispatch a Vanguard Agent.

## **2\. Inbound Webhooks: Dispatching an Agent**

**Endpoint:** POST /v2026.1/fleet/dispatch

When your fleet backend receives a critical UDS code from a grounded vehicle, you forward the payload to PAN to lock the L402 bounty and request an Agent.

### **Supported Physical UDS Codes**

PAN Vanguard Agents are trained exclusively to resolve exterior physical faults. Do not send webhooks for internal software/compute failures or high-voltage EV battery issues.

| UDS Fault Code | Description | Standard ORP Action |
| :---- | :---- | :---- |
| LIDAR\_MUD\_OCCLUSION | Heavy soil/mud on primary or secondary LiDAR dome. | HP Potion \+ Microfiber Pull |
| OPTICAL\_LENS\_OBSTRUCTED | Camera lens covered by debris, adhesive, or biological matter. | HP Potion \+ Microfiber Pull |
| CABIN\_DOOR\_AJAR | Passenger failed to fully close the door, preventing routing. | Manual Door Secure |
| PERIMETER\_VANDALISM | Unknown physical obstruction placed on or directly around AV. | Perimeter Clear & Visual Check |

### **Example Dispatch Payload**

{  
  "fleet\_id": "WAYMO\_CORP",  
  "vehicle\_vin\_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  
  "uds\_fault\_code": "LIDAR\_MUD\_OCCLUSION",  
  "telemetry": {  
    "lat": 33.3214,  
    "lng": \-111.6608,  
    "heading": 184.2,  
    "parking\_context": "STREET\_LEVEL"  
  },  
  "l402\_bounty\_sats": 25000  
}

## **3\. Outbound Callbacks: Mission Telemetry**

Once an Agent is dispatched, the PAN Gateway will push real-time state changes to your registered Fleet Callback URL (e.g., https://api.yourfleet.com/pan/callbacks). This allows your remote operators to monitor the physical recovery in real-time.

### **Standard Event Types**

* mission.agent\_dispatched: An Agent has accepted the L402 contract. Includes eta\_seconds.  
* mission.agent\_arrived: The Agent has achieved a UWB (Ultra-Wideband) proximity lock with the AV.  
* mission.orp\_completed: The Agent has finished the physical Optical Reclamation Protocol (cleaning the sensor).  
* mission.sla\_breach: The Agent failed to arrive within 15 minutes. The mission is being automatically re-routed.

### **Example Callback Payload (mission.orp\_completed)**

{  
  "event\_id": "evt\_99887766",  
  "event\_type": "mission.orp\_completed",  
  "mission\_id": "MSN-88A9-4B2C",  
  "timestamp": "2026-05-22T14:32:01Z",  
  "data": {  
    "agent\_id": "VANGUARD-042",  
    "action\_taken": "CLEARED\_HP\_POTION",  
    "message": "Physical intervention complete. Awaiting AV UDS clear signal."  
  }  
}

## **4\. The "Clear" Signal (Releasing Escrow)**

**Endpoint:** POST /v2026.1/fleet/mission/{mission\_id}/clear

This is the most critical webhook in the PAN ecosystem. PAN does **not** rely on the human Agent's word that the job is done. The ultimate source of truth is the vehicle itself.

After the Agent completes the ORP (indicated by the mission.orp\_completed callback), your vehicle's onboard AI must run a self-diagnostic sweep. If the sensor reads clear, your backend fires the clear webhook to PAN.

This webhook triggers the L402 Settlement Engine to release the cryptographic preimage, instantly settling the Satoshi bounty into the Vanguard Agent's wallet and generating the SB 1417 Audit Log.

{  
  "mission\_id": "MSN-88A9-4B2C",  
  "vehicle\_vin\_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  
  "diagnostic\_status": "FAULT\_CLEARED",  
  "timestamp": "2026-05-22T14:32:15Z"  
}

## **5\. Security Requirements**

All inbound and outbound webhooks must be strictly authenticated to prevent unauthorized dispatches or spoofed "Clear" signals.

* **Inbound (To PAN):** Must include the X-PAN-Signature header (HMAC-SHA256). See [Authentication Standards](https://www.google.com/search?q=./auth.md).  
* **Outbound (From PAN):** PAN signs all outbound callbacks using your Fleet Secret. Your backend must verify the HMAC signature before processing the state change to prevent payload injection attacks.