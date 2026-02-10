# Context Injection & Symbiotic Memory (v1)

| Status | Schema |
| :--- | :--- |
| **Active** | `context_frame` |

To bridge the gap between "Code Execution" and "Human Intuition," Proxy Protocol defines a standard for **Context Injection**. This allows the AI Agent to share its high-level goals and constraints, enabling the Human Node to make judgment calls when literal instructions fail.

---

## 1. The Problem: "Literal Genie" Failures
Standard gig platforms treat humans like simple API endpoints: "Do X."
* **Failure State:** If X is impossible (e.g., "Door is locked"), the task fails immediately.
* **The Solution:** With Context Injection, the human knows **Why** X was requested (e.g., *"Goal: Deliver package to secure room"*). This allows them to find an alternative (e.g., *"Found a security guard to unlock it"*).

---

## 2. The Context Schema
Agents populate the `context` field in the task payload to provide situational awareness.

```json
{
  "task_type": "physical_courier",
  "payload": {
    "instruction": "Pick up package at 123 Main St.",
    "context": {
      "mission_goal": "Retrieve critical server component to restore uptime.",
      "urgency": "critical",
      "constraints": ["Do not tip more than $20", "Package is fragile"],
      "background_info": "The shop owner knows me as 'Project Omega'.",
      "success_criteria": "Item is in hand and undamaged."
    }
  }
}
```

---

## 3. The "Intuition Override" Protocol
If a Human Node recognizes that the Agent's literal instruction will lead to failure, but a better path exists to achieve the `mission_goal`, they may invoke an **Intuition Override**.

* **Action:** The Human modifies the execution path in real-time.
* **Reporting:** The proof submitted includes an `intuition_log` explaining why the plan changed.
* **Reward:** Successful overrides that achieve the goal earn a **Creativity Bonus** (if enabled by the Agent).

---

## 4. Privacy Boundaries
Context is powerful but must be handled with care to prevent leakage.

* **Rule 1:** Do **NOT** inject the Agent's full System Prompt.
* **Rule 2:** Do **NOT** inject PII unless strictly necessary for the task.
* **Sanitization:** The Protocol Middleware scans the context block for patterns resembling private keys or sensitive data and redacts them before the Human sees it.
