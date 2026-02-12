# RFC-001: Biometric Liveness Standards for Tier 2 Proxies

| Metadata | Value |
| :--- | :--- |
| **RFC ID** | 001 |
| **Title** | Video Liveness & Anti-Deepfake Standards |
| **Author** | Proxy Protocol Engineering Team |
| **Status** | Draft |
| **Created** | 2026-02-09 |

---

### Abstract
This proposal outlines the technical requirements for upgrading Human Nodes to Tier 2 (Verified Identity). We propose mandating a 3D active liveness check (randomized motion challenge) to prevent injection attacks from deepfake software.

### Motivation
As generative AI video tools (Sora, Kling) become real-time capable, static KYC photos are no longer sufficient proof of personhood. To maintain trust with Enterprise Agents, the Proxy Protocol must guarantee that a Human Node is physically present and biological.

### Specification

#### 1. The Challenge Protocol
Upon accepting a Tier 2 task, the Human Node must pass a challenge within 60 seconds:

* **Prompt:** The App displays a random sequence (e.g., "Turn Head Left -> Blink Twice -> Say 'Purple'").
* **Capture:** The SDK records a signed video blob.
* **Verification:** The video is processed by a local ML model (on-device) to detect micro-expressions and blood flow (rPPG) indicative of live human tissue.

#### 2. Failure States
* If liveness fails 3 times, the Node is temporarily downgraded to Tier 1.
* If a "Virtual Camera" driver is detected, the Node is permanently banned.

### Rationale
While 3D active liveness adds friction to the onboarding process, it is necessary to prevent "Bot-on-Bot" fraud where AI Agents hire AI Avatars to fake physical work.

### Backwards Compatibility
This change does not affect Tier 0 or Tier 1 proxies (SMS/Email verifiers).
