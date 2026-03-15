# **Proxy Agent Network (PAN) | Webhook Security & Idempotency**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

## **1\. The Cyber-Physical Threat Model**

In traditional SaaS infrastructure, a spoofed webhook might result in a duplicate database row. In the Proxy Agent Network (PAN), a spoofed Unified Diagnostic Service (UDS) webhook results in the physical deployment of a Vanguard Agent to a set of GPS coordinates, accompanied by the locking of real financial capital (L402 Satoshis).

To mitigate "Swatting" (maliciously deploying Agents) and network saturation, PAN enforces strict cryptographic signature verification and temporal idempotency on all API traffic.

## **2\. Verifying Outbound Callbacks (Fleet Side)**

When PAN dispatches a Vanguard Agent, our gateway sends real-time state changes (e.g., mission.agent\_arrived, mission.orp\_completed) to your registered Fleet Callback URL.

To ensure your AV backend only processes legitimate state changes from the PAN network, we sign every outbound webhook using your **Master Fleet Secret** (sk\_fleet\_live\_...).

### **Signature Verification Requirements**

1. PAN includes the X-PAN-Signature and X-PAN-Timestamp headers in every outbound webhook.  
2. Your backend must concatenate POST:{URI}:{Timestamp}:{RawBody}.  
3. Generate an HMAC-SHA256 hash of this string using your Fleet Secret.  
4. Compare your generated hash against the X-PAN-Signature header using a constant-time string comparison function (to prevent timing attacks).

### **Python Example (FastAPI/Starlette)**

import hmac  
import hashlib  
import time  
from fastapi import Request, HTTPException

FLEET\_SECRET \= b"sk\_fleet\_live\_your\_secret\_key"

async def verify\_pan\_webhook(request: Request):  
    timestamp \= request.headers.get("X-PAN-Timestamp")  
    signature \= request.headers.get("X-PAN-Signature")  
      
    \# 1\. Prevent Replay Attacks (Reject if older than 60 seconds)  
    if abs(int(time.time()) \- int(timestamp)) \> 60:  
        raise HTTPException(status\_code=400, detail="Timestamp expired")  
          
    body \= await request.body()  
    uri \= request.url.path  
      
    \# 2\. Reconstruct the signed payload  
    payload \= f"POST:{uri}:{timestamp}:{body.decode('utf-8')}".encode('utf-8')  
    expected\_hash \= hmac.new(FLEET\_SECRET, payload, hashlib.sha256).hexdigest()  
      
    \# 3\. Constant-time comparison  
    if not hmac.compare\_digest(signature, expected\_hash):  
        raise HTTPException(status\_code=401, detail="Invalid PAN Signature")  
          
    return True

## **3\. Inbound Idempotency (The 15-Minute Rule)**

Autonomous Vehicles (AVs) frequently experience cellular dead zones, particularly in dense urban canyons or multi-level parking structures. If an AV broadcasts a /fleet/dispatch webhook but loses connectivity before receiving PAN's 201 Created acknowledgment, the AV's internal retry logic will likely fire the payload again.

To prevent PAN from dispatching 5 Vanguard Agents to the same vehicle and draining your Concurrent Mission Quota, the Fleet Gateway enforces an **Idempotency Lock**.

### **The Idempotency Hash**

Upon receiving a /fleet/dispatch request, the PAN Gateway computes a unique hash using three immutable data points:

SHA-256( vehicle\_vin\_hash \+ uds\_fault\_code \+ 15\_minute\_time\_window )

### **The Idempotency State Machine**

1. **First Request:** PAN creates the mission, locks the L402 escrow, dispatches an Agent, and caches the Idempotency Hash.  
2. **Duplicate Request (Within 15 Min):** If your AV resends the exact same fault code for the exact same VIN within the 15-minute SLA window, PAN intercepts the request.  
3. **The 409 Response:** PAN will **not** create a new mission. Instead, it returns a 409 Conflict status code, safely echoing back the original, active mission\_id and the assigned Agent's ETA.

### **Example 409 Conflict Response**

{  
  "error": "IDEMPOTENT\_LOCK\_ACTIVE",  
  "message": "A Vanguard Agent is already deployed for this VIN and Fault Code.",  
  "original\_mission\_id": "MSN-88A9-4B2C",  
  "assigned\_agent\_status": "EN\_ROUTE",  
  "eta\_seconds": 312  
}

## **4\. Forced Overrides**

In rare circumstances, a Fleet Operator may need to override the idempotency lock (e.g., if a Vanguard Agent cleared a LIDAR\_MUD\_OCCLUSION, but the AV was immediately splashed with mud again 2 minutes later by a passing truck).

To bypass the lock and force a new dispatch, include the boolean flag "force\_override": true in your /fleet/dispatch payload. *Note: Using this flag will consume an additional slot in your Concurrent Mission Quota and generate a new L402 HODL invoice.*