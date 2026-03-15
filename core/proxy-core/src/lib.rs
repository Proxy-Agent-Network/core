use pyo3::prelude::*;

// 1. Tell the Rust compiler to include our separated modules
pub mod tpm_binding;
pub mod secure_memory;
pub mod economics; 

// 2. Import the hardened hardware enclave we just wrote
use tpm_binding::NodeHardware;

// 3. This is the master function that PyO3 uses to build the Python library
#[pymodule]
fn proxy_core(_py: Python, m: &PyModule) -> PyResult<()> {
    // We register our hardened class so Python can access it
    m.add_class::<NodeHardware>()?;
    
    Ok(())
}