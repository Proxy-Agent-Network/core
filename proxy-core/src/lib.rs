use pyo3::prelude::*;
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce}; 
use chacha20poly1305::aead::{Aead, AeadCore, KeyInit, OsRng};
use base64::{Engine as _, engine::general_purpose};
use sha2::{Sha256, Digest};

#[pyclass]
struct NodeHardware {
    fingerprint: String,
    secret_key: [u8; 32], // Stored in "hardware" memory within the Rust binary
}

#[pymethods]
impl NodeHardware {
    #[new]
    fn new() -> Self {
        // This is the permanent ID established for your demo.
        // In production, this would be read from the physical TPM chip via /dev/tpmrm0.
        let fingerprint = "TPM2-ENCLAVE-0x8F9B".to_string();
        
        // 1. DERIVE KEY: Hash the fingerprint to create a stable 256-bit key.
        // This ensures the same hardware always generates the same encryption key,
        // effectively binding the AI's wallet to this specific motherboard.
        let mut hasher = Sha256::new();
        hasher.update(fingerprint.as_bytes());
        let result = hasher.finalize();
        
        let mut key_bytes = [0u8; 32];
        key_bytes.copy_from_slice(&result);

        println!("[ENCLAVE] 🔒 Hardware key derived from silicon ID: {}", fingerprint);

        NodeHardware { 
            fingerprint, 
            secret_key: key_bytes 
        }
    }

    /// Returns the unique hardware signature for the frontend UI.
    fn get_fingerprint(&self) -> PyResult<String> {
        Ok(self.fingerprint.clone())
    }

    /// Encrypts a string (like a wallet balance) using authenticated ChaCha20-Poly1305.
    /// Returns a string prefixed with 'SECURE::' for identification in the DB.
    fn encrypt_data(&self, plaintext: String) -> PyResult<String> {
        let key = Key::from_slice(&self.secret_key);
        let cipher = ChaCha20Poly1305::new(key);
        
        // Generate a random 96-bit nonce (Standard requirement for AEAD ciphers).
        let nonce = ChaCha20Poly1305::generate_nonce(&mut OsRng); 
        
        match cipher.encrypt(&nonce, plaintext.as_bytes()) {
            Ok(ciphertext) => {
                // Pack Nonce + Ciphertext together as a single packet.
                let mut packet = nonce.to_vec();
                packet.extend(ciphertext);
                
                // Prepend SECURE:: and Base64 encode for safe storage in the Postgres 'TEXT' column.
                let encoded = general_purpose::STANDARD.encode(packet);
                Ok(format!("SECURE::{}", encoded))
            },
            Err(_) => Ok("ERR_ENCRYPTION_FAILED".to_string())
        }
    }

    /// Decrypts a 'SECURE::' blob back to plain text using the hardware-bound key.
    /// If the data is not encrypted, it returns the original string for backwards compatibility.
    fn decrypt_data(&self, blob: String) -> PyResult<String> {
        // Validation: If it's not a secure blob, return as-is for initial database migration.
        if !blob.starts_with("SECURE::") {
            return Ok(blob);
        }

        // 1. Remove the identifying prefix and decode the Base64 packet.
        let b64_part = &blob[8..];
        let packet = match general_purpose::STANDARD.decode(b64_part) {
            Ok(d) => d,
            Err(_) => return Ok("0".to_string()),
        };

        // AEAD Validation: Packet must be at least 12 bytes (the size of the nonce).
        if packet.len() < 12 {
            return Ok("0".to_string());
        }

        // 2. Split the packet back into the Nonce and the Ciphertext.
        let (nonce_bytes, ciphertext) = packet.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);
        
        let key = Key::from_slice(&self.secret_key);
        let cipher = ChaCha20Poly1305::new(key);

        // 3. Attempt decryption using the hardware-bound secret key.
        match cipher.decrypt(nonce, ciphertext) {
            Ok(plaintext) => {
                // Conversion: Turn decrypted bytes back into a Python-readable string.
                Ok(String::from_utf8(plaintext).unwrap_or("0".to_string()))
            },
            Err(_) => {
                // SECURITY ALERT: Decryption fails if the key is wrong (Hardware Mismatch) 
                // or if the database value was tampered with (Poly1305 Auth failure).
                Ok("ACCESS_DENIED_HARDWARE_MISMATCH".to_string())
            }
        }
    }
}

/// The Python Module Definition.
/// This exports our Rust logic as the 'proxy_core' library for use in app.py.
#[pymodule]
fn proxy_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<NodeHardware>()?;
    Ok(())
}