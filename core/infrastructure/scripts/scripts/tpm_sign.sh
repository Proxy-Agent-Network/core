#!/bin/bash

# PROXY PROTOCOL - TPM SIGNING UTILITY (v1)
# Wrapper for tpm2_sign to generate hardware proofs.
# ----------------------------------------------------
# Usage: ./tpm_sign.sh <input_file> <output_signature>

IDENTITY_HANDLE="0x81010002" # Standard AK Handle for Proxy Nodes

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <output_signature>"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_FILE=$2

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found."
    exit 1
fi

echo "[*] Requesting signature from Infineon TPM..."
echo "    -> Key Handle: $IDENTITY_HANDLE"
echo "    -> Hash Algo:  SHA256"

# Execute Signing
# -c: Key Context/Handle
# -g: Hash Algorithm
# -o: Output Signature
# -f: Format (plain/tss)
if tpm2_sign -c $IDENTITY_HANDLE -g sha256 -o "$OUTPUT_FILE" "$INPUT_FILE"; then
    echo "✅ Signature generated: $OUTPUT_FILE"
    exit 0
else
    echo "❌ Signing Failed. Is the TPM initialized?"
    exit 1
fi
