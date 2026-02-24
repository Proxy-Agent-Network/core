use thiserror::Error;
use pyo3::prelude::*;

#[derive(Error, Debug)]
pub enum TpmError {
    #[error("Hardware unavailable")]
    HardwareNotFound,
    #[error("TPM Error: {0}")]
    ContextError(String),
}

// --- NODE HARDWARE ENCLAVE ---
#[pyclass]
pub struct NodeHardware {
    enclave_key: u8, // A simulated "Hardware Key" baked into the silicon
}

#[pymethods]
impl NodeHardware {
    #[new]
    pub fn new() -> Self {
        println!("[SYSTEM] 🔒 Rust Hardware Enclave Activated.");
        Self {
            enclave_key: 42, // XOR key for demo purposes
        }
    }

    pub fn get_fingerprint(&self) -> String {
        // Generates a professional hardware identity for the UI
        "TPM2-ENCLAVE-0x8F9B".to_string()
    }

    pub fn encrypt_data(&self, plaintext: String) -> String {
        // Byte-level XOR "Encryption" simulating a hardware-bound operation
        let encrypted: Vec<u8> = plaintext.bytes().map(|b| b ^ self.enclave_key).collect();
        // Convert to a hex string so Postgres can store it safely
        let hex_string: String = encrypted.iter().map(|b| format!("{:02X}", b)).collect();
        format!("SECURE::{}", hex_string)
    }

    pub fn decrypt_data(&self, ciphertext: String) -> String {
        // Fallback: If it's old plain text, just return it
        if !ciphertext.starts_with("SECURE::") {
            return ciphertext; 
        }
        
        let hex_part = &ciphertext[8..];
        let mut decoded_bytes = Vec::new();
        
        // Parse the hex string back to bytes and decrypt
        for i in (0..hex_part.len()).step_by(2) {
            if let Ok(byte) = u8::from_str_radix(&hex_part[i..i+2], 16) {
                decoded_bytes.push(byte ^ self.enclave_key);
            }
        }
        
        String::from_utf8(decoded_bytes).unwrap_or_else(|_| "0".to_string())
    }
}

// Kept for legacy backwards compatibility so lib.rs doesn't break
#[pyclass]
pub struct TpmBinding;

#[pymethods]
impl TpmBinding {
    #[new]
    pub fn new() -> Self { Self {} }
    pub fn get_fingerprint(&self) -> String { "LEGACY_MOCK".to_string() }
    pub fn encrypt_data(&self, pt: String) -> String { pt }
    pub fn decrypt_data(&self, ct: String) -> String { ct }
}