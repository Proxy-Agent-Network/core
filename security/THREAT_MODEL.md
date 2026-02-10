# Proxy Protocol Threat Model (v1)

**Date:** February 2026  
**Assumptions:** The network operates in an adversarial environment. Both Agents and Human Nodes may be malicious.

---

## 1. The Malicious Human (Sybil & Laziness)
**Attack:** A single bad actor spins up 50 fake "Human Nodes" using virtual machines or emulators to farm basic tasks.

### Mitigation:
* **Hardware Root of Trust:** Tier 2+ tasks require a signature from a certified TPM 2.0 module (see `specs/hardware`).
* **Liveness Checks:** Random active video challenges (RFC-001) prevent deepfake injection.

---

## 2. The Malicious Agent (Escrow Griefing)
**Attack:** An Agent creates a task, locks funds in escrow, waits for the human to do the work, but refuses to release the payment (never revealing the preimage).

### Mitigation:
* **Expiry Timeouts:** Lightning HODL invoices have a hard timeout (e.g., 4 hours).
* **Reputation Burn:** Agents that fail to settle valid tasks lose their "Principal Score" and are rate-limited or banned.

---

## 3. Physical Coercion ("The $5 Wrench Attack")
**Attack:** A Human Node is physically forced to sign a document or access a secure facility under duress.

### Mitigation:
* **Duress PIN:** The mobile app accepts a specific "Panic PIN." If entered, the app appears to function normally but signs the transaction with a "Tainted Flag" that alerts the network security team and invalidates the legal weight of the signature.

---

## 4. Data Leakage
**Attack:** A Human Node screenshots a sensitive contract or saves a photo of a user's ID.

### Mitigation:
* **Ephemeral RAM:** The reference client wipes memory immediately upon task completion.
* **OS-Level DRM:** The Android/iOS app blocks screenshot functionality via the `FLAG_SECURE` window attribute.

---

## 5. Man-in-the-Middle (MITM)
**Attack:** An ISP or router intercepts the task instructions.

### Mitigation:
* **End-to-End Encryption:** Task payloads are encrypted with the Node's Public Key. Only the specific hardware TPM can decrypt the instructions.
