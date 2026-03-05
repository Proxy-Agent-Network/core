# **Proxy Agent Network (PAN) | Service Catalog & Base Bounties**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target:** Fleet API (V2X) Integrations

## **1\. Physical Service Constraints**

The Proxy Agent Network (PAN) is strictly an exterior physical infrastructure layer. Vanguard Agents are trained to resolve environmental and physical edge-cases that ground Autonomous Vehicles (AVs).

Agents **cannot** resolve internal software faults, reboot compute nodes, or service high-voltage EV battery systems. Dispatches must strictly map to the supported physical Unified Diagnostic Service (UDS) fault codes listed below.

All prices are denominated in Bitcoin Satoshis via the L402 Lightning Network. *Note: USD equivalents are estimates based on a $60,000 BTC exchange rate. Actual settlement is purely in Satoshis.*

## **2\. Sensor Reclamation (The ORP)**

The most common intervention. Environmental debris completely blinds a critical optical or LiDAR sensor, preventing autonomous routing.

* **Supported UDS Codes:** LIDAR\_MUD\_OCCLUSION, OPTICAL\_LENS\_OBSTRUCTED, RADAR\_FASCIA\_BLOCKED  
* **Agent Action:** Execution of the 4-Phase Optical Reclamation Protocol (ORP) utilizing the PAN-issued "HP Potion" solvent and single-use microfiber cloths.  
* **Base L402 Bounty:** 25,000 Sats (\~$15.00 USD)  
* **Target SLA:** \< 15 Minutes (from Dispatch to UDS Clear)

## **3\. Cabin & Closure Security**

A passenger exits the vehicle but fails to fully latch the door or trunk, preventing the AV from safely resuming its route.

* **Supported UDS Codes:** CABIN\_DOOR\_AJAR, TRUNK\_NOT\_LATCHED, FRUNK\_UNSECURED  
* **Agent Action:** Physical inspection of the latch perimeter for obstructions (e.g., a caught seatbelt or bag strap), followed by a manual closure of the door. *Note: Agents will not enter the cabin.*  
* **Base L402 Bounty:** 20,000 Sats (\~$12.00 USD)  
* **Target SLA:** \< 15 Minutes

## **4\. Perimeter Obstructions & Minor Vandalism**

The AV is trapped by a physical object in its path that its software cannot confidently navigate around (e.g., a maliciously placed traffic cone on the hood, a tipped-over trash can, or a tumbleweed).

* **Supported UDS Codes:** PERIMETER\_VANDALISM, PATH\_OBSTRUCTED\_DEBRIS  
* **Agent Action:** The Agent removes the non-threatening physical obstruction from the vehicle's immediate path, allowing the AV to recalculate its trajectory.  
* **Base L402 Bounty:** 30,000 Sats (\~$18.00 USD)  
* **Target SLA:** \< 15 Minutes

## **5\. Escalation & Scene Secure (Wait Time)**

The AV has suffered severe kinetic damage (e.g., a collision) or a permanent hardware failure that cannot be resolved via the ORP. The Fleet Operator requires a human to secure the scene while the official Fleet Tow Truck is en route.

* **Supported UDS Codes:** KINETIC\_COLLISION, CRITICAL\_HARDWARE\_FAILURE, FLAT\_TIRE  
* **Agent Action:** The Agent parks behind the AV, activates hazard lights, deploys MUTCD-compliant safety triangles, and provides encrypted edge-vision photos of the damage to the Fleet Operator. The Agent waits until the Tow arrives.  
* **Base L402 Bounty:** 50,000 Sats base \+ 1,000 Sats/minute wait time (\~$30.00 \+ $0.60/min).  
* **Target SLA:** N/A (Agent remains on-site until relieved).

## **6\. Dynamic Surge Pricing**

The base bounties listed above apply during nominal network conditions (Agent Utilization Ratio \< 75%).

During severe weather events (e.g., Haboobs/Dust Storms) or localized gridlock, the Sector Routing Engine will automatically apply a **Surge Multiplier (up to 5.0x)** to these base bounties to incentivize dormant Agents to enter ACTIVE\_PATROL status.

*For real-time pricing and surge multipliers, query the GET /sector/status API endpoint.*