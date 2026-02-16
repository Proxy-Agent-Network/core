# Reputation Score & Consensus Mechanism

**Version:** 1.1  
**Core Logic:** Weighted Proof-of-Accuracy  
**Tier Update:** Codification of Super-Elite (High Court) status.

Proxy Protocol uses a dynamic **Reputation Score (REP)** (0-1000) to determine a Node's eligibility for tasks, their required collateral stake, and their authority within the governance layer.

---

## 1. The Score Calculation

A Node's REP score is updated after every completed task epoch (24 hours).

```text
REP = (Successful_Tasks * 1.0) - (Failed_Tasks * 5.0) + (Node_Age_Bonus)
```

| Score Range | Tier Status | Privileges |
| :--- | :--- | :--- |
| **0 - 300** | Banned | None (Stake Slashed) |
| **301 - 500** | Probation | Requires Double-Verification |
| **501 - 800** | Verified | Standard Tasks |
| **801 - 950** | Elite | Zero-Collateral access, Priority Queue |
| **951 - 1000** | Super-Elite | High Court Adjudication, Appellate Court VRF |

---

## 2. Double-Verification (The "Check-Check" Protocol)

For high-value tasks (>$100) or Probationary Nodes, the network enforces **Redundant Execution**.

### The Flow:
1. **Agent Request:** "Photograph the document at 123 Main St."
2. **Dispatch A:** Node A (Probation) accepts the task.
3. **Dispatch B:** Node B (Elite) accepts the same task (as a silent auditor).
4. **Consensus:**
    * Both nodes upload a hash of their photo.
    * If `Hash(A)` is visually similar to `Hash(B)` (via perceptual hashing), both get paid.
    * If they diverge, a **Jury Tribunal** is summoned to decide who is lying.

---

## 3. Slashing Conditions

If a Node is found to be lying (e.g., submitting a blank photo) during a Double-Verification or Jury process:

* **The Penalty:** 50% of their staked BTC is burned immediately.
* **The Reward:** 50% of the slashed funds go to the truthful Node (whistleblower reward).

---

## 4. The Super-Elite Tier (High Court)

Nodes that maintain a reputation score greater than **950** enter the Super-Elite tier. This tier represents the "Root of Trust" for the human layer of the protocol.

### A. Economic Requirements
* **Mandatory Bond:** To activate Super-Elite privileges, nodes must lock a minimum bond of **2,000,000 Satoshis** into the `jury_bond.py` engine.
* **Skin in the Game:** This bond is subject to a 30% slash if the node votes against the Schelling Point consensus during adjudication.

### B. Adjudication Privileges
* **High Court Selection:** Only Super-Elite nodes are eligible for selection in the 7-person Appellate Court via the `appellate_vrf.py` logic.
* **Adjudication Fees:** Super-Elite nodes earn a share of task fees and "Slash Bonuses" from penalized bad actors for every dispute they correctly adjudicate.

---

## 5. Reputation Decay

Nodes must remain active to maintain their standing.

* REP decays by **1 point** for every 7 days of inactivity.
* If a Super-Elite node falls below 951 REP, their High Court eligibility is suspended until the score is restored.

---

> *“Reputation is the collateral of the biological node.”*
