# **Proxy Agent Network (PAN) | SB 1417 Statutory Audit Framework**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet Legal Counsel & Regulatory Compliance Teams

## **1\. Legislative Context: The "Self-Certification" Ban**

In response to the rapid scaling of Level 4 autonomous fleets, the Arizona Legislature passed **SB 1417 (AZ Rev Stat § 28-9701)**, also known as the "Autonomous Vehicle Physical Redundancy Act."

Prior to 2026, Fleet Operators were permitted to self-certify the physical clearing of critical sensor occlusions. SB 1417 recognized this as a fundamental conflict of interest. The statute now explicitly mandates that if a vehicle's primary optical, LiDAR, or radar arrays register a critical fault code that forces a public roadway grounding, the physical clearing of that fault *must* be executed and cryptographically logged by a certified, independent third party.

The Proxy Agent Network (PAN) is uniquely architected from the ground up to act as this independent, zero-trust auditing layer.

## **2\. The Optical Health Report (OHR)**

To satisfy Arizona Department of Public Safety (DPS) audit requirements, the PAN Compliance Engine generates an immutable **Optical Health Report (OHR)** for every physical intervention.

The OHR mathematically binds the digital intent of the autonomous vehicle to the verified physical identity of the human Vanguard Agent. An OHR is only generated if all four of the following cryptographic conditions are met in sequence:

1. **Dispatch:** The Fleet Operator requests an intervention and locks the L402 Satoshi bounty.  
2. **Presence Verification:** The Vanguard Agent establishes an Ultra-Wideband (UWB) proximity lock (\< 1.5 meters) with the stranded asset, signing the Time-of-Flight distance with their mobile device's Secure Enclave/TPM 2.0 chip.  
3. **Execution:** The Agent executes the physical Optical Reclamation Protocol (ORP).  
4. **Machine Verification:** The Autonomous Vehicle runs an internal diagnostic sweep, verifies the sensor array is unobstructed, clears the Unified Diagnostic Service (UDS) fault code, and releases the L402 Lightning network preimage.

## **3\. Liability Shielding & Transfer Windows**

By utilizing the PAN network, Fleet Operators successfully transfer the liability of the physical intervention to PAN's comprehensive $5M Hired Non-Owned Auto (HNOA) and Errors & Omissions (E\&O) insurance umbrella.

### **The Liability Window**

Liability transfer is strictly bounded by cryptographic timestamps:

* **Assumption of Liability:** PAN assumes full liability for the physical state of the specific sensor array the exact millisecond the Vanguard Agent's TPM registers the **UWB Proximity Lock**.  
* **Release of Liability:** PAN's liability concludes the exact millisecond the AV broadcasts the **UDS Clear Webhook** and releases the L402 payment. By releasing the payment, the AV's onboard AI is legally asserting that the hardware is clean, functional, and ready for autonomous routing.

### **Agent Indemnification**

Vanguard Agents are protected against false claims of property damage by the AV's own internal hardware logs. If the AV registers a "cleared" state, the Fleet Operator has legally accepted the quality of the Agent's work. Any subsequent sensor failures after the AV resumes routing are the sole liability of the Fleet Operator.

## **4\. Immutable Storage & DPS Filings**

### **Data Retention**

To comply with SB 1417, PAN retains the cryptographic hashes and raw JSON payloads of all Optical Health Reports for a rolling period of **7 years** on immutable, write-once-read-many (WORM) ledger storage.

### **DPS Monthly Reporting**

Fleet Partners do not need to manually build compliance reports. Fleet Legal teams can query the PAN Compliance API GET /compliance/audit/monthly to download pre-formatted, DPS-ready CSVs and JSON arrays containing the TPM-signed attestations of every physical intervention executed in the previous 30 days.

### **Privacy Boundaries**

PAN acts exclusively as an auditor of *exterior physical hardware state*. To maintain the strictest privacy standards and minimize legal exposure:

* PAN does **not** ingest, process, or store raw interior cabin video.  
* PAN does **not** ingest passenger telemetry or personally identifiable information (PII).  
* PAN does **not** have access to the Fleet Operator's proprietary routing algorithms or source code.