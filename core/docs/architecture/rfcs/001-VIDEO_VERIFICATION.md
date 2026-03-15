# **RFC-001: Zero-Biometric Physical Presence & Hardware Attestation**

| Metadata | Value |
| :---- | :---- |
| **RFC ID** | 001 |
| **Title** | Zero-Biometric Physical Presence & Hardware Attestation |
| **Author** | PAN Command / Network Engineering |
| **Status** | Accepted (Mesa Pilot) |
| **Created** | 2026-02-09 |

### **Abstract**

This proposal formally rejects the use of video-based biometric liveness checks (e.g., active facial scanning, rPPG) for Vanguard Agent identity verification. It establishes the **Zero-Biometric Privacy Policy** and mandates the use of localized hardware attestation (TPM 2.0 / Apple Secure Enclave) combined with spatial Ultra-Wideband (UWB) verification to cryptographically guarantee physical human presence.

### **Motivation**

Early drafts of the Proxy Protocol relied on video liveness challenges (e.g., "Turn Head Left \-\> Blink") to prove an Agent was biological and physically present. However, as generative AI video tools (Sora, Kling) become capable of real-time deepfake injection via virtual camera drivers, video verification is no longer a reliable proof of personhood.

Furthermore, ingesting, processing, and storing raw biometric data (facial maps, retinal scans) of our Veteran workforce creates a massive centralized honeypot, exposing PAN to extreme legal liability under expanding state privacy laws. Fleet Operators require proof that a Vanguard Agent is physically standing next to an Autonomous Vehicle (AV), not a video of their face.

### **Specification**

To upgrade to **Active Patrol** status and accept an L402 bounty, Vanguard Agents must satisfy a Two-Factor Physicality Protocol:

#### **1\. The Hardware Attestation (Silicon Identity)**

Instead of capturing a video payload, identity is mathematically bound to the silicon of the PAN-issued mobile device.

* **The Challenge:** When an Agent accepts a mission, the PAN Gateway issues a cryptographic nonce.  
* **Local Biometrics Only:** The Agent authenticates using standard OS-level biometrics (FaceID/Fingerprint). **Crucially, this biometric data never leaves the device.** It merely unlocks the hardware Secure Enclave.  
* **The Signature:** The Secure Enclave/TPM signs the nonce using its non-exportable private key. The PAN Gateway verifies this signature against the Agent's registered public key.

#### **2\. The Spatial Attestation (UWB Time-of-Flight)**

To prove the Agent is actually at the scene (and not solving the hardware challenge from their couch via GPS spoofing):

* The Agent must establish a UWB proximity lock (\< 1.5 meters) with the stranded AV's beacon.  
* The Secure Enclave signs the UWB Time-of-Flight distance measurement, embedding it into the Arizona SB 1417 Optical Health Report.

### **Failure States & Anti-Spoofing**

* **Compromised Kernel:** If Apple DeviceCheck or Android Play Integrity reports a rooted, jailbroken, or emulated environment, the Agent's device is permanently blacklisted.  
* **UWB Spoofing:** Because UWB measures distance via the literal speed of light between two physical radios, remote network-based location spoofing is physically impossible.

### **Rationale**

While establishing a strict hardware requirement (iPhone 16+ / Pixel 9+) increases capital expenditure for the network, it is the only way to completely eliminate "Phantom Agent" fraud without violating the Zero-Biometric mandate. It protects Fleet Partners' $150,000 assets with military-grade cryptography rather than fallible AI-vision models.

### **Backwards Compatibility**

This RFC deprecates all legacy Tier 1/Tier 2 software-only identities. Standard web-based onboarding or hardware architectures lacking a dedicated TPM 2.0 coprocessor are permanently restricted from the Mesa Pilot routing pool.