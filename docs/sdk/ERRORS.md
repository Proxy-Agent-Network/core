# **Proxy Agent Network (PAN) | Error Code Reference**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

## **1\. Error Response Format**

When the PAN Fleet Gateway encounters an error, it returns a standard HTTP status code along with a JSON response body containing a specific error\_code and a descriptive message.

Your Fleet backend should parse the error\_code string to trigger automated retry logic or operational alerts.

### **Example Error Response**

{  
  "error\_code": "QUOTA\_EXHAUSTED",  
  "message": "Maximum concurrent mission quota (25) reached for Sector: MESA\_AZ\_01.",  
  "status\_code": 503,  
  "request\_id": "req\_998877665544"  
}

## **2\. Authentication & Security Errors (401 / 403\)**

These errors occur when the X-PAN-Signature or X-PAN-Timestamp headers fail cryptographic validation.

| Error Code | HTTP Status | Description & Resolution |
| :---- | :---- | :---- |
| AUTH\_MISSING\_HEADERS | 401 Unauthorized | The request is missing required HMAC signature headers. Ensure X-PAN-Signature and X-PAN-Timestamp are present. |
| AUTH\_INVALID\_SIGNATURE | 401 Unauthorized | The HMAC-SHA256 signature does not match the payload. Verify you are hashing the exact POST:{URI}:{Timestamp}:{RawBody} string with your Master Fleet Secret. |
| AUTH\_TIMESTAMP\_EXPIRED | 403 Forbidden | The timestamp provided is more than 60 seconds out of sync with PAN servers. Resync your server's NTP daemon to prevent replay attacks. |

## **3\. Dispatch & Geofence Errors (400 / 404\)**

These errors occur when a Fleet attempts to dispatch an Agent to an unsupported location or for an unsupported vehicle fault.

| Error Code | HTTP Status | Description & Resolution |
| :---- | :---- | :---- |
| UDS\_CODE\_UNSUPPORTED | 400 Bad Request | The provided uds\_fault\_code is not an exterior physical fault (e.g., sending an internal compute error). Vanguard Agents cannot service this fault. |
| GEOFENCE\_OUT\_OF\_BOUNDS | 400 Bad Request | The provided GPS coordinates fall outside active PAN Operational Design Domains (ODDs). Currently restricted to Maricopa County Sector 1\. |
| VEHICLE\_VIN\_INVALID | 400 Bad Request | The vehicle\_vin\_hash format is invalid. It must be a valid SHA-256 hex string. |
| MISSION\_NOT\_FOUND | 404 Not Found | The requested mission\_id does not exist in the active sector ledger or has been archived. |

## **4\. Concurrency & Idempotency Errors (409 / 503\)**

Because PAN interacts with physical human agents, strict concurrency and idempotency rules are enforced.

| Error Code | HTTP Status | Description & Resolution |
| :---- | :---- | :---- |
| IDEMPOTENT\_LOCK\_ACTIVE | 409 Conflict | A duplicate dispatch request was received within the 15-minute SLA window. The response body will echo the active mission\_id and ETA. No new Agent was dispatched. |
| QUOTA\_EXHAUSTED | 503 Service Unavailable | Your Fleet has reached its maximum concurrent Agent deployments for the requested sector. Wait for an active ORP to clear before dispatching again. |
| SECTOR\_AGENTS\_DEPLETED | 503 Service Unavailable | Severe network anomaly. All Vanguard Agents in the sector are currently deployed, and L402 Surge limits have been capped. Apply exponential backoff and retry. |

## **5\. Settlement & L402 Errors (402)**

These errors occur when the L402 Lightning Network escrow fails to lock the required Satoshi bounty.

| Error Code | HTTP Status | Description & Resolution |
| :---- | :---- | :---- |
| L402\_BOUNTY\_TOO\_LOW | 402 Payment Required | The max\_l402\_sats provided in your dispatch payload is lower than the current active Surge Pricing for the sector. Increase your cap or wait for the surge to cool down. |
| L402\_ESCROW\_FAILED | 402 Payment Required | Your Master Fleet Treasury node lacks sufficient inbound liquidity to route the HODL invoice to the PAN Gateway. Rebalance your Lightning channels. |

## **6\. Rate Limiting (429)**

| Error Code | HTTP Status | Description & Resolution |
| :---- | :---- | :---- |
| RATE\_LIMIT\_EXCEEDED | 429 Too Many Requests | You have exceeded the digital token-bucket rate limit for the endpoint. Read the X-RateLimit-Reset header and pause requests until the specified Unix timestamp. |

