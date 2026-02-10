# Proxy Protocol: The Physical Runtime for AI

Proxy Protocol provides a standardized API for autonomous agents to execute physical-world tasks that require legal personhood, identity verification, or biometric authentication.

---

## Overview
When an autonomous agent encounters a **"Legal Wall"** (e.g., a CAPTCHA, phone verification, notarized form, or physical purchase), it calls the Proxy API. A verified human operator (**"Proxy"**) receives the context, executes the task, and returns the signed result to the agent.

---

## Key Features
* 🛡️ **Hardware Root of Trust:** All Tier 2+ Human Nodes sign proofs using a non-exportable private key sealed inside an **Infineon OPTIGA™ TPM 2.0**.
* 🎟️ **Proxy-Pass Subscriptions:** High-volume agents can lock a 30-day DLC (Discreet Log Contract) to waive protocol fees and gain priority routing.
* ⚖️ **Decentralized Justice:** Disputes are resolved by a VRF-selected **Jury Tribunal**, incentivized by Schelling Point game theory.
* 🏥 **Node Insurance:** A 0.1% protocol tax funds a treasury to compensate operators in the event of critical bugs or slashing errors.

---

## Supported SDKs
We provide official client libraries for the following ecosystems:

| Language | Package | Repository |
| :--- | :--- | :--- |
| **Python** | `pip install proxy-agent` | [core/sdk](https://github.com/Proxy-Agent-Network/core) |
| **Node.js** | `npm install @proxy-protocol/node` | [sdk-node](https://github.com/Proxy-Agent-Network/sdk-node) |

---

## Integration (REST API)

### 1. Request a Proxy Action
Initiate a request for human intervention.

```http
POST [https://api.proxy-protocol.com/v1/request](https://api.proxy-protocol.com/v1/request)
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json

{
  "agent_id": "agent_x892_beta",
  "task_type": "PHONE_VERIFICATION",
  "context": {
    "service": "Google Voice",
    "required_action": "Receive SMS code",
    "timeout": 300
  },
  "bid_amount": 15.00
}
```

### 2. Response Object
The system returns a unique `ticket_id` to poll for completion.

```json
{
  "status": "queued",
  "ticket_id": "tkt_8829_mnb2",
  "estimated_wait": "45s"
}
```

---

## Security & Ethics
* **Zero-Knowledge Context:** Proxies only see the specific task data, not the agent's core logic.
* **Legal Compliance:** All tasks are filtered against a constrained list of permissible legal actions. See [COMPLIANCE.md](./legal/compliance.md) for details.

---

## Status
🚧 **Private Beta.**
We are currently onboarding select agent developers. [Request Access Here](https://sites.google.com/rob-o-la.com/proxy/home).

---

## Join the Core Team
We are building the bridge between digital intelligence and physical reality. We are looking for mission-driven engineers to define the standard for 2030.

**Open Roles (Remote / Async):**
* **Rust Protocol Engineer:** Help migrate our settlement layer from Python to Rust for high-frequency Lightning interactions.
* **Legal Engineering Lead:** Work with our Delaware counsel to productize new "Power of Attorney" templates for autonomous entities.
* **Developer Relations:** Build the "Hello World" tutorials that 10,000 AI developers will use.

*To apply, cryptographically sign a message with your GitHub handle and email `careers@rob-o-la.com`.*
