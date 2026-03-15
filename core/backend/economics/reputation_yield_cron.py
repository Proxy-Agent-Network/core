import time
import json
import logging
from datetime import datetime
from typing import List, Dict

# Proxy Protocol Internal Modules
from core.economics.proxy_pass_escrow import ProxyPassEscrow, ProxyPass

# PROXY PROTOCOL - REPUTATION YIELD PAYOUT CRON (v1.0)
# "Automated Satoshi rewards for network liquidity providers."
# ----------------------------------------------------

class YieldPayoutCron:
    """
    Background worker that executes weekly Satoshi payouts.
    Typically triggered by a systemd-timer or a k8s CronJob.
    """
    def __init__(self, escrow_manager: ProxyPassEscrow):
        self.escrow = escrow_manager
        
        # Configuration
        self.MIN_PAYOUT_THRESHOLD = 100 # Don't send Keysends smaller than 100 Sats
        self.PAYOUT_LOG = "/var/log/proxy_yield_payouts.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger("YieldCron")

    def run_payout_sweep(self) -> Dict:
        """
        Main execution loop.
        Iterates through all active Proxy-Passes and settles accrued yield.
        """
        self.logger.info("⚡ Starting weekly Reputation Yield sweep...")
        
        sweep_stats = {
            "timestamp": datetime.now().isoformat(),
            "passes_processed": 0,
            "total_sats_dispatched": 0,
            "skipped_dust": 0,
            "failed_payments": 0
        }

        # 1. Get all active subscriptions from the Escrow Manager
        active_pass_ids = [pid for pid, p in self.escrow.active_passes.items() if p.is_active]

        for pass_id in active_pass_ids:
            try:
                # 2. Check validity (Expiry check)
                if not self.escrow.check_validity(pass_id):
                    self.logger.info(f"[*] Pass {pass_id} has expired. Skipping yield.")
                    continue

                # 3. Calculate Accrued Yield
                accrued = self.escrow.get_accrued_yield(pass_id)
                
                # 4. Dust Protection
                if accrued < self.MIN_PAYOUT_THRESHOLD:
                    sweep_stats["skipped_dust"] += 1
                    continue

                # 5. Dispatch Keysend Payout
                # In production, this calls the LND node's Keysend API
                success = self._dispatch_lightning_keysend(pass_id, accrued)
                
                if success:
                    # 6. Record Claim in Escrow Ledger
                    self.escrow.claim_yield(pass_id)
                    sweep_stats["passes_processed"] += 1
                    sweep_stats["total_sats_dispatched"] += accrued
                    self.logger.info(f"[✓] Paid {accrued} Sats to {pass_id}")
                else:
                    sweep_stats["failed_payments"] += 1

            except Exception as e:
                self.logger.error(f"[!] Error processing {pass_id}: {str(e)}")
                sweep_stats["failed_payments"] += 1

        self.logger.info(f"Sweep Complete. Dispatched {sweep_stats['total_sats_dispatched']} Sats across {sweep_stats['passes_processed']} passes.")
        return sweep_stats

    def _dispatch_lightning_keysend(self, pass_id: str, amount: int) -> bool:
        """
        Internal shim for LND Spontaneous Payout.
        Uses the custom TLV record 696969 to flag the payment as 'Yield'.
        """
        p_pass = self.escrow.active_passes.get(pass_id)
        if not p_pass: return False

        # In production:
        # payload = {
        #     "dest": p_pass.owner_pubkey,
        #     "amt": amount,
        #     "dest_custom_records": {696969: "REPUTATION_YIELD_V1"}
        # }
        # response = lnd_client.send_keysend(payload)
        # return response.status == "SUCCEEDED"
        
        return True # Mock Success for protocol logic flow

# --- Production Simulation ---
if __name__ == "__main__":
    # Initialize Escrow and Cron
    escrow = ProxyPassEscrow()
    cron = YieldPayoutCron(escrow)

    # Mock Data: Create a high-value 'Whale' Pass
    # 25M Sats locked. Weekly yield (0.5%) = 125,000 Sats.
    pass_id = escrow.provision_pass(
        owner_id="DEV_AGI_LABS", 
        amount_sats=25_000_000, 
        tier="ELITE" # Use string for demo; real code uses Enum
    )['pass_id']

    print(f"[*] Initialized Pass: {pass_id}")
    
    # Simulate 1 week passing
    # We manually adjust the last_yield_claim timestamp for the test
    one_week_ago = time.time() - (7 * 24 * 60 * 60)
    escrow.active_passes[pass_id].last_yield_claim = one_week_ago

    # Run Cron
    report = cron.run_payout_sweep()
    
    print("\n--- CRON EXECUTION REPORT ---")
    print(json.dumps(report, indent=2))
