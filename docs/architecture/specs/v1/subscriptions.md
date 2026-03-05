# **Proxy Agent Network (PAN) | Enterprise SLA & Reserved Capacity**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0 (Supersedes v1 Proxy-Pass)

**Target:** Fleet Procurement & Operations

## **1\. The Physical Capacity Problem**

In cloud computing, compute power scales infinitely. In the Proxy Agent Network (PAN), physical Vanguard Agents are a finite resource.

During nominal operations, standard L402 pricing easily clears the queue. However, during a mass-grounding event (e.g., a sudden Arizona dust storm blinding 50 Autonomous Vehicles simultaneously in a single square mile), the Agent Utilization Ratio (AUR) will hit 100%.

When Vanguard Agent supply is exhausted, PAN must decide which Fleet's vehicles are recovered first. To solve this, PAN offers **Reserved Capacity SLAs** for enterprise Fleet Partners.

## **2\. Enterprise Capacity Tiers**

Instead of paying flat per-transaction routing fees, Enterprise Fleets can commit to a monthly capacity retainer. This guarantees Vanguard availability and routing priority during severe Geohash Brownouts.

| Tier | Monthly Retainer | Routing Fee | Quota Limit | Brownout Priority |
| :---- | :---- | :---- | :---- | :---- |
| **On-Demand (Standard)** | $0 / Pay-as-you-go | 15% | 5 Active | Standard FIFO. First to be queued during surges. |
| **Sector Priority** | $5,000 / Sector | 10% | 25 Active | Level 2\. Bypasses standard queues up to 4.0x Surge. |
| **Sector Anchor** | $25,000 / Sector | 5% | 100+ Active | Level 1\. Highest priority. Guaranteed 15-min SLA. |

\[\!NOTE\]

The monthly retainer strictly covers PAN's infrastructure routing and SLA guarantees. 100% of the underlying L402 Satoshi bounties are still paid directly to the Vanguard Agents for their physical labor.

## **3\. Technical Implementation (Liquidity Commitments)**

We do not use legacy "subscription tokens." Enterprise SLA status is mathematically bound to your Fleet's Lightning Network topology and API provisioning.

1. **The API Upgrade:** PAN Command upgrades your sk\_fleet\_live\_... Master Key to the requested tier, immediately unlocking higher Concurrent Mission Quotas.  
2. **Channel Capacity (The Commitment):** To activate *Sector Anchor* status, the Fleet Treasury must open a direct, high-capacity Lightning channel with the PAN Sector 1 Master Node (Minimum capacity: 2.5 BTC).  
3. **Instant Settlement:** This dedicated inbound liquidity ensures that even during massive network congestion, your L402 HODL invoices route instantly to Vanguard Agents without hitting multi-hop routing failures.

## **4\. Priority Routing Logic (Brownout Conditions)**

When a specific Geohash enters Stage 🔴 **Brownout** (\>95% Agent Utilization), the Sector Routing Engine suspends standard First-In, First-Out (FIFO) logic.

1. **Queue Triage:** All On-Demand dispatches are placed into a holding queue (receiving a 503 QUOTA\_EXHAUSTED or 409 response).  
2. **Anchor Primacy:** Any active Vanguard Agent that completes an intervention is instantly routed to the nearest stranded AV belonging to a **Sector Anchor** fleet.  
3. **Surge Exemption:** Anchor Fleets maintain their strict 15-minute SLA guarantees without being forced to bid against the absolute maximum 5.0x Surge Multiplier cap.

By becoming a Sector Anchor, a Fleet Operator fundamentally reserves a percentage of the local Vanguard workforce as a dedicated, hyper-local rapid response team.