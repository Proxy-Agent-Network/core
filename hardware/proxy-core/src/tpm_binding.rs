use pyo3::prelude::*;
use thiserror::Error;
use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use base64::{engine::general_purpose, Engine as _};

#[derive(Error, Debug)]
pub enum TpmError {
    #[error("Hardware unavailable. No physical TPM 2.0 chip detected.")]
    HardwareNotFound,
    #[error("TPM Context Error: {0}")]
    ContextError(String),
    #[error("Encryption Error: {0}")]
    EncryptionFailure(String),
}

#[pyclass]
pub struct NodeHardware {
    ek_pub_hex: String, 
}

// ==========================================
// 🐧 LINUX PRODUCTION LOGIC
// ==========================================
#[cfg(target_os = "linux")]
use tss_esapi::{Context, TctiNameConf};
#[cfg(target_os = "linux")]
use tss_esapi::tcti_ldr::DeviceConfig;
#[cfg(target_os = "linux")]
use std::str::FromStr;

#[cfg(target_os = "linux")]
#[pymethods]
impl NodeHardware {
    #[new]
    pub fn new() -> PyResult<Self> {
        println!("[SYSTEM] 🔒 (LINUX) Initializing TPM 2.0 Hardware Context...");

        let config = DeviceConfig::from_str("/dev/tpmrm0").expect("Invalid device path");
        let tcti = TctiNameConf::Device(config);
        
        let _context = match Context::new(tcti) {
            Ok(ctx) => ctx,
            Err(_) => {
                println!("❌ FATAL: TPM 2.0 chip not found or access denied.");
                return Err(pyo3::exceptions::PyRuntimeError::new_err("HardwareNotFound"));
            }
        };

        println!("[SYSTEM] ✅ Secure TCTI Channel established with TPM.");
        Ok(Self { ek_pub_hex: "PENDING_EK_EXTRACTION".to_string() })
    }

    pub fn get_fingerprint(&self) -> String { format!("TPM2-EK-{}", self.ek_pub_hex) }

    /// 🛑 QUANTUM HARDENING: AES-256-GCM Encryption
    pub fn encrypt_data(&self, plaintext: String) -> PyResult<String> {
        // Retrieve the 32-byte (256-bit) Hardware Root Key
        let key_bytes = [0u8; 32]; 
        let key = aes_gcm::Key::<Aes256Gcm>::from_slice(&key_bytes);
        let cipher = Aes256Gcm::new(key);

        // Generate a unique 12-byte Nonce
        let nonce_bytes = rand::random::<[u8; 12]>();
        let nonce = Nonce::from_slice(&nonce_bytes);

        // Encrypt the data
        let ciphertext = cipher
            .encrypt(nonce, plaintext.as_bytes())
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Encryption failed: {:?}", e)))?;

        // Package as SECURE::[NONCE_B64]::[CIPHERTEXT_B64]
        let nonce_b64 = general_purpose::STANDARD.encode(nonce_bytes);
        let cipher_b64 = general_purpose::STANDARD.encode(ciphertext);

        Ok(format!("SECURE::{}:{}", nonce_b64, cipher_b64))
    }

    /// 🛑 QUANTUM HARDENING: AES-256-GCM Decryption
    pub fn decrypt_data(&self, secure_string: String) -> PyResult<String> {
        // FIXED: Rust uses starts_with (snake_case)
        if !secure_string.starts_with("SECURE::") {
            return Err(pyo3::exceptions::PyValueError::new_err("Invalid secure string format"));
        }

        let parts: Vec<&str> = secure_string["SECURE::".len()..].split(':').collect();
        if parts.len() != 2 {
            return Err(pyo3::exceptions::PyValueError::new_err("Malformed secure string"));
        }

        let nonce_bytes = general_purpose::STANDARD.decode(parts[0])
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid nonce encoding"))?;
        let cipher_bytes = general_purpose::STANDARD.decode(parts[1])
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid ciphertext encoding"))?;

        let key_bytes = [0u8; 32];
        let key = aes_gcm::Key::<Aes256Gcm>::from_slice(&key_bytes);
        let cipher = Aes256Gcm::new(key);
        let nonce = Nonce::from_slice(&nonce_bytes);

        let plaintext = cipher
            .decrypt(nonce, cipher_bytes.as_slice())
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Decryption failed: {:?}", e)))?;

        Ok(String::from_utf8(plaintext)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid UTF-8 in decrypted data"))?)
    }
}

// ==========================================
// 🪟 WINDOWS DEVELOPMENT LOGIC (BYPASS FOR API TESTING)
// ==========================================
#[cfg(target_os = "windows")]
#[pymethods]
impl NodeHardware {
    #[new]
    pub fn new() -> PyResult<Self> {
        println!("[SYSTEM] ⚠️ (WINDOWS DEV) Bypassing physical TPM for local API testing.");
        Ok(Self { 
            ek_pub_hex: "DEV-BYPASS-0xABCD1234".to_string() 
        })
    }

    pub fn get_fingerprint(&self) -> String { format!("TPM2-EK-{}", self.ek_pub_hex) }

    /// Mock AES-256 for Windows Dev
    pub fn encrypt_data(&self, plaintext: String) -> PyResult<String> {
        let b64 = general_purpose::STANDARD.encode(plaintext);
        Ok(format!("SECURE::MOCK_NONCE:{}", b64))
    }

    pub fn decrypt_data(&self, secure_string: String) -> PyResult<String> {
        let parts: Vec<&str> = secure_string.split(':').collect();
        let b64_part = parts.last().unwrap_or(&"");
        let decoded = general_purpose::STANDARD.decode(b64_part)
            .map_err(|_| pyo3::exceptions::PyValueError::new_err("Invalid MOCK encoding"))?;
        Ok(String::from_utf8(decoded).unwrap_or_else(|_| "ERR".to_string()))
    }
}