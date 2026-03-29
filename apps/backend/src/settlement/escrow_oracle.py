import json
import logging
import asyncio
from functools import partial
from typing import Dict, Tuple

from fastapi import HTTPException

# Proxy Protocol Internal Modules (Rust FFI & Python Services)
from core.economics.hodl_escrow import EscrowManager
from core.reputation.slashing_engine import SlashingEngine

# 🟢 THE FIX: Import the actual verification logic from Phase 1
from api.onboarding_api import verify_play_integrity_token

# PROXY PROTOCOL - ESCROW ORACLE MIDDLEWARE (v2.0)
# "The uncompromising arbiter of zero-trust task settlement."
# ----------------------------------------------------

class EscrowOracle:
    """
    The Oracle orchestrates the verification pipeline. It ensures that 
    no Satoshi leaves escrow unless the hardware (Play Integrity), 
    compliance (SB 1417), and physical proof (AV Signature) meet 
    the protocol's strict requirements.
    """
    # 🟢 THE FIX: Inject redis_client to fetch the agent's registered public key
    def __init__(self, escrow_manager: EscrowManager, slashing_engine: SlashingEngine, redis_client):
        self.escrow = escrow_manager
        self.slasher = slashing_engine
        self.redis_client = redis_client
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("EscrowOracle")

    async def finalize_task(self, task_id: str, payment_hash: str, proof_payload: Dict) -> Dict:
        """
        Executes the three-stage verification gate:
        1. Hardware Attestation (Play Integrity JWT)
        2. Content Integrity (SB 1417 Evidence URLs)
        3. Settlement (Ed25519 Rust Verification & Lightning Release)
        """
        self.logger.info(f"[*] Starting final zero-trust audit for Task: {task_id}")

        agent_id = proof_payload.get("agent_id")
        hardware_token = proof_payload.get("hardware_attestation_token")
        evidence_urls = proof_payload.get("evidence_urls", [])
        av_signature_hex = proof_payload.get("av_signature_hex")

        if not all([agent_id, hardware_token, av_signature_hex]):
            return {"status": "error", "code": "PX_301", "message": "Malformed payload. Missing cryptographic proofs."}

        # 🟢 THE FIX: Fetch the public key from Redis that was bound during Key Ceremony
        public_key_b64 = await self.redis_client.get(f"pan:agent:{agent_id}:pubkey")
        if not public_key_b64:
            self.logger.error(f"🚨 Unregistered Agent: {agent_id} attempted settlement.")
            return {"status": "error", "code": "PX_403", "message": "Agent hardware key not registered."}

        # Ensure it's decoded to a string if Redis returned bytes
        if isinstance(public_key_b64, bytes):
            public_key_b64 = public_key_b64.decode('utf-8')

        # --- STAGE 1: HARDWARE ROOT OF TRUST ---
        # 🟢 THE FIX: Await the actual Play Integrity verification, offloaded to a thread pool
        is_hw_valid = await self._verify_hardware_token(hardware_token, agent_id, public_key_b64)

        if not is_hw_valid:
            self.logger.error(f"🚨 Hardware Fraud Detected for Agent {agent_id}.")
            # Trigger Slashing (burn reputation/bonds for spoofing attempts)
            slash_report = self.slasher.execute_slash(
                agent_id, 
                2000000, 
                "PX_400: Hardware Spoofing - Invalid Play Integrity Token"
            )
            # Cancel Escrow securely via Rust API
            try:
                self.escrow.cancel_contract(payment_hash)
            except Exception as e:
                self.logger.error(f"Failed to cancel contract: {e}")
                
            return {"status": "slashed", "report": slash_report}

        # --- STAGE 2: SB 1417 COMPLIANCE ---
        if not evidence_urls or len(evidence_urls) == 0:
            self.logger.warning(f"⚠️ COMPLIANCE FAILURE: Agent {agent_id} submitted no evidence.")
            return {"status": "held", "code": "PX_450", "message": "SB 1417 Violation: Missing visual evidence."}
            
        security_meta = proof_payload.get("security", {})
        if security_meta.get("duress_signal"):
            self.logger.warning(f"⚠️ SILENT ALARM: Agent {agent_id} reported duress.")
            return {"status": "held", "code": "PX_404", "message": "Security intervention required."}

        # --- STAGE 3: ZERO-TRUST SETTLEMENT ---
        # If hardware is valid and compliance is met, we pass the AV's signature to Rust.
        self.logger.info(f"✅ Pre-Checks Passed. Handing off to Rust FFI for Ed25519 Verification...")
        
        try:
            # The payload the AV signed is typically the task_id to prevent replay across missions
            payload_to_verify = task_id 
            
            success = self.escrow.settle_contract(payment_hash, payload_to_verify, av_signature_hex)
            
            if success:
                self.logger.info(f"✅ Cryptographic Audit Passed. Lightning Preimage Revealed for {task_id}.")
                return {
                    "status": "settled",
                    "payment_hash": payment_hash,
                    "agent_id": agent_id,
                    "attestation_level": "HARDWARE_ENCLAVE_AND_ED25519"
                }
            else:
                self.logger.error("🚨 Rust settlement rejected: Invalid AV Signature.")
                return {"status": "error", "code": "PX_401", "message": "Cryptographic signature validation failed."}
                
        except Exception as e:
            # Safely catch the PyValueError mapped from the Rust Mutex PoisonError or state machine guard
            self.logger.error(f"❌ Contract Settlement Halted by FFI: {e}")
            return {"status": "error", "code": "PX_500", "message": str(e)}

    async def _verify_hardware_token(self, token: str, agent_id: str, public_key_b64: str) -> bool:
        """
        Calls the Play Integrity verification logic from Phase 1.
        Runs in a thread executor to prevent blocking the async event loop.
        """
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                None,
                partial(
                    verify_play_integrity_token,
                    token=token,
                    expected_agent_id=agent_id,
                    expected_public_key=public_key_b64
                )
            )
        except HTTPException as e:
            self.logger.error(f"Play Integrity Verification Failed: {e.detail}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during hardware verification: {e}")
            return False

# --- Backend Integration Example ---
if __name__ == "__main__":
    import asyncio
    print("--- ESCROW ORACLE SETTLEMENT SIMULATION ---")
    
    # Mock implementations for local testing
    class MockSlashingEngine:
        def execute_slash(self, agent_id, amount, reason):
            return f"Slashed {amount} from {agent_id} for {reason}"

    class MockRedisClient:
        async def get(self, key):
            if "pubkey" in key:
                return b"mock_base64_public_key=="
            return None
            
    async def run_sim():
        try:
            escrow = EscrowManager()
            slasher = MockSlashingEngine()
            redis_client = MockRedisClient()
            oracle = EscrowOracle(escrow, slasher, redis_client)
            
            contract_id = "TASK-777"
            payment_hash = "mock_hash_abc123"
            amount = 25000
            
            # 🟢 THE FIX: Explicitly tagged the RFC test vector
            # ⚠️ RFC 8037 test vector. Never use in production — blocked by SecurityVault.
            mock_av_pubkey = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a" 
            
            escrow.create_contract(contract_id, payment_hash, amount, mock_av_pubkey)
            escrow.accept_contract(payment_hash)
            escrow.begin_contract(payment_hash)
            
            print(f"Contract state: {escrow.get_contract_state(payment_hash)}")
        except Exception as e:
            print(f"Simulation failed: {e}")
            
    asyncio.run(run_sim())