# Proxy Agent Network (PAN) | Core Infrastructure

![Sector Status](https://img.shields.io/badge/Sector-Mesa_AZ_01-blue)
![Compliance](https://img.shields.io/badge/Compliance-SB_1417-success)
![Protocol](https://img.shields.io/badge/Protocol-L402-orange)

## The Human Infrastructure for the Autonomous Era
PAN is a decentralized physical infrastructure network (DePIN) providing the critical "Last-Mile" physical layer for autonomous vehicle (AV) fleets. We utilize a hardware-attested, veteran-led workforce to resolve physical edge-cases (sensor occlusions, recovery, and maintenance) that ground AV assets.

### 🛠 Tech Stack
* **Settlement Engine:** L402 (Lightning Network) for M2H (Machine-to-Human) instant micro-payments.
* **Identity & Trust:** Hardware-backed attestation via TPM 2.0 (Android StrongBox) and Apple Secure Enclave.
* **Compliance:** Automated logging for **Arizona SB 1417** (Section 28-9701) sensor diagnostic audits.
* **Mobile Client:** Kotlin Multiplatform targeting iOS and Android for Agent field operations.

### 🛰 Operational Design Domain (ODD)
* **Primary Sector:** Mesa, AZ (Sector 1)
* **Anchor Point:** Waymo/Magna Integration Facility (85212)
* **Response SLA:** < 12 Minutes

## 🏗 Repository Structure
* `/docs/SB-1417/`: Statutory compliance frameworks and audit log schemas.
* `/src/L402-Gateway/`: Settlement logic for autonomous vehicle-triggered bounties.
* `/protocols/ORP/`: Optical Reclamation Protocol (HP Potion) standard operating procedures.
* `/composeApp/`: Shared Kotlin Multiplatform code for Vanguard mobile applications.
* `/iosApp/`: iOS specific entry points and SwiftUI code.

## 📱 Mobile App Development (Kotlin Multiplatform)

### Build and Run Android Application
To build and run the development version of the Android app, use the run configuration from the run widget in your IDE’s toolbar or build it directly from the terminal:
* **macOS/Linux:** `./gradlew :composeApp:assembleDebug`
* **Windows:** `.\gradlew.bat :composeApp:assembleDebug`

### Build and Run iOS Application
To build and run the development version of the iOS app, use the run configuration from the run widget in your IDE’s toolbar or open the `/iosApp` directory in Xcode and run it from there.

## 🎖 The Vanguard 50
We are currently recruiting 50 Veterans for the Mesa Pilot. 
* **Go-Live:** Memorial Day Weekend 2026.
* **Sign-up:** [proxyagent.network/enlist](https://www.proxyagent.network/enlist)

---
**CONFIDENTIAL // PROPRIETARY INFRASTRUCTURE**
© 2026 Proxy Agent Network LLC.