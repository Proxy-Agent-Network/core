# **Proxy Agent Network (PAN) | Cyber-Physical Threat Model**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet CISOs, Security Engineers, & Threat Hunters

## **1\. Defining the Cyber-Physical Threat**

The Proxy Agent Network (PAN) represents a unique intersection of digital infrastructure and physical reality. In traditional web security, an API vulnerability leads to data exfiltration. In the PAN architecture, a compromised API or hardware node can result in the unauthorized physical deployment of human actors to $150,000 robotic assets in live traffic.

Because the stakes are physical, our threat model goes beyond standard OWASP Top 10 vulnerabilities to address location spoofing, hardware cloning, and localized fleet denial-of-service (DoS) attacks.

## **2\. Identified Threat Actors**

We design our mitigations against three distinct classes of threat actors:

1. **Rogue Agents:** Insider threats attempting to manipulate the routing algorithm or spoof locations to extract L402 Satoshi bounties without performing the physical work.  
2. **Hacktivists / Vandals:** Anti-autonomous vehicle groups attempting to artificially ground fleets or swarm specific Geohashes with false dispatches.  
3. **Advanced Persistent Threats (APTs):** Highly sophisticated actors attempting to compromise the L402 Lightning network escrow, or disrupt municipal transit infrastructure by targeting the Fleet API gateway.

## **3\. Attack Vectors & Mitigations**

### **Vector A: Location Spoofing (The "Phantom Agent" Attack)**

* **The Threat:** A rogue Agent uses a GPS-spoofing application or a rooted Android emulator to trick the PAN Routing Engine into believing they have arrived at the stranded AV, allowing them to claim the bounty from their couch.  
* **The Mitigation (UWB & TPM):** PAN completely distrusts GPS for the final 15 meters of an intervention. The Agent must establish a physical Ultra-Wideband (UWB) Time-of-Flight proximity lock. Because UWB relies on the speed of light between two physical radios, it cannot be spoofed over a network. Furthermore, the Agent's mobile Secure Enclave / TPM 2.0 must cryptographically sign this UWB distance measurement.

### **Vector B: Webhook Injection ("Fleet Swatting")**

* **The Threat:** An attacker intercepts or guesses a Fleet Operator's API structure and fires thousands of fake /fleet/dispatch webhooks, attempting to drain the Fleet's L402 escrow and deploy all available Vanguard Agents to fake locations.  
* **The Mitigation (HMAC & Quotas):** 1\. Every dispatch request requires an HMAC-SHA256 signature generated using a non-transmitted Fleet Secret Key, coupled with a strict 60-second temporal expiration.  
  2\. Even if a signature is successfully forged, the physical attack is bounded by **Concurrent Mission Quotas**. A Fleet is hard-capped (e.g., max 25 concurrent Agents). Once the quota is hit, the PAN Gateway drops further dispatches, preventing total network exhaustion.

### **Vector C: L402 Escrow Draining (Double Billing)**

* **The Threat:** Due to spotty 5G coverage, an AV repeatedly fires the same LIDAR\_MUD\_OCCLUSION UDS fault code every 10 seconds. Without safeguards, this could generate dozens of L402 HODL invoices for a single event, draining the Fleet's Lightning channel liquidity.  
* **The Mitigation (Idempotency Locks):** The PAN Gateway hashes VIN \+ Fault Code \+ 15-Minute SLA Window. If a duplicate request matches an active hash, the Gateway returns a 409 Conflict and echoes the existing mission\_id. No additional L402 invoice is generated, and no additional Agent is dispatched.

### **Vector D: Device Cloning (Sybil Attacks)**

* **The Threat:** An attacker extracts the private key from a high-reputation Vanguard Agent's device and loads it onto a farm of emulators to artificially dominate the Sector Routing Engine.  
* **The Mitigation (Silicon Fusing):** During provisioning, the ECDSA keypair is generated directly inside the Apple Secure Enclave or Android StrongBox. The private key is non-exportable and mathematically fused to the silicon. The PAN App utilizes DeviceCheck (iOS) and Play Integrity API (Android) to continuously poll the OS kernel. If a compromised or emulated environment is detected, the device's public key is instantly slashed from the Identity Registry.

### **Vector E: Hardware Extortion (The "Hostage" AV)**

* **The Threat:** An Agent arrives at a stranded AV but refuses to clear the sensor unless the Fleet Operator manually sends a higher L402 payment outside the PAN protocol.  
* **The Mitigation (Deterministic Routing):** The Agent has no leverage. If the AV's onboard AI does not broadcast the FAULT\_CLEARED UDS webhook within the 15-minute SLA \+ a 15-minute grace period, the L402 HODL invoice automatically expires. The funds mathematically revert to the Fleet Treasury. The Agent receives $0 and suffers a severe Vanguard Trust Score (VTS) slashing penalty, leading to immediate network revocation.

## **4\. Geohash Brownouts (Kinetic Overload)**

While PAN can mitigate digital spoofing, we must also protect against coordinated physical attacks (e.g., protesters placing traffic cones on the hoods of 50 AVs simultaneously in a single intersection).

To prevent Vanguard Agents from driving into a hostile or overwhelmed Geohash, the PAN Routing Engine utilizes an automated **Brownout Protocol**. If a single square mile generates more than 15 unique UDS critical faults within a 5-minute window, the Routing Engine will temporarily suspend that Geohash. Fleet webhooks for that zone will return a 503 Service Unavailable, forcing the Fleet to reroute their remaining assets around the compromised zone until law enforcement secures the physical perimeter.