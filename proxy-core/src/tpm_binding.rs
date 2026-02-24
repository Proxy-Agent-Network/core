use pyo3::prelude::*;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum TpmError {
    #[error("Hardware unavailable. No physical TPM 2.0 chip detected.")]
    HardwareNotFound,
    #[error("TPM Context Error: {0}")]
    ContextError(String),
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
#[pymethods]
impl NodeHardware {
    #[new]
    pub fn new() -> PyResult<Self> {
        println!("[SYSTEM] 🔒 (LINUX) Initializing TPM 2.0 Hardware Context...");

        let tcti = TctiNameConf::Device("/dev/tpmrm0".to_string());
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
}

// ==========================================
// 🪟 WINDOWS DEVELOPMENT LOGIC
// ==========================================
#[cfg(target_os = "windows")]
#[pymethods]
impl NodeHardware {
    #[new]
    pub fn new() -> PyResult<Self> {
        println!("[SYSTEM] ⚠️ (WINDOWS DEV) TPM 2.0 Physical pass-through blocked by OS.");
        println!("❌ FATAL: Cannot access Linux physical /dev/tpmrm0 on Windows platform.");
        Err(pyo3::exceptions::PyRuntimeError::new_err("HardwareNotFound: Windows Environment"))
    }

    pub fn get_fingerprint(&self) -> String { format!("TPM2-EK-{}", self.ek_pub_hex) }
}