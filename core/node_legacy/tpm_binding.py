import proxy_core

class NodeHardware:
    def __init__(self):
        # UPDATED: Use the correct class name exposed by Rust
        try:
            self._rust = proxy_core.NodeHardware()
        except AttributeError:
            # Fallback in case of old binary, but we expect NodeHardware now
            self._rust = proxy_core.TpmBinding()

    def get_fingerprint(self):
        return self._rust.get_fingerprint()

    def encrypt_data(self, plaintext):
        # Maps Python call -> Rust Core
        return self._rust.encrypt_data(plaintext)

    def decrypt_data(self, ciphertext):
        # Maps Python call -> Rust Core
        return self._rust.decrypt_data(ciphertext)