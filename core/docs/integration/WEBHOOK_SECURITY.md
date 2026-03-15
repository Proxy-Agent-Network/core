# **Proxy Agent Network (PAN) | Webhook Security & Egress Standards**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet DevOps & Security Engineering

Because PAN outbound webhooks deliver critical operational telemetry (e.g., Vanguard Agent UWB proximity locks, L402 Escrow state changes, and SB 1417 Optical Health Reports), securing your receiving endpoint is paramount. This document outlines the mandatory security controls for production Fleet Operator integrations.

## **1\. The "Zero-Trust" Delivery Model**

We assume the public internet is hostile. Simply utilizing an obfuscated URL (e.g., https://api.yourfleet.com/pan/callbacks\_123) is insufficient for cyber-physical infrastructure.

**Mandatory Implementations for Fleet Backends:**

* **Signature Verification:** Prove the sender is the PAN Sector Gateway using HMAC-SHA256 and constant-time comparison.  
* **Replay Protection:** Prove the state change is fresh (sub-60 seconds).  
* **Source Validation:** Prove the TCP connection originates from an authorized PAN egress IP.

## **2\. IP Whitelisting (The Network Layer)**

For enterprise autonomous fleets, we strongly recommend configuring your perimeter firewalls (AWS WAF, Cloudflare, Palo Alto) to drop any requests to your PAN webhook listener that do not originate from our dedicated Sector 1 egress IPs.

**Mesa Sector 1 Production Egress IPs:**

* 35.232.11.42/32 (Primary Gateway)  
* 34.102.88.105/32 (Failover Gateway)

\[\!NOTE\]

These IP addresses are static for the duration of the Mesa Pilot. PAN Command will provide 30 days' notice via the secure Signal channel before modifying or expanding routing infrastructure.

## **3\. Fleet Secret Rotation Strategy**

Your Master Fleet Key (sk\_fleet\_live\_...) is used to generate the X-PAN-Signature on all outbound webhooks. It must be treated with the same security posture as a TLS private key.

### **Routine Rotation (Quarterly)**

We recommend rotating your Fleet Secret every 90 days to maintain compliance:

1. **Generate:** Call POST /v2026.1/fleet/keys/generate to provision a secondary active key.  
2. **Dual-Verify:** Your backend should be configured to temporarily accept HMAC signatures computed from either the **Old** or **New** secret.  
3. **Retire:** Once you confirm your systems are cleanly processing the new signatures, call POST /v2026.1/fleet/keys/revoke targeting the old key.

### **Emergency Rotation (Compromise)**

If you suspect your Fleet Secret has been exposed (e.g., accidentally committed to GitHub):

1. Call POST /v2026.1/fleet/keys/emergency\_rotate immediately.  
2. The PAN API will return a new secret and **instantly invalidate** the old one.

**Warning:** Emergency rotation will cause immediate, localized downtime. Outbound PAN webhooks will fail signature validation on your backend until your environment variables are updated.

## **4\. Replay Attack Mitigation**

To prevent a malicious actor from intercepting a valid mission.orp\_completed payload and re-sending it later to confuse your AV tracking systems, your backend MUST enforce strict temporal bounds.

* **Timestamp Check:** Every outbound request includes an X-PAN-Timestamp header containing the Unix epoch of the event.  
* **The Rule:** If Abs(Now() \- X-PAN-Timestamp) \> 60 seconds, your backend must **REJECT** the request with a 403 Forbidden. Ensure your receiving server's NTP daemon is accurately synced.  
* **Idempotency:** Your webhook handler must extract the event\_id from the JSON payload. Store this ID in a rapid-access cache (e.g., Redis) and discard any subsequent webhooks sharing the same event\_id to prevent duplicate state execution.