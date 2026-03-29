use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use ed25519_dalek::{PublicKey, Signature, Verifier};

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
    pub av_pubkey_hex: String, // 🟢 NEW: Bound to the specific AV that faulted
    pub state: EscrowState,
}

impl HodlContract {
    pub fn new(contract_id: String, payment_hash: String, amount_sats: u64, av_pubkey_hex: String) -> Self {
        Self {
            contract_id,
            payment_hash,
            amount_sats,
            av_pubkey_hex,
            state: EscrowState::Open,
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct EscrowManager {
    // Wrapped in Mutex for thread safety across the Python/Rust FFI boundary
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

    /// Creates a cryptographically locked HODL invoice for the bounty.
    pub fn create_contract(&self, contract_id: String, payment_hash: String, amount: u64, av_pubkey_hex: String) -> PyResult<String> {
        let contract = HodlContract::new(contract_id.clone(), payment_hash.clone(), amount, av_pubkey_hex);
        
        // 🟢 THE FIX: Safely map Mutex PoisonError to Python Exception to avoid FFI panics
        let mut store = self.contracts.lock().map_err(|_| PyValueError::new_err("Internal state lock corrupted."))?;
        
        if store.contains_key(&payment_hash) {
            return Err(PyValueError::new_err("FATAL: Contract with this payment hash already exists."));
        }
        
        store.insert(payment_hash.clone(), contract);
        Ok(format!("Contract {} securely locked for {} sats.", contract_id, amount))
    }

    /// Transitions contract from Open -> Accepted
    pub fn accept_contract(&self, payment_hash: String) -> PyResult<bool> {
        let mut store = self.contracts.lock().map_err(|_| PyValueError::new_err("Internal state lock corrupted."))?;
        let contract = store.get_mut(&payment_hash).ok_or_else(|| PyValueError::new_err("Contract not found."))?;

        if contract.state != EscrowState::Open {
            return Err(PyValueError::new_err("Contract must be Open to accept."));
        }
        
        contract.state = EscrowState::Accepted;
        Ok(true)
    }

    /// Transitions contract from Accepted -> InProgress
    pub fn begin_contract(&self, payment_hash: String) -> PyResult<bool> {
        let mut store = self.contracts.lock().map_err(|_| PyValueError::new_err("Internal state lock corrupted."))?;
        let contract = store.get_mut(&payment_hash).ok_or_else(|| PyValueError::new_err("Contract not found."))?;

        if contract.state != EscrowState::Accepted {
            return Err(PyValueError::new_err("Contract must be Accepted before transitioning to InProgress."));
        }
        
        contract.state = EscrowState::InProgress;
        Ok(true)
    }

    /// 🟢 THE FIX: Zero-Trust Settlement & Strict State Machine Enforcement
    /// The Oracle MUST provide a valid Ed25519 signature from the AV confirming the physical intervention 
    /// was successful before state can transition to Settled.
    pub fn settle_contract(&self, payment_hash: String, payload: String, signature_hex: String) -> PyResult<bool> {
        let mut store = self.contracts.lock().map_err(|_| PyValueError::new_err("Internal state lock corrupted."))?;
        
        let contract = match store.get_mut(&payment_hash) {
            Some(c) => c,
            None => return Err(PyValueError::new_err("Contract not found.")),
        };

        // 🟢 THE FIX: Enforce strict state machine transition
        if contract.state != EscrowState::InProgress {
            return Err(PyValueError::new_err("Contract must be InProgress before settlement."));
        }

        // 1. Decode AV Public Key
        let pubkey_bytes = hex::decode(&contract.av_pubkey_hex)
            .map_err(|_| PyValueError::new_err("Invalid AV public key hex format."))?;
            
        if pubkey_bytes.len() != 32 {
            return Err(PyValueError::new_err("AV public key must be exactly 32 bytes."));
        }
        
        let public_key = PublicKey::from_bytes(&pubkey_bytes)
            .map_err(|_| PyValueError::new_err("Malformed Ed25519 public key bytes."))?;

        // 2. Decode AV Signature
        let sig_bytes = hex::decode(&signature_hex)
            .map_err(|_| PyValueError::new_err("Invalid signature hex format."))?;
            
        if sig_bytes.len() != 64 {
            return Err(PyValueError::new_err("Signature must be exactly 64 bytes."));
        }
        
        let signature = Signature::from_bytes(&sig_bytes)
            .map_err(|_| PyValueError::new_err("Malformed Ed25519 signature bytes."))?;

        // 3. Cryptographic Verification
        match public_key.verify(payload.as_bytes(), &signature) {
            Ok(_) => {
                // Signature is mathematically sound. The AV agrees the job is done.
                contract.state = EscrowState::Settled;
                Ok(true)
            },
            Err(_) => {
                // Forged or tampered payload
                Ok(false)
            }
        }
    }
    
    /// Allows cancellation unless the contract is already settled
    pub fn cancel_contract(&self, payment_hash: String) -> PyResult<bool> {
        let mut store = self.contracts.lock().map_err(|_| PyValueError::new_err("Internal state lock corrupted."))?;
        let contract = store.get_mut(&payment_hash).ok_or_else(|| PyValueError::new_err("Contract not found."))?;

        if contract.state == EscrowState::Settled {
            return Err(PyValueError::new_err("Cannot cancel a settled contract."));
        }
        
        contract.state = EscrowState::Cancelled;
        Ok(true)
    }
    
    pub fn get_contract_state(&self, payment_hash: String) -> PyResult<String> {
        let store = self.contracts.lock().map_err(|_| PyValueError::new_err("Internal state lock corrupted."))?;
        match store.get(&payment_hash) {
            Some(c) => Ok(format!("{:?}", c.state)),
            None => Err(PyValueError::new_err("Contract not found.")),
        }
    }
}