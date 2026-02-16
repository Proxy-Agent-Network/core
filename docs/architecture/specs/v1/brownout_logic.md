# Automated Brownout & Congestion Control (v1)

| Status | Module |
| :--- | :--- |
| **Active** | Traffic Shaping |

To maintain **Quality of Service (QoS)** for high-value tasks during periods of network congestion, the Proxy Protocol implements an **Automated Brownout** mechanism.

---

## 1. The Logic (Traffic Shedding)
When the network Mempool exceeds specific utilization thresholds, the protocol automatically "sheds" low-reputation nodes. This ensures that scarce compute and verification resources are reserved for the most reliable actors.

### Congestion Stages

| Stage | Trigger (Pending Tasks) | Min. REP Required | Impact |
| :--- | :--- | :--- | :--- |
| 🟢 **Green** | < 1,000 | 300 (Probation) | Normal operations. |
| 🟡 **Yellow** | 1,000 - 5,000 | 500 (Verified) | Probationary nodes are paused. |
| 🟠 **Orange** | 5,000 - 10,000 | 700 (High Trust) | Only established nodes receive tasks. |
| 🔴 **Red** | > 10,000 | 900 (Elite) | "Whale Mode." Only top 10% active. |

---

## 2. Node Experience
When a Brownout is active, filtered nodes experience the following:

* **Notification:** Low-REP nodes receive a `429 Too Many Requests` or `503 Service Unavailable` with a specific header: `X-Proxy-Brownout: Active`.
* **Dashboard:** The Node Operator app displays: *"Network Busy. Priority given to Elite Nodes. Improving your Reputation Score will grant access during high traffic."*
* **No Penalty:** Being filtered out during a Brownout **does not** count as downtime or impact the Node's SLA score.

---

## 3. Agent Experience (Whale Assurance)
High-paying Agents (those who bid above the average fee) are guaranteed routing to the remaining active nodes.

> [!TIP]
> **Whale Benefit:** During high-traffic events, reliable execution is mathematically guaranteed for those willing to pay the congestion premium.

---

## 4. Recovery
The protocol checks Mempool depth **every block** (approx. 10 minutes). Once pending tasks drop below the threshold, the Brownout level is lowered, and lower-tier nodes automatically reconnect to the network.
