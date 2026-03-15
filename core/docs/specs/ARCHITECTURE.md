# Proxy Agent Network (PAN) | Cyber-Physical Architecture

**Version:** 2026.1.0
**Status:** Active (Mesa Pilot)
**ODD:** Sector 1 (Maricopa County, AZ)

---

## 1. Abstract
As autonomous vehicle (AV) fleets scale, they encounter a hard physical limit: hardware cannot physically maintain itself. A mud-splattered LiDAR lens or a vandalized camera array requires human intervention.

The **Proxy Agent Network (PAN)** is a decentralized, cyber-physical protocol bridging AV diagnostic intent with elite human physical execution. It utilizes **Mobile Hardware Attestation (TPM 2.0 / Secure Enclave)** for immutable identity, **L402 Lightning Protocols** for instant Machine-to-Human (M2H) micro-settlements, and the **SB 1417 Compliance Engine** to generate legally binding sensor audit logs.

---

## 2. The 6-Layer Architecture

The PAN protocol operates strictly on Zero-Trust principles across six primary layers:

### Layer 1: Hardware Root of Trust (Identity)
* **Role:** Prevents Sybil attacks, GPS spoofing, and identity fraud.
* **Mechanism:** Rust bindings interfacing with physical TPM 2.0 / Apple Secure Enclave chips on Vanguard Agent mobile devices.
* **Security:** Agents must cryptographically sign mission acceptance payloads using non-exportable private keys bound to their physical hardware.

### Layer 2: The Fleet Gateway API (Ingestion)
* **Role:** The enterprise ingress point (`fleet_gateway.py`).
* **Mechanism:** Ingests Unified Diagnostic Service (UDS) webhooks directly from AV Fleet Operators (Waymo, Zoox).
* **Security:** Implements strict HMAC-SHA256 signature verification and idempotency locks to eliminate duplicate dispatching for the same grounded asset.

### Layer 3: L402 Economic Settlement (Financial)
* **Role:** Machine-native financial layer replacing 30-day net invoices.
* **Mechanism:** Tasks are broadcast with Lightning Network (Satoshi) bounties.
* **Security:** Escrow logic utilizes `HODL Invoices`. Funds are only deducted from the Fleet Treasury when the AV's onboard AI confirms the physical fault code is cleared.

### Layer 4: Sector Dispatch (Geofencing & SLA)
* **Role:** Workload routing and 15-minute SLA enforcement.
* **Mechanism:** Cross-references incoming UDS coordinates with active Agent geofences. Utilizes GPS for macro-routing and Ultra-Wideband (UWB) for micro-homing (finding the specific AV in a crowded parking lot).

### Layer 5: The Compliance Engine (SB 1417)
* **Role:** The regulatory audit layer (`audit_engine.py`).
* **Mechanism:** Generates immutable "Optical Health Reports" detailing the physical intervention (ORP execution), the Agent's hardware signature, and the AV's VIN/Fault code to satisfy Arizona DPS statutory mandates.

### Layer 6: Tactical Ops Hub (Observability)
* **Role:** Real-time Mesa Sector 1 mission control.
* **Mechanism:** HTML/JS/WebSocket architecture streaming active fleet fault codes, Vanguard Agent deployment vectors, and live L402 settlement ledgers.

---

## 3. Cryptographic Auditability: The SB 1417 Engine

Because Vanguard Agents physically interact with $150k+ sensor arrays, liability and regulatory compliance are paramount. PAN mitigates physical liability via the **SB 1417 Compliance Engine**:

1. **Intervention Hashing:** Every step of the Optical Reclamation Protocol (ORP) is time-stamped and signed by the Agent's mobile hardware enclave.
2. **Immutable Ledgers:** The Fleet Gateway compiles the UDS fault, the Agent's signature, and the L402 settlement hash into a single JSON schema.
3. **Regulatory Output:** This data is hashed via SHA-256 and stored as a legally binding "Optical Health Report," proving to insurance carriers and state regulators exactly *who* touched the AV and *when*.

---

## 4. The Core M2H Transaction Loop

The following sequence describes the lifecycle of an autonomous AV recovery mission.

```mermaid
sequenceDiagram
    participant AV as 🚗 Autonomous Vehicle
    participant Gateway as 📡 Fleet Gateway
    participant Node as 🎖️ Vanguard Agent
    participant LND as ⚡ LND Escrow
    participant Audit as 🛡️ SB 1417 Engine

    AV->>Gateway: UDS Webhook (LIDAR_OCCLUSION)
    Gateway->>Gateway: Calculate Dynamic L402 Bounty
    Gateway->>LND: Lock Funds (HODL Invoice)
    Gateway->>Node: Dispatch Alert (GPS Coords)
    Node->>Node: TPM 2.0 Hardware Attestation
    Node-->>Gateway: Cryptographic Acceptance
    Node->>AV: Execute Optical Reclamation Protocol (ORP)
    AV->>AV: Internal Sensor Diagnostic Check
    AV->>Gateway: Fault Code Cleared
    Gateway->>LND: Reveal Preimage (Sats Transferred to Agent)
    Gateway->>Audit: Generate & Sign Optical Health Report