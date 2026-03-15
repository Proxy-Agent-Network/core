# **ADR 001: L402 Lightning Network for Machine-to-Human (M2H) Settlements**

**Date:** 2026-01-15

**Status:** Accepted (Mesa Pilot)

**Context:** PAN Core Infrastructure / Settlement Engine

## **Context**

The Proxy Agent Network (PAN) requires a sub-second, zero-custody settlement layer to transfer financial value from Autonomous Vehicles (Machines) to Vanguard Agents (Humans).

When an AV generates a physical Unified Diagnostic Service (UDS) fault code (e.g., LIDAR\_MUD\_OCCLUSION), it must programmatically deploy capital to incentivize a human to perform the Optical Reclamation Protocol (ORP).

* **Constraint 1 (Zero-Custody):** PAN acts as an infrastructure routing layer. For legal and regulatory reasons, we cannot custody Fleet Operator capital or Vanguard Agent earnings.  
* **Constraint 2 (Machine-Native Escrow):** The bounty must be cryptographically locked. It can only be released when the AV's onboard AI verifies the sensor is clean. Human dispute resolution is too slow.  
* **Constraint 3 (Instant Finality):** To maintain the 15-minute SLA and motivate high-tier Veterans, settlement must be instantaneous upon task completion. 30-day net terms are unacceptable.

## **Options Considered**

### **1\. Traditional Fiat (Stripe Connect / ACH)**

* **Pros:** Standard enterprise developer experience. Highly understood by Fleet Operator finance teams.  
* **Cons:** High fixed fees ($0.30 \+ 2.9%) degrade unit economics. Cannot natively support cryptographic escrows without PAN acting as a legally liable custodian holding funds in a centralized bank account.  
* **Verdict:** Rejected. Incompatible with the Zero-Custody constraint.

### **2\. Layer 1/Layer 2 Smart Contracts (Ethereum / Solana)**

* **Pros:** Highly programmable escrows via Solidity/Rust smart contracts.  
* **Cons:** Introduces the "Oracle Problem." Bridging the AV's internal UDS fault code to an on-chain smart contract requires trusted off-chain relays, introducing latency and gas fee volatility. Mobile wallet UX for Vanguard Agents remains a friction point.  
* **Verdict:** Rejected for the 2026 Pilot.

### **3\. L402 (Lightning Network \+ HTTP 402\)**

* **Pros:** Sub-cent routing fees. Instant settlement finality. **HODL Invoices** natively solve the M2H escrow problem: the Fleet Operator locks the Satoshi bounty in a Hashed Timelock Contract (HTLC). The AV simply releases the 32-byte Preimage via webhook when the sensor clears, instantly pulling the funds to the Agent's mobile wallet. PAN never touches the funds.  
* **Cons:** Requires Fleet Operators to manage Lightning Node liquidity and channel routing.  
* **Verdict:** **Selected.**

## **Decision**

We will utilize the **Bitcoin Lightning Network** via the **L402 Protocol Standard** for the primary M2H settlement and escrow mechanism.

## **Consequences**

* **Gateway Engineering:** We must build a high-throughput, Rust-based L402 Gateway (src/L402-Gateway/) utilizing ldk-node and tokio to handle concurrent HODL invoice generation and timeout sweeps.  
* **Fleet Treasury Nodes:** Fleet Partners (Waymo, Zoox) must provision internal Lightning Nodes to route outbound liquidity to the PAN Sector Gateways.  
* **Satoshi Denomination:** All internal network pricing, including the Dynamic Surge Multipliers, will be denominated and settled in Satoshis (Sats), though Fleet dashboards may display USD equivalents for UX purposes.  
* **Sovereign Fleet Philosophy:** This aligns with our core philosophy that a Level 4 Autonomous Vehicle should be a fully sovereign economic actor capable of hiring its own human support staff without centralized corporate invoicing.