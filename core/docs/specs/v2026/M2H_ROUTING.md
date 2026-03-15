# **Proxy Agent Network (PAN) | Machine-to-Human (M2H) Routing**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Routing Engine & Sector Operations

## **1\. The M2H Paradigm Shift**

The traditional gig economy operates on a Human-to-Machine (H2M) model: a human user opens an app and requests a machine (or service) to come to them.

The Proxy Agent Network (PAN) reverses this polarity. In the **Machine-to-Human (M2H)** model, the $150,000 Autonomous Vehicle (AV) acts as an independent economic actor. When grounded by a physical edge-case, the machine autonomously evaluates its internal state, generates a cryptographic bounty, and temporarily hires a human (the Vanguard Agent) to perform a hyper-specific physical task.

This requires a highly deterministic routing engine that prioritizes machine uptime over human preference.

## **2\. The Deterministic Routing Pipeline**

The PAN Sector Routing Engine operates at sub-second latency to guarantee our 15-minute Time-to-Site SLA. The pipeline executes in five distinct phases:

### **Phase 1: Ingestion & Idempotency**

1. The stranded AV transmits a Unified Diagnostic Service (UDS) fault code via the Fleet Gateway.  
2. The Gateway checks the vehicle\_vin\_hash against the active Idempotency Lock. If the AV is already being serviced, the webhook is dropped.

### **Phase 2: Isochrone Generation**

PAN does not route using simple "as-the-crow-flies" radial distances.

1. The engine ingests the AV's GPS coordinates.  
2. It generates a **12-minute drive-time isochrone (polygon)** around the AV, factoring in real-time Mesa traffic telemetry and road closures.  
3. Any Vanguard Agent located outside this polygon is instantly disqualified from the routing pool.

### **Phase 3: Candidate Filtering & VTS Weighting**

The system filters the eligible Agents inside the polygon based on their **Vanguard Trust Score (VTS)**:

* **Surge Tasks:** If the L402 bounty includes a surge multiplier \> 2.0x, the task is exclusively broadcast to **Elite Tier** (VTS 85-100) Agents for the first 10 seconds (First Right of Refusal).  
* **Standard Tasks:** Broadcast simultaneously to Elite and Standard Agents.  
* **Hardware Check:** The engine verifies the Agent's mobile TPM/Secure Enclave is currently online and attesting.

### **Phase 4: The Broadcast & Lock**

1. The L402 HODL invoice (the bounty) is pushed to the filtered Agents' Tactical Apps.  
2. The contract is resolved on a "First-to-Accept" basis.  
3. The millisecond an Agent taps ACCEPT, their device signs the intent with their hardware private key.  
4. The contract is cryptographically locked to that Agent. All other Agents see the task disappear from their map.

### **Phase 5: Telemetry Hand-off**

The Fleet Gateway opens a dedicated WebSocket connection, streaming the assigned Agent's real-time GPS telemetry back to the Fleet Operator's backend.

## **3\. Re-Routing & SLA Breaches**

Because PAN guarantees a 15-minute arrival time, the routing engine cannot wait indefinitely if an Agent hits unexpected delays.

* **The 12-Minute Warning:** If the Agent has not achieved a UWB (Ultra-Wideband) proximity lock with the AV by the 12-minute mark, the routing engine places a secondary Agent on "Standby."  
* **The SLA Expiration:** At exactly 15 minutes and 0 seconds, if the primary Agent has not established a UWB lock:  
  1. The primary Agent's contract is forcefully cancelled.  
  2. The primary Agent suffers a \-15 VTS SLA Breach slashing penalty.  
  3. The standby Agent is instantly upgraded to Primary, typically accompanied by an automated L402 Surge increase to cover the fleet's extended downtime.

## **4\. Sector Density Management (Brownouts)**

To prevent localized Agent exhaustion, the routing engine enforces Geohash limits.

If an anomalous event (e.g., a targeted vandalism attack, construction debris) grounds 15 AVs in a single square mile simultaneously, the engine will artificially "Brownout" incoming UDS requests from that specific Geohash once the local Agent capacity reaches 85%.

This forces Fleet Operators to route their unaffected vehicles *around* the anomalous zone until the local Vanguard Agents can clear the backlog, rather than blindly driving more vehicles into a physical trap.