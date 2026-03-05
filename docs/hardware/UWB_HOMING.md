# **Proxy Agent Network (PAN) | UWB & BLE Precision Homing**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Vanguard Mobile SDK & Fleet Hardware Integrations

## **1\. The "Last 50 Meters" Problem**

Traditional gig-economy routing relies exclusively on GPS. However, for Autonomous Vehicle (AV) recovery, GPS degrades into a single point of failure during the final, most critical phase of the mission.

If a Waymo or Zoox vehicle is grounded on the 3rd floor of a concrete parking garage, or in a dense urban canyon where multipath interference bounces GPS signals, a Vanguard Agent cannot rely on a 2D map. Furthermore, finding the correct vehicle among a fleet of identically wrapped AVs requires precision beyond standard coordinates.

To solve this, PAN utilizes a **Two-Stage Micro-Homing Protocol** powered by Bluetooth Low Energy (BLE) and Ultra-Wideband (UWB).

## **2\. The Two-Stage Homing Protocol**

Once the Vanguard Agent's macro-routing (GPS) brings them within the general vicinity of the stranded AV, the PAN Tactical App seamlessly transitions into Micro-Homing mode.

### **Stage 1: The BLE Handshake (\~50 Meters)**

* **Trigger:** When the Agent's device registers a GPS coordinate within 50 meters of the target, it begins scanning for the AV's unique encrypted BLE beacon.  
* **Handshake:** The Agent's device broadcasts an encrypted challenge payload. The AV verifies the Agent's assigned mission\_id and responds with an acknowledgment.  
* **State Change:** The PAN Gateway updates the mission status to APPROACHING.

### **Stage 2: UWB Precision Targeting (\~15 Meters)**

* **Trigger:** Once the BLE handshake is established and signal strength (RSSI) indicates the Agent is within \~15 meters, the app activates the mobile device's UWB chip (e.g., Apple U1/U2 or Android NXP/Samsung UWB).  
* **Augmented Reality (AR) HUD:** The Agent's screen transitions to an AR camera view. UWB Time-of-Flight (ToF) calculations provide centimeter-level distance and highly accurate directional vectors.  
* **Component-Level Guidance:** The AR HUD does not just point to the vehicle; it points to the exact physical sensor that triggered the UDS fault (e.g., highlighting the "Front-Left LiDAR Dome" with a red digital reticle).

## **3\. Cryptographic Proof of Presence (PoP)**

UWB is not utilized solely for navigation; it is a critical security and anti-fraud mechanism.

GPS coordinates are notoriously easy to spoof via developer tools or malicious software. A rogue Agent could attempt to accept a task, spoof their location to the AV, and claim they cleared the sensor without ever leaving their couch.

**UWB Time-of-Flight cannot be spoofed remotely.** Because UWB measures the literal speed of light between the AV's transmitter and the Agent's phone, the Agent *must* be physically standing within centimeters of the vehicle.

1. **The Proximity Lock:** The 15-minute SLA timer only stops when the Agent achieves a verified UWB Proximity Lock (\< 1.5 meters from the target sensor).  
2. **TPM Signing:** Once the lock is achieved, the Agent's mobile Secure Enclave / TPM signs the UWB distance measurement.  
3. **Audit Log Inclusion:** This signed measurement is permanently embedded in the SB 1417 Optical Health Report, proving physical presence to State Regulators.

## **4\. Hardware Requirements**

To participate in the PAN network and execute the UWB handshake, both the Vanguard Agent and the Fleet Operator must meet specific hardware constraints.

### **Vanguard Agent (Mobile Nodes)**

Agents must operate one of the following PAN-certified devices equipped with spatial UWB chips:

* Apple iPhone 16 Pro, 17 Pro, or newer (U2/U3 chip).  
* Google Pixel 9 Pro or newer.  
* Samsung Galaxy S24+ or newer.

### **Fleet Operators (AV Nodes)**

AV Fleet Partners must ensure their vehicle architecture supports UWB beaconing.

* Most modern AV platforms (e.g., Zeekr/Waymo 6th Gen, Cruise Origin) include UWB for secure passive entry (Digital Key 3.0 standards).  
* The PAN Fleet SDK hooks into these existing UWB transmitters, temporarily re-purposing them as M2H homing beacons when a physical UDS fault is triggered.

## **5\. Fallback Protocols**

If an AV's UWB transmitter is damaged in a collision, or if severe environmental interference blocks the 6-8 GHz UWB spectrum:

1. The Agent's Tactical App automatically downgrades to **BLE RSSI Proximity**.  
2. The Agent utilizes visual identification via the AV's license plate and exterior fleet ID numbers.  
3. The Agent must manually select FORCE\_MANUAL\_LOCK in the app, which flags the intervention for secondary manual review by the PAN Command auditing team.