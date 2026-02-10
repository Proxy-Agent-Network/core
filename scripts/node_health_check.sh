#!/bin/bash

# PROXY PROTOCOL - NODE HEALTH CHECK v1.0
# "The Medic Script: Diagnose your node in 5 seconds."
# ----------------------------------------------------
# Usage: ./node_health_check.sh

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

echo "[*] Starting Diagnostics..."
echo "--------------------------------"
sleep 1

# 1. Check TPM Hardware
echo -n "[?] Hardware Root of Trust (TPM 2.0)... "
if [ -c /dev/tpm0 ]; then
    echo -e "${GREEN}DETECTED${NC}"
else
    echo -e "${RED}FAIL${NC}"
    echo "    -> CRITICAL: /dev/tpm0 not found. Is the Infineon module seated correctly?"
fi

# 2. Check Docker Container Status
echo -n "[?] Proxy Node Container... "
if docker ps | grep -q proxy_physical_node; then
    echo -e "${GREEN}RUNNING${NC}"
else
    echo -e "${RED}STOPPED${NC}"
    echo "    -> Try running: docker-compose up -d"
fi

# 3. Check LND Connection (Mock check for process)
echo -n "[?] Lightning Network Daemon... "
if pgrep -x "lnd" > /dev/null; then
    echo -e "${GREEN}ACTIVE${NC}"
else
    echo -e "${YELLOW}WARNING${NC} (Process not found)"
    echo "    -> Ensure LND is running if you are a routing node."
fi

# 4. Check Internet Connectivity
echo -n "[?] Network Latency (8.8.8.8)... "
ping -c 1 -W 1 8.8.8.8 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}ONLINE${NC}"
else
    echo -e "${RED}OFFLINE${NC}"
    echo "    -> Check your ethernet/wifi connection."
fi

echo "--------------------------------"
echo "Diagnostic Complete."
