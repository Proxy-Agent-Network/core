use serde::{Deserialize, Serialize};
use anyhow::{Context, Result};
use chrono::Utc;

// --- DATA STRUCTURES ---
#[derive(Serialize, Deserialize, Debug)]
struct AttestationResponse {
    node_id: String,
    timestamp: String,
    pcr_hash: String,
    signature: String,
    hardware_secured: bool,
    provider: String,
}

// --- INTERFACE ---
trait TpmProvider {
    fn get_node_id(&self) -> Result<String>;
    fn sign_quote(&self, nonce: &str) -> Result<(String, String)>;
    fn is_hardware_backed(&self) -> bool;
}

// --- MOCK IMPLEMENTATION ---
struct MockTpm { simulated_key: String }

impl MockTpm {
    fn new() -> Self {
        Self { simulated_key: "0xSIMULATED_TPM_KEY_DEV_MODE_882".to_string() }
    }
}

impl TpmProvider for MockTpm {
    fn get_node_id(&self) -> Result<String> { Ok(self.simulated_key.clone()) }

    fn sign_quote(&self, nonce: &str) -> Result<(String, String)> {
        // Simulate hardware delay
        std::thread::sleep(std::time::Duration::from_millis(100));
        let mock_data = format!("PCR0:SECURE|NONCE:{}", nonce);
        let pcr_hash = sha256_digest(mock_data.as_bytes());
        let signature = base64::encode(format!("SIG_OF_{}", pcr_hash));
        Ok((pcr_hash, signature))
    }

    fn is_hardware_backed(&self) -> bool { false }
}

fn sha256_digest(data: &[u8]) -> String {
    use sha2::{Digest, Sha256};
    hex::encode(Sha256::digest(data))
}

// --- MAIN ---
fn main() -> Result<()> {
    let provider = MockTpm::new();
    let args: Vec<String> = std::env::args().collect();
    let nonce = if args.len() > 1 { &args[1] } else { "DEFAULT_NONCE" };

    let (pcr_hash, signature) = provider.sign_quote(nonce)
        .context("Failed to generate TPM quote")?;
    
    let response = AttestationResponse {
        node_id: provider.get_node_id()?,
        timestamp: Utc::now().to_rfc3339(),
        pcr_hash,
        signature,
        hardware_secured: provider.is_hardware_backed(),
        provider: "RUST_MOCK_TPM".into(),
    };

    println!("{}", serde_json::to_string(&response)?);
    Ok(())
}