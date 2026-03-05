# **Proxy Agent Network (PAN) | Zero-Biometric Privacy Policy**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Vanguard Agents, Fleet Partners, & Regulatory Bodies

## **1\. The Zero-Biometric Philosophy**

Traditional gig-economy platforms often harvest massive amounts of personal data, including facial recognition scans, continuous background GPS telemetry, and broad device permissions.

The Proxy Agent Network (PAN) operates under a strict **Data Minimization and Zero-Biometric** mandate. Because our Vanguard Agents interface with highly sensitive autonomous assets, identity verification is paramount. However, we believe identity should be cryptographic, not biometric.

PAN **never** ingests, processes, transmits, or stores raw biometric data (e.g., fingerprints, facial maps, retinal scans). All biometric authentication occurs strictly on-device, within the local Apple Secure Enclave or Android TPM 2.0 (StrongBox). PAN only receives the resulting cryptographic mathematical signature asserting that a successful local authentication occurred.

## **2\. Vanguard Agent Privacy & Telemetry**

We respect the privacy of our Veteran workforce. Location tracking is strictly governed by the Agent's active duty state.

* **OFF\_DUTY:** When an Agent toggles their status offline in the PAN Tactical App, all location services are immediately and entirely terminated. PAN retains no background location hooks and cannot track off-duty personnel.  
* **ACTIVE\_PATROL:** PAN collects macro-level, low-fidelity GPS pings (every 15 seconds) strictly for the purpose of Sector Isochrone routing and network density mapping.  
* **MISSION\_EN\_ROUTE:** High-fidelity, real-time telemetry (1-second intervals) is collected and streamed to the Fleet Operator exclusively for the duration of the active mission to calculate Time-to-Site SLAs. This streaming ceases the moment the L402 contract is settled or cancelled.

## **3\. Autonomous Fleet & Passenger Isolation**

PAN provides a physical infrastructure layer for the *exterior* hardware of Autonomous Vehicles (AVs). To limit legal liability and protect civilian privacy, PAN enforces a strict architectural isolation from passenger data.

* **No Interior Visibility:** PAN APIs do not ingest, request, or store interior cabin video feeds, passenger audio recordings, or in-cabin telemetry.  
* **No Passenger PII:** PAN does not receive passenger names, payment information, or account details from our Fleet Partners.  
* **Routing Obfuscation:** PAN is only provided with the GPS coordinates of the stranded vehicle. We do not receive the vehicle's final destination or passenger routing history.

## **4\. SB 1417 Data Retention**

Under Arizona SB 1417 (AZ Rev Stat § 28-9701), PAN acts as an independent, third-party auditor for autonomous sensor diagnostics. To satisfy state regulatory requirements, PAN must retain specific cryptographic artifacts.

* **The Optical Health Report (OHR):** PAN retains the immutable, cryptographic hashes of all completed missions, including the Agent's TPM signature, the UWB proximity distance, and the UDS fault code.  
* **Retention Period:** These compliance logs are retained on Write-Once-Read-Many (WORM) storage for a period of **7 years** to satisfy state auditing and insurance liability requirements.  
* **High-Fidelity Telemetry Purge:** Standard GPS routing data from the MISSION\_EN\_ROUTE phase is permanently purged from our active databases 48 hours after mission completion.

## **5\. Third-Party Sharing**

PAN does not sell, rent, or monetize Vanguard Agent or Fleet Partner data to third-party data brokers or advertisers.

Data sharing is strictly limited to:

1. **Fleet Partners:** We stream the assigned Vanguard Agent's real-time telemetry, UWB attestation, and TPM signature to the specific Fleet Operator (e.g., Waymo, Zoox) that issued the L402 bounty.  
2. **Regulatory & Law Enforcement:** We will only surrender OHR compliance logs to the Arizona Department of Public Safety (DPS) or law enforcement agencies when compelled by a valid subpoena, warrant, or mandatory state audit request.

## **6\. Contacting the Data Protection Officer (DPO)**

For inquiries regarding data retention, deletion requests, or compliance with this policy, please contact PAN Command via the secure internal Signal channel or email compliance@proxyagent.network.