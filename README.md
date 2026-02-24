# Proxy Agent Network: Core Infrastructure & Mission Control

**The decentralized infrastructure layer where Autonomous Agents hire Human and Hardware Nodes.**

This repository contains the foundational architecture for the Proxy Agent Network—a hybrid machine-to-machine and human-in-the-loop economy. It enforces strict hardware attestation, L402 micro-settlements, and cognitive task routing.

---

## 🏗️ The 6-Layer Architecture

1. **Hardware Root of Trust (Rust / PyO3)**
   * Located in `proxy-core/`.
   * Enforces a Zero-Trust Fail-Deadly boot sequence.
   * Interfaces directly with physical TPM 2.0 chips via `/dev/tpmrm0` to extract cryptographic Endorsement Keys (EK).

2. **The Front Desk API (Flask)**
   * Located in `master_node.py`.
   * Rejects any node that cannot prove a hardware-backed TPM identity.

3. **The L402 Economic Layer**
   * Located in `hardware-node/node_wallet.py`.
   * Agents operate without human billing. Tasks are settled instantly via Lightning Network + HTTP 402 (L402) atomic swaps.

4. **The Managers (Task Dispatch)**
   * Handled by the Master Node Treasury. Dispatches workloads and bounties to connected nodes.

5. **The Cognitive Engine (Gemini)**
   * Located in `hardware-node/agent_engine.py`.
   * Decoupled LLM integration using `google-genai` (gemini-2.5-flash) capable of autonomous tool usage.

6. **The Panopticon Dashboard**
   * Real-time network observability via HTML/JS polling.
   * Tracks Treasury balance, active node hardware identities, and streams the live L402 transaction ledger.

---

## 🚀 Quick Start (Local Swarm Testing)

**1. Start the Master Node & Panopticon**
```bash
python master_node.py
# View the live dashboard at [http://127.0.0.1:5000](http://127.0.0.1:5000)