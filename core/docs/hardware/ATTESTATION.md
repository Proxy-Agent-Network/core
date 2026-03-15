# **Proxy Agent Network (PAN) | Hardware Attestation (TPM 2.0 / Enclave)**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Mobile Hardware & Identity Registry

## **1\. The Zero-Trust Mobile Node**

In standard gig-economy platforms, worker identity is verified via an email, a password, and a standard OAuth token. This architecture is highly vulnerable to account sharing, GPS spoofing, and emulator farms.

Because Vanguard Agents physically interact with $150,000 autonomous assets and generate legally binding Arizona SB 1417 compliance logs, the Proxy Agent Network (PAN) cannot rely on software-level identity. We require a **Hardware Root of Trust**.

Every PAN-issued mobile device acts as a cryptographic node on the network. The human is not the node; the human *operates* the hardware node using biometric authorization.

## **2\. The Hardware Root of Trust**

PAN supports two strictly whitelisted mobile architectures:

1. **Apple iOS (iPhone 16 Pro+):** Utilizing the Apple Secure Enclave.  
2. **Android (Pixel 9 Pro+ / Samsung Galaxy S24+):** Utilizing the Android StrongBox (TPM 2.0).

### **Key Generation & Non-Exportability**

During the Vanguard Agent onboarding process at the Mesa Operations Hub, the PAN app instructs the device's secure hardware coprocessor to generate an ECDSA (Elliptic Curve Digital Signature Algorithm) secp256r1 public/private keypair.

* **The Private Key:** is mathematically fused to the silicon of the TPM/Secure Enclave. It is non-exportable. It cannot be backed up to iCloud, copied to another device, or extracted by the PAN app itself.  
* **The Public Key:** is exported and registered in the PAN Identity Registry, permanently bound to the Agent's verified identity (SSN/DD-214 background check).

## **3\. The Attestation Lifecycle**

To execute missions, the device must continuously prove its cryptographic integrity to the PAN Gateway.

### **Phase 1: Shift Authentication (Boot)**

When an Agent swipes to ACTIVE\_PATROL, the PAN Gateway generates a cryptographic nonce (a random, single-use string) and sends it to the device. The Agent must authenticate to the Secure Enclave via biometrics (FaceID/Fingerprint). The Enclave signs the nonce using the locked Private Key and returns the signature. The Gateway verifies this against the registered Public Key.

### **Phase 2: Action Signing (Mission Execution)**

Standard API tokens are not used to update mission statuses. When an Agent taps ACCEPT on an L402 bounty, or signals ORP\_COMPLETED, the PAN Tactical App generates a JSON payload containing the action intent, GPS coordinates, and a timestamp.

The Secure Enclave signs the SHA-256 hash of this entire payload. This guarantees the action was executed by the specific hardware device at that exact moment.

### **Phase 3: Continuous Hardware Attestation (SafetyNet/DeviceCheck)**

To prevent tampering (e.g., rooting, jailbreaking, or using GPS-spoofing software), the PAN Tactical App silently polls Google Play Integrity API (Android) and Apple DeviceCheck (iOS) every 5 minutes while on patrol. If the OS reports a compromised kernel, the device is immediately locked out of the network.

## **4\. SB 1417 Compliance Integration**

The Arizona SB 1417 mandate requires an independent audit of the physical intervention. The hardware attestation signature is the core legal mechanism that shields Fleet Operators from liability.

When the AV clears its fault code, the **Optical Health Report (OHR)** is generated. The OHR directly embeds the Agent's TPM signature. This mathematically proves to State Regulators and insurance adjusters that a vetted, sober, and certified Vanguard Agent was physically holding the authorized device next to the vehicle when the repair was executed.

## **5\. Device Loss & Hardware Slashing**

Because the identity is bound to the silicon:

* **Lost/Stolen Device:** If a Vanguard Agent reports a device as lost, the associated Public Key is instantly cryptographically revoked ("Slashed") from the Identity Registry. Even if a bad actor bypasses the biometric lock, the hardware signature will be rejected by the PAN Gateway.  
* **Device Upgrades:** A Vanguard Agent cannot simply download the app on a new phone. The new device must go through a localized provisioning sequence at the Mesa Hub to generate a new hardware-bound keypair and update the Identity Registry.