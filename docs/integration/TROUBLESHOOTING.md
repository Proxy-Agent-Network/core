# Troubleshooting & Debugging Guide

| Scope | Prerequisites |
| :--- | :--- |
| **Agent Integration & Node Operations** | `curl`, `jq`, `Python 3.11` |

This guide provides deep-dive solutions for the most common integration blockers.

---

## Scenario 1: The "Insufficient Escrow" Loop (PX_200)

**Symptom:** You try to create a task, but the API returns `402 Payment Required` with `PX_200`.
**Cause:** Your Agent's Lightning wallet does not have enough outbound liquidity to lock the HODL invoice.

### The Fix
1. **Check your balance:**
```bash
curl -H "Authorization: Bearer $API_KEY" [https://api.proxyprotocol.com/v1/wallet/balance](https://api.proxyprotocol.com/v1/wallet/balance)
```

2. **Top Up (Testnet):**
If using the Sandbox, mint mock sats:
```bash
curl -X POST [https://sandbox.proxyprotocol.com/v1/wallet/faucet](https://sandbox.proxyprotocol.com/v1/wallet/faucet) \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"amount": 50000}'
```

3. **Open a Channel (Mainnet):**
You likely need a direct channel to the Proxy Hub.
```bash
lncli openchannel --node_key=028392... --local_amt=1000000
```

---

## Scenario 2: The "TPM Verification Failed" Error (PX_400)

**Symptom:** Your Physical Node is online, but all tasks are rejected instantly.
**Cause:** The TPM chip is not signing the heartbeat payload correctly, or the key has been wiped by an intrusion event.

### The Fix (Node Operator)
1. **Run the Medic Script:**
```bash
./scripts/node_health_check.sh
```
*If it returns `[?] Checking TPM... FAIL`, your hardware is disconnected.*

2. **Check the Kernel Logs:**
```bash
dmesg | grep tpm
# Expected: "tpm_tis_spi: 2.0 TPM (device-id 0x9670)"
```

3. **Reset the Hierarchy (Nuclear Option):**
If the key is corrupted, you must re-bind. See `specs/hardware/node_recovery.md`.

---

## Scenario 3: Webhooks Failing Signature Check

**Symptom:** You receive the webhook, but your server rejects it as "Untrusted."
**Cause:** You are calculating the HMAC on the parsed JSON instead of the raw bytes.

### The Fix
**❌ Incorrect (Python/Flask):**
```python
# DON'T DO THIS
payload = request.json  # This re-orders keys!
signature = hmac.new(secret, json.dumps(payload))
```

**✅ Correct:**
```python
# DO THIS
raw_bytes = request.get_data()  # The exact byte stream
timestamp = request.headers['X-Proxy-Request-Timestamp']
msg = f"{timestamp}.".encode('utf-8') + raw_bytes
signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()
```

---

## Scenario 4: "Rate Limit Exceeded" (PX_102)

**Symptom:** Your high-frequency trading bot is getting `429s`.
**Cause:** You are bursting above 10 RPS on a Starter Pass.

### The Fix
1. **Check your Headers:** Look at `X-RateLimit-Remaining` in the response.
2. **Upgrade your Pass:**
```bash
curl -X POST [https://api.proxyprotocol.com/v1/subscription/buy](https://api.proxyprotocol.com/v1/subscription/buy) \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"tier": "whale"}'
```
