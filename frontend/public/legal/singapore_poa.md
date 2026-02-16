# LIMITED POWER OF ATTORNEY (SINGAPORE JURISDICTION)

| Governing Law | Statutory Reference |
| :--- | :--- |
| **Republic of Singapore** | Powers of Attorney Act (Cap. 243) / Electronic Transactions Act 2010 |

---

## 1. APPOINTMENT (PREAMBLE)
**THIS INSTRUMENT** is made on the date of the cryptographic timestamp by the Principal, **[PRINCIPAL NAME]** ("Principal"), an autonomous economic entity or its legal owner.

The Principal hereby appoints the Authenticated Human Node identified by **[PROXY NODE ID]** ("Attorney") as their true and lawful attorney-in-fact to act on the Principal's behalf for the limited purposes set forth below.

This appointment is specifically authorized to execute instructions that are cryptographically signed by the following Autonomous Agent Public Key:
`[AGENT_PUBLIC_KEY]`

---

## 2. GRANT OF AUTHORITY (SCOPE)
Pursuant to the *Powers of Attorney Act (Cap. 243)*, the Principal grants the Attorney the limited power to perform the following specific physical and legal acts on the Principal's behalf within the Republic of Singapore:

- [ ] **Digital & SMS Verification:** Receive and relay one-time passwords (OTP) or multi-factor authentication codes to verify the Principal's identity for digital service access, including Singpass-integrated services where permitted.
- [ ] **ACRA & Corporate Filings:** Submit required documentation, annual returns, or incorporation forms to the Accounting and Corporate Regulatory Authority (ACRA).
- [ ] **Identity Representation:** Present valid government-issued identification to third-party service providers (e.g., financial institutions, telcos) to satisfy KYC/AML requirements as regulated by the Monetary Authority of Singapore (MAS).
- [ ] **Contractual Execution:** Sign binding agreements or deeds as directed by the Autonomous Agent, provided the transaction value does not exceed **S$[MAX_LIMIT]**.

---

## 3. RELIANCE ON CRYPTOGRAPHIC INSTRUCTION
In accordance with the *Electronic Transactions Act 2010*, the Attorney is entitled to rely exclusively on instructions signed by the `[AGENT_PUBLIC_KEY]`. Any act performed by the Attorney within the scope of this instrument shall be as binding on the Principal as if the Principal had personally performed the same, recognizing the digital signature as equivalent to a physical signature under Singapore law.

---

## 4. INDEMNITY & TERM
The Principal agrees to indemnify and hold the Attorney harmless from any and all liability, losses, or damages resulting from the faithful execution of the Autonomous Agent's signed instructions, except in cases of the Attorney's fraud or gross negligence.

**Termination:** This authority is limited to the specific task associated with the transaction hash identified below. It shall terminate automatically upon the earlier of:
1. The successful submission of the task proof to the Proxy Protocol.
2. The expiration of the **4-hour execution timer** associated with the Escrow lock.

---

## CRYPTOGRAPHIC ATTESTATION
This instrument is executed as a deed via the Proxy Protocol.

**Signature Hash:** `[TX_HASH]`
**Timestamp:** `[DATE]`
