# **Proxy Agent Network (PAN) | Authentication & Security Standards**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0 (Supersedes v1 Bearer Token Model)

**Target:** Fleet API (V2X) & Vanguard Mobile Nodes

## **1\. Deprecation of Bearer Tokens**

The legacy v1 Proxy Protocol utilized standard HTTP Bearer Tokens (Authorization: Bearer). Because the Proxy Agent Network (PAN) now triggers the physical deployment of human beings to $150,000 autonomous assets, standard static tokens are highly vulnerable to interception, replay attacks, and leakage.

**Bearer Tokens are officially deprecated.** All requests to the PAN API must now utilize the Dual-Layer Zero-Trust Authentication Model.

## **2\. The Dual-Layer Security Model**

The Proxy Network uses two distinct authentication schemes depending on the actor:

* **Fleet Operators (Server-to-Server):** HMAC-SHA256 Request Signing.  
* **Vanguard Agents (Mobile-to-Server):** Hardware Attestation (TPM 2.0 / Apple Secure Enclave).

## **3\. Fleet Operator Authentication (HMAC)**

Fleet Operators (e.g., Waymo, Zoox) are issued a Master Secret Key (sk\_fleet\_live\_...). **This key is never transmitted over the network.** Instead, it is used to cryptographically sign every HTTP request, verifying both identity and payload integrity.

### **Header Construction**

Every API request must include a calculated signature and a strict UTC timestamp:

POST /v2026.1/fleet/dispatch HTTP/1.1  
Host: api.proxyagent.network  
X-PAN-Timestamp: 1780541400  
X-PAN-Signature: a8f5f167f44f4964e6c998dee827110c...  
Content-Type: application/json

### **Signature Generation Logic**

The X-PAN-Signature is an HMAC-SHA256 hash of the following concatenated string:

{HTTP\_METHOD}:{URI}:{X-PAN-Timestamp}:{Raw\_JSON\_Body}

## **4\. Vanguard Agent Authentication (Hardware)**

Vanguard Agents do not use passwords or API keys. Their identity is bound directly to the silicon of their whitelisted mobile device to prevent GPS spoofing and Sybil attacks.

* **No Software Keys:** The ECDSA secp256r1 private key is generated and fused into the hardware Secure Enclave during physical provisioning at the Mesa Hub.  
* **Payload Signing:** When an Agent accepts a mission or completes an Optical Reclamation Protocol (ORP), the JSON payload is hashed, passed to the Secure Enclave, and signed with the non-exportable private key.  
* **Biometric Gating:** The hardware will only sign the payload after a successful local biometric verification (FaceID/Fingerprint), ensuring the authorized human is physically holding the device.

## **5\. Security Best Practices**

1. **NTP Synchronization:** The PAN Gateway enforces a strict 60-second temporal window. If your Fleet server's X-PAN-Timestamp drifts more than 60 seconds from our NTP servers, the request is rejected (403 Forbidden) to prevent replay attacks.  
2. **Verify Outbound Webhooks:** Always verify the X-PAN-Signature on webhooks coming *from* PAN to your Fleet backend to prevent payload injection ("Fleet Swatting").  
3. **Key Rotation:** We recommend rotating your sk\_fleet\_live keys every 90 days via the PAN Fleet Dashboard.

## **6\. Rate Limits & Physical Quotas**

Basic digital rate limits (RPS) have been superseded by **Concurrent Mission Quotas** (Physical Constraints).

* **Standard Tier:** 5 Active Missions per Sector.  
* **Enterprise Tier:** 100+ Active Missions per Sector.

If you exceed your physical deployment limits, the API will return a 503 Service Unavailable (QUOTA\_EXHAUSTED) response until an active Vanguard Agent clears a fault and re-enters the available routing pool.