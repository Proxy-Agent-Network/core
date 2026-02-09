# Proxy Protocol: The Physical Runtime for AI

**Proxy Protocol** provides a standardized API for autonomous agents to execute physical-world tasks that require legal personhood, identity verification, or biometric authentication.

## Overview

When an autonomous agent encounters a "Legal Wall" (e.g., a captcha, a phone verification, a notarized form, or a physical purchase), it calls the Proxy API. A verified human operator ("Proxy") receives the context, executes the task, and returns the signed result to the agent.

## Integration (Draft v1)

### 1. Request a Proxy Action
Initiate a request for human intervention.

```json
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
