# PROXY PROTOCOL - TPM FACTORY RESET (v1)
# DANGER: This is destructive. It creates the "Dead Node" state.
# ----------------------------------------------------
# Usage: sudo ./tpm_wipe.sh

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)."
  exit 1
fi

echo "⚠️  WARNING: THIS WILL WIPE THE TPM HIERARCHY."
echo "    - All private keys will be lost forever."
echo "    - This node identity will be effectively dead."
echo "    - Use this ONLY for recovery or decomissioning."
echo ""
read -p "Are you sure? Type 'DELETE' to confirm: " -r
echo ""

if [ "$REPLY" != "DELETE" ]; then
    echo "Aborted."
    exit 0
fi

echo "[*] Stopping Node Daemon..."
systemctl stop proxy-node

echo "[*] Sending TPM2_Clear command..."
# platform auth is usually empty by default on RPi
tpm2_clear -c p

if [ $? -eq 0 ]; then
    echo "✅ TPM Wiped. Hierarchy is empty."
    echo "    -> You must now run the Binding Ceremony to create a new identity."
else
    echo "❌ Wipe Failed. Check platform auth/lockout status."
    exit 1
fi
