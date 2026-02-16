# Node Recovery & Re-Certification Protocol

| Applicability | Incident Type |
| :--- | :--- |
| **Tier 2 & Tier 3 Physical Nodes** | Accidental Tamper Trip / Chassis Intrusion / TPM Corruption |

---

## 1. The "Zero-Recovery" Principle
To maintain the integrity of the Hardware Root of Trust, private keys wiped by the TPM during a tamper event are **mathematically unrecoverable**. There is no "backup seed" or "admin override." This is a feature, not a bug.

> [!CAUTION]
> If your Node has been "bricked" due to accidental intrusion or TPM failure (`PX_400`), you must treat it as a factory-fresh device.

---

## 2. The Re-Certification Workflow

### Step A: Physical Inspection
Before attempting to reconnect, verify the physical integrity of the chassis.
* **GPIO Reset:** Ensure the GPIO plunger switch is physically reset.
* **Security Seal:** Verify the case is sealed with new tamper-evident holographic tape (Rule 4.2).

### Step B: TPM Factory Reset
You must clear the "Owner Hierarchy" of the TPM to allow new key generation. This requires root access on the Raspberry Pi.

```bash
# On the Raspberry Pi terminal
sudo systemctl stop proxy-node
sudo tpm2_clear
sudo systemctl start proxy-node
```

**Note:** The daemon will detect the empty TPM and automatically trigger the **Key Generation Ceremony** on startup.

### Step C: The "Lost Node" Claim
Since your old Node ID (Public Key A) is dead, you must inform the network to transfer your stake (if eligible) to your new Node ID (Public Key B).

1. **Generate New Keys:** The Node will automatically generate Public Key B.
2. **Submit Claim:** Log into the Partner Dashboard and select "Report Broken Node."
3. **Link Identities:** Sign a message with your Human Identity Key (from your mobile app) linking Key A (Dead) to Key B (New).

---

## 3. Probation Period
Re-certified nodes are placed on a **7-day Probation** to ensure stability.

* **Traffic:** Capped at 10% of normal volume.
* **Monitoring:** All tasks require **double-verification** (a second node checks your work).
* **Reputation:** Your previous reputation score is restored at 90% (10% penalty for operational instability).

---

## 4. Hardware Replacement
If the TPM module itself was damaged (e.g., voltage spike), the Infineon module or the entire compute unit must be replaced. The old unit should be e-cycled securely to ensure no residual data remains.
