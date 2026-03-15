# **Proxy Agent Network (PAN) | Error Code Reference**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

When the PAN Gateway returns an error, the HTTP response body will include a standard JSON error object containing a specific PX\_ numeric code and a string identifier. Do not rely solely on HTTP status codes; utilize the PX\_ code for granular programmatic retry logic and escalation.

## **1\. Authentication & Webhook Security (1xx)**

Errors related to cryptographic request signing and replay-attack prevention.

| Code | String Identifier | HTTP | Description | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| PX\_100 | AUTH\_MISSING\_HEADERS | 401 | Missing HMAC headers. | Ensure X-PAN-Signature and X-PAN-Timestamp are included. |
| PX\_101 | AUTH\_INVALID\_SIGNATURE | 401 | HMAC-SHA256 mismatch. | Verify you are hashing POST:{URI}:{Timestamp}:{RawBody} with your Fleet Secret. |
| PX\_102 | AUTH\_TIMESTAMP\_EXPIRED | 403 | Temporal drift \> 60s. | Resync your Fleet server's NTP daemon to prevent replay attacks. |
| PX\_103 | AUTH\_KEY\_REVOKED | 403 | Fleet Key deactivated. | Your sk\_fleet\_live key was rolled or revoked. Update your environment variables. |

## **2\. L402 Escrow & Liquidity (2xx)**

Errors regarding Lightning Network channel capacity, HODL invoices, and dynamic surge limits.

| Code | String Identifier | HTTP | Description | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| PX\_200 | L402\_BOUNTY\_TOO\_LOW | 402 | Spend cap below current surge. | Your max\_l402\_sats is lower than the active Sector Surge pricing. Increase the cap. |
| PX\_201 | L402\_ESCROW\_FAILED | 402 | Lightning route failed. | Your Treasury node lacks inbound liquidity to route to the PAN Sector Gateway. |
| PX\_202 | L402\_INVOICE\_TIMEOUT | 408 | 30-Minute absolute timeout. | The AV failed to clear the UDS fault. HTLC cancelled and funds reverted to Fleet. |
| PX\_203 | L402\_PREIMAGE\_INVALID | 400 | Preimage hash mismatch. | The AV FAULT\_CLEARED webhook provided an invalid cryptographic secret. |

## **3\. Dispatch & Mission Logic (3xx)**

Validation errors for UDS fault codes, isochrone routing, and idempotency locks.

| Code | String Identifier | HTTP | Description | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| PX\_300 | UDS\_CODE\_UNSUPPORTED | 400 | Invalid fault for physical ORP. | Do not dispatch Vanguard Agents for internal compute/software errors. |
| PX\_301 | GEOFENCE\_OUT\_OF\_BOUNDS | 400 | AV outside active ODD. | The GPS coordinates provided are outside the Mesa AZ-01 Sector polygon. |
| PX\_302 | IDEMPOTENT\_LOCK\_ACTIVE | 409 | Duplicate dispatch request. | Received identical VIN+UDS code within 15 mins. Use force\_override: true if intentional. |
| PX\_303 | MISSION\_NOT\_FOUND | 404 | Invalid or archived mission. | The mission\_id queried does not exist in the active Sector ledger. |

## **4\. Hardware Attestation & Security (4xx)**

Critical errors involving TPM 2.0 signatures, UWB spoofing, and Agent compliance. *(Typically seen in outbound webhooks or audit queries)*.

| Code | String Identifier | HTTP | Description | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| PX\_400 | TPM\_SIGNATURE\_INVALID | 403 | Hardware signature failed. | Agent's Secure Enclave signature is invalid. **CRITICAL SECURITY EVENT**. |
| PX\_401 | UWB\_SPOOFING\_DETECTED | 403 | Time-of-Flight manipulation. | Distance measurement mathematically impossible. Agent permanently slashed. |
| PX\_402 | OS\_ATTESTATION\_FAILED | 403 | Rooted/Jailbroken device. | Apple DeviceCheck or Play Integrity flagged the kernel. Node bricked. |
| PX\_403 | SLA\_BREACH\_TIMEOUT | 410 | 15-Minute SLA expired. | Agent failed to secure a UWB lock in time. Contract cancelled, re-routing initiated. |

## **5\. Sector State & Congestion (5xx)**

Server-side constraints, physical network overload, or quota exhaustion.

| Code | String Identifier | HTTP | Description | Remediation |
| :---- | :---- | :---- | :---- | :---- |
| PX\_500 | GEOHASH\_BROWNOUT\_ACTIVE | 503 | Physical zone saturated. | \>95% Agent Utilization in a 1-sq-mile area. Route AVs away from this intersection. |
| PX\_501 | QUOTA\_EXHAUSTED | 503 | Concurrent max reached. | You have hit your Tier limit for active Vanguard Agents. Wait for a mission to clear. |
| PX\_502 | RATE\_LIMIT\_EXCEEDED | 429 | Digital RPS cap exceeded. | You hit the token-bucket limit. Implement exponential backoff and retry. |
| PX\_503 | GATEWAY\_DESYNC | 500 | LND / Redis internal error. | PAN internal failure. Check status.proxyagent.network for Sector 1 uptime. |

