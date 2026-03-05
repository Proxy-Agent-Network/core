# **Proxy Agent Network (PAN) | Cyber-Physical Threat Model**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Assumptions:** The network operates in an adversarial, open-world physical environment. Both digital API vectors and physical hardware vectors must be secured.

## **1\. The Phantom Agent (Location Spoofing & Sybil Attacks)**

**Attack:** A bad actor attempts to farm L402 Satoshi bounties without leaving their home by spinning up emulators and utilizing GPS-spoofing software to simulate arriving at the stranded Autonomous Vehicle (AV).

### **Mitigation:**

* **Hardware Root of Trust:** PAN strictly bans software-based identity. The Vanguard Tactical App requires a hardware signature from an Apple Secure Enclave or Android TPM 2.0 (StrongBox) to verify the physical device. Emulators are permanently blacklisted via DeviceCheck and Play Integrity.  
* **Spatial Attestation (UWB):** GPS is untrusted for the final 15 meters. The Agent must establish an Ultra-Wideband (UWB) Time-of-Flight lock with the AV. Because UWB measures distance via the literal speed of light between two physical radios, it is impossible to spoof remotely.

## **2\. Fleet Swatting (Webhook Injection)**

**Attack:** An attacker intercepts a Fleet Operator's API schema and floods the PAN Gateway with fake /fleet/dispatch payloads, attempting to artificially deploy all available Vanguard Agents to fake locations and exhaust the Fleet's L402 Lightning liquidity.

### **Mitigation:**

* **HMAC-SHA256 Signatures:** All inbound dispatch webhooks must be cryptographically signed using the Fleet's non-transmitted Secret Key.  
* **Temporal Idempotency Lock:** The PAN Gateway hashes VIN \+ UDS\_Fault\_Code \+ 15-Min\_Window. If an attacker (or a glitching AV) sends 50 identical dispatches in 10 seconds, the Gateway returns a 409 Conflict, echoing the original mission ID and consuming zero additional Agent quota or L402 funds.

## **3\. Escrow Griefing & The "Hostage AV"**

**Attack:** A Vanguard Agent arrives on site, establishes a UWB lock, but refuses to clear the sensor unless the remote Fleet Operator manually sends a higher L402 payment outside of the PAN protocol constraints.

### **Mitigation:**

* **Deterministic Settlement:** Human leverage is entirely removed from the financial layer. If the AV's onboard AI does not broadcast the FAULT\_CLEARED webhook within the 30-minute absolute network timeout, the Lightning HODL invoice automatically expires.  
* **Economic & Reputation Slashing:** The funds mathematically revert to the Fleet Treasury. The Agent receives $0 and suffers a HARDWARE\_DAMAGE or ABANDONED\_CONTRACT Vanguard Trust Score (VTS) slashing penalty, leading to immediate network revocation.

## **4\. Physical Environmental Hazards**

**Attack:** A Vanguard Agent is dispatched to an AV that is surrounded by a hostile crowd, actively being vandalized, or involved in a severe kinetic collision (e.g., severe structural damage, not just a dirty sensor).

### **Mitigation:**

* **The Abort Protocol:** Agents are trained infrastructure technicians, not law enforcement. The Tactical App allows the Agent to trigger an ABORT: SCENE UNSAFE command from the safety of their response vehicle.  
* **Zero-Penalty Escalation:** This safely cancels the L402 contract without a VTS slashing penalty and immediately escalates the UDS webhook back to the Fleet Operator for 911/Police dispatch.

## **5\. Proprietary Data & PII Leakage**

**Attack:** A Vanguard Agent takes a high-resolution photo of a damaged, unreleased AV sensor array and attempts to leak it to the press, or accidentally captures civilian license plates/pedestrian faces in the background.

### **Mitigation:**

* **Edge-Vision PII Obfuscation (PIP-018):** The Agent's device runs a local ML model that automatically applies a heavy Gaussian blur to all human faces and civilian license plates *before* the image is saved.  
* **RSA-OAEP Edge Encryption (PIP-016):** The photo is encrypted in volatile RAM using the Fleet Operator's Public Key. The unencrypted source file is permanently zero-filled from the mobile device. The Agent cannot access the photo after capture, and PAN Command cannot decrypt it in transit.