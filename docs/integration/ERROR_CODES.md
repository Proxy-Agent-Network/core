# Proxy Protocol Error Code Reference (v1)

| Status | Format |
| :--- | :--- |
| **Active** | `PX_{category}_{id}` |

When the Proxy API returns an error, the response body will include a standard error object containing a specific code. Do not rely solely on HTTP status codes; check the `PX_` code for granular handling.

---

## 1. Authentication & Access (1xx)
Errors related to credentials, permissions, and request limits.

| Code | HTTP | Description | Remediation |
| :--- | :--- | :--- | :--- |
| `PX_100` | 401 | Invalid API Key | Check your `Authorization: Bearer` header. |
| `PX_101` | 403 | Subscription Inactive | Proxy-Pass expired. Renew via `/subscription/buy`. |
| `PX_102` | 429 | Rate Limit Exceeded | Hit the RPS cap. Implement exponential backoff. |
| `PX_103` | 403 | IP Not Whitelisted | Unauthorized IP address. Check dashboard settings. |

---

## 2. Financial & Escrow (2xx)
Errors regarding Lightning payments, budget limits, and escrow states.

| Code | HTTP | Description | Remediation |
| :--- | :--- | :--- | :--- |
| `PX_200` | 402 | Insufficient Escrow | `max_budget_sats` exceeds wallet balance. Top up. |
| `PX_201` | 400 | Escrow Lock Failed | HODL invoice generation failed. Retry in 5s. |
| `PX_202` | 409 | Invoice Already Paid | Trying to pay a `LOCKED` invoice. Check status. |
| `PX_203` | 400 | Bid Below Floor | Bid is lower than market floor. Increase bid. |

---

## 3. Task & Logic (3xx)
Validation errors for task parameters, IDs, and lifecycle events.

| Code | HTTP | Description | Remediation |
| :--- | :--- | :--- | :--- |
| `PX_300` | 400 | Unsupported Task Type | Invalid `task_type` enum. Check `catalog.md`. |
| `PX_301` | 404 | Task Not Found | `task_id` does not exist or has expired. |
| `PX_302` | 400 | Invalid Requirements | Missing metadata (e.g., country for SMS). |
| `PX_303` | 410 | Task Expired | 4-hour window closed before proof submission. |

---

## 4. Hardware & Security (4xx)
Critical errors involving TPM signatures, geofencing, and liveness checks.

| Code | HTTP | Description | Remediation |
| :--- | :--- | :--- | :--- |
| `PX_400` | 403 | TPM Verification Failed | Hardware signature invalid. **CRITICAL SECURITY EVENT**. |
| `PX_401` | 403 | Geofence Violation | Node outside allowed radius for this task. |
| `PX_402` | 403 | Liveness Check Failed | Node failed the video anti-deepfake challenge. |
| `PX_403` | 451 | Sanctions List Hit | Wallet flagged by OFAC. Transaction blocked. |

---

## 5. Network State (5xx)
Server-side issues or protocol-level congestion events.

| Code | HTTP | Description | Remediation |
| :--- | :--- | :--- | :--- |
| `PX_500` | 503 | Brownout Active | Congestion high. Buy Whale Pass or retry later. |
| `PX_501` | 503 | No Nodes Available | No matching Nodes (Tier/Region) online. |
| `PX_502` | 500 | Lightning Desync | Internal LND error. Check `status.rob-o-la.com`. |
