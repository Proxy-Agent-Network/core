use pyo3::prelude::*;

// Internal modules
mod secure_memory;
mod tpm_binding;
mod economics;

use secure_memory::SecurePayload;
use tpm_binding::TpmBinding;
use economics::hodl_escrow::EscrowManager;

/// The "proxy_core" Python module.
#[pymodule]
fn proxy_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    
    // 1. Export Secure Memory
    m.add_class::<SecurePayload>()?;

    // 2. Export TPM Binding
    m.add_class::<TpmBinding>()?;

    // 3. Export Financial Logic (Now Uncommented!)
    m.add_class::<EscrowManager>()?; 

    Ok(())
}