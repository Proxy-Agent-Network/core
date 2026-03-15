# PAN Tactical: Proxy Agent Network 🌐

**An enterprise-grade, multi-tenant mobile platform for Autonomous Vehicle (AV) incident response.**

PAN Tactical is a distributed edge-to-cloud architecture that allows human field agents ("Proxy Agents") to receive live dispatch coordinates, navigate to stranded autonomous vehicles, perform physical interventions, and mint cryptographic smart-contract receipts.

---

## 🚀 Core Architecture

* **Bidirectional Telemetry:** Android Foreground Services stream persistent GPS coordinates to a Firebase RTDB ledger, powering a live Web Command Center.
* **Store-and-Forward Resilience:** An offline-first sync engine caches encrypted PII-redacted evidence arrays to the local SSD during dead-zone operations (e.g., underground parking garages) and automatically syncs when 5G is restored.
* **Tactical Routing:** Integrates the OSRM routing API to generate custom polyline paths directly on the Google Map, with dynamic switching between Vehicle and Foot Patrol modes.
* **Identity & Security:** Secures all endpoints via Firebase Authentication UIDs and dynamic Android Hardware Attestation tokens.
* **High-Priority Dispatch:** Leverages Firebase Cloud Messaging (FCM) to wake sleeping devices and drop Heads-Up Notifications (HUN) for rapid response times.

---

## ⚡ Key Features

1. **Dynamic Loadout & Reverse Auction:** Agents toggle specific hardware capabilities (e.g., "Jump Kits", "Tire Repair") and set market bids. The Command Center automatically filters missions based on real-time loadouts.
2. **Foot Patrol Mode:** Dynamically restricts service radiuses and disables heavy-equipment tasks for agents operating in dense, gridlocked urban environments.
3. **AI Privacy Filter:** Natively runs an onboard sanitation pass to blur human faces and license plates before evidence arrays leave the hardware.
4. **Live Command Dashboard:** A serverless Web UI that plots active agents, renders their operational footprint, and allows one-click manual dispatching.

---

## 🛠 Tech Stack & Project Structure

This project is built using **Kotlin Multiplatform (KMP)** targeting Android and iOS, with a heavy V1 focus on native Android hardware integrations.

**Edge Node (Mobile Terminal)**
* **Language:** Kotlin
* **UI Framework:** Compose Multiplatform (Material 3)
* **Networking:** Ktor, OkHttp, Coil
* **Sensors & Hardware:** Google Play Location Services, CameraX, Text-to-Speech (TTS)
* **Background Tasks:** Android Foreground Services, Coroutines

**Command Center & Cloud (Backend)**
* **Platform:** Firebase (RTDB, Auth, FCM)
* **Web UI:** HTML, CSS, Vanilla JS, Google Maps JavaScript API
* **Third-Party APIs:** ImgBB (Evidence Array Hosting), OSRM (Routing)

### Repository Layout
* `/composeApp`: Contains the shared Compose UI and platform-specific implementations.
  * `commonMain`: Shared UI and business logic.
  * `androidMain`: Android-specific hardware implementations (Foreground Services, CameraX, FCM).
  * `iosMain`: iOS-specific implementations.
* `/iosApp`: The iOS application entry point (Xcode project).

---

## ⚙️ Build and Run Instructions

### Android Application (V1 Primary Target)
To build and run the development version of the Android app, use the run configuration in your IDE (Android Studio / IntelliJ) or build it directly from the terminal:

**macOS/Linux:**

    ./gradlew :composeApp:assembleDebug

**Windows:**

    .\gradlew.bat :composeApp:assembleDebug

### iOS Application
*Note: V1 relies heavily on Android-specific hardware APIs. Full iOS feature parity requires implementation of iOS-equivalent background tasks and location services.*

To build and run the development version of the iOS app, open the `/iosApp` directory in Xcode and run it from there, or use your IDE's run widget.