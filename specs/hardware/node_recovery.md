# Node Recovery & Re-Certification Protocol

**Applicability:** Tier 2 & Tier 3 Physical Nodes  
**Incident Type:** Accidental Tamper Trip / Chassis Intrusion

---

## 1. The "Zero-Recovery" Principle
To maintain the integrity of the Hardware Root of Trust, private keys wiped by the TPM during a tamper event are mathematically unrecoverable. There is no "backup seed" or "admin override." This is a feature, not a bug.

**If your Node has been "bricked" due to accidental intrusion, you must treat it as a factory-fresh device.**

---

## 2. The Re-Certification Workflow

### Step A: Physical Inspection
Before attempting to reconnect, verify the physical integrity of the chassis.
* Ensure the GPIO plunger switch is reset.
* Verify the case is sealed with new tamper-evident holographic tape (Rule 4.2).

### Step B: TPM Factory Reset
You must clear the "Owner Hierarchy" of the TPM to allow new key generation.

```bash
# On the Raspberry Pi terminal
sudo tpm2_clear
sudo systemctl restart proxy-node
```

### Step C: The "Lost Node" Claim
Since your old Node ID (Public Key A) is dead, you must inform the network to transfer your stake (if eligible) to your new Node ID (Public Key B).

1.  **Generate New Keys:** The Node will automatically generate Public Key B on startup.
2.  **Submit Claim:** Log into the Partner Dashboard and select "Report Broken Node."
3.  **Link Identities:** Sign a message with your **Human Identity Key** (via the Proxy Mobile App) linking Key A (Dead) to Key B (New).

---

## 3. Probation Period
Re-certified nodes are placed on a **7-day Probation period**:

* **Traffic:** Capped at 10% of normal volume.
* **Monitoring:** All tasks require double-verification (a second node checks your work).
* **Reputation:** Your previous reputation score is restored at 90% (a 10% penalty for operational instability).

---

## 4. Hardware Replacement
If the TPM itself was damaged during the incident, the entire compute module must be replaced. The old unit should be e-cycled according to local environmental regulations.
