# **Proxy Agent Network (PAN) | Troubleshooting & Debugging Guide**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations & Backend Engineers

This guide provides deep-dive solutions for the most common integration blockers encountered by Fleet Operators when connecting their Autonomous Vehicle (AV) backends to the PAN Sector Gateway.

## **Scenario 1: The "L402 Bounty Too Low" Loop (PX\_200)**

**Symptom:** You attempt to dispatch an Agent via POST /fleet/dispatch, but the API immediately returns 402 Payment Required with PX\_200.

**Cause:** A severe weather event or kinetic anomaly has triggered a Geohash Surge. Your dispatch payload's max\_l402\_sats cap is strictly lower than the active Sector Surge rate.

### **The Fix**

1. **Poll the Sector Oracle:** Check the real-time pricing for the specific Geohash.

curl \-H "X-PAN-Signature: \[HMAC\]" \[https://api.proxyagent.network/v2026.1/sector/MESA\_AZ\_01/status\](https://api.proxyagent.network/v2026.1/sector/MESA\_AZ\_01/status)

2. **Increase your Cap:** If the surge\_multiplier is 3.5, your max\_l402\_sats must be at least Base\_Rate \* 3.5.  
3. **Queueing Strategy:** If you refuse to pay the surge, you must gracefully catch the 402 and place your stranded AV in an internal retry queue until the Sector Surge cools down.

## **Scenario 2: "Physical Quota Exhausted" (PX\_501)**

**Symptom:** Your API requests are returning 503 Service Unavailable with QUOTA\_EXHAUSTED.

**Cause:** You have hit the maximum number of concurrent Vanguard Agents allowed for your Fleet's tier (e.g., 25 active missions for *Sector Priority* fleets).

### **The Fix**

1. **Check Active Missions:** Ensure your backend is properly processing the mission.orp\_completed and AV FAULT\_CLEARED webhooks to close out active missions.  
2. **Upgrade Tier:** If your AV fleet size has organically outgrown your current tier, contact PAN Command to upgrade to the **Sector Anchor** tier (100+ concurrent Agents).  
3. **Wait for Clearance:** Your backend must halt further dispatches until an existing Agent completes an Optical Reclamation Protocol (ORP) and frees up a slot.

## **Scenario 3: Webhooks Failing Signature Check (PX\_101)**

**Symptom:** The PAN Gateway rejects your /dispatch requests as "Invalid Signature", or your backend keeps dropping outbound PAN callbacks as "Untrusted."

**Cause:** Your backend is calculating the HMAC-SHA256 signature using parsed/re-serialized JSON instead of the exact raw byte stream. JSON parsers often reorder keys or strip whitespace, breaking the cryptographic hash.

### **The Fix**

**❌ Incorrect (Python/Flask/FastAPI):**

\# DON'T DO THIS: Request.json() alters the payload bytes\!  
payload \= request.json()   
signature \= hmac.new(FLEET\_SECRET, json.dumps(payload), hashlib.sha256)

**✅ Correct:**

\# DO THIS: Hash the raw byte stream directly  
raw\_bytes \= await request.body()   
timestamp \= request.headers\['X-PAN-Timestamp'\]

\# Format: POST:{URI}:{Timestamp}:{RawBody}  
msg \= f"POST:{request.url.path}:{timestamp}:".encode('utf-8') \+ raw\_bytes  
signature \= hmac.new(FLEET\_SECRET, msg, hashlib.sha256).hexdigest()

*Note: Also ensure your server's NTP clock is synced. Signatures drift-fail after 60 seconds (PX\_102).*

## **Scenario 4: "Idempotency Lock Active" (PX\_302)**

**Symptom:** You send a dispatch request and receive a 409 Conflict.

**Cause:** Due to poor cellular connectivity at the AV's location, your vehicle sent the same LIDAR\_MUD\_OCCLUSION webhook twice in under 15 minutes. The PAN Gateway locked the duplicate to prevent double-billing and deploying two Agents to one car.

### **The Fix**

1. **Do not blind-retry on 409s.** 2\. **Parse the Response:** The 409 Conflict payload includes the *existing* mission\_id and the assigned Agent's ETA. Catch this response and map it to your internal AV tracking logic.  
2. **The Nuclear Override:** If the vehicle was genuinely occluded *again* 5 minutes after a successful clear, you must explicitly inject "force\_override": true into your JSON payload.

## **Scenario 5: "Hardware Attestation Rejected" (PX\_400 / PX\_402)**

**Symptom:** An active mission abruptly cancels, and you receive a mission.sla\_breach callback citing OS\_ATTESTATION\_FAILED.

**Cause:** The assigned Vanguard Agent's mobile device failed a continuous security check (e.g., Apple DeviceCheck flagged a jailbreak, or a UWB distance calculation mathematically failed, indicating spoofing).

### **The Fix (Fleet Operator)**

You do not need to take engineering action. The PAN Routing Engine automatically slashes the compromised Agent, revokes their identity key, and instantly routes the next closest Vanguard Agent to your stranded AV. Your mission\_id remains the same; you will simply see a new agent\_dispatched event in your webhook logs.