# **Proxy Agent Network (PAN) | Vanguard Hardware Reference Design**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Vanguard Agents & Procurement Teams

## **1\. The Cyber-Physical Node Concept**

Unlike traditional blockchain networks where a "Node" is a server sitting in a data center, the Proxy Agent Network (PAN) relies on **Cyber-Physical Nodes**. A PAN Node consists of a highly secure mobile compute unit bonded to a vetted human operator (the Vanguard Agent), equipped with specialized physical tools to interact with Autonomous Vehicle (AV) hardware.

To maintain our $5M HNOA/E\&O liability shield and ensure compliance with Arizona SB 1417, PAN enforces strict, uncompromising hardware whitelists.

## **2\. Layer 1: The Mobile Compute Node (Cryptographic & Spatial)**

The mobile device is the Agent's sole interface with the PAN Routing Engine and the L402 Lightning Network. It is responsible for hardware attestation and precision spatial homing.

### **2.1 Whitelisted Devices**

Vanguard Agents must operate one of the following devices. No exceptions.

* **Apple:** iPhone 16 Pro, iPhone 16 Pro Max, iPhone 17 Pro, iPhone 17 Pro Max.  
* **Google:** Pixel 9 Pro, Pixel 9 Pro XL, Pixel 10 Pro.  
* **Samsung:** Galaxy S24+, Galaxy S24 Ultra, Galaxy S25+.

### **2.2 Required Sub-Components**

These specific models are whitelisted because they contain two non-negotiable hardware components:

1. **Hardware Root of Trust (TPM 2.0 / Secure Enclave):** Required to generate non-exportable ECDSA secp256r1 keypairs for signing the Optical Health Report.  
2. **Ultra-Wideband (UWB) Radio:** Apple U2/U3 or NXP/Samsung UWB chips are mandatory. Used for Time-of-Flight (ToF) spatial calculations to guide the Agent to the exact centimeter of the occluded AV sensor, preventing GPS spoofing.

## **3\. Layer 2: The Physical Reclamation Kit ("HP Potion")**

Vanguard Agents are strictly forbidden from using off-the-shelf cleaning supplies, which can degrade the $10,000+ anti-reflective coatings on AV LiDAR arrays and cameras.

### **3.1 The ORP Standard Kit**

Every Vanguard Agent is issued a standard Optical Reclamation Protocol (ORP) field kit containing:

* **The Solvent:** 1L bottle of 99.9% Deionized, Ultra-Pure Water (0 PPM) formulated with a proprietary, non-abrasive optical surfactant.  
* **The Abrasives:** Pack of 50 single-use, sealed 120gsm optical-grade microfiber cloths (edgeless/laser-cut to prevent scratching).  
* **The Propellant:** 150 PSI moisture-free, zero-residue compressed air duster.  
* **Sanitation:** Box of 100 powder-free black nitrile gloves (6 mil thickness).

\[\!IMPORTANT\]

**Cross-Contamination Rule:** Microfiber cloths are strictly single-use. Reusing a cloth across multiple AV interventions traps silica (sand) and creates micro-scratches. This is a severe slashing offense.

## **4\. Layer 3: Safety & Vehicle Assets (PPE)**

Vanguard Agents frequently operate in high-risk traffic environments (e.g., a stranded AV blocking a lane on US-60 or Southern Ave).

### **4.1 Personal Protective Equipment (PPE)**

* **High-Visibility Vest:** ANSI/ISEA 107-2020 Class 3 compliant. MUTCD High-Vis Yellow (\#E8FF00) with 2-inch silver retroreflective striping. The PAN "Hex-Shield" logo is printed in Infrastructure Slate (\#0A192F) on the rear panel.  
* **Base Uniform:** PAN-issued tactical moisture-wicking polo (Infrastructure Slate).  
* **Identification:** PAN physical cryptographic ID badge worn on a high-retention chest clip.

### **4.2 Response Vehicle Markings**

Vanguard Agents utilize personal vehicles to navigate the macro-route. Upon arriving at the stranded AV, the vehicle must be temporarily marked.

* **Hazard Lighting:** SAE J845 Class 1 certified amber/white LED light bar (magnetically roof-mounted). *Red/Blue emergency lights are strictly prohibited and illegal for non-LEO use.*  
* **Signage:** Two 24" x 12" high-reflectivity magnetic door decals displaying "PROXY AGENT NETWORK" and the Agent's unique 4-digit ID number in LiDAR Cyan (\#64FFDA).