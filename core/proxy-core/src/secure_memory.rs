use zeroize::{Zeroize, ZeroizeOnDrop};
use pyo3::prelude::*;
use std::fmt;

/// A container for sensitive task instructions that must be wiped from RAM.
#[pyclass]
#[derive(Zeroize, ZeroizeOnDrop)]
pub struct SecurePayload {
    content: Vec<u8>,
}

#[pymethods]
impl SecurePayload {
    #[new]
    pub fn new(data: String) -> Self {
        Self {
            content: data.into_bytes(),
        }
    }

    pub fn read_sensitive(&self) -> String {
        String::from_utf8_lossy(&self.content).to_string()
    }
}

impl fmt::Debug for SecurePayload {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "SecurePayload(***REDACTED***)")
    }
}