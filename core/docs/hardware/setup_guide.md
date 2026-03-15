# **Proxy Agent Network (PAN) | Sector Edge Node Setup Guide**

**Status:** Active (Mesa Pilot)

**Version:** 2026.1.0

**Target Hardware:** Sector Edge Server (ARM64 / x86\_64)

**OS:** Ubuntu Server 24.04 LTS (64-bit)

This guide walks you through provisioning a **Sector Edge Node**. This node acts as the local brain for a specific Operational Design Domain (ODD), such as MESA\_AZ\_01. It manages local Vanguard Agent routing, ingests Fleet UDS webhooks, and holds the L402 Lightning network escrows.

## **1\. System Dependencies**

First, update your package repositories and install the required TPM, Redis (for idempotency locks), and Rust compilation libraries.

sudo apt update && sudo apt upgrade \-y  
sudo apt install \-y \\  
    tpm2-tools \\  
    libtpm2-pkcs11-1 \\  
    redis-server \\  
    build-essential \\  
    pkg-config \\  
    libssl-dev \\  
    git \\  
    curl

\# Install Rust Toolchain  
curl \--proto '=https' \--tlsv1.2 \-sSf \[https://sh.rustup.rs\](https://sh.rustup.rs) | sh  
source $HOME/.cargo/env

## **2\. Install the Gateway Software**

Clone the PAN Core repository and compile the high-throughput Rust gateway daemon.

git clone \[https://github.com/Proxy-Agent-Network/core.git\](https://github.com/Proxy-Agent-Network/core.git)  
cd core/src/L402-Gateway  
cargo build \--release

## **3\. TPM Initialization (The Sector Binding Ceremony)**

This step generates your **Sector Identity Key** inside the server's secure hardware element (TPM 2.0). This key is used to cryptographically sign outbound webhooks (e.g., mission.orp\_completed) sent to Fleet Partners like Waymo and Zoox.

\[\!CAUTION\]

**WARNING:** This process is irreversible. Once generated, the private key cannot be exported or backed up. If the physical server's motherboard is destroyed, the Sector Identity is permanently lost and must be re-provisioned from PAN Command.

\# Initialize the Server TPM  
sudo tpm2\_startup \-c

\# Generate Primary Key (Endorsement Hierarchy)  
sudo tpm2\_createprimary \-C e \-g sha256 \-G rsa \-c sector\_primary.ctx

\# Output Public Key (This is your Sector Gateway ID)  
sudo tpm2\_readpublic \-c sector\_primary.ctx \-o sector\_identity.pub

## **4\. Lightning Network Escrow (LND) Configuration**

Your Sector Node needs to connect to the Lightning Network to generate HODL invoices and escrow the Fleet Operators' Satoshi bounties.

1. **Edit the config file:** nano config.toml  
2. **Set your LND RPC endpoint**, Redis cache, and active Geohash.

\[network\]  
sector\_id \= "MESA\_AZ\_01"  
environment \= "production"

\[lnd\]  
rpc\_endpoint \= "127.0.0.1:10009"  
macaroon\_path \= "/home/pan-admin/.lnd/data/chain/bitcoin/mainnet/admin.macaroon"  
tls\_cert\_path \= "/home/pan-admin/.lnd/tls.cert"

\[routing\]  
redis\_url \= "redis://127.0.0.1:6379"  
idempotency\_window\_secs \= 900  \# 15 Minute SLA lock

## **5\. Start the Sector Daemon**

Launch the node and verify the connection to the PAN Identity Registry and Fleet Treasuries.

./target/release/pan-gateway \--config ./config.toml

**Expected Output:**

\[INFO\] Sector Node Online. Geohash: MESA\_AZ\_01  
\[INFO\] TPM Signature Module: ACTIVE. Identity: \<sector\_identity\_hash\>  
\[INFO\] L402 Lightning Escrow (LND): CONNECTED. Inbound Liquidity: 5.2 BTC  
\[INFO\] Redis Idempotency Cache: ONLINE.  
\[INFO\] Listening for Fleet UDS webhooks on port 8080...  
