"""
tpm_binding.py - Rust Bridge
----------------------------
Binds directly to the TCG TSS stack via Rust FFI.
Prevents Time-of-Check Time-of-Use (TOCTOU) attacks.
"""
import proxy_core
import logging

logger = logging.getLogger(__name__)

class NodeHardware:
    def __init__(self):
        self._rust_tpm = proxy_core.TpmBinding()
        # On Windows (Mock Mode), this will always return True
        if not self._rust_tpm.check_availability():
            logger.warning("⚠️ Real TPM not found. Running in EMULATION mode.")

    def get_fingerprint(self) -> str:
        """Returns the unique hardware fingerprint (EK Public Key Hash)."""
        return self._rust_tpm.get_node_fingerprint()

    def sign_attestation(self, nonce: str) -> str:
        """
        Generates a signed quote over PCRs 0, 1, 7.
        The private key never leaves the hardware (or Rust enclave).
        """
        return self._rust_tpm.generate_attestation_quote(nonce)