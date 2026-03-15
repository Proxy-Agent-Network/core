# **Proxy Agent Network (PAN) | Dynamic Surge Bounties & L402 Repricing**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1

**ODD:** Sector 1 (Maricopa County, AZ)

## **1\. The Economics of Physical Edge Cases**

Unlike digital API requests, physical Vanguard Agents cannot teleport, and their supply is strictly bounded by geographical constraints. During nominal operations, a baseline Satoshi bounty (e.g., $15.00 equivalent) is sufficient to maintain our 15-minute Service Level Agreement (SLA).

However, autonomous vehicle (AV) failure rates are highly correlated with localized environmental anomalies. A sudden "Haboob" (dust storm) rolling through Mesa will simultaneously blind the LiDAR arrays of dozens of vehicles in a concentrated area. To maintain the 15-minute SLA during mass-grounding events, the PAN Fleet Gateway utilizes **L402 Dynamic Surge Repricing**.

## **2\. Algorithmic Activation Triggers**

The Sector Routing Engine continuously calculates network density every 5 seconds. Surge pricing is automatically triggered when any of the following thresholds are breached within a Sector Geohash:

1. **Agent Utilization Ratio (AUR):** If the ratio of ACTIVE\_AGENTS currently executing an Optical Reclamation Protocol (ORP) versus AVAILABLE\_AGENTS exceeds 85%.  
2. **UDS Fault Velocity:** If the network ingests more than 10 Unified Diagnostic Service (UDS) occlusion webhooks per minute within a 5-mile radius.  
3. **SLA Degradation Warning:** If the average estimated time of arrival (ETA) for the last 5 dispatched tasks exceeds 12 minutes (approaching the 15-minute critical threshold).

## **3\. The Repricing Algorithm**

When a trigger condition is met, the PAN Gateway dynamically adjusts the base Lightning HODL invoice for incoming AV requests.

* **Base L402 Bounty:** 25,000 Sats (\~$15.00 USD)  
* **Surge Multiplier (![][image1]):** Scales linearly based on the Agent Utilization Ratio, capped at a maximum of 5.0x.  
* **Maximum Surge Bounty:** 125,000 Sats (\~$75.00 USD)

*Formula:* Bounty \= Base\_Bounty \* (1.0 \+ Max(0, (AUR \- 0.75) \* 10))

## **4\. Vanguard Agent Activation (UX)**

The primary goal of Surge Bounties is not just to pay active Agents more, but to pull *dormant* or off-duty Agents into the Sector.

* **Critical Push Alerts:** When the Surge Multiplier exceeds 2.0x, Vanguard Agents in adjacent sectors (or those marked "Off Duty" at home) receive Apple Critical Alerts / Android High-Priority FCM pushes, bypassing "Do Not Disturb" modes.  
* **Heatmapping:** The Agent Tactical App displays real-time hex-grid heatmaps, visually guiding Veterans to the highest-yielding intersections.

## **5\. Fleet Operator Cost Controls (Caps)**

Fleet Partners (e.g., Waymo, Zoox) maintain ultimate control over their OpEx burn rate.

* **The max\_surge\_multiplier Field:** When a Fleet provisions their Master API Key, they can set a hard cap on their willingness to pay (e.g., max\_surge\_multiplier: 3.0).  
* **SLA Trade-offs:** If the network Surge Multiplier climbs to 4.0x, but a specific Fleet has capped their spend at 3.0x, their AVs are placed in a **Secondary Routing Queue**.  
* **Impact:** The Fleet saves money, but forfeits the strict 15-minute SLA guarantee. Their vehicles will only be serviced once the high-paying surge tasks are cleared and the network returns to nominal density.

## **6\. Surge Cooldown & Finality**

Surge pricing is highly volatile and recalculates on a 30-second rolling window. However, to protect Vanguard Agents from "bait-and-switch" scenarios:

* The Satoshi bounty displayed on the Agent's screen at the moment of ACCEPT is cryptographically locked into the L402 HODL invoice.  
* Even if the dust storm clears 2 minutes later and the network Surge drops to 1.0x, the Agent is guaranteed the surged payout upon successful clearing of the AV's fault code.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABf0lEQVR4Xu2TP0sDQRDFc5BCQRs1CLm77MUmWIZg4x+w0DKW+gFsrG1OOxsLQQRrS5E0KRVELPwSloJFglUQRC0Ujb+X7MllRUhAuzx47N7Mm9nZt0kmM8S/whgzDx9g2/I2n89PuboEhUJhFc2H1Wq99n1/0tV1QPIQNmEDUeDmBRWTr8EnWCeUdTXfyOVyY4hOoyg6Zn1hmoqrAR75LbiL5hNuu4Ie0GQG0Qnruq7FWnU1xMu26Q77dzSLrqYHYRiuaQLWOQpe3SmCIBglv8fqk7uAd8VicTqt+QEVcPIK4lnYgvtOfkN52/Te9OunHkenawp4RspTnoYRDWO2WXtw/35SO2IPuBG1z3QbxWpstbEZxE/76WnKxDNNpqsroUPNoH4m3/ITtogvwwM9kuKyh3jD9OlnTRYkMfllur+AOiwn8UH8XEB0XiqVxlOxKrG2taTzWIK9we9+4uMSgkcVW77BTeUoqtDwKvk/Ez+Cz2ktmktsmejtOsQQf4ov5R135KkRWTUAAAAASUVORK5CYII=>