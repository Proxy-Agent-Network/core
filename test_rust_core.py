import proxy_core
import time

print(f"✅ Protocol Loaded: {proxy_core.__name__}")

# 1. Test Secure Memory (Zeroize)
secret = proxy_core.SecurePayload("Top Secret Launch Codes: 8877")
print(f"🔐 Memory Enclave: {secret.read_sensitive()}")

# 2. Test Hardware Binding
tpm = proxy_core.TpmBinding()
if tpm.check_availability():
    print(f"🛡️  TPM Status: ONLINE")
    print(f"🆔 Node Fingerprint: {tpm.get_node_fingerprint()}")
    print(f"📜 Attestation Quote: {tpm.generate_attestation_quote('nonce_99')}")

# 3. Test Financial Rails
escrow = proxy_core.EscrowManager()
invoice = escrow.create_invoice(5000) # 5,000 Sats
print(f"⚡ Settlement Layer: {invoice}")
