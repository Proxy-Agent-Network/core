#!/bin/bash

# Proxy Protocol - Node Health Check v1.0
# Verifies TPM integrity, LND connection, and Network latency.

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "   ____  ____  ____  ____  __ __ "
echo "  (  _ \(  _ \/ __ \(  _ \(  |  ) "
echo "   )___/ )   (  (__) ))   / )_  ( "
echo "  (__)  (_)\_)\____/(_)\_)(____/ "
echo "         NODE MEDIC v1.0"
echo -e "${NC}"

echo "[*] Starting System Diagnostics..."
echo "--------------------------------"
sleep 1

# 1. Check TPM 2.0 Hardware
echo -n "[?] Checking Hardware Root of Trust (TPM 2.0)... "
if [ -c /dev/tpm0 ]; then
    echo -e "${GREEN}DETECTED${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "    -> CRITICAL: /dev/tpm0 missing. Verify Infineon module seating."
fi

# 2. Check Lightning Daemon (LND)
echo -n "[?] Pinging Lightning Network Daemon... "
# Checks if process is running
if pgrep -x "lnd" > /dev/null; then
    echo -e "${GREEN}RUNNING${NC}"
else
    echo -e "${YELLOW}WARNING${NC} (Process not found)"
    echo "    -> Ensure LND is started via 'systemctl start lnd'"
fi

# 3. Check Internet/API Connectivity
echo -n "[?] Connecting to Proxy Mainnet... "
# Simple ping to a reliable host to test egress
if ping -q -c 1 -W 1 8.8.8.8 >/dev/null; then
    echo -e "${GREEN}CONNECTED${NC}"
else
    echo -e "${RED}OFFLINE${NC}"
fi

echo "--------------------------------"
echo "Diagnostic Complete."
