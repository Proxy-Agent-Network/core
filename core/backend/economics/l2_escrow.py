import json
import time
from enum import Enum
from dataclasses import dataclass

# PROXY PROTOCOL - CROSS-CHAIN ESCROW BRIDGE (v1)
# "Settlement on any chain."
# ----------------------------------------------------
# Dependencies: pip install web3

class ChainID(Enum):
    BASE_MAINNET = 8453
    ARBITRUM_ONE = 42161
    OPTIMISM = 10

@dataclass
class L2Transaction:
    tx_hash: str
    chain_id: int
    amount_usdc: float
    status: str
    agent_wallet: str
    node_wallet: str

class L2EscrowEngine:
    def __init__(self, rpc_urls: dict = None):
        self.rpc_urls = rpc_urls or {
            ChainID.BASE_MAINNET: "https://mainnet.base.org",
            ChainID.ARBITRUM_ONE: "https://arb1.arbitrum.io/rpc"
        }
        # Mock Smart Contract Address for the Proxy Vault
        self.VAULT_ADDRESS = "0xProxyProtocolVaultV1_88293"
        
    def _verify_allowance(self, chain_id: ChainID, wallet: str, amount: float) -> bool:
        """
        Mock Check: Has the agent approved the Vault to spend their USDC?
        """
        print(f"[*] Checking USDC allowance on Chain {chain_id.name} for {wallet}...")
        # In prod: web3.eth.contract.functions.allowance(...).call()
        return True

    def lock_funds(self, chain_id: ChainID, agent_wallet: str, amount_usdc: float, task_id: str) -> L2Transaction:
        """
        Locks USDC in the L2 Smart Contract.
        """
        if not self._verify_allowance(chain_id, agent_wallet, amount_usdc):
            raise PermissionError("Insufficient Allowance. Approve USDC first.")

        print(f"[*] Initiating Deposit on {chain_id.name}...")
        print(f"    -> Agent: {agent_wallet}")
        print(f"    -> Amount: ${amount_usdc} USDC")
        print(f"    -> Task Tag: {task_id}")

        # Simulate EVM Transaction delay
        # time.sleep(1) 
        
        tx_hash = f"0x_mock_tx_{int(time.time())}_{task_id}"
        
        return L2Transaction(
            tx_hash=tx_hash,
            chain_id=chain_id.value,
            amount_usdc=amount_usdc,
            status="LOCKED",
            agent_wallet=agent_wallet,
            node_wallet="PENDING_MATCH"
        )

    def release_funds(self, tx: L2Transaction, node_wallet_evm: str):
        """
        Called by the Protocol Oracle when the task is verified.
        Transfers USDC from Vault to Human Node.
        """
        print(f"[*] Releasing Escrow {tx.tx_hash}...")
        print(f"    -> Destination: {node_wallet_evm}")
        
        tx.status = "SETTLED"
        tx.node_wallet = node_wallet_evm
        
        print(f"✅ L2 SETTLEMENT COMPLETE. Funds moved on-chain.")

# --- CLI Simulation ---
if __name__ == "__main__":
    bridge = L2EscrowEngine()
    
    print("--- CROSS-CHAIN AGENT REQUEST ---")
    
    # Scene: An Agent on Base wants to hire a human
    agent_addr = "0xAgent_Alpha_123"
    human_addr = "0xHuman_Node_456"
    task_cost = 50.00 # $50 USDC
    
    try:
        # 1. Lock
        escrow_tx = bridge.lock_funds(
            ChainID.BASE_MAINNET, 
            agent_addr, 
            task_cost, 
            "task_crosschain_001"
        )
        print(f"[>] Locked: {escrow_tx.tx_hash} ({escrow_tx.status})")
        
        print("\n... Task Executes in Physical World ...\n")
        
        # 2. Settle
        bridge.release_funds(escrow_tx, human_addr)
        
    except Exception as e:
        print(f"[!] Error: {e}")
