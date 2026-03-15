# **Proxy Agent Network (PAN) | Mobile Node Recovery & Hardware Re-Provisioning**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Vanguard Agents & Mesa Hub Operations

| Applicability | Incident Type |
| :---- | :---- |
| **Vanguard Mobile Nodes** | Device Loss / Hardware Destruction / OS Compromise (Root/Jailbreak) |

## **1\. The "Zero-Recovery" Principle**

The Proxy Agent Network (PAN) relies on a Hardware Root of Trust to mathematically guarantee the physical presence of a Vanguard Agent during an autonomous vehicle intervention.

To maintain this integrity, the ECDSA private keys generated during an Agent's onboarding are fused to the silicon of the mobile device's Apple Secure Enclave or Android TPM 2.0 (StrongBox). **They are mathematically unrecoverable and non-exportable.** There is no "backup seed phrase" or "cloud sync."

\[\!CAUTION\]

If your authorized mobile device is physically destroyed, lost, or subjected to a factory reset, your current cryptographic identity is permanently "bricked." You must provision a factory-fresh device.

## **2\. The Hardware Revocation Protocol (Slashing)**

If a device is lost or stolen, it represents a critical security risk to the Fleet Operators, even if the device is protected by biometrics. The Vanguard Agent must immediately sever the hardware's access to the PAN routing engine.

1. **Immediate Reporting:** The Agent must contact PAN Command via the secure emergency line or the Mesa Hub terminal.  
2. **Cryptographic Severance:** The PAN Identity Registry immediately revokes the lost device's Public Key.  
3. **Network Rejection:** Any subsequent attempts by the lost device to sign a UWB proximity lock or accept an L402 bounty will be rejected with a 401 Unauthorized (Invalid Signature) error by the Sector Gateway.

## **3\. The Re-Provisioning Ceremony**

Because PAN binds a digital identity to a physical human, losing a device does *not* erase the Agent's hard-earned Vanguard Trust Score (VTS) or pending L402 payouts. However, associating a new hardware node to the existing human profile requires a physical verification step.

### **Step A: Physical Verification (Mesa Hub)**

The Vanguard Agent must physically present themselves at the Mesa Operations Hub (85212). Remote hardware provisioning is strictly forbidden to prevent SIM-swapping and social engineering attacks.

* The Agent must present their physical PAN ID Badge and state-issued identification.  
* The Agent's new mobile device must meet the strict hardware whitelist (iPhone 16 Pro+ or Pixel 9 Pro+).

### **Step B: The Binding Sequence**

1. The Agent logs into the PAN Tactical App on the new device while connected to the secure Mesa Hub localized network.  
2. The PAN App instructs the new device's Secure Enclave/TPM to generate a new ECDSA secp256r1 keypair.  
3. PAN Command physically countersigns the authorization, linking the new Public Key to the Agent's verified human profile in the Identity Registry.

## **4\. Hardware Probation Period**

While the Agent retains their VTS and Elite routing status, the newly provisioned Mobile Node is placed on a **7-Day Hardware Probation** to ensure OS stability and prevent emulator spoofing.

* **Aggressive Attestation:** During ACTIVE\_PATROL, the PAN Tactical App will poll Apple DeviceCheck or Android Play Integrity API every 60 seconds (up from the standard 5 minutes) to ensure the OS kernel has not been tampered with post-provisioning.  
* **UWB Calibration:** The first 3 Optical Reclamation Protocols (ORPs) executed with the new device will require a prolonged UWB handshake (an additional 5 seconds) to calibrate the new Time-of-Flight radio against the AV fleet's beacons.  
* **L402 Escrow Limits:** During the 7-day probation, the Agent is ineligible for single bounties exceeding a 3.0x Surge Multiplier to mitigate financial risk in the event of a compromised provisioning sequence.