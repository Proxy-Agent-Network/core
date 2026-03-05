# **Proxy Agent Network (PAN) | Zero-Knowledge & Privacy Architecture**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Security Operations & Regulatory Compliance

**The Problem:** To mathematically prove that an authorized human executed a physical intervention on an Autonomous Vehicle (AV), traditional systems require harvesting sensitive biometric data (e.g., facial scans, ID photos) and high-fidelity location tracking. This creates a massive "data honeypot" risk.

**The Solution:** PAN implements a Zero-Knowledge (ZK) privacy flow utilizing **Hardware Enclaves**, **Edge-Vision ML**, and **Asymmetric Telemetry Encryption**.

## **1\. Zero-Knowledge Biometrics (Local-First)**

For an Agent to accept an L402 contract or sign an SB 1417 Optical Health Report (OHR), PAN must verify that the authorized human is physically holding the device. However, PAN **never** ingests or stores raw biometric data.

* **Input:** Raw biometric scan (FaceID / Fingerprint).  
* **Process:** The biometric evaluation occurs entirely inside the mobile device's physical Secure Enclave (Apple) or StrongBox (Android TPM 2.0).  
* **Output:** The PAN Tactical App receives a cryptographic boolean (e.g., biometric\_match=true). This unlocks the hardware's private key, which signs the UWB proximity payload. PAN only receives the resulting mathematical signature, maintaining a Zero-Knowledge posture regarding the Agent's actual biometric map.

## **2\. Edge-Vision PII Obfuscation (PIP-018)**

When a Vanguard Agent is required to take a compliance photo of a severely damaged AV sensor (e.g., a shattered LiDAR dome), the background may inadvertently capture civilian bystanders or private license plates.

* **Local Inference:** Before the image is saved or transmitted, a local ML model (CoreML / ML Kit) sweeps the frame in volatile RAM.  
* **Obfuscation:** All detected human faces and non-AV license plates are heavily blurred (Gaussian, 30px minimum).  
* **The "Toxic Waste" Policy:** The original, unredacted raw image is immediately zero-filled from the device's memory. It is never written to disk or uploaded to the cloud.

## **3\. Asymmetric Telemetry Encryption (PIP-016)**

Fleet Operators (e.g., Waymo, Zoox) consider their hardware failure rates and proprietary UDS diagnostic imagery to be highly classified trade secrets.

To prevent PAN from becoming a centralized vulnerability for Fleet espionage, proprietary mission telemetry is treated as "toxic waste."

1. **Edge Encryption:** Any high-resolution photos or proprietary diagnostic outputs captured by the Vanguard Agent are encrypted locally on the mobile device using the **Fleet Operator's RSA-OAEP Public Key**.  
2. **Blind Routing:** PAN routes the encrypted payload to the Fleet Operator. PAN Command cannot decrypt or view the contents of the payload.  
3. **Data Expiry:** High-fidelity Agent routing telemetry (1-second GPS polling) used to calculate Time-to-Site is permanently purged from PAN databases **48 hours** after the AV broadcasts the FAULT\_CLEARED webhook.

\[\!IMPORTANT\]

**Regulatory Exception:** The specific cryptographic hashes comprising the SB 1417 Optical Health Report (Agent ID, TPM Signature, Timestamp, UWB Distance) are *not* encrypted. They are retained in plaintext on immutable WORM storage for **7 years** to satisfy mandatory Arizona DPS auditing requirements.