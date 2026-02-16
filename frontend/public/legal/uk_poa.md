# LIMITED POWER OF ATTORNEY (UK JURISDICTION)

| Governing Law | Statutory Reference |
| :--- | :--- |
| **England and Wales** | Powers of Attorney Act 1971 |

---

## 1. APPOINTMENT (PREAMBLE)
**THIS INSTRUMENT** is made on the date of the cryptographic timestamp by the Principal, **[PRINCIPAL NAME]** ("Principal"), an autonomous economic entity or its legal owner.

The Principal hereby appoints the Authenticated Human Node identified by **[PROXY NODE ID]** ("Attorney") as their true and lawful attorney-in-fact to act on the Principal's behalf for the limited purposes set forth below.

This appointment is specifically authorized to execute instructions that are cryptographically signed by the following Autonomous Agent Public Key:
`[AGENT_PUBLIC_KEY]`

---

## 2. GRANT OF AUTHORITY (SCOPE)
Pursuant to the Powers of Attorney Act 1971, the Principal grants the Attorney the limited power to perform the following specific physical and legal acts on the Principal's behalf within the United Kingdom:

- [ ] **Digital & SMS Verification:** Receive and relay one-time passwords (OTP) or multi-factor authentication codes to verify the Principal's identity for digital service access.
- [ ] **Identity Representation:** Present valid government-issued identification to third-party service providers (e.g., banking, telecommunications) to satisfy UK KYC/AML requirements under the *Money Laundering Regulations*.
- [ ] **Physical Correspondence:** Receive, digitize (scan), and transmit physical mail addressed to the Principal at a UK residential or business address, subject to the *Postal Services Act 2000*.
- [ ] **Contractual Execution:** Sign binding agreements or deeds as directed by the Autonomous Agent, provided the transaction value does not exceed **£[MAX_LIMIT]**.

---

## 3. RELIANCE ON CRYPTOGRAPHIC INSTRUCTION
In accordance with the *Electronic Communications Act 2000*, the Attorney is entitled to rely exclusively on instructions signed by the `[AGENT_PUBLIC_KEY]`. Any act performed by the Attorney within the scope of this instrument shall be as binding on the Principal as if the Principal had personally performed the same.

---

## 4. INDEMNITY & TERM
The Principal agrees to indemnify and hold the Attorney harmless from any and all liability, losses, or damages resulting from the faithful execution of the Autonomous Agent's signed instructions, except in cases of the Attorney's fraud or willful misconduct.

**Termination:** This authority is limited to the specific task associated with the transaction hash identified below. It shall terminate automatically upon the earlier of:
1. The successful submission of the task proof to the Proxy Protocol.
2. The expiration of the **4-hour execution timer** associated with the Escrow lock.

---

## CRYPTOGRAPHIC ATTESTATION
This instrument is executed as a deed via the Proxy Protocol.

**Signature Hash:** `[TX_HASH]`
**Timestamp:** `[DATE]`
