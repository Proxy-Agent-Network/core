# Python SDK Reference

**Package:** `proxy-agent`  
**Version:** `0.1.0`  
**Base URL:** `https://api.proxy-protocol.com/v1`

---

## Client Class
The main entry point for interacting with the Proxy Network.

```python
from proxy_agent import ProxyClient

client = ProxyClient(api_key="sk_live_...")
```

---

## Methods

### `get_market_ticker()`
Fetches the current floor prices for all task types and network congestion data.

* **Returns:** `Dict`
    * `rates`: Object containing price in Sats for `verify_sms_otp`, `legal_notary_sign`, etc.
    * `congestion_multiplier`: `Float` (1.0 = standard, 2.0 = high demand).

---

### `create_task(task_type, requirements, max_budget_sats)`
Broadcasts a task intent to the network mempool.

**Parameters:**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `task_type` | `str` | One of the supported enum values (e.g., `'verify_sms_otp'`). |
| `requirements` | `dict` | Metadata specific to the task (e.g., `{"country": "US"}`). |
| `max_budget_sats` | `int` | The maximum amount you are willing to lock in escrow. |

* **Returns:** `TaskObject` containing the `id` and `status`.

---

### `get_task_status(task_id)`
Polls the network for the result of a specific task.

**Parameters:**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `task_id` | `str` | The unique ID returned by `create_task`. |

* **Returns:** `Dict`
    * `status`: `matching` | `in_progress` | `completed` | `failed`
    * `result`: The proof payload (available only if status is `completed`).

---

## Full Example: SMS Verification

```python
from proxy_agent import ProxyClient

client = ProxyClient("sk_live_your_key")

# 1. Create the task
task = client.create_task(
    task_type="verify_sms_otp",
    requirements={"service": "Twitter", "region": "US"},
    max_budget_sats=5000
)

print(f"Task Created: {task.id}")

# 2. Poll for result
# (In production, use our Webhook integration for efficiency)
status_data = client.get_task_status(task.id)
if status_data['status'] == 'completed':
    print(f"Verification Code: {status_data['result']['otp_code']}")
```
