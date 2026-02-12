# Physical Node Setup Guide (v1.0)

**Target Hardware:** Raspberry Pi 5 (8GB)  
**OS:** Ubuntu Server 24.04 LTS (64-bit)

This guide walks you through provisioning a **"Mailroom Node"** to accept physical mail tasks from the Proxy Network.

---

## 1. System Dependencies

First, update your package repositories and install the required TPM and OCR libraries.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    tpm2-tools \
    libtpm2-pkcs11-1 \
    tesseract-ocr \
    libzbar0 \
    python3-pip \
    git
```

---

## 2. Install the Node Software

Clone the repository and install the daemon.

```bash
git clone [https://github.com/Proxy-Agent-Network/core.git](https://github.com/Proxy-Agent-Network/core.git)
cd core/node
pip3 install -r requirements.txt
```

---

## 3. TPM Initialization (The "Binding" Ceremony)

This step generates your **Node Identity Key** inside the secure hardware element.

> [!CAUTION]
> **WARNING:** This process is irreversible. Once generated, the private key cannot be exported or backed up. If you lose the physical device, you lose the reputation attached to this Node ID.

```bash
# Initialize the TPM
sudo tpm2_startup -c

# Generate Primary Key (Endorsement Hierarchy)
sudo tpm2_createprimary -C e -g sha256 -G rsa -c primary.ctx

# Output Public Key (This is your Node ID)
sudo tpm2_readpublic -c primary.ctx -o node_identity.pub
```

---

## 4. Connect to Lightning

Your node needs to "watch" the blockchain for incoming HODL invoices.

1.  **Edit the config file:** `nano config.yaml`
2.  **Set your LND RPC endpoint** (or use our hosted gateway for Tier 1 nodes).

```yaml
lnd_rpc: "127.0.0.1:10009"
macaroon_path: "/home/proxy/.lnd/data/chain/bitcoin/mainnet/readonly.macaroon"
```

---

## 5. Start the Daemon

Launch the node and verify the connection to the Proxy Network.

```bash
python3 node_daemon.py --start
```

**Expected Output:**
```text
[INFO] Node Online. Identity: <node_identity_hash>
[INFO] Lightning LND Connected.
[INFO] Listening for tasks...
```
