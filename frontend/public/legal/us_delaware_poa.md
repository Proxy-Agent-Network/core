# LIMITED POWER OF ATTORNEY (US - DELAWARE)

| Governing Law | Statutory Reference |
| :--- | :--- |
| **State of Delaware** | Delaware Code Title 12, Chapter 40 (Durable Power of Attorney Act) |

---

## 1. APPOINTMENT (PREAMBLE)
I, **[PRINCIPAL NAME]** ("Principal"), an autonomous economic entity or its legal owner, hereby appoint the Human Proxy Node identified by **[PROXY NODE ID]** ("Attorney-in-Fact") to act as my agent.

This appointment is specifically authorized to execute instructions that are cryptographically signed by the following Autonomous Agent Public Key:
`[AGENT_PUBLIC_KEY]`

---

## 2. GRANT OF AUTHORITY (SCOPE)
Pursuant to the Delaware Statutory Durable Power of Attorney Act, the Principal grants the Attorney-in-Fact the limited power to perform the following acts within the State of Delaware or as required by Delaware-registered entities:

- [ ] **Corporate Filings:** Submit certificates of incorporation, amendments, or annual reports to the Delaware Secretary of State.
- [ ] **Identity Verification:** Present government-issued identification to financial institutions or service providers to satisfy KYC (Know Your Customer) requirements for accounts owned by the Principal.
- [ ] **Digital Acknowledgment:** Receive and relay one-time passwords (OTP) or multi-factor authentication codes required to access digital accounts.
- [ ] **Contractual Execution:** Affix a physical or digital signature to agreements as directed by the Autonomous Agent, provided the transaction value does not exceed **$[MAX_LIMIT]**.

---

## 3. RELIANCE ON CRYPTOGRAPHIC INSTRUCTION
The Attorney-in-Fact is entitled to rely exclusively on instructions signed by the `[AGENT_PUBLIC_KEY]`. Any act performed by the Attorney-in-Fact within the scope of this instrument is as binding on the Principal as if the Principal were personally present and executed the same.

---

## 4. INDEMNITY & TERM
The Principal agrees to indemnify and hold the Attorney-in-Fact harmless from any and all liability, losses, or damages incurred while acting in good faith under this instrument.

**Termination:** This authority is limited to the specific task associated with the transaction hash identified below. It shall terminate automatically upon the earlier of:
1. The successful submission of the task proof to the Proxy Protocol.
2. The expiration of the **4-hour execution timer** associated with the Escrow lock.

---

## CRYPTOGRAPHIC ATTESTATION
This instrument is executed as a deed via the Proxy Protocol.

**Signature Hash:** `[TX_HASH]`
**Timestamp:** `[DATE]`
