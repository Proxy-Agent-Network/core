#!/bin/bash

# PROXY PROTOCOL - TAMPER RESPONSE v1.0
# "SCORCHED EARTH" PROTOCOL
# ----------------------------------------------------
# TRIGGERED BY: GPIO Interrupt (Chassis Open) or Critical Security Event
# EFFECT: Irreversible data loss.

LOG_FILE="/var/log/proxy_tamper.log"
CONFIG_DIR="/app/config"
SECRETS_DIR="/app/secrets"

echo "[$(date -u)] 🚨 CRITICAL: TAMPER EVENT DETECTED. INITIATING WIPE." >> $LOG_FILE

# 1. Kill the Node Daemon immediately to stop new signings
echo "[!] Killing Proxy Node process..."
pkill -9 -f "node_daemon.py"

# 2. The Nuclear Option: Clear the TPM
# This removes the Primary Seed, making all derived keys permanently unusable.
if command -v tpm2_clear >/dev/null; then
    echo "[!] Wiping Hardware Root of Trust..."
    # Platform Auth is usually empty by default on Pis, or set via ENV
    tpm2_clear -c p
    echo "[$(date -u)] TPM Hierarchy Cleared." >> $LOG_FILE
else
    echo "[ERROR] tpm2-tools not found! Cannot wipe hardware keys." >> $LOG_FILE
fi

# 3. Shred Local Secrets (Overwrite 3x then delete)
echo "[!] Shredding local configuration files..."
if [ -d "$SECRETS_DIR" ]; then
    find $SECRETS_DIR -type f -exec shred -u -n 3 -z {} \;
fi

if [ -f "$CONFIG_DIR/config.yaml" ]; then
    shred -u -n 3 -z "$CONFIG_DIR/config.yaml"
fi

# 4. Broadcast "Dying Breath" (Optional)
# Try to tell the network we are compromised (Best Effort)
# curl -X POST https://api.proxyprotocol.com/v1/nodes/tamper_alert \
#      -d '{"node_id": "LOCAL_ID", "reason": "chassis_intrusion"}' \
#      --max-time 2 > /dev/null 2>&1

# 5. Flush RAM and Halt
echo "[!] Syncing disks and halting..."
sync
echo 1 > /proc/sys/kernel/sysrq
echo o > /proc/sysrq-trigger # Immediate power off
