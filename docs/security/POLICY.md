# **Proxy Agent Network (PAN) | Security Policy & Defense-in-Depth**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet CISOs, Security Teams, & Researchers

## **1\. The Cyber-Physical Threat Model**

Most enterprise SaaS platforms model threats around data exfiltration or service disruption. The Proxy Agent Network (PAN) faces a vastly more complex threat matrix: our API endpoints trigger the physical deployment of human beings to interact with $150,000 autonomous assets in active traffic environments.

A compromised PAN endpoint does not just result in a data leak; it could result in unauthorized physical access to a grounded vehicle, "swatting" (maliciously deploying Agents), or the financial draining of Fleet Lightning treasuries.

To mitigate these risks, PAN operates on a strict **Zero-Trust, Defense-in-Depth** architecture across four distinct layers.

## **2\. Layer 1: Hardware Root of Trust (Identity)**

We completely reject software-based identity (passwords, standard OAuth, or SMS OTPs) for our Vanguard Agents. Software identity is vulnerable to account sharing, phishing, and emulator farms.

* **TPM 2.0 & Secure Enclave:** Every Agent operates a certified mobile node. Cryptographic ECDSA keypairs are generated inside the silicon during provisioning.  
* **Non-Exportability:** The private key cannot be extracted by the OS or the PAN application.  
* **Biometric Gating:** The secure enclave will only sign action intents (like accepting a mission) after verifying the Agent's biometrics locally.  
* **Continuous Attestation:** The network silently polls Apple DeviceCheck and Android Play Integrity to instantly slash rooted or jailbroken devices from the routing pool.

## **3\. Layer 2: Network & API Security (V2X Communications)**

Machine-to-Human (M2H) dispatch requests must be cryptographically verified to prevent unauthorized payloads.

* **HMAC-SHA256 Request Signing:** All inbound Fleet dispatches and outbound PAN callbacks require a constant-time HMAC signature verification.  
* **Anti-Replay Protection:** API requests with an X-PAN-Timestamp drifting more than 60 seconds from our NTP servers are instantly dropped.  
* **Temporal Idempotency Locks:** To prevent network saturation from a disconnected AV double-sending a fault code, PAN hashes the VIN \+ Fault Code \+ 15-Min Window. Duplicate requests within the SLA window receive a 409 Conflict without consuming quota.

## **4\. Layer 3: Spatial & Physical Security (Anti-Spoofing)**

A malicious actor might attempt to intercept a bounty by spoofing their GPS coordinates to make it appear they are standing next to a vehicle.

* **UWB Time-of-Flight:** GPS is only used for macro-routing. The final 15 meters require a Bluetooth Low Energy (BLE) handshake and an Ultra-Wideband (UWB) proximity lock. UWB Time-of-Flight calculates distance at the speed of light and cannot be spoofed remotely.  
* **Sector Geofencing:** Agents are strictly bounded to their assigned Operational Design Domain (ODD). If an Agent leaves the Mesa AZ-01 polygon, their telemetry is dropped and they are forced into an OFF\_DUTY state.

## **5\. Layer 4: Financial Security (Zero-Custody L402)**

PAN acts as an information and routing bridge; it does not custody Fleet capital.

* **HODL Invoices:** Satoshi bounties are locked in point-to-point Hashed Timelock Contracts (HTLCs) on the Lightning Network.  
* **Machine-Verified Settlement:** PAN cannot unilaterally authorize a payout. The funds are only released when the Autonomous Vehicle's onboard AI clears the physical fault code and releases the cryptographic preimage.  
* **Time-Bound Escrow:** If an intervention fails or an SLA is breached, the HODL invoice expires (maximum 30 minutes) and funds mathematically revert to the Fleet Operator's treasury.

## **6\. Vulnerability Disclosure & Bug Bounty**

We welcome collaboration with the security research community. If you believe you have discovered a vulnerability in the PAN Gateway, the L402 escrow logic, or the Mobile SDK, please adhere to our responsible disclosure guidelines.

* **Do NOT** perform physical penetration testing on live Autonomous Vehicles.  
* **Do NOT** attempt to socially engineer Vanguard Agents in the field.  
* **Do NOT** execute volumetric DDoS attacks against production endpoints.

Please submit all technical findings, proof-of-concept code, and CVSS scores via our encrypted Signal drop or PGP-encrypted email to security@proxyagent.network. Critical vulnerabilities affecting the L402 settlement engine or TPM attestation flow are eligible for high-tier bounties paid directly in BTC.