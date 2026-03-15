"""
secure_memory.py - Rust Bridge
------------------------------
This module now acts as a bridge to the 'proxy_core' Rust library.
It provides True Memory Encryption and automatic zeroization via the Rust Drop trait.
"""
import proxy_core

class SecureMemory:
    def __init__(self, data: str):
        """
        Initialize a SecurePayload in the Rust heap.
        The Python string 'data' should be discarded immediately after this call.
        """
        self._rust_payload = proxy_core.SecurePayload(data)

    def access(self) -> str:
        """
        Briefly decodes the data for usage.
        WARNING: The returned string is visible in Python memory. Use and discard.
        """
        return self._rust_payload.read_sensitive()

    def __del__(self):
        """
        When this Python object dies, the Rust struct is dropped,
        triggering the Zeroize trait to wipe the RAM.
        """
        # Python's GC will eventually clean this up, calling the Rust destructor.
        pass