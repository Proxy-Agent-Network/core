# **Proxy Agent Network (PAN) | Python Fleet SDK Reference**

**Package:** pan-fleet-sdk

**Version:** 2026.1.0 (Mesa Pilot)

**Base URL:** https://api.proxyagent.network/v2026.1

## **Client Class**

The main entry point for Fleet Operators (e.g., Waymo, Zoox) to programmatically interact with the PAN routing and L402 escrow network.

from pan\_fleet import PanFleetClient

\# Initialize with your Master Fleet API Key  
client \= PanFleetClient(  
    api\_key="sk\_fleet\_live\_...",   
    environment="production"  
)

## **Methods**

### **get\_sector\_status(sector\_id)**

Fetches real-time Vanguard Agent density, network congestion, and active L402 surge multipliers for a specific geographic sector.

**Parameters:**

| Parameter | Type | Description |

| :--- | :--- | :--- |

| sector\_id | str | The PAN routing sector (e.g., 'MESA\_AZ\_01'). |

* **Returns:** Dict  
  * active\_agents: int (Number of agents currently on patrol).  
  * surge\_multiplier: float (1.0 \= standard pricing, 3.0 \= heavy congestion/weather event).  
  * estimated\_sla\_secs: int (Current average time-to-site).

### **dispatch\_mission(vin\_hash, uds\_code, location, max\_l402\_sats)**

Broadcasts a critical physical intervention request to the Sector's Vanguard Agent pool. Instantly generates an L402 HODL invoice to lock the bounty.

**Parameters:**

| Parameter | Type | Description |

| :--- | :--- | :--- |

| vin\_hash | str | SHA-256 hash of the stranded AV's VIN. |

| uds\_code | str | The diagnostic fault code (e.g., 'LIDAR\_MUD\_OCCLUSION'). |

| location | dict | GPS Coordinates {"lat": 33.3214, "lng": \-111.6608}. |

| max\_l402\_sats | int | The maximum Satoshi bounty your fleet will authorize, including surge caps. |

* **Returns:** MissionObject containing the mission\_id, assigned\_agent\_id, and l402\_invoice.

### **get\_mission\_status(mission\_id)**

Polls the network for the physical status of a deployed Vanguard Agent. *(Note: In production, use our Webhook implementation to reduce polling overhead).*

**Parameters:**

| Parameter | Type | Description |

| :--- | :--- | :--- |

| mission\_id | str | The unique ID returned by dispatch\_mission. |

* **Returns:** Dict  
  * status: AGENT\_DISPATCHED | UWB\_PROXIMITY\_LOCK | ORP\_IN\_PROGRESS | UDS\_CLEARED | SLA\_BREACH  
  * eta\_seconds: int (Time until Agent arrives on site).

### **fetch\_sb1417\_audit(mission\_id)**

Retrieves the cryptographically signed Optical Health Report generated after a successful intervention. Used for state regulatory compliance and insurance shielding.

* **Returns:** Dict (The raw JSON schema of the SB 1417 Audit Log, signed by the Agent's hardware TPM).

## **Full Example: Automated LiDAR Recovery**

from pan\_fleet import PanFleetClient  
import time

client \= PanFleetClient("sk\_fleet\_live\_your\_key")

\# 1\. AV onboard AI detects mud on the primary LiDAR array  
fault\_code \= "LIDAR\_MUD\_OCCLUSION\_FL"  
vehicle\_location \= {"lat": 33.3214, "lng": \-111.6608}

\# 2\. Check current sector pricing and density  
status \= client.get\_sector\_status("MESA\_AZ\_01")  
print(f"Current Surge Multiplier: {status\['surge\_multiplier'\]}x")

\# 3\. Dispatch Vanguard Agent & Lock L402 Bounty  
mission \= client.dispatch\_mission(  
    vin\_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  
    uds\_code=fault\_code,  
    location=vehicle\_location,  
    max\_l402\_sats=50000  \# Willing to pay up to \~$30 USD in a surge  
)

print(f"Mission Dispatched: {mission.id}. ETA: {mission.eta\_seconds} seconds.")

\# 4\. Monitor execution (Simulated via Polling)  
while True:  
    state \= client.get\_mission\_status(mission.id)  
    print(f"Agent Status: {state\['status'\]}")  
      
    if state\['status'\] \== 'UDS\_CLEARED':  
        print("Hardware fault cleared. L402 Preimage released.")  
          
        \# Fetch compliance log for DPS filing  
        audit\_log \= client.fetch\_sb1417\_audit(mission.id)  
        print(f"SB 1417 Log Saved: {audit\_log\['audit\_id'\]}")  
        break  
          
    time.sleep(15)  
