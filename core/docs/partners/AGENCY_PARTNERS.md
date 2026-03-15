# Proxy Agent Network (PAN) | OEM & Fleet Management Partner Program

**Status:** Invite Only (Mesa Pilot Q2 2026)
**ODD Focus:** Sector 1 (Maricopa County, AZ)

PAN is designed as a headless, cyber-physical infrastructure layer. We empower Tier-1 Fleet Management Companies (FMCs), Autonomous Vehicle (AV) Insurance Carriers, and Sensor OEMs to build branded, SLA-backed "Field Recovery" services on top of our Vanguard Agent network.

---

### The Model: B2B2B Infrastructure
You own the fleet or hardware relationship. We provide the physical edge-case execution.

1.  **The Offering:** You sell a LiDAR array or a Fleet Depot contract to a Robotaxi company, bundled with an automated "15-Minute Field Recovery" SLA.
2.  **The Trigger:** Your proprietary hardware/software detects a sensor occlusion and pings the PAN Fleet Gateway via your Master API Key.
3.  **The Execution:** A cryptographically verified Vanguard Agent is dispatched, executes the Optical Reclamation Protocol (ORP), and clears the fault.
4.  **The Compliance:** We generate the SB 1417 Audit Log, passing the cryptographic proof back to your dashboard.
5.  **The Settlement:** PAN bills your LND node the wholesale Lightning bounty. You bill your fleet client the retail recovery fee.

---

### Enterprise Multi-Tenant Architecture
Channel Partners are issued a **Master Fleet Key** (`sk_fleet_master_...`) which allows for:

* **Sub-Fleet Management:** Create isolated webhook environments for each of your AV operator clients (e.g., separating Waymo UDS codes from Zoox UDS codes).
* **Consolidated Escrow:** Fund a single Lightning Network escrow channel to manage L402 M2H micro-settlements across your entire client portfolio.
* **White-Labeled Audits:** Ingest our raw JSON SB 1417 audit logs and format them into your own branded compliance PDFs for your clients.

---

### Partnership & Volume Tiers

| Monthly Interventions | Escrow Requirement | SLA / Support Level |
| :--- | :--- | :--- |
| **< 100 / month** | 0.05 BTC | Standard API Documentation |
| **100 - 1,000 / month** | 0.50 BTC | Priority Dispatch Geofencing |
| **> 1,000 / month** | 2.00 BTC | Dedicated Vanguard Squads & Signal Channel |

---

### Apply for Partnership
We are currently selecting two Tier-1 channel partners for the 2026 Mesa Pilot. To request a Master Fleet Key, please open a **GitHub Issue** in this repository with the tag `[OEM-PARTNER]` and describe your hardware stack or managed fleet size operating in Maricopa County.