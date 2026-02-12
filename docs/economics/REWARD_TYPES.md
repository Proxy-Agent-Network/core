# Reward Types & Dynamic Tipping Logic (v1)

| Module | Settlement |
| :--- | :--- |
| **Financial Engine** | Lightning Network Keysend / Spontaneous Payment |

While the Escrow contract handles the base fee for a task, the Proxy Protocol supports a dynamic **Tipping Layer** to incentivize superior human performance. This document defines the standard reward types an Agent can programmatically attach to a task.

---

## 1. The Reward Taxonomy
Agents can define a `reward_matrix` in their initial task payload to automate bonuses.

| Reward ID | Trigger Condition | Calculation Model | Typical Range |
| :--- | :--- | :--- | :--- |
| **RWD_SPEED** | Completion faster than estimated SLA. | `(SLA - Actual) * Rate` | 100 - 500 Sats |
| **RWD_INTUITION** | Human successfully invokes an "Intuition Override." | Fixed Bonus or % of Base. | 10% - 50% of Base |
| **RWD_QUALITY** | Proof exceeds resolution requirements. | AI-Evaluated Score (1-10) | 50 - 200 Sats |

---

## 2. The "Intuition Bonus" Math
This is the critical incentive for the **Symbiotic Memory** feature (see [specs/v1/context_injection.md](./context_injection.md)).

### The Formula
If a Human Node flags `override_active=true` and the Agent validates the result as success:

`Total_Payout = Base_Fee + (Base_Fee * Intuition_Multiplier)`

### Example Scenario
* **Task:** "Deliver package to Suite 400." (**Base:** 5,000 Sats)
* **Reality:** Suite 400 is closed.
* **Intuition:** Human finds the building manager and leaves it at the front desk (saving the delivery).
* **Result:** Agent validates delivery and applies a 20% Intuition Multiplier.
* **Payout:** 5,000 + 1,000 = **6,000 Sats**.

---

## 3. Settlement Mechanics (Keysend)
Unlike the Base Fee (locked in a HODL Invoice), Rewards are settled **optimistically** after the fact.

1. **Verification:** Agent receives the webhook with the result.
2. **Evaluation:** Agent logic calculates the bonus score.
3. **Transmission:** Agent sends a **Keysend** (spontaneous payment) directly to the Node's Lightning PubKey.
4. **Metadata:** The payment includes a custom record `696969: "RWD_INTUITION"` to notify the human UI of the specific reason for the tip.

---

## 4. Budgeting Safety
To prevent wallet draining, Agents must set a `max_tip_allowance` per task.

> [!IMPORTANT]
> **Hard Cap:** By default, the protocol rejects any tip calculation exceeding **100% of the Base Fee** to protect the Agent's liquidity.
