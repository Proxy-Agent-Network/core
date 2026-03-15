# Proxy Agent Network (PAN) | Agent Geofence Telemetry

**Status:** Active (Mesa Pilot)
**Version:** 2026.1.0
**Target:** Vanguard Tactical App & Fleet Dashboards

---

## 1. The Telemetry Paradigm

To guarantee a sub-15-minute Time-to-Site SLA, the Proxy Agent Network (PAN) Routing Engine must maintain an ultra-accurate map of available Vanguard Agents. However, PAN is deeply committed to the privacy of its Veteran workforce. 

Unlike traditional gig-economy applications that continuously harvest background location data to sell to third-party data brokers, PAN utilizes a strict **Privacy-by-Default State Machine**. Location telemetry is highly granular when active, but cryptographically walled off when an Agent is off-duty.

## 2. Telemetry State Machine

A Vanguard Agent's location data is handled differently depending on their current network state.

### State 0: `OFF_DUTY`
* **Condition:** The Agent has toggled their status offline in the Tactical App.
* **Telemetry:** **ZERO.** The PAN app completely releases the iOS/Android background location hook. PAN Command has no knowledge of the Agent's location.

### State 1: `ACTIVE_PATROL`
* **Condition:** The Agent has signed their shift attestation via TPM and is waiting for an L402 bounty in their assigned Sector.
* **Telemetry:** **Macro-Polling (Every 15s).** The device pings the PAN Routing Engine with low-fidelity GPS coordinates to update the Sector Isochrone Map. This data is kept entirely internal and is *never* exposed to Fleet Partners.

### State 2: `MISSION_EN_ROUTE`
* **Condition:** The Agent has tapped `ACCEPT` on a mission, locking the L402 HODL invoice.
* **Telemetry:** **High-Fidelity Streaming (Every 1s).** The PAN Gateway opens a secure WebSocket connection. The Agent's real-time GPS coordinates, heading, and speed are streamed directly.
* **Fleet Visibility:** This stream is piped directly to the Fleet Operator's backend (e.g., Waymo/Zoox) so remote operators can track the Agent's ETA to the stranded AV.

### State 3: `UWB_PROXIMITY_LOCK`
* **Condition:** The Agent arrives within 15 meters of the AV.
* **Telemetry:** **Micro-Homing.** Macro-GPS is suspended. Spatial telemetry is handled exclusively via Ultra-Wideband (UWB) to guide the Agent to the specific sensor array.

## 4. Sector Geofence Enforcement (Mesa Pilot)

Vanguard Agents are currently restricted to specific Operational Design Domains (ODDs). For the Q2 2026 Pilot, the only active Geofence is **Sector 1 (Mesa, AZ - 85212)**.

* **Boundary Logic:** The PAN Tactical App contains a locally cached polygon of the Sector boundary. 
* **Out of Bounds:** If an Agent on `ACTIVE_PATROL` crosses outside the Sector polygon (e.g., driving onto the US-60 West toward Tempe), the app will sound a short alert and automatically transition the Agent to `OFF_DUTY`. 
* **Reasoning:** PAN cannot guarantee a 15-minute SLA to Mesa-based AV fleets if an Agent is currently driving out of the county. Agents must physically re-enter the polygon to toggle back on.

## 5. Hardware & OS-Level Constraints

To maintain constant `ACTIVE_PATROL` connectivity without draining the mobile device's battery or being killed by the mobile OS, the PAN app leverages specific hardware permissions:

* **iOS (Apple):** The app utilizes the `UIBackgroundModes` location flag. Agents must grant **"Always Allow"** location permissions to ensure the app is not suspended by iOS memory management while sitting idle in a cupholder.
* **Android (Google/Samsung):** The app runs a `Foreground Service` bound to a persistent notification. This explicitly prevents Android's Doze mode from putting the PAN Routing Engine to sleep during critical patrol hours.

## 6. Telemetry Data Retention

All high-fidelity telemetry (`MISSION_EN_ROUTE` streams) is purged from PAN's active databases **48 hours** after the completion of an Optical Reclamation Protocol (ORP). 

Only the final, TPM-signed UWB proximity lock coordinate is retained indefinitely as part of the immutable Arizona SB 1417 Optical Health Report.