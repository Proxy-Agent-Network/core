# **Proxy Agent Network (PAN) | Webhook & Callback Integration**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations & DevOps

**Retry Policy:** Exponential Backoff (up to 24 hours)

Because autonomous vehicles (AVs) require sub-second coordination with physical infrastructure, Fleet Operators must not rely on API polling. You must configure a **Fleet Callback URL** in the PAN Partner Dashboard to receive real-time, push-based mission telemetry from the PAN Sector Gateway.

## **1\. Supported Events**

PAN broadcasts discrete state changes as the Vanguard Agent executes the physical intervention.

| Event Name | Trigger | Payload Includes |
| :---- | :---- | :---- |
| mission.agent\_dispatched | A Vanguard Agent has accepted the L402 HODL contract. | agent\_id, eta\_seconds |
| mission.agent\_arrived | Agent has achieved a UWB proximity lock with the AV. | uwb\_distance\_cm, timestamp |
| mission.orp\_completed | Agent finished the Optical Reclamation Protocol. | action\_taken, message |
| mission.sla\_breach | Agent failed to arrive within 15 minutes. | reason, rerouting\_active |
| escrow.settled | AV cleared the fault; PAN released the L402 preimage. | settled\_sats, invoice\_hash |

## **2\. Payload Structure**

All webhooks are transmitted as POST requests containing a standard JSON envelope.

{  
  "event\_id": "evt\_998877665544",  
  "event\_type": "mission.orp\_completed",  
  "mission\_id": "MSN-88A9-4B2C",  
  "timestamp": "2026-05-22T14:32:01Z",  
  "data": {  
    "agent\_id": "VANGUARD-042",  
    "action\_taken": "CLEARED\_HP\_POTION",  
    "message": "Physical intervention complete. Awaiting AV UDS clear signal."  
  }  
}

## **3\. Security: Verifying Signatures**

To prevent "Fleet Swatting" (payload injection attacks attempting to spoof mission states), you **must** verify the X-PAN-Signature header sent with every request.

*For full security architecture and IP whitelists, refer to [WEBHOOK\_SECURITY.md](https://www.google.com/search?q=./WEBHOOK_SECURITY.md).*

### **The Cryptographic Logic:**

1. Extract the timestamp from X-PAN-Timestamp.  
2. Reconstruct the signature payload string: POST:{Your\_URI}:{Timestamp}:{Raw\_JSON\_Body}.  
3. Compute an **HMAC-SHA256** hash using your Master sk\_fleet\_live\_... secret.  
4. Compare your computed hash to the X-PAN-Signature header using a constant-time comparison function.

### **Python Example (FastAPI):**

import hmac  
import hashlib  
import time  
from fastapi import Request, HTTPException

FLEET\_SECRET \= b"sk\_fleet\_live\_your\_secret\_key"

async def verify\_pan\_webhook(request: Request):  
    timestamp \= request.headers.get("X-PAN-Timestamp")  
    signature \= request.headers.get("X-PAN-Signature")  
      
    \# 1\. Enforce 60-second replay protection  
    if abs(int(time.time()) \- int(timestamp)) \> 60:  
        raise HTTPException(status\_code=403, detail="Temporal drift exceeded (Replay Protection)")  
          
    raw\_body \= await request.body()  
    uri \= request.url.path  
      
    \# 2\. Reconstruct payload  
    payload \= f"POST:{uri}:{timestamp}:{raw\_body.decode('utf-8')}".encode('utf-8')  
      
    \# 3\. Compute HMAC-SHA256  
    expected\_hash \= hmac.new(FLEET\_SECRET, payload, hashlib.sha256).hexdigest()  
      
    \# 4\. Constant-time compare  
    if not hmac.compare\_digest(signature, expected\_hash):  
        raise HTTPException(status\_code=401, detail="Invalid PAN Signature")  
          
    return True

## **4\. Delivery Retries & Idempotency**

If your Fleet backend returns anything other than a 2XX success code (or times out after 5 seconds), the PAN Gateway will automatically queue the event for retry:

* **Attempt 1:** Immediate  
* **Attempt 2:** \+ 5 seconds  
* **Attempt 3:** \+ 30 seconds  
* **Attempt 4:** \+ 5 minutes  
* *...scaling up to 24 hours.*

\[\!CAUTION\]

**Idempotency & The Critical Path:** Always cache the event\_id in Redis to ensure you do not process the same state change twice. Furthermore, if your backend goes offline and misses the mission.orp\_completed webhook, your AV will not know to run its diagnostic sweep. You must monitor PAN uptime and implement active polling fallbacks during your own internal outages.