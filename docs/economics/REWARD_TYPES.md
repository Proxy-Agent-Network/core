# **Proxy Agent Network (PAN) | L402 SLA Bonuses & Hazard Pay**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Mechanism:** Lightning Network Keysend (Spontaneous Payments)

**Target:** Fleet Treasury & Operations

While the primary L402 HODL invoice handles the base physical recovery fee and active network surge pricing, the Proxy Agent Network (PAN) supports a deterministic **Bonus Layer**.

In the Machine-to-Human (M2H) model, Vanguard Agents do not receive subjective "tips" based on customer service. Instead, Fleet Operators can programmatically attach automated bonuses to incentivize ultra-fast clearance times or compensate for hazardous physical environments.

## **1\. The Bonus Taxonomy**

Fleet Operators can define an optional bonus\_matrix in their initial /fleet/dispatch payload to automate these incentives.

| Bonus ID | Trigger Condition | Calculation Model | Typical Range |
| :---- | :---- | :---- | :---- |
| BNS\_RAPID\_SLA | Agent clears the UDS fault in under 8 minutes (cutting the 15-minute SLA in half). | Fixed Sats or % of Base. | 5,000 \- 15,000 Sats |
| BNS\_HAZARD | AV telemetry indicates the vehicle is stranded in a high-speed live lane or active dust storm (Haboob). | Fixed Hazard Premium. | 25,000 Sats |
| BNS\_TOW\_WAIT | Hardware is permanently damaged. Agent secures the scene until the Fleet Tow arrives. | Per-Minute Rate. | 1,000 Sats / Minute |

## **2\. The Rapid SLA Math**

To minimize Fleet downtime, operators can incentivize Vanguard Agents to bypass standard routing speeds (safely) to prioritize their specific vehicle.

### **The Formula**

If a Fleet flags bns\_rapid\_sla\_active=true and the PAN Gateway verifies the timestamp delta between AGENT\_DISPATCHED and the UDS\_CLEARED webhook is less than 480 seconds (8 minutes):

Total\_Payout \= (Base\_Fee \* Surge\_Multiplier) \+ BNS\_RAPID\_SLA

### **Example Scenario**

* **The Fault:** LIDAR\_MUD\_OCCLUSION blocking a major intersection.  
* **The Base:** 25,000 Sats.  
* **The Incentive:** Fleet attaches a 10,000 Sat BNS\_RAPID\_SLA for clearance under 8 minutes.  
* **The Reality:** The Vanguard Agent arrives and clears the dome in 6 minutes, 45 seconds.  
* **The Payout:** The HODL invoice settles the 25,000 Sats. The Fleet backend automatically verifies the timestamp and transmits the 10,000 Sat bonus.

## **3\. Settlement Mechanics (LND Keysend)**

Because standard L402 HODL Invoices lock a mathematically exact amount of Satoshis at the moment of dispatch, conditional post-execution bonuses cannot be cleanly added to the initial escrow without trapping excess Fleet liquidity.

Therefore, conditional bonuses are settled **optimistically after the fact**:

1. **Verification:** The Fleet Operator's backend receives the FAULT\_CLEARED webhook from the AV.  
2. **Evaluation:** The Fleet's internal logic calculates if the SLA speed threshold or Hazard conditions were met.  
3. **Transmission:** The Fleet Treasury Node executes a **Keysend** (spontaneous Lightning payment) directly to the Vanguard Agent's registered Lightning PubKey.  
4. **Metadata:** The Keysend includes a custom TLV (Type-Length-Value) record 696969: "BNS\_RAPID\_SLA" to notify the Agent's Tactical HUD of the specific reason for the instant bonus payout.

## **4\. Budgeting Safety & Cost Controls**

To prevent automated scripts from draining Fleet Treasury liquidity, Fleet Operators must set a hard max\_bonus\_allowance\_sats per mission.

\[\!IMPORTANT\]

**Hard Cap:** By default, the PAN Gateway will reject any programmatic Keysend bonus calculation that exceeds **200% of the Base Fee** to protect the Fleet Operator from runaway algorithmic spending loops.