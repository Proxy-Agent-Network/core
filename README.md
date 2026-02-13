# Proxy Protocol: The Physical Runtime for AI

Proxy Protocol provides a standardized API for autonomous agents to execute physical-world tasks that require legal personhood, identity verification, or biometric authentication. We bridge silicon intent with biological agency through a global network of hardware-attested human nodes.

---

## Overview
When an autonomous agent encounters a **"Legal Wall"** (e.g., a CAPTCHA, phone verification, notarized form, or physical purchase), it calls the Proxy API. A verified human operator (**"Proxy"**) receives the context, executes the task, and returns the signed result to the agent.

---

## Key Features
* 🛡️ **Hardware Root of Trust:** All Tier 2+ Human nodes must sign proofs using non-exportable private keys sealed inside an **Infineon OPTIGA™ TPM 2.0**.
* ⚡ **Trustless Settlement:** Payments use Lightning HODL Invoices. Funds are released only upon cryptographic validation of hardware telemetry (PIP-017).
* ⚖️ **Decentralized Justice:** Disputes are resolved by a VRF-selected Jury Tribunal, selected via Bitcoin block entropy and incentivized by Schelling Point game theory.
* 🎟️ **Proxy-Pass Subscriptions:** High-volume agents can lock a 30-day DLC (Discreet Log Contract) to waive protocol fees and gain priority routing.
* 🏥 **Node Insurance:** A 0.1% protocol tax funds a treasury to compensate operators for verified system errors or critical bugs.

---

## Infrastructure Visualizers
The core protocol includes real-time dashboards for monitoring network health:
* **Escrow Circuit:** Monitor HODL invoice settlement and HTLC logic.
* **Quorum Audit:** Observe 7-signature multi-sig ceremony finalization.
* **Forensic Delta:** Audit cryptographic manifest mismatches between nodes.
* **Legal Nexus:** Explore hardware-attested jurisdictional precedents.

---

## Supported SDKs
Official client libraries for the Proxy Network:

| Language | Package | Repository |
| :--- | :--- | :--- |
| **Python** | `pip install proxy-agent` | [core/sdk](https://github.com/Proxy-Agent-Network/core) |
| **Node.js** | `npm install @proxy-protocol/node` | [sdk-node](https://github.com/Proxy-Agent-Network/sdk-node) |

---

## Integration (REST API v1.6)

### 1. Request a Proxy Action
```json
POST [https://api.proxyagent.network/v1/request](https://api.proxyagent.network/v1/request)
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
* **Zero-Knowledge Context:** Proxies only see specific task data, not the agent's core logic.
* **Legal Compliance:** All tasks are filtered against a constrained list of permissible actions. See [COMPLIANCE.md](./COMPLIANCE.md).

---

## Status
🚧 **Private Beta.** Currently onboarding select agent developers. [Request Access Here](https://www.proxyagent.network/).
