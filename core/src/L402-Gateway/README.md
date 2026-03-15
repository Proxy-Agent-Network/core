# **L402 Gateway & Settlement Engine**

**Status:** Active (Mesa Pilot)

**Language:** Rust (v1.75+)

**Dependencies:** ldk-node, lightning-invoice, tokio

## **1\. Overview**

The /src/L402-Gateway/ module is the financial heart of the Proxy Agent Network (PAN). It is a zero-custody, high-throughput escrow engine that bridges HTTP REST webhooks from Autonomous Vehicle (AV) Fleet Operators with the Lightning Network (Bitcoin Layer 2).

By leveraging **L402 (Lightning 402 Payment Required)** standards, this gateway allows a stranded Waymo or Zoox vehicle to programmatically lock a Satoshi bounty in a Hashed Timelock Contract (HTLC), which is only released to a Vanguard Agent upon physical resolution of the vehicle's hardware fault.

## **2\. Module Architecture**

The Gateway is built on an Actor Model using tokio::sync::mpsc channels to prevent race conditions during concurrent fleet surges.

### **Core Components (/src/L402-Gateway/core/)**

* **lnd\_client.rs**: The primary gRPC interface with the PAN Master Lightning Node. Handles channel liquidity routing and peer connections to Fleet Operator Treasuries.  
* **invoice\_mgr.rs**: Generates mathematically secure **HODL Invoices**. Responsible for generating the 32-byte cryptographic secret (the preimage) and the corresponding SHA-256 payment hash.  
* **escrow\_timeout.rs**: A time-series sweeper that monitors the 15-minute Vanguard SLA and the 30-minute max-escrow lock. Automatically cancels routing if SLAs are breached.  
* **surge\_oracle.rs**: Calculates dynamic L402 repricing based on Sector 1 geohash density and incoming UDS webhook velocity.

## **3\. The Cryptographic Settlement State Machine**

Every Machine-to-Human (M2H) intervention transitions through a strict cryptographic state machine.

### **State 1: INVOICE\_GENERATED**

The AV Fleet Gateway ingests a UDS fault (e.g., LIDAR\_OCCLUSION). The invoice\_mgr.rs generates a random 32-byte secret (Preimage R) and hashes it to create Hash(R). An L402 HODL invoice containing Hash(R) is returned to the Fleet Operator.

### **State 2: HTLC\_LOCKED**

The Fleet Operator's Lightning Node routes the Satoshi bounty along the Lightning Network toward the PAN Gateway. The funds are cryptographically locked in transit. *PAN does not custody these funds; they are held by the network's HTLC math.*

### **State 3: AGENT\_DISPATCHED**

The locked bounty is offered to the nearest Vanguard Agent. The Agent accepts the contract via their mobile TPM 2.0 hardware signature. The 15-minute SLA timer begins.

### **State 4: UDS\_CLEARED\_SIGNAL**

The Vanguard Agent completes the Optical Reclamation Protocol (ORP). The AV runs an internal diagnostic, verifies the sensor is clean, and sends a 200 OK webhook to the PAN Gateway indicating the fault code is cleared.

### **State 5: PREIMAGE\_REVEALED (Terminal Success)**

Upon receiving the UDS\_CLEARED\_SIGNAL, the PAN Gateway injects the secret Preimage R into the Lightning Network.

1. The network recognizes the secret.  
2. The HTLC unlocks.  
3. The Satoshis instantly route into the Vanguard Agent's mobile Lightning wallet.

### **State 6: SLA\_BREACH\_CANCELLED (Terminal Failure)**

If escrow\_timeout.rs detects the 15-minute timer has expired before the Agent achieves a UWB proximity lock, or if 30 minutes pass without a UDS\_CLEARED\_SIGNAL, the Gateway cancels the HODL invoice. The HTLC expires, and the locked funds instantly revert to the Fleet Operator.

## **4\. Security & Idempotency Rules**

To protect Fleet Operators from double-billing during network latency or hardware retry loops, the L402 Gateway enforces strict idempotency.

* **Cache Layer:** All incoming AV webhooks are hashed (SHA-256(VIN \+ UDS\_CODE \+ TIMESTAMP\_HOUR)) and stored in Redis.  
* **Duplicate Rejection:** If the Gateway receives a duplicate hash while an HTLC is currently LOCKED or DISPATCHED, it will drop the request and return a 409 Conflict, echoing the existing L402 invoice string.  
* **Max Bounty Hardcap:** The Gateway will forcefully reject any dynamic surge bounty exceeding 150,000 Sats to prevent runaway algorithmic spend loops.

## **5\. Local Development & Regtest**

To simulate the L402 Gateway locally without spending real Bitcoin:

\# 1\. Spin up the local Polar/Regtest Lightning Network  
make start-regtest

\# 2\. Compile and run the Gateway Actor  
cargo run \--bin l402\_gateway \-- \--network=regtest \--sector=MESA\_01

\# 3\. Simulate a Fleet Operator UDS Webhook  
curl \-X POST http://localhost:8080/v1/l402/lock \\  
  \-H "Authorization: Bearer test\_fleet\_key" \\  
  \-d '{"vin": "WXYZ123", "fault": "LIDAR\_MUD", "sats": 25000}'  
