# **Proxy Agent Network (PAN) | Rate Limits & Fleet Quotas**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

## **1\. The Cyber-Physical Constraint**

Traditional REST APIs restrict traffic solely to protect database and server infrastructure. The Proxy Agent Network (PAN) is different. When you POST to our /fleet/dispatch endpoint, you are initiating the deployment of a physical human being (a Vanguard Agent) in the real world.

Because Vanguard Agents are a finite resource within any given Operational Design Domain (ODD), our rate limits and quotas are designed to prevent rogue API loops from exhausting the local Agent pool and artificially spiking L402 Surge pricing for other Fleet Partners.

## **2\. API Rate Limits (Digital Constraints)**

To protect the Fleet Gateway servers, standard token-bucket rate limiting applies to all REST endpoints. Limits are tracked per Master Fleet Key.

| Endpoint Group | Allowed Rate | Burst Capacity |
| :---- | :---- | :---- |
| **Telemetry & Status** (GET /sector/status) | 600 / minute | 50 / second |
| **Audit Logs** (GET /compliance/audit) | 120 / minute | 10 / second |
| **Mission Dispatch** (POST /fleet/dispatch) | 30 / minute | 5 / second |

### **HTTP Headers**

Every API response includes standard headers detailing your current limit consumption:

X-RateLimit-Limit: 600  
X-RateLimit-Remaining: 598  
X-RateLimit-Reset: 1780541460

If you exceed the digital rate limit, the API will return a 429 Too Many Requests status code. We strongly recommend implementing an exponential backoff with jitter in your Fleet webhook dispatchers.

## **3\. Concurrent Mission Quotas (Physical Constraints)**

In addition to digital rate limits, PAN enforces **Concurrent Mission Quotas**. This defines the maximum number of Vanguard Agents your specific fleet can have deployed simultaneously within a single Sector Geohash (e.g., MESA\_AZ\_01).

Your Physical Quota is determined by your Partnership Tier and your L402 Escrow lockup.

| Partnership Tier | Required Escrow | Max Concurrent Agents (Per Sector) |
| :---- | :---- | :---- |
| **Tier 1 (Testing)** | 0.05 BTC | 5 Active Missions |
| **Tier 2 (Growth)** | 0.50 BTC | 25 Active Missions |
| **Tier 3 (Anchor)** | 2.00 BTC | 100+ Active Missions |

### **Handling Quota Exhaustion (503 Service Unavailable)**

If your fleet attempts to dispatch a new mission while at your maximum concurrent quota, the API will reject the dispatch and return a 503 Service Unavailable with a specific QUOTA\_EXHAUSTED error code.

The dispatch will only be accepted once an active Agent completes an ORP (Optical Reclamation Protocol) and the vehicle clears the fault, freeing up a slot in your quota.

## **4\. Idempotency & Retry Loops**

Autonomous Vehicle (AV) onboard computers frequently operate in areas with degraded cellular connectivity. If a vehicle loses connection immediately after sending a /fleet/dispatch webhook, it may blindly retry the request.

If a Fleet sends 10 identical dispatch requests for the same vehicle within 5 seconds, PAN will **not** dispatch 10 Vanguard Agents and will **not** deduct 10 slots from your Concurrent Mission Quota.

* **The Idempotency Lock:** The PAN Gateway calculates a unique hash combining vin\_hash, uds\_fault\_code, and a 15-minute time window.  
* **The Response:** Any duplicate dispatch requests within that 15-minute window will receive a 409 Conflict response that safely echoes back the original mission\_id and the assigned Agent's ETA, consuming 0 additional quota.

## **5\. Requesting Limit Increases**

If your AV operations are expanding beyond your current Concurrent Mission Quota, or if you anticipate a massive scale-up for an upcoming software rollout, please contact PAN Command via your dedicated Signal channel at least 72 hours in advance so we can adjust Veteran recruitment targeting in your specific ODD.