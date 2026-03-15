# **Proxy Agent Network (PAN) | Vanguard Trust Score & Slashing**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0 (Supersedes v1 REP Score & Jury Tribunal)

**Target:** Vanguard Agents & Sector Routing Engine

## **1\. The Deterministic Trust Model**

Legacy decentralized networks relied on subjective human consensus (e.g., "Jury Tribunals" or "Double-Verification") to determine if a task was completed correctly.

In the Proxy Agent Network (PAN), human subjectivity is entirely removed. The **Autonomous Vehicle (AV)** is the ultimate, deterministic arbiter.

* If the Vanguard Agent clears the sensor, the AV's internal diagnostic sweep registers a success, broadcasts the FAULT\_CLEARED webhook, and the L402 bounty is released.  
* If the sensor is not cleared, the AV remains silent, the L402 HODL invoice times out, and the Agent is automatically slashed.

There are no human juries. Machine logic is final.

## **2\. The Vanguard Trust Score (VTS)**

A Vanguard Agent's standing is tracked via their **Vanguard Trust Score (VTS)**, scaling from 0 to 100\.

* **Starting Balance:** All Agents begin the Mesa Pilot at VTS: 100\.  
* **Routing Priority:** VTS acts as the primary weighting metric in the Sector Dispatch algorithm.

| Score Range | Tier Status | Network Privileges & Restrictions |
| :---- | :---- | :---- |
| **85 \- 100** | **Elite** | First Right of Refusal. Access to 3.0x+ L402 Surge Bounties. |
| **50 \- 84** | **Standard** | Standard routing pool. Excluded from peak surge multiplier caps. |
| **25 \- 49** | **Probationary** | Reduced dispatch frequency. Mandatory ORP (Optical Reclamation Protocol) retraining required. |
| **0 \- 24** | **Revoked** | Permanent network demotion and cryptographic blacklisting. |

## **3\. Slashing Conditions (Penalties)**

"Slashing" automatically deducts points from the Agent's VTS for failing to meet strict physical Service Level Agreements (SLAs) or violating Standard Operating Procedures (SOPs).

### **Minor Infractions (Recoverable)**

| Infraction | VTS Penalty | Trigger Condition |
| :---- | :---- | :---- |
| SLA\_BREACH | \-15 Pts | Agent accepts a contract but fails to register a UWB proximity lock within the 15-minute SLA timer. |
| ORP\_FAILURE | \-10 Pts | Agent signals ORP completion, but the AV's diagnostic system fails to clear the UDS fault code. |
| ABANDONED\_CONTRACT | \-20 Pts | Agent accepts a mission but manually cancels via the Tactical App before arrival. |

### **Critical Infractions (Zero-Tolerance)**

| Infraction | Penalty | Trigger Condition |
| :---- | :---- | :---- |
| UWB\_SPOOFING | Permanent Ban | Attempting to spoof the Ultra-Wideband proximity handshake without physical presence. |
| CABIN\_BREACH | Permanent Ban | Utilizing physical force to open an AV door without explicit CABIN\_EMERGENCY authorization. |
| HARDWARE\_DAMAGE | Permanent Ban | Fleet Operator flags severe physical damage to the sensor array caused by unauthorized tools (violating the HP Potion SOP). Triggers E\&O Liability dispute. |

## **4\. Financial Slashing & L402 Forfeiture**

PAN **rejects** the legacy requirement of forcing human workers to purchase and lock up Bitcoin collateral (staking).

Financial slashing is executed via the **L402 HODL Invoice Timeout**, not by burning staked funds.

* If an Agent suffers an SLA\_BREACH or ORP\_FAILURE, the PAN Gateway simply cancels the L402 HTLC (Hashed Timelock Contract).  
* The Satoshi bounty is never released to the Agent and instantly reverts to the Fleet Operator's Treasury.  
* The Agent incurs the physical costs of deployment (fuel, time) with zero compensation.

## **5\. Reputation Rehabilitation**

Because minor infractions (like an SLA\_BREACH) can occasionally occur due to extreme, unforeseeable traffic conditions in Maricopa County, the VTS system allows for rehabilitation.

* **The Recovery Metric:** An Agent regains **\+1 VTS point** for every **3 consecutive, flawless ORP executions** (arriving under 12 minutes, clearing the UDS code on the first attempt).  
* A penalized Agent must rebuild their score to regain Elite status and access to High-Surge bounties.