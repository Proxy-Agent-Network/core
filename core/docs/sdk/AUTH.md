# **Proxy Agent Network (PAN) | Authentication Standards (HMAC & TPM)**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) & Vanguard Mobile SDK

## **1\. The Zero-Trust Security Model**

The Proxy Agent Network (PAN) operates a strict Zero-Trust architecture. Because our API endpoints trigger physical human deployment to $150,000+ autonomous assets, standard API tokens are insufficient.

PAN utilizes a dual-authentication model:

1. **Fleet Operators (Server-to-Server):** HMAC-SHA256 Request Signing to prevent man-in-the-middle (MITM) and replay attacks.  
2. **Vanguard Agents (Mobile-to-Server):** TPM 2.0 / Secure Enclave Hardware Attestation to mathematically guarantee the physical identity and presence of the human responder.

## **Part 1: Fleet Operator Authentication (HMAC)**

When a Fleet Gateway (e.g., Waymo's backend) dispatches a webhook to PAN, the request must be cryptographically signed using a pre-shared Master Fleet Key.

*Note: If you are using the pan-fleet-sdk (Python/Node), this HMAC generation is handled automatically.*

### **The HMAC Signature Process**

1. **The Shared Secret:** Upon onboarding, your Fleet is issued an sk\_fleet\_live\_... secret key. **Never transmit this key over the network.**  
2. **The Payload String:** Concatenate the following elements exactly as shown, separated by a colon ::  
   * HTTP Method (e.g., POST)  
   * Endpoint URI (e.g., /v2026.1/fleet/dispatch)  
   * Current Unix Timestamp (e.g., 1780541400\)  
   * Raw JSON Request Body  
3. **The Hash:** Generate an HMAC-SHA256 hash of the Payload String using your Fleet Secret Key.  
4. **The Headers:** Include the timestamp and the resulting hash in your HTTP headers.

### **Required HTTP Headers**

X-PAN-Timestamp: 1780541400  
X-PAN-Signature: a8f5f167f44f4964e6c998dee827110c...

### **Python Raw Implementation Example**

import hmac  
import hashlib  
import time  
import json  
import requests

fleet\_secret \= b"sk\_fleet\_live\_your\_secret\_key"  
uri \= "/v2026.1/fleet/dispatch"  
body \= json.dumps({"vin\_hash": "e3b0c...", "uds\_code": "LIDAR\_MUD"})  
timestamp \= str(int(time.time()))

\# Construct payload string  
payload \= f"POST:{uri}:{timestamp}:{body}".encode('utf-8')

\# Generate HMAC-SHA256 signature  
signature \= hmac.new(fleet\_secret, payload, hashlib.sha256).hexdigest()

headers \= {  
    "X-PAN-Timestamp": timestamp,  
    "X-PAN-Signature": signature,  
    "Content-Type": "application/json"  
}

response \= requests.post(f"\[https://api.proxyagent.network\](https://api.proxyagent.network){uri}", headers=headers, data=body)

### **Anti-Replay Protection**

The PAN API will reject any request where X-PAN-Timestamp drifts more than **60 seconds** from the PAN server's current UTC time.

## **Part 2: Vanguard Agent Attestation (TPM / Secure Enclave)**

To prevent GPS spoofing, Sybil attacks, and account sharing, Vanguard Agents do not use passwords. Their identity is inextricably linked to the physical hardware of their PAN-issued mobile device (iPhone 16+ or Android Pixel 9+).

### **The Hardware Root of Trust**

1. **Key Generation (Provisioning):** During the Mesa Sector onboarding phase, the Agent's mobile device generates a public/private keypair directly inside the Apple Secure Enclave or Android StrongBox (TPM).  
2. **Non-Exportable:** The private key is mathematically locked inside the silicon. It cannot be extracted, copied, or intercepted, even by the PAN mobile app itself.  
3. **Public Key Registration:** The corresponding public key is registered in the PAN Identity Registry, mapped to the Agent's Veteran DD-214 background check.

### **Mission Execution Signing**

When an Agent accepts a mission or completes the Optical Reclamation Protocol (ORP), they are required to sign the payload.

1. The PAN app generates a JSON payload containing the mission\_id, UWB proximity distance, and the timestamp.  
2. The app requests the Secure Enclave to sign the hash of this payload.  
3. The Agent authenticates to the Enclave (via FaceID/Biometrics). *Note: PAN never sees the biometric data; it only receives the mathematical signature from the Enclave.*  
4. The signed payload is transmitted to the PAN Gateway.

### **SB 1417 Compliance**

This TPM-backed signature is the cornerstone of the Arizona SB 1417 Optical Health Report. It proves to State Regulators that the exact, certified individual was physically holding the device next to the autonomous vehicle when the fault was cleared.