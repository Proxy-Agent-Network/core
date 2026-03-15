# **Proxy Agent Network (PAN) | Optical Reclamation Protocol (ORP)**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1

**Target Hardware:** Waymo 6th Gen (Zeekr), Cruise Origin, Zoox L4

**Authorized Personnel:** Certified Vanguard Agents Only

## **1\. Purpose & Scope**

Autonomous Vehicle (AV) sensor suites (LiDAR, Radar, and Optical Cameras) are highly sensitive, calibrated instruments. A single micro-abrasion on a LiDAR dome can permanently degrade the vehicle's spatial mapping capabilities, resulting in thousands of dollars in hardware replacement costs.

The **Optical Reclamation Protocol (ORP)** is the strict, zero-deviation Standard Operating Procedure (SOP) for physically clearing environmental occlusions (mud, biological debris, dust) from these arrays. Strict adherence to the ORP is required to maintain PAN's $5M HNOA/E\&O liability shield.

## **2\. The Authorized "HP Potion" Kit**

Vanguard Agents are strictly forbidden from using commercial cleaning agents (e.g., Windex) or standard paper towels. Agents must only use the PAN-issued "HP Potion" field kit, which contains:

* **Solvent:** 99.9% Deionized, Ultra-Pure Water (0 PPM) mixed with a proprietary, non-abrasive optical surfactant.  
* **Abrasive Pad:** Single-use, sealed 120gsm optical-grade microfiber cloths (edgeless).  
* **Air Clearance:** 150 PSI compressed air duster (moisture-free).  
* **PPE:** Powder-free black nitrile gloves.

## **3\. The 4-Phase Execution SOP**

Upon arriving at the stranded AV, the Vanguard Agent must execute the following protocol in exact sequence:

### **Phase 1: Secure & Attest**

1. **Perimeter Secure:** Park the PAN response vehicle safely behind the AV. Activate high-visibility hazard beacons.  
2. **UWB Proximity Lock:** Approach the AV on foot. Open the PAN Tactical App to establish a Bluetooth/Ultra-Wideband (UWB) proximity lock.  
3. **Cryptographic Check-In:** The mobile app will utilize the device's Secure Enclave/TPM 2.0 to sign a proximity attestation, notifying the Fleet Gateway that the ORP has commenced.

### **Phase 2: Non-Kinetic Clearance**

1. **Don PPE:** Put on fresh nitrile gloves. *Never touch an optical array with bare skin; skin oils degrade anti-reflective coatings.*  
2. **Air Sweep:** From a distance of 6 inches, use the compressed air duster to blast away loose grit, sand, and dust from the occluded sensor. *Do not shake the air can.*

### **Phase 3: Solvent Application (Kinetic)**

1. **Lubrication:** Generously spray the "HP Potion" solvent directly onto the occluded area. Allow 15 seconds for the surfactant to break down biological or mud adhesion.  
2. **The "Pull" Technique:** Fold the optical microfiber cloth into quarters. Place the cloth flat against the sensor glass. Pull the cloth in a **single, straight motion** across the surface.  
3. **Zero-Rotation Rule:** *NEVER wipe in a circular motion.* Circular wiping traps grit under the cloth and creates swirling micro-abrasions. If a second pass is needed, flip the cloth to a clean quarter and repeat the straight pull.

### **Phase 4: Digital Verification & Egress**

1. **Step Back:** Step back 5 feet from the AV to clear its proximity collision sensors.  
2. **Diagnostic Wait:** The AV's onboard AI will automatically cycle its sensor diagnostics (typically takes 10-15 seconds).  
3. **L402 Settlement:** Once the AV confirms the Unified Diagnostic Service (UDS) fault code is cleared, it will instantly release the Lightning network preimage. The PAN app will chime, indicating the Satoshi bounty has settled to the Agent's wallet.  
4. **Audit Generation:** The PAN API automatically generates the SB 1417 Optical Health Report, and the AV resumes its autonomous routing.

## **4\. Strict Prohibitions (Slashing Offenses)**

Violation of any of the following rules will result in immediate termination of the Agent's PAN certification and forfeiture of pending L402 escrow balances:

* **Cabin Entry:** Never attempt to open the doors or interact with passengers unless explicitly authorized by a specialized CABIN\_EMERGENCY UDS webhook.  
* **Hood/Compute Access:** Never attempt to open the AV's hood or access the internal compute/high-voltage systems.  
* **Cross-Contamination:** Never reuse a microfiber cloth between different AV interventions. Discard the cloth after every single completed ORP.  
* **Hardware Force:** If an occlusion (e.g., dried concrete, heavy paint vandalism) cannot be cleared by the standard HP Potion protocol, the Agent must select ESCALATE\_TO\_TOW in the app. Never use scraping tools or excessive physical force.