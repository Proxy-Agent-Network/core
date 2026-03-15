# **Proxy Agent Network (PAN) | Vanguard Reputation & Slashing**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.1

**Target:** Vanguard Agents & Network Economics

## **1\. The Deterministic Trust Model**

Traditional gig-economy platforms (e.g., Uber, DoorDash) rely on subjective 5-star user reviews to govern their workforce. The Proxy Agent Network (PAN) cannot rely on subjectivity. An Autonomous Vehicle (AV) cannot leave a "review" after a physical intervention.

Therefore, PAN utilizes a **Deterministic Trust Model**. A Vanguard Agent's standing is entirely dictated by mathematical SLAs, cryptographic hardware attestations, and the AV's internal diagnostic state. There are no human dispute resolutions.

## **2\. The Vanguard Trust Score (VTS)**

Every Vanguard Agent is assigned a Vanguard Trust Score (VTS), ranging from 0 to 100\.

* All Agents begin the Mesa Pilot at VTS: 100\.  
* The VTS acts as a routing weight in the Sector Dispatch algorithm.  
* Agents with a higher VTS receive priority for high-value L402 Surge Bounties.

### **VTS Tiers**

* **Elite (85 \- 100):** Eligible for Tier-1 Fleet dispatches (e.g., Waymo, Zoox) and Priority Surge Bounties. This allows for one minor infraction (like an SLA\_BREACH or ORP\_FAILURE) due to uncontrollable factors like traffic before dropping tiers.  
* **Standard (50 \- 84):** Eligible for standard dispatches. Excluded from 3.0x+ Surge limits.  
* **Probationary (25 \- 49):** Reduced dispatch frequency. Mandatory ORP (Optical Reclamation Protocol) retraining required.  
* **Revoked (\< 25):** Permanent network demotion and cryptographic blacklisting.

## **3\. Slashing Conditions**

"Slashing" is the automated protocol mechanism for penalizing Vanguard Agents who fail to meet strict network parameters. Slashing instantly deducts points from the Agent's VTS.

### **Minor Infractions (Recoverable)**

| Infraction | VTS Penalty | Trigger Condition |
| :---- | :---- | :---- |
| SLA\_BREACH | \-15 Pts | Agent accepts an L402 contract but fails to register a UWB proximity lock within the 15-minute SLA timer. |
| ORP\_FAILURE | \-10 Pts | Agent signals ORP completion, but the AV's diagnostic system fails to clear the UDS fault code after 3 attempts. |
| ABANDONED\_CONTRACT | \-20 Pts | Agent accepts a mission but manually cancels via the PAN Tactical App before arrival. |

### **Critical Infractions (Immediate Revocation \- "Zero Tolerance")**

| Infraction | Penalty | Trigger Condition |
| :---- | :---- | :---- |
| UWB\_SPOOFING | Permanent Ban | Attempting to mathematically spoof the Ultra-Wideband proximity handshake without physical presence. |
| CABIN\_BREACH | Permanent Ban | Utilizing physical force to open an AV door or interacting with passengers without explicit CABIN\_EMERGENCY authorization. |
| HARDWARE\_DAMAGE | Permanent Ban | Fleet Operator flags severe physical damage to the sensor array caused by unauthorized tools (violating the HP Potion SOP). |

## **4\. Financial Slashing (L402 Forfeiture)**

Unlike proof-of-stake blockchains, Vanguard Agents do not front their own capital to operate on the network. Therefore, financial slashing does not steal an Agent's past earnings.

Instead, financial slashing is executed via the **HODL Invoice Timeout**.

If an Agent suffers an SLA\_BREACH or ORP\_FAILURE, the PAN Gateway simply cancels the L402 HTLC (Hashed Timelock Contract). The Satoshi bounty is never released to the Agent and instantly reverts to the Fleet Operator's Treasury.

The Agent incurs the physical costs of deployment (fuel, time) with zero compensation.

## **5\. Reputation Rehabilitation**

Because minor infractions like SLA\_BREACH can occasionally occur due to extreme, unforeseeable circumstances (e.g., severe traffic collisions blocking all routes), the VTS allows for rehabilitation.

* **The Recovery Metric:** An Agent regains **\+1 VTS point** for every **3 consecutive, flawless ORP executions** (arriving under 12 minutes, clearing the UDS code on the first attempt).  
* A penalized Agent must "grind" their way back to Tier-1 status through flawless execution on lower-priority tasks.

## **6\. SB 1417 & Legal Accountability**

Under Arizona SB 1417, Vanguard Agents operate as certified third-party auditors of autonomous vehicle sensors.

In the event of a Critical Infraction (such as HARDWARE\_DAMAGE), PAN reserves the right to revoke the Agent's liability shield under our $5M HNOA/E\&O policy. The cryptographic audit logs (including TPM signatures and UWB proximity timestamps) will be turned over to the Fleet Operator for civil recourse.