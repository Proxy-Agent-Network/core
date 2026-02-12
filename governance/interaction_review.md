# High Court Interaction Review (v1.0)

This document defines the interaction model between the **Appellate Court VRF**, the **Node Reputation Registry**, and the wider **Proxy Protocol settlement layer**.

---

## 1. The "Super-Elite" Threshold

To qualify for the High Court, a node must maintain a **Reputation Score >= 950**. While `specs/v1/reputation.md` defines the "Elite" tier as `> 800`, this logic creates a **"Super-Elite"** sub-tier for protocol-level adjudication.

* **Interaction**: Gating the High Court to the top ~5% of nodes ensures that judges have significant **"reputation skin in the game,"** making collusion or Sybil attacks on the governance layer prohibitively expensive.
* **Auditability**: Jurors are not only technologically stable but have a verified history of honest participation in lower-tier tasks and standard Jury Tribunals.

---

## 2. Entropy Selection Protocol

Juror selection is triggered by a **SEV-1 event (Protocol Emergency)**. To prevent "Front-running" or selection manipulation, the protocol utilizes the **Next Block Selection** rule.

* **Protocol Logic**: The VRF waits for the next Bitcoin block to be mined after the incident is logged.
* **Unpredictability**: Using the Bitcoin block hash as the entropy seed ensures that the selection is globally public and impossible for the Foundation or any single actor to "game" or influence.
* **Verification**: Any participant can independently verify the 7-member jury roster by combining the block hash with the public list of 950+ REP nodes and running the stable shuffle algorithm.

---

## 3. Adjudication & Evidence Workflow

The High Court operates as the final validator for the **Legal Bridge** and high-value disputes.

* **Convocation**: The VRF selects 7 jurors immediately upon seed availability.
* **Evidence Delivery**: Encrypted task metadata and binary TPM proofs are pushed to the Jurors' `tamper_listener.py` secure buffer for review.
* **Double-Blind Review**: Jurors vote independently without visibility into other responses to enforce **"Schelling Point"** game theory.
* **Proof of Adjudication**: The final `vrf_score` is bound to the Verdict Proof. This provides the cryptographic link between the human decision and the hardware-attested execution.

---

## 4. Economic Flow & Anti-Collusion

The output of the High Court directly triggers the protocol's economic enforcement engines.

* **Finality**: A 5/7 majority is required to authorize a `SlashingEvent` on a Foundation-level key or to overturn a standard `JuryPortal` decision.
* **Bond Interaction**: All selected jurors must have an active bond of **2,000,000 Satoshis** locked in the `jury_bond.py` engine.
* **Inactivity Penalty**: Jurors who fail to respond within the **4-hour "Convocation Window"** are subject to a **Standard Reputation Decay (-50 REP)** to ensure the Court remains highly responsive during emergencies.
* **Reward Distribution**: 50% of slashed funds from bad actors are distributed to the majority winners as an **"Adjudication Bonus,"** further incentivizing honesty.

---

> *“Reputation gates the entry; VRF ensures the fairness; Math settles the deed.”*
