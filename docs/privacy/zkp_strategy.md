# Privacy & Zero-Knowledge Strategy

**Problem:** To verify a human's identity (e.g., ID Card), a protocol traditionally requires access to that sensitive document. This creates a "data honey-pot" risk.  
**Solution:** Proxy Protocol implements a Zero-Knowledge (ZK) verification flow utilizing **TLS Notary** and **Local Secure Processing**.

---

## 1. The "Local-First" Principle
For Tier 2 (Identity) tasks, raw data—including photos of IDs and biometrics—is processed directly on the Human Node's device inside a Secure Enclave. This data is **never** uploaded to Proxy Protocol servers.

* **Input:** Raw Camera Feed (ID Card).
* **Process:** Local OCR extraction + Liveness Check.
* **Output:** A cryptographic boolean (e.g., `is_valid=true`, `age>18=true`) signed by the device's hardware TPM.

---

## 2. TLS Notary (Web Proofs)
When a Human Proxy logs into a bank or government portal to verify data for an Agent, the network utilizes **TLS Notary (DECO/mpc-tls)**.

1.  **Handshake:** The Human Node opens a TLS session with the institution (e.g., a Bank).
2.  **Verification:** The Proxy Protocol acts as a secondary verifier of the encryption handshake without having access to the session key.
3.  **Proof:** The Human Node proves to the Agent: *"I am logged into Bank of America and my balance is > $0"* without revealing the password, session tokens, or the exact balance.

---

## 3. Data Expiry (The "Toxic Waste" Policy)
Any data that must be transmitted (e.g., a photo of a physical letter) is treated as "toxic waste"—handled with extreme care and disposed of quickly.

* **Encryption:** All payloads are encrypted with the **Agent's Public Key**. The Proxy Network infrastructure cannot read the content.
* **Storage:** Files are pinned to IPFS with a **24-hour TTL (Time To Live)**.
* **Deletion:** After 24 hours, the garbage collector automatically unpins the file, rendering the data irretrievable from the network.

> [!IMPORTANT]
> Because Proxy Protocol does not store PII, we cannot "recover" lost task results after the 24-hour window has expired. Agents must ingest and archive their own data.
