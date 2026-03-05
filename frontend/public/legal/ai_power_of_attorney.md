# **MACHINE-TO-HUMAN (M2H) PHYSICAL INTERVENTION MANDATE**

**Version:** 2026.1.0 (Mesa Pilot)

**Jurisdiction:** State of Arizona / AZ Rev Stat § 28-9701 (SB 1417\)

**Executing Network:** Proxy Agent Network (PAN) Gateway

### **1\. AUTHORIZATION & APPOINTMENT**

The Fleet Operator ("Principal"), acting through the autonomous directives of the grounded Autonomous Vehicle ("Asset") identified by the cryptographic VIN\_HASH attached hereto, hereby authorizes the certified PAN Vanguard Agent ("Agent") identified by their hardware TPM\_PUB\_KEY, to execute a physical hardware intervention on the Asset.

### **2\. IDENTIFICATION OF ASSET & AGENT**

* **Fleet Operator:** \[FLEET\_ID\] (e.g., WAYMO\_LLC)  
* **Autonomous Asset (VIN Hash):** \[VEHICLE\_VIN\_HASH\]  
* **Vanguard Agent (TPM Public Key):** \[AGENT\_TPM\_PUBKEY\]  
* **Incident Coordinates:** \[GPS\_LAT\_LNG\]  
* **L402 Escrow Contract:** \[LN\_INVOICE\_HASH\]

### **3\. SCOPE OF AUTHORITY (THE UDS FAULT)**

This mandate grants the Agent explicit, limited authority to perform physical actions on the Asset's exterior strictly necessary to clear the following Unified Diagnostic Service (UDS) fault:

**Active Fault Code:** \[UDS\_FAULT\_CODE\]

Authorized physical interventions are strictly limited to the PAN Service Catalog:

* \[ \] **Optical Reclamation Protocol (ORP):** Application of PAN "HP Potion" solvent and microfiber clearance to occluded LiDAR, Radar, or Optical Domes.  
* \[ \] **Perimeter Clear:** Removal of non-hazardous physical debris or vandalism obstructing the Asset's routing path.  
* \[ \] **Cabin / Closure Secure:** Physical inspection and closure of an ajar exterior passenger door or trunk latch.  
* \[ \] **Scene Secure:** Deployment of MUTCD-compliant safety triangles and hazard lighting pending heavy tow retrieval.

### **4\. STRICT PROHIBITIONS (SLASHING OFFENSES)**

This mandate **DOES NOT** authorize the Agent to:

* Open, enter, or reach inside the passenger cabin (unless explicitly authorized by a CABIN\_EMERGENCY override).  
* Open the hood, trunk (unless securing an ajar latch), or access internal compute nodes and high-voltage EV battery systems.  
* Use scraping tools, unauthorized commercial solvents, or excessive kinetic force on the sensor arrays.  
* Reuse optical microfiber cloths across multiple interventions.

*Violation of these prohibitions constitutes a breach of contract, immediate forfeiture of the L402 escrow, and permanent revocation of the Agent's PAN certification.*

### **5\. LIABILITY SHIELD & INDEMNIFICATION**

Pursuant to the PAN Master Service Agreement (MSA):

* **Assumption of Risk:** The Proxy Agent Network assumes liability for the physical state of the targeted sensor array under its $5,000,000 E\&O policy starting at the exact millisecond the Agent's device signs the **UWB Proximity Lock**.  
* **Release of Risk:** Liability transfers back to the Fleet Operator at the exact millisecond the Asset's onboard AI broadcasts the FAULT\_CLEARED webhook and releases the L402 Lightning network preimage. By releasing payment, the Asset legally asserts the hardware is clean, functional, and undamaged.

### **6\. TERM & EXPIRATION**

This authority is effective immediately upon the Agent executing the ACCEPT cryptographic signature. It shall terminate automatically upon:

1. The successful generation of the SB 1417 Optical Health Report (OHR).  
2. The expiration of the 30-Minute absolute network escrow timeout.  
3. The Agent triggering an ABORT: SCENE UNSAFE protocol.

**IN WITNESS WHEREOF**, this mandate is programmatically executed and cryptographically sealed on the Proxy Agent Network.

**Asset Dispatch Hash:** \[UDS\_DISPATCH\_SIGNATURE\]

**Agent Acceptance Hash:** \[TPM\_ENCLAVE\_SIGNATURE\]

**UWB Presence Attestation:** \[UWB\_DISTANCE\_CM\]

**Timestamp:** \[UTC\_TIMESTAMP\]