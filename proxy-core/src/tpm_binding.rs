use thiserror::Error;
use pyo3::prelude::*;

#[derive(Error, Debug)]
pub enum TpmError {
    #[error("Hardware unavailable")]
    HardwareNotFound,
    #[error("TPM Error: {0}")]
    ContextError(String),
}

// --- MOCK IMPLEMENTATION (Windows/Dev) ---
#[pyclass]
pub struct TpmBinding;

#[pymethods]
impl TpmBinding {
    #[new]
    pub fn new() -> Self {
        println!("[WARN] Running with MOCK TPM (Development Mode)");
        Self {}
    }

    pub fn check_availability(&self) -> bool {
        true
    }

    pub fn get_node_fingerprint(&self) -> String {
        "MOCK_FINGERPRINT_DEV_001".to_string()
    }

    pub fn generate_attestation_quote(&self, nonce: &str) -> String {
        format!("MOCK_QUOTE::{}_SIGNED", nonce)
    }
}