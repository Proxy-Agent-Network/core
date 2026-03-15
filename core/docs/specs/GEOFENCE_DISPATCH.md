# Proxy Agent Network (PAN) | Geofencing & SLA Enforcement

**Status:** Active (Mesa Pilot)
**Version:** 2026.1
**ODD:** Sector 1 (Maricopa County, AZ)

---

## 1. The 15-Minute Mandate
The core value proposition of the Proxy Agent Network is speed. Autonomous Vehicle (AV) fleets lose thousands of dollars in revenue and incur massive reputational damage when a vehicle is stranded in live traffic. 

PAN guarantees a **15-Minute Maximum Time-to-Site SLA**. To achieve this without the overhead of centralized depots, the protocol relies on a hyper-local, two-tiered spatial routing architecture: **Macro-Routing (GPS)** and **Micro-Homing (UWB)**.

## 2. Macro-Routing: Sector Geofencing (GPS)

The Operational Design Domain (ODD) is divided into hexagonal geohashes. Vanguard Agents are not permitted to "free roam"; they must toggle their operational status to `ACTIVE_PATROL` within a specific sector.

### The Dispatch Algorithm:
1. **Fault Ingestion:** The Fleet Gateway receives a UDS webhook containing the stranded AV's exact GPS coordinates (e.g., `33.3214, -111.6608`).
2. **Isochrone Mapping:** The PAN routing engine calculates a 12-minute drive-time polygon (isochrone) around the stranded AV, accounting for real-time traffic telemetry.
3. **Candidate Filtering:** The system pings all active Vanguard Agents within the polygon.
4. **Bounty Broadcast:** The L402 HODL invoice is offered to the optimal candidates. The first Agent to accept the contract via Hardware Attestation (Secure Enclave) locks the bounty.
5. **Geofence Lock:** Once accepted, all other Agents are released, and the assigned Agent's telemetry is streamed directly to the Fleet Operator's dashboard.

## 3. Micro-Homing: Precision Recovery (UWB & BLE)

**The Parking Lot Problem:** Arriving at a GPS coordinate is insufficient if the AV is buried in a crowded 1,000-car transit center or a multi-level parking garage where GPS degrades.

To solve this, PAN Agents utilize their mobile hardware (iPhone U1/U2 chips or Android equivalent) to execute **Micro-Homing**:
* **BLE Handshake:** At 50 meters, the Agent's PAN app initiates a Bluetooth Low Energy handshake with the grounded AV.
* **UWB Precision:** At 15 meters, the app transitions to Ultra-Wideband (UWB), providing the Agent with an augmented reality directional arrow and distance-to-target accuracy within 10 centimeters.
* **Verification:** The UWB handshake serves as cryptographic proof of physical proximity, authorizing the Agent to begin the Optical Reclamation Protocol (ORP).

## 4. SLA Enforcement & Reputation Slashing

The PAN network is deterministic and unforgiving regarding SLA breaches. 

* **The 15-Minute Boundary:** From the millisecond the Agent accepts the L402 contract, a 15-minute countdown begins.
* **UWB Lock Requirement:** The Agent must achieve a UWB proximity lock with the AV before the timer expires.
* **SLA Breach (Slashing):** If the timer expires before a proximity lock is achieved:
  1. The L402 HODL invoice is automatically cancelled.
  2. The task is instantly re-routed to a secondary Agent (often utilizing Surge Pricing to guarantee immediate pickup).
  3. The at-fault Agent suffers a severe **Reputation Slash**.
* **Vanguard Revocation:** Agents who drop below a 98% SLA adherence rate are permanently demoted and lose access to Tier-1 Fleet API interventions.

## 5. Network Surges & Density Thresholds

To maintain the SLA, PAN must guarantee Agent density. If the ratio of active faults to available Agents in a sector drops below safe margins (e.g., during a severe dust storm causing mass sensor occlusions):

1. **Geofence Expansion:** The system expands the acceptable drive-time polygon to 20 minutes.
2. **L402 Surge Pricing:** The protocol automatically multiplies the base Lightning bounty (e.g., 3x, 5x) to incentivize off-duty Agents in adjacent sectors to immediately activate and deploy.