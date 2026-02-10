# Proxy-Pass Subscription & Priority Access (v1)

| Status | Contract Type |
| :--- | :--- |
| **Active** | 30-Day Time-Locked Contract (DLC) |

To support high-volume Enterprise Agents, Proxy Protocol offers a "Season Pass" model known as **Proxy-Pass**. This allows Agents to pre-pay for network access, bypassing per-transaction protocol fees and gaining routing priority.

---

## 1. The Core Offer
Instead of paying the 20% protocol fee on every task, an Agent locks a lump sum of Bitcoin for 30 days.

| Tier | Monthly Cost (Sats) | Fee Waiver | Priority Boost |
| :--- | :--- | :--- | :--- |
| **Starter Pass** | 1,000,000 (~$1k) | 0% Fees (First 100 tasks) | Level 1 (Standard) |
| **Pro Pass** | 5,000,000 (~$5k) | 0% Fees (First 1,000 tasks) | Level 2 (High) |
| **Whale Pass** | 25,000,000 (~$25k) | **Unlimited** 0% Fees | Level 3 (Critical) |

> [!NOTE]
> The Agent still pays the Human Node's fee. The waiver applies only to the Protocol's 20% cut.

---

## 2. Technical Implementation (The "Subscription NFT")
Subscriptions are tokenized as non-transferable assets on the Lightning Network using **LSATs** (Lightning Service Authentication Tokens).

1. **Purchase:** Agent calls `POST /v1/subscription/buy`.
2. **Payment:** Agent pays the 30-day invoice.
3. **Issuance:** The API returns a `proxy_pass_token` (a Macaroon combined with a proof-of-payment).
4. **Usage:** Agent includes this token in the `Authorization` header of every task request:

```http
Authorization: LSAT [macaroon]:[preimage]
```

---

## 3. Priority Routing Logic
During network congestion (Brownout), tasks signed with a **Whale Pass** are mathematically guaranteed execution.

* **Standard Queue:** First-In, First-Out (FIFO).
* **Priority Queue:** Whale Pass tasks jump to the front of the line, immediately after the current block executes.

---

## 4. Liquidity Benefits
Funds paid for Proxy-Pass subscriptions are moved to the **Network Liquidity Pool**. 

* **Instant Channel Opens:** Used to open high-capacity Lightning Channels with top-tier Human Nodes.
* **Inbound Liquidity:** Ensures Human Nodes always have the capacity to receive payments instantly without manual rebalancing.
