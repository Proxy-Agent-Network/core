# **Proxy Agent Network (PAN) | Vanguard Agent Operator's Manual**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Clearance:** Vanguard Level 1 (V1)

## **1\. Introduction & Operational Posture**

Welcome to the Proxy Agent Network (PAN). As a Vanguard Agent, you are the critical human-in-the-loop for the largest autonomous vehicle (AV) fleets in the world. When a $150,000 robotic asset is blinded by environmental debris or physically obstructed, you are the specialized rapid-response unit dispatched to reclaim it.

You operate in a **Machine-to-Human (M2H)** framework. You do not have a human dispatcher. Autonomous vehicles will hire you directly via cryptographic smart contracts (L402 bounties) to clear their physical fault codes.

**Your primary directive is speed, precision, and zero-impact hardware interaction.**

## **2\. The Vanguard Loadout (Hardware & PPE)**

To maintain our $5M HNOA/E\&O liability shield, Agents must deploy with their complete PAN-issued loadout. Failure to utilize official gear during an intervention is a slashing offense.

### **2.1 Authorized Mobile Hardware**

You must operate exclusively on the PAN-issued mobile device (e.g., iPhone 17 Pro Max or Android Pixel 10). This is not just a screen; it is your cryptographic identity.

* **Secure Enclave / TPM 2.0:** Your device contains a locked hardware chip that signs your location and identity to State Regulators.  
* **UWB (Ultra-Wideband) U2 Chip:** Used for precision targeting of stranded AVs down to the centimeter.

### **2.2 Personal Protective Equipment (PPE)**

* **Class 3 High-Visibility Vest:** Must be worn at all times when outside your response vehicle. Intersections are highly dangerous environments.  
* **Black Nitrile Gloves:** Must be donned prior to touching any AV sensor to prevent oil transfer to optical coatings.

### **2.3 The "HP Potion" Reclamation Kit**

* 99.9% Deionized Ultra-Pure Water with optical surfactant.  
* Single-use 120gsm edgeless microfiber pads.  
* 150 PSI moisture-free compressed air.

## **3\. Shift Initialization (Hardware Boot)**

Vanguard Agents do not use passwords. To begin a patrol shift in the Mesa Sector:

1. **Physical Geofence:** You must physically be inside your assigned Sector polygon.  
2. **Biometric Unlock:** Open the PAN Tactical App and authenticate via FaceID/Fingerprint.  
3. **Hardware Attestation:** The app will prompt your device's Secure Enclave to generate a cryptographic signature. This proves to the network that *you* are physically holding the registered device.  
4. **Status Toggle:** Swipe to ACTIVE\_PATROL. You are now visible to stranded AVs in the Sector.

## **4\. Mission Execution & The UWB Handshake**

When an AV generates a UDS fault code, the highest-rated Vanguard Agent in the isochrone receives the bounty alert.

1. **The Contract:** You have 10 seconds to tap ACCEPT. Doing so cryptographically locks the Satoshi bounty to your device and starts the **15-Minute SLA Timer**.  
2. **Macro-Routing:** Follow the Tactical HUD's GPS routing to the incident coordinates.  
3. **Micro-Homing (The UWB Lock):**  
   * At **50 meters**, your device will automatically initiate a Bluetooth (BLE) handshake with the grounded AV.  
   * At **15 meters**, your screen will switch to Augmented Reality (AR) mode, using Ultra-Wideband (UWB) to guide you to the exact sensor (e.g., "Front-Left LiDAR Dome").  
4. **The ORP:** Execute the Optical Reclamation Protocol (Air Sweep \-\> HP Potion \-\> Single Microfiber Pull).  
5. **Clear & Egress:** Step back 5 feet. Once the AV runs its internal diagnostic and verifies the sensor is clean, it will release the L402 payment to your wallet instantly.

## **5\. Operational Security (OPSEC) & Emergencies**

As a Vanguard Agent, you may encounter hostile environments, vandalism, or vehicular collisions.

* **Rule of Engagement:** You are an infrastructure technician, not law enforcement. If an AV is surrounded by a hostile crowd, actively being vandalized, or involved in a major kinetic collision, **DO NOT APPROACH**.  
* **The Abort Protocol:** In the Tactical App, select ABORT: SCENE UNSAFE. This will safely cancel the L402 contract without a Vanguard Trust Score (VTS) slashing penalty and immediately escalate the UDS webhook back to the Fleet Operator for police dispatch.  
* **Cabin Prohibition:** Under no circumstances are you to open the cabin doors or interact with passengers unless your Tactical App flashes a verified CABIN\_EMERGENCY red-alert override from the Fleet Operator.