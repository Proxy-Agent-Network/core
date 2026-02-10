# Physical Node Reference Design (v1)

**Status:** Alpha (Testing in Arizona/Singapore)  
**Type:** Reference Implementation

The Proxy Protocol "Mailroom Node" is a standardized hardware configuration for high-volume Physical Proxies. It allows for the automated ingestion, scanning, and shredding of physical mail on behalf of AI Agents.

---

## 1. Hardware Bill of Materials (BOM)

To run a verified Mailroom Node, the following hardware is required to meet the `proof_of_physicality` cryptographic standards.

| Component | Specification | Purpose |
| :--- | :--- | :--- |
| **Compute** | Raspberry Pi 5 (8GB RAM) | Local OCR and Encryption |
| **Camera** | Sony IMX708 (12MP, Autofocus) | High-res document capture |
| **Security** | Infineon OPTIGA™ TPM 2.0 | Private Key storage (Hardware Root of Trust) |
| **Connectivity** | LoRaWAN Module (Optional) | Proof of Location (Helium/TTN) |

---

## 2. The Workflow

1.  **Ingest:** Physical mail arrives at the Node's address.
2.  **Scan:** The operator places the envelope under the camera.
3.  **OCR:** The Node locally processes the image (Tesseract/OCR) to extract metadata (Sender, Date).
4.  **Signal:** The Node broadcasts a `mail_received` event to the Agent via Lightning Network.
5.  **Action:** The Agent replies with `OPEN`, `FORWARD`, or `SHRED`.

---

## 3. Security Architecture

* **Air-Gapped Keys:** The Node's signing key never leaves the TPM module.
* **Local Processing:** OCR happens on-device. No raw images are uploaded to the cloud unless explicitly requested by the Agent.
* **Anti-Tamper:** The reference casing includes a chassis intrusion switch that wipes the keys if the hardware is tampered with or opened.

---

## 4. Certification

Partners wishing to manufacture compatible nodes must submit a prototype to the **Proxy Foundation** for certification. Use the tag `[HARDWARE]` when opening a GitHub issue to begin the process.
