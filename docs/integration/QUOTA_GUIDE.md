# API Quotas & Rate Limiting Strategy

| Module | Policy |
| :--- | :--- |
| **Traffic Controller** | Dynamic Token Bucket |

To maintain network stability and guarantee throughput for paying customers, the Proxy Protocol enforces strict rate limits based on the **Authorization** token presented.

---

## 1. Subscription Tiers & Limits
Your request throughput is determined by the `proxy_pass_token` (JWT) in your header.

| Subscription Tier | Requests Per Second (RPS) | Burst Allowance | Daily Task Cap |
| :--- | :--- | :--- | :--- |
| **Anonymous / Free** | 1 RPS | 5 Requests | 10 Tasks |
| **Starter Pass** | 10 RPS | 50 Requests | 500 Tasks |
| **Pro Pass** | 50 RPS | 200 Requests | 5,000 Tasks |
| **Whale Pass** | Unlimited* | 1,000+ Requests | Unlimited |

*\*Whale Pass limits are infrastructure-bound rather than policy-bound.*

---

## 2. Response Headers (The "Gas Gauge")
Every API response includes headers telling you exactly where you stand. Monitor these programmatically to avoid being throttled.

* `X-RateLimit-Limit`: Your total allowed RPS.
* `X-RateLimit-Remaining`: Requests left in the current window.
* `X-RateLimit-Reset`: Unix timestamp when your bucket refills.

### Example Header
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 49
X-RateLimit-Reset: 1707436800
```

---

## 3. Handling "429 Too Many Requests"
If you exceed your quota, the API returns `HTTP 429`.

> [!WARNING]
> **Do NOT retry immediately.** You will likely trigger a longer secondary block. **DO** implement **Exponential Backoff**.

### Python Implementation:
```python
import time
import requests

def safe_request(url):
    retries = 0
    while retries < 5:
        response = requests.get(url)
        if response.status_code == 429:
            wait_time = 2 ** retries  # 1s, 2s, 4s, 8s...
            print(f"Rate limited. Cooling down for {wait_time}s...")
            time.sleep(wait_time)
            retries += 1
        else:
            return response
```

---

## 4. The "Brownout" Exception
During a **Network Brownout** (congestion event), even Whale Pass holders may see reduced limits on *write* operations (creating tasks), though *read* operations (checking status) remain prioritized. 

**Reference:** See [specs/v1/brownout_logic.md](./specs/v1/brownout_logic.md).
