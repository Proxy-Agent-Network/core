# Reputation Score & Consensus Mechanism

**Version:** 1.0  
**Core Logic:** Weighted Proof-of-Accuracy (PoA)

Proxy Protocol uses a dynamic **Reputation Score (REP)** ranging from `0-1000` to determine a Node's eligibility for tasks and their required collateral stake.

---

## 1. The Score Calculation
A Node's REP score is updated after every completed task epoch (24 hours).

**Formula:** `REP = (Successful_Tasks * 1.0) - (Failed_Tasks * 5.0) + (Node_Age_Bonus)`

### Score Tiers

| Score Range | Tier Status | Privileges |
| :--- | :--- | :--- |
| **0 - 300** | Banned | None (Stake Slashed) |
| **301 - 500** | Probation | Requires Double-Verification |
| **501 - 800** | Verified | Standard Tasks |
| **801 - 1000** | Elite | Zero-Collateral access, Priority Queue |

---

## 2. Double-Verification (The "Check-Check" Protocol)
For high-value tasks (>$100) or Probationary Nodes, the network enforces **Redundant Execution**.

### The Flow:
1.  **Agent Request:** "Photograph the document at 123 Main St."
2.  **Dispatch A:** Node A (Probation) accepts the task.
3.  **Dispatch B:** Node B (Elite) accepts the same task as a **silent auditor**.
4.  **Consensus:**
    * Both nodes upload a hash of their photo.
    * If `Hash(A)` is visually similar to `Hash(B)` (via perceptual hashing), both get paid.
    * If they diverge, a **Jury Tribunal** is summoned to decide the malicious actor.

---

## 3. Slashing Conditions
If a Node is found to be lying (e.g., submitting a blank photo or fraudulent data) during a Double-Verification or Jury process:

* **The Penalty:** 50% of their staked BTC is burned immediately.
* **The Reward:** 50% of the slashed funds are transferred to the truthful Node as a **Whistleblower Reward**.

---

## 4. Reputation Decay
Nodes must remain active to maintain their standing. **REP decays by 1 point for every 7 days of inactivity**, incentivizing consistent participation in the physical economy.
