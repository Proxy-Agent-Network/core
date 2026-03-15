use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use pyo3::prelude::*;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum EscrowState {
    Open,
    Accepted,
    InProgress,
    Settled,
    Cancelled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HodlContract {
    pub contract_id: String,
    pub payment_hash: String,
    pub amount_sats: u64,
    pub state: EscrowState,
}

impl HodlContract {
    pub fn new(amount: u64) -> Self {
        Self {
            contract_id: "mock_id".to_string(),
            payment_hash: "mock_hash".to_string(),
            amount_sats: amount,
            state: EscrowState::Open,
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct EscrowManager {
    // Wrapped in Mutex for thread safety across Python/Rust boundary
    contracts: Arc<Mutex<HashMap<String, HodlContract>>>,
}

#[pymethods]
impl EscrowManager {
    #[new]
    pub fn new() -> Self {
        Self {
            contracts: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn create_invoice(&self, amount: u64) -> String {
        let contract = HodlContract::new(amount);
        let mut store = self.contracts.lock().unwrap();
        store.insert(contract.payment_hash.clone(), contract.clone());
        format!("Invoice created for {} sats", amount)
    }
}