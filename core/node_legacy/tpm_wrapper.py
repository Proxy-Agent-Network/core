import subprocess
import json
import os
import platform
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TPM_Bridge")

class TPMBinding:
    def __init__(self):
        # 1. Detect OS to determine file extension
        is_windows = platform.system().lower() == "windows"
        filename = "proxy-tpm-engine.exe" if is_windows else "proxy-tpm-engine"
        
        # 2. Construct the full path
        self.binary_path = os.path.join(
            os.path.dirname(__file__), 
            "rust_tpm/target/debug",
            filename
        )

    def get_attestation_quote(self, nonce: str) -> dict:
        # 3. Check if binary exists before trying to run
        if not os.path.exists(self.binary_path):
            logger.error(f"❌ Binary not found at: {self.binary_path}")
            return None

        try:
            # 4. Run the binary
            result = subprocess.run(
                [self.binary_path, nonce],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Rust Error: {e.stderr}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {result.stdout}")
            return None

if __name__ == "__main__":
    tpm = TPMBinding()
    print(f"🔍 Looking for engine at: {tpm.binary_path}")
    
    # Test Run
    data = tpm.get_attestation_quote("test_challenge_123")
    
    if data:
        print("\n✅ SUCCESS! Received Secure Payload:")
        print(json.dumps(data, indent=2))
    else:
        print("\n❌ Failed to get quote.")