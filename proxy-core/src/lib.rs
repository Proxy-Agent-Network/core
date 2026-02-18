use pyo3::prelude::*;
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce}; 
// UPDATED: Added 'AeadCore' to this import line to fix the compilation error
use chacha20poly1305::aead::{Aead, AeadCore, KeyInit, OsRng};
use base64::{Engine as _, engine::general_purpose};
use sha2::{Sha256, Digest};

#[pyclass]
struct NodeHardware {
    fingerprint: String,
    secret_key: [u8; 32], // Stored in "hardware" memory
}

#[pymethods]
impl NodeHardware {
    #[new]
    fn new() -> Self {
        // In a real scenario, we would read the actual TPM chip here.
        let fingerprint = "MOCK_FINGERPRINT_DEV_001".to_string();
        
        // 1. DERIVE KEY: Hash the fingerprint to create a stable key
        // This ensures the same node always generates the same key
        let mut hasher = Sha256::new();
        hasher.update(fingerprint.as_bytes());
        let result = hasher.finalize();
        
        let mut key_bytes = [0u8; 32];
        key_bytes.copy_from_slice(&result);

        NodeHardware { 
            fingerprint, 
            secret_key: key_bytes 
        }
    }

    fn get_fingerprint(&self) -> PyResult<String> {
        Ok(self.fingerprint.clone())
    }

    /// Encrypts a string using ChaCha20-Poly1305
    fn encrypt_data(&self, plaintext: String) -> PyResult<String> {
        let key = Key::from_slice(&self.secret_key);
        let cipher = ChaCha20Poly1305::new(key);
        
        // Generate a random 96-bit nonce (never reuse nonces!)
        // This function requires the 'AeadCore' trait to be in scope
        let nonce = ChaCha20Poly1305::generate_nonce(&mut OsRng); 
        
        match cipher.encrypt(&nonce, plaintext.as_bytes()) {
            Ok(ciphertext) => {
                // Pack Nonce + Ciphertext together
                let mut packet = nonce.to_vec();
                packet.extend(ciphertext);
                
                // Return as Base64 string for safe database storage
                Ok(general_purpose::STANDARD.encode(packet))
            },
            Err(_) => Ok("ERR_ENCRYPTION_FAILED".to_string())
        }
    }

    /// Decrypts a Base64 blob back to text
    fn decrypt_data(&self, blob: String) -> PyResult<String> {
        // 1. Decode Base64
        let packet = match general_purpose::STANDARD.decode(blob) {
            Ok(d) => d,
            Err(_) => return Ok("ERR_INVALID_BASE64".to_string()),
        };

        // Validation: Must be at least 12 bytes (nonce size)
        if packet.len() < 12 {
            return Ok("ERR_CORRUPT_DATA".to_string());
        }

        // 2. Split Nonce and Ciphertext
        let (nonce_bytes, ciphertext) = packet.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);
        
        let key = Key::from_slice(&self.secret_key);
        let cipher = ChaCha20Poly1305::new(key);

        // 3. Decrypt
        match cipher.decrypt(nonce, ciphertext) {
            Ok(plaintext) => Ok(String::from_utf8(plaintext).unwrap_or("ERR_UTF8".to_string())),
            Err(_) => Ok("ACCESS_DENIED_INVALID_KEY".to_string())
        }
    }
}

#[pymodule]
fn proxy_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<NodeHardware>()?;
    Ok(())
}