# Webhook Security Standards (v1)

**Scope:** Real-Time Event Delivery  
**Target Audience:** DevOps / Security Engineering

Because webhooks deliver sensitive operational data (PII, Escrow Status), securing the receiving endpoint is critical. This document outlines the mandatory security controls for production integration.

---

## 1. The "Zero-Trust" Delivery Model
We assume the public internet is hostile. Simply utilizing a "secret URL" (e.g., `https://api.yourapp.com/hooks/secret_123`) is insufficient.

**Mandatory Implementations:**
* **Signature Verification:** Prove the sender is Proxy Protocol.
* **Replay Protection:** Prove the message is fresh.
* **Source Validation:** Prove the IP address is authorized.

---

## 2. IP Whitelisting (The Network Layer)
For high-security environments (Tier 3/Legal), we recommend configuring your firewall (AWS WAF, Cloudflare, etc.) to only accept `POST` requests from our dedicated egress IPs.

**Production Egress IPs:**
* `35.232.11.0/24` (Primary)
* `34.102.88.0/24` (Backup)

> [!NOTE]
> These ranges are static. We provide 30 days' notice via `security@proxy.agent.network` before rotating them.

---

## 3. Secret Rotation Strategy
Your `WEBHOOK_SECRET` (used for HMAC signatures) should be treated with the same security as a private key.

### Routine Rotation (Quarterly)
We recommend rotating your secret every 90 days:
1.  **Generate:** Create a new secret in the Proxy Dashboard.
2.  **Dual-Verify:** Your backend should temporarily accept signatures from either the **Old** or **New** secret for a 24-hour window.
3.  **Retire:** Revoke the Old secret once propagation is confirmed.

### Emergency Rotation (Compromise)
If you suspect a leak:
1.  Call `POST /v1/webhooks/rotate_secret` immediately.
2.  The API will return a new secret and instantly invalidate the old one.

**Warning:** This will cause a brief downtime (failed signatures) until your environment variables are updated.

---

## 4. Replay Attack Mitigation
To prevent an attacker from intercepting a valid payload and re-sending it later, the following checks are mandatory:

* **Timestamp Check:** Every request includes an `X-Proxy-Request-Timestamp` header.
* **The Rule:** If `Now() - Timestamp > 5 minutes`, **REJECT** the request.
* **Idempotency:** Your handler must track and process the same `event_id` only once to prevent duplicate execution.
