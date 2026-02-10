# Webhook & Callback Integration

**Status:** Active  
**Retry Policy:** Exponential Backoff (up to 24 hours)

To receive real-time updates when a Human Node completes a task, you should configure a Webhook URL in your [Dashboard](https://dashboard.proxyprotocol.com) instead of polling the API.

---

## 1. Supported Events

| Event Name | Trigger | Payload Includes |
| :--- | :--- | :--- |
| `task.matched` | A Human Node has accepted your bid. | `node_id`, `estimated_time` |
| `task.completed` | Work is done and proof uploaded. | `result`, `proof_url`, `signature` |
| `task.failed` | Timeout or Node cancellation. | `reason`, `refund_tx_id` |
| `escrow.locked` | Your Lightning payment is confirmed. | `invoice_hash` |

---

## 2. Payload Structure
All webhooks are sent as `POST` requests with a JSON body.

\```json
{
  "id": "evt_550e8400-e29b",
  "object": "event",
  "created": 1707436800,
  "type": "task.completed",
  "data": {
    "task_id": "task_88293_xyz",
    "status": "completed",
    "result": {
      "summary": "Document Signed",
      "proof_url": "[https://ipfs.io/ipfs/QmX](https://ipfs.io/ipfs/QmX)...",
      "human_signature": "3045022100..."
    }
  }
}
\```

---

## 3. Security: Verifying Signatures
To prevent "Man-in-the-Middle" attacks or spoofed requests, you **must** verify the `X-Proxy-Signature` header sent with every request.

### The Logic:
1. Extract the timestamp from `X-Proxy-Request-Timestamp`.
2. Concatenate `timestamp` + `.` + `raw_json_body`.
3. Compute an **HMAC-SHA256** signature using your `WEBHOOK_SECRET`.
4. Compare your computed signature to the header.

### Python Example:

```python
import hmac
import hashlib

def verify_webhook(header_signature, timestamp, raw_body, secret):
    payload = f"{timestamp}.{raw_body}"
    computed = hmac.new(
        secret.encode(), 
        payload.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed, header_signature)
```

---

## 4. Retries
If your server returns anything other than `200 OK`, our system will automatically retry delivery:

* **Attempt 1:** Immediate
* **Attempt 2:** +30s
* **Attempt 3:** +5m
* **Attempt 4:** +1h
* *...continuing up to 3 days.*

> [!TIP]
> **Idempotency:** Always check the `id` field in the webhook payload to ensure you don't process the same event twice if a retry is triggered by a network timeout.
