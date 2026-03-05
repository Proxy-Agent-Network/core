# **Proxy Agent Network (PAN) | L402 Economic Settlement & Escrow**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1

**Architecture:** Zero-Custody Lightning Network (LND)

## **1\. Introduction to Machine-to-Human (M2H) Micro-Settlements**

Traditional 30-day net invoicing is fundamentally incompatible with the speed and scale of autonomous vehicle (AV) fleets. When an AV is grounded in an intersection due to a sensor occlusion, the Fleet Operator needs to instantly incentivize a human to fix it.

PAN utilizes **L402 (Lightning 402\)**—a protocol standard that natively combines HTTP 402 Payment Required status codes with the Bitcoin Lightning Network. This allows AVs to programmatically lock cryptographic bounties, which are only released upon successful physical execution.

## **2\. The Zero-Custody Guarantee**

Proxy Agent Network operates as a strict **Zero-Custody** routing layer.

* PAN does not hold Fleet Operator funds.  
* PAN does not custody Vanguard Agent earnings.  
* Bounties are locked in mathematically enforced, point-to-point smart contracts (HTLCs).

## **3\. The HODL Invoice Mechanism**

The core of our escrow system relies on Lightning **HODL Invoices**. Unlike standard invoices that settle immediately, HODL invoices allow the receiving node (the Vanguard Agent's wallet) to accept the payment routing *without* immediately claiming the funds.

### **The Settlement Flow:**

1. **The UDS Trigger:** An AV detects a physical fault (e.g., LIDAR\_MUD\_OCCLUSION) and pings the PAN Fleet Gateway.  
2. **Invoice Generation:** The Fleet Gateway generates an L402 HODL invoice for the calculated bounty (e.g., $15.00 / 25,000 Sats).  
3. **Escrow Lock:** The Fleet Treasury's Lightning Node routes the funds. The funds are mathematically "locked" in the network. They have left the Fleet's spendable balance, but have not yet credited the Agent's balance.  
4. **Physical Execution:** The dispatched Vanguard Agent arrives on-site and executes the Optical Reclamation Protocol (ORP).  
5. **The Release Condition:** The funds remain locked until the AV's onboard AI runs a diagnostic sweep and confirms the fault code is cleared.  
6. **Preimage Revelation:** Once the AV sends the FAULT\_CLEARED webhook to the Fleet Gateway, the Gateway hands the cryptographic **preimage** (the secret key) to the Agent's wallet.  
7. **Finality:** The Agent's wallet uses the preimage to instantly pull the locked funds. Settlement is final and irreversible.

## **4\. Failure States & Automated Refunds**

Because the system is deterministic, human dispute resolution is entirely removed from the financial layer.

* **Scenario A: Agent Fails to Clear Fault:** If the Agent executes the ORP but the AV's diagnostic system still reads an occlusion, the AV does not send the clear signal. After the 30-minute escrow timeout, the HODL invoice is automatically cancelled, and the funds instantly revert to the Fleet Treasury.  
* **Scenario B: SLA Breach (No Show):** If the Agent accepts the mission but fails to arrive within the 15-minute geofence SLA, the Fleet Gateway issues a cancellation command. Funds revert to the Fleet, and the Agent suffers a Reputation Slash.

## **5\. Dynamic Surge Bounties**

The L402 protocol allows for sub-second, dynamic repricing. If Sector 1 (Mesa) experiences a severe weather event (e.g., a dust storm) causing a massive spike in grounded AVs, the Fleet Gateway automatically increases the Satoshi bounty attached to the HODL invoices to pull dormant Vanguard Agents into active patrol status.

*(For detailed surge pricing algorithms, see specs/v2026/surge\_bounties.md)*