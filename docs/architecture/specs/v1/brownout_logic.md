# **Proxy Agent Network (PAN) | Sector Brownout & Congestion Control**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) & Routing Engine

## **1\. The Physical Constraint (Traffic Shedding)**

In a purely digital API environment, congestion is solved by spinning up more servers. In the Proxy Agent Network (PAN), Vanguard Agents cannot teleport. If a localized physical anomaly (e.g., a severe "Haboob" dust storm, a major kinetic collision blocking an intersection, or targeted vandalism) grounds 50 Autonomous Vehicles (AVs) in a single square mile, the local Vanguard Agent supply will be instantly exhausted.

To maintain the integrity of our **15-Minute SLA** and prevent Vanguard Agents from driving blindly into a compromised or hostile physical zone, PAN implements the **Automated Geohash Brownout Protocol**.

Instead of shedding *Agents*, PAN sheds *AV Dispatch Requests*, forcing Fleet Operators to route their unaffected vehicles *around* the compromised physical zone.

## **2\. Stages of Sector Congestion**

The PAN Routing Engine calculates the **Agent Utilization Ratio (AUR)** and **UDS Fault Velocity** on a rolling 30-second window per Level-6 Geohash.

| Stage | Trigger Conditions | Surge Multiplier | Protocol Impact |
| :---- | :---- | :---- | :---- |
| 🟢 **Nominal** | AUR \< 75% | 1.0x \- 1.5x | Standard operations. All VTS Tiers eligible. |
| 🟡 **Elevated** | AUR 76% \- 85% | 1.6x \- 2.9x | Standard tasks routed normally. Secondary queues active. |
| 🟠 **Critical** | AUR 86% \- 94% *(\>10 UDS/min)* | 3.0x \- 5.0x | **VTS Triage:** Only Elite Agents (VTS 85+) receive dispatches to ensure rapid clearance. Fleet Operators hitting quota caps are queued. |
| 🔴 **Brownout** | AUR \> 95% *(\>15 UDS/min)* | Capped (5.0x) | **Geohash Sealed.** No new UDS dispatch requests accepted for this specific 1-sq-mile zone. |

## **3\. Fleet Operator Experience (The Brownout Response)**

When a specific Geohash enters Stage 🔴 **Brownout**, the PAN Fleet Gateway actively protects the physical safety of Vanguard Agents and the operational efficiency of Fleet Partners.

* **API Rejection:** Any new POST /fleet/dispatch webhook originating from coordinates within the Brownout Geohash will be immediately rejected.  
* **The 503 Payload:** The Fleet backend receives a 503 Service Unavailable with the specific error code GEOHASH\_BROWNOUT\_ACTIVE.  
* **Fleet Action Required:** The Fleet Operator's internal routing engine must ingest this 503 and immediately redirect all other active, healthy autonomous vehicles *away* from this intersection/zone to prevent a massive cascading gridlock event.

\[\!TIP\]

**SLA Protection:** By rejecting the dispatch, PAN ensures your Fleet is not charged a 5.0x L402 Surge Bounty for an Agent that mathematically cannot arrive within the 15-minute window due to physical traffic saturation.

## **4\. Vanguard Agent Experience (Triage Mode)**

During 🟠 **Critical** and 🔴 **Brownout** stages, the physical environment is assumed to be highly degraded or hazardous.

* **Elite Triage:** To ensure the fastest possible clearance of the grounded AVs and restore municipal traffic flow, the PAN Tactical App temporarily filters out Probationary and Standard Agents from the affected Geohash. Only **Elite-Tier Vanguard Agents (VTS 85-100)** are permitted to accept L402 contracts in the hot zone.  
* **Tactical Warning:** The Agent's Augmented Reality HUD will display a HAZARD WARNING, alerting them to the anomalous density of stranded vehicles and instructing them to strictly adhere to the Abort Protocol if the scene is unsafe.

## **5\. Automated Recovery**

Unlike legacy systems that rely on 10-minute block times, the PAN Geohash Brownout is highly elastic.

The Sector Routing Engine recalculates the UDS Fault Velocity and AUR every **30 seconds**. The exact moment the local Vanguard Agents clear enough UDS faults to drop the AUR below 85%, the Brownout is automatically lifted. Fleet Operators will immediately begin receiving 201 Created responses for that Geohash, and the L402 Surge Multiplier will begin to cool down.