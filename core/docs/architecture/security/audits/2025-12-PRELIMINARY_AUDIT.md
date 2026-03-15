# **Proxy Agent Network (PAN) | Pre-Pilot Security Assessment (Internal)**

**Date:** December 15, 2025

**Scope:** PAN Gateway (Rust) & Vanguard Mobile SDK

**Auditor:** PAN SecOps & Infrastructure Team

**Status:** 🟡 PASSED (with remediations)

## **Executive Summary**

This internal assessment focused on the cryptographic integrity of the L402 Lightning settlement layer, the hardware attestation flow (TPM 2.0 / Secure Enclave) for Vanguard Agents, and the idempotency of incoming Fleet Operator UDS webhooks. The goal is to secure the network prior to the Q2 2026 Mesa Pilot involving live $150,000 autonomous assets.

## **Scope**

* **Target:** L402 Gateway Engine & Sector Dispatch Logic  
* **Repositories:** pan-core (Rust), vanguard-ios-sdk, pan-fleet-python  
* **Commit Hash:** f7a9b2c (v2025.12-alpha)

## **Key Findings**

### **1\. L402 Escrow Time-Lock Vulnerability**

* **Severity:** **High**  
* **Finding:** The Lightning HODL invoice expiration was temporarily defaulting to standard 24-hour limits during testing. If an Autonomous Vehicle (AV) suffered total power failure and could not transmit the FAULT\_CLEARED webhook, Fleet Operator funds would be needlessly locked in the routing channels for a full day.  
* **Remediation:** Overhauled the escrow\_timeout.rs module. Enforced a strict 30-minute absolute timeout for all M2H (Machine-to-Human) interventions. If the Preimage is not revealed within 30 minutes, the HTLC is automatically canceled and Satoshis revert to the Fleet Treasury.  
* **Status:** ✅ Fixed.

### **2\. Fleet Secret Key (HMAC) Leakage in Logs**

* **Severity:** **Medium**  
* **Finding:** During load testing, malformed /fleet/dispatch payloads that triggered a 500 Internal Server Error were dumping the raw HTTP headers into the journald logs, exposing the X-PAN-Signature and occasionally unredacted sk\_fleet\_live\_... master keys from testing environments.  
* **Remediation:** Implemented a strict redaction middleware. All headers matching X-PAN-\* and any string matching the regex ^sk\_fleet\_(live|test)\_\[a-zA-Z0-9\]+$ are now masked with \[REDACTED\] prior to hitting stdout or logging pipelines.  
* **Status:** ✅ Fixed.

### **3\. Idempotency Lock Bypass (Fleet Swatting)**

* **Severity:** **Critical**  
* **Finding:** A simulated AV node suffering from network jitter rapidly fired identical LIDAR\_MUD\_OCCLUSION webhooks 15 times in 2 seconds. The Gateway processed them concurrently, bypassing the Fleet's "Concurrent Mission Quota" and successfully dispatching 3 different Vanguard Agents to the same physical vehicle.  
* **Remediation:** Implemented the strict 15-Minute Idempotency Lock utilizing Redis. The Gateway now computes SHA-256(VIN \+ UDS\_CODE \+ TIME\_WINDOW). Duplicate requests within 15 minutes now correctly return a 409 Conflict and echo the existing mission\_id without deploying additional personnel or locking redundant L402 funds.  
* **Status:** ✅ Fixed.

### **4\. Edge-Vision PII Redaction Latency**

* **Severity:** **Low**  
* **Finding:** The local iOS CoreML model responsible for redacting bystander faces (PIP-018) prior to capturing hardware photos was causing a 4.5-second UI freeze on older iPhone 14 Pro test devices, delaying the SB 1417 audit log generation.  
* **Remediation:** Optimized the bounding box blur threshold and offloaded the image processing entirely to background threads, unblocking the main UI and ensuring the Agent's SLA timer is not artificially inflated.  
* **Status:** ✅ Fixed.

## **Conclusion**

With the implementation of the 15-minute idempotency lock and the 30-minute L402 timeout limits, the v2025.12-alpha codebase is structurally sound for the Mesa Pilot.

A full third-party penetration test and smart-contract/HTLC audit is scheduled for **March 2026** prior to onboarding production API keys from Tier-1 Fleet Partners (Waymo/Zoox).