# **Proxy Agent Network (PAN) | API Quotas & Physical Rate Limiting**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

To maintain network stability and guarantee rapid dispatch for enterprise Autonomous Vehicle (AV) fleets, the PAN Gateway enforces two distinct layers of rate limiting: **Digital Rate Limits** (protecting our servers) and **Physical Quotas** (protecting the finite supply of Vanguard Agents).

## **1\. Digital Rate Limits (RPS)**

Standard token-bucket rate limiting applies to all REST endpoints, tracked via your Master Fleet Key (sk\_fleet\_live\_...).

| Endpoint Group | Allowed Rate | Burst Capacity |
| :---- | :---- | :---- |
| **Telemetry & Status** (GET /sector/status) | 600 / minute | 50 / second |
| **Audit Logs** (GET /compliance/audit) | 120 / minute | 10 / second |
| **Mission Dispatch** (POST /fleet/dispatch) | 30 / minute | 5 / second |

### **Response Headers (The "Gas Gauge")**

Every API response includes headers detailing your current digital limit consumption. Monitor these programmatically to avoid being throttled.

HTTP/1.1 200 OK  
X-RateLimit-Limit: 600  
X-RateLimit-Remaining: 598  
X-RateLimit-Reset: 1780541460

## **2\. Physical Quotas (Concurrent Missions)**

Because a POST /fleet/dispatch request physically deploys a human being, you are bound by a **Concurrent Mission Quota**. This is the maximum number of Vanguard Agents your specific fleet can have deployed simultaneously within a single Sector Geohash (e.g., MESA\_AZ\_01).

| Fleet Capacity Tier | Required L402 Escrow | Max Concurrent Agents |
| :---- | :---- | :---- |
| **On-Demand (Testing)** | 0.05 BTC | 5 Active Missions |
| **Sector Priority** | 0.50 BTC | 25 Active Missions |
| **Sector Anchor** | 2.00 BTC | 100+ Active Missions |

*(Note: If you hit this limit, the API returns 503 QUOTA\_EXHAUSTED. You must wait for an active ORP to clear before dispatching another Agent).*

## **3\. Handling "429 Too Many Requests"**

If your AV backend exceeds the digital RPS limits, the PAN Gateway returns HTTP 429\.

\[\!WARNING\]

**Do NOT retry immediately.** Rapid retries will trigger a longer secondary IP block. **DO** implement **Exponential Backoff with Jitter**.

### **Python Implementation Example:**

import time  
import requests

def safe\_dispatch\_request(url, headers, payload):  
    retries \= 0  
    while retries \< 5:  
        response \= requests.post(url, headers=headers, json=payload)  
          
        if response.status\_code \== 429:  
            \# Check the reset header if available, otherwise exponential backoff  
            reset\_time \= response.headers.get("X-RateLimit-Reset")  
            if reset\_time:  
                wait\_time \= max(0, int(reset\_time) \- int(time.time())) \+ 1  
            else:  
                wait\_time \= (2 \*\* retries) \# 1s, 2s, 4s, 8s...  
                  
            print(f"\[WARN\] PAN Gateway rate limited. Cooling down for {wait\_time}s...")  
            time.sleep(wait\_time)  
            retries \+= 1  
        elif response.status\_code \== 503:  
            print("\[CRITICAL\] Physical Quota or Brownout active. Route AV safely and pause dispatches.")  
            break  
        else:  
            return response  
              
    raise Exception("Max retries exceeded for PAN Dispatch.")

## **4\. The "Brownout" Exception (503 Service Unavailable)**

During a severe weather or kinetic anomaly (e.g., an Arizona dust storm), a specific Geohash may reach \>95% Vanguard Agent Utilization.

When this happens, the PAN Gateway enters a **Brownout**, returning 503 GEOHASH\_BROWNOUT\_ACTIVE for all new dispatches in that 1-square-mile zone.

* **Standard Fleets:** Must route unaffected AVs away from the zone.  
* **Sector Anchors:** Are placed in an exclusive priority queue and are automatically routed the next available Vanguard Agent as soon as an existing mission clears.

**Reference:** See [Sector Brownout & Congestion Control](https://www.google.com/search?q=../architecture/specs/v1/brownout_logic.md) for detailed telemetry triggers.