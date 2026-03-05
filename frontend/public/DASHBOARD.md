# **Proxy Agent Network (PAN) | Sector Command Dashboard**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** PAN Sector Operators & Fleet Command

This directory contains the Jinja2/HTML templates and frontend logic for the PAN Sector Command Dashboard—the primary observability interface for monitoring live autonomous vehicle interventions, Vanguard Agent telemetry, and L402 Lightning settlements.

## **🎨 The Tactical Theme Engine**

The dashboard utilizes a decoupled theme-engine.js that manages UI aesthetics for different physical operating environments using the \<html\> tag's data-theme attribute.

### **Core Themes**

| Theme ID | Description | Primary Font | Environment Use |
| :---- | :---- | :---- | :---- |
| slate | **(Default)** High-contrast dark mode using Infrastructure Slate. | Urbanist / JetBrains Mono | NOC / Command Center |
| high-vis | Daylight optimized with MUTCD Yellow/Black contrast. | Urbanist | Field Operators (Mobile) |
| corporate | Clean, light-mode interface for compliance reporting. | Inter | Fleet Legal / Executive |

### **UI Stability & Performance**

* **FOUC Prevention:** A pre-render script injection in the \<head\> prevents "Flash of Unstyled Content" by loading the saved theme from localStorage before the DOM paints.  
* **Dynamic CSS Variables:** Themes control logic-based colors for the Sector Telemetry Maps (e.g., \--surge-glow: \#B87333 for active Geohash brownouts) to ensure immediate visual recognition of physical traffic anomalies.

## **🎛️ Ops Command Center (command.html)**

The operational nerve center allowing PAN Command to monitor and manually override network routing during severe physical events.

1. **UDS Dispatch Monitor:** Live feed of incoming POST /fleet/dispatch webhooks from Fleet Partners (Waymo, Zoox).  
2. **Brownout Override (Danger Zone):** Provides a manual toggle to execute a Geohash Brownout (suspending new dispatches in a 1-sq-mile zone) if physical safety is compromised, overriding the automated AUR calculation.  
3. **Vanguard Registry Search:** A real-time client-side filter allowing operators to find specific Agents by vanguard\_id, current Vanguard Trust Score (VTS), or active hardware attestation status (e.g., checking if a TPM 2.0 key is revoked).

## **📜 SB 1417 Ledger & L402 Telemetry**

The dashboard features a detailed telemetry modal (\#mission-modal) that tracks the lifecycle of an AV intervention in real-time.

### **Mission Hierarchy & Nesting**

The ledger uses visual indentation to group the cryptographic state machine of a specific intervention:

1. **Base Mission:** The primary trigger (e.g., MSN-88A9-4B2C | LIDAR\_MUD\_OCCLUSION).  
2. **Nested Telemetry:** Indented state changes:  
   * └─ 📡 HODL Invoice Locked (25,000 Sats)  
   * └─ 📍 UWB Proximity Lock Achieved (\< 1.5m)  
   * └─ 🛡️ TPM Signature Verified  
   * └─ ⚡ Preimage Revealed (Fault Cleared)

### **Tactical Audio Rack**

The header includes an Audio Control Rack for NOC operators. SFX are tiered based on mission criticality:

* **UDS Ingest:** Low-pitch sonar ping when a new stranded AV enters the queue.  
* **SLA Warning:** High-frequency pulse if a mission crosses the 12-minute ETA threshold.  
* **L402 Settlement:** Crisp, satisfying chime indicating the AV has cleared its fault and funds are released.

## **📈 Sector Logic & Observability**

The client-side logic separates "Server Truth" from "Display Truth" to handle high-frequency telemetry without locking the browser UI.

1. **WebSocket Telemetry:** Replaces legacy polling. The client maintains an active WSS connection to /stream/sector/{sector\_id} for sub-second Agent GPS updates and UWB lock notifications.  
2. **Surge Multiplier Visualization:** The UI dynamically calculates and displays the current Agent Utilization Ratio (AUR). As the AUR passes 75%, the dashboard initiates a pulsing \--surge-glow on the affected Geohash sectors.  
3. **Idempotency Drops:** If the gateway drops a duplicate UDS webhook from a glitching AV (The 15-Minute Rule), the UI briefly flashes a grey \[DUPLICATE BLOCKED\] tag in the ledger to maintain NOC visibility without triggering new mission logic.