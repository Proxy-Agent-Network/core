# **Proxy Agent Network (PAN) | L402 Escrow Mechanics & Liquidity Logic**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Mechanism:** Hashed Timelock Contracts (HTLCs) via Lightning Network HODL Invoices.

**Target:** Fleet Treasury & Operations

Unlike traditional gig-economy escrow—where a centralized corporation custodies the money—PAN utilizes **Zero-Custody Cryptographic Escrow**. The Satoshi bounty is locked on the Lightning Network itself and can only be routed if a mathematical secret (the **Preimage**) is revealed by the Autonomous Vehicle (AV) clearing its physical fault.

## **1\. The M2H State Machine**

Every Machine-to-Human (M2H) intervention progresses through a strict, zero-trust state machine managed by the PAN Gateway.

| State | Description | Trigger |
| :---- | :---- | :---- |
| INVOICE\_GENERATED | Fleet requests dispatch. PAN generates a HODL invoice with a 32-byte secret. | POST /fleet/dispatch |
| HTLC\_LOCKED | Fleet Treasury node pays the invoice. Funds are mathematically held by routing nodes. | Lightning Payment Detected |
| AGENT\_DISPATCHED | Vanguard Agent taps ACCEPT. | TPM-Signed Acceptance |
| PREIMAGE\_REVEALED | AV verifies the sensor is clean. The secret is revealed, instantly pulling funds to the Agent. | AV FAULT\_CLEARED Webhook |
| ESCROW\_CANCELLED | Agent breaches SLA, or the AV fails to clear the fault within the network timeout. | 15-Min SLA / 30-Min Timeout |

## **2\. HODL Invoice Logic (The Lock & Release)**

1. **The Lock:** When a stranded AV generates a Unified Diagnostic Service (UDS) fault code, the PAN Gateway generates a random secret (the preimage) and its corresponding SHA-256 hash. The Fleet Operator pays an invoice locked to this specific hash.  
2. **The Hold:** The Lightning Network holds the transaction in a "pending" state. The Satoshis have left the Fleet Operator's spendable balance but have **not** reached the Vanguard Agent. PAN does not custody these funds; they are held by the network cryptography.  
3. **The Release:**  
   * The Vanguard Agent arrives and executes the Optical Reclamation Protocol (ORP).  
   * The AV's onboard diagnostic system runs a sweep. If the sensor reads clear, the Fleet backend fires the FAULT\_CLEARED webhook.  
   * PAN injects the **Preimage** into the Lightning Network.  
   * This mathematical key unlocks the HTLC, settling the funds into the Vanguard Agent's mobile wallet in milliseconds.

## **3\. Safety Buffers & Timeouts**

To protect both the Fleet Operator's liquidity and the Vanguard Agent's fiat-denominated earnings, PAN enforces strict buffers:

* **The Volatility Buffer (TWAP):** Because Vanguard Agents measure their fuel and time in fiat (USD), the PAN Gateway syncs a Time-Weighted Average Price (TWAP) oracle every 60 seconds. A **2% Satoshi buffer** is added to the HTLC lock amount. If the price of Bitcoin drops during the 15-minute drive time, the buffer ensures the Agent still receives the exact USD equivalent promised at dispatch. Any unused buffer instantly reverts to the Fleet Operator.  
* **The Hard Timeout (30 Minutes):** Traditional escrows can lock funds indefinitely. In PAN, an absolute network limit of **30 minutes** is enforced. If the Vanguard Agent fails to clear the fault, or if the AV suffers a catastrophic failure and cannot send the clear signal, the HTLC expires. The funds mathematically revert to the Fleet Treasury, preventing liquidity from being trapped.

\[\!NOTE\]

**Liability Shielding:** By tying financial settlement directly to the AV's UDS diagnostic sweep, PAN removes all human subjectivity from the billing process. If the machine pays, the machine has legally asserted the hardware is clean and undamaged.