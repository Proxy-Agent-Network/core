import stripe
import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional

# Set up logging for the Gateway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FiatGateway")

# ==========================================
# 1. The Abstract Interface 
# ==========================================
class LiquidityProvider(ABC):
    @abstractmethod
    def get_quote(self, usd_amount: float) -> int:
        pass

    @abstractmethod
    def fund_hodl_invoice(self, bolt11_invoice: str) -> bool:
        pass

    @abstractmethod
    def settle_to_fiat(self, agent_id: str, amount_sats: int) -> bool:
        pass

# ==========================================
# 2. The Mock Provider 
# ==========================================
class MockLiquidityProvider(LiquidityProvider):
    """Safe testing harness. No real funds are moved."""
    def __init__(self, mock_delay: float = 0.0):
        self.mock_btc_price = 95000.00
        self.volatility_buffer = 0.02
        self.mock_delay = mock_delay # Configurable delay for fast tests

    def get_quote(self, usd_amount: float) -> int:
        raw_btc = usd_amount / self.mock_btc_price
        buffered_btc = raw_btc * (1 - self.volatility_buffer)
        sats = int(buffered_btc * 100_000_000)
        logger.info(f"[MockProvider] Quoted {sats} sats for ${usd_amount:.2f} USD")
        return sats

    def fund_hodl_invoice(self, bolt11_invoice: str) -> bool:
        logger.info(f"[MockProvider] Simulating funding of BOLT11: {bolt11_invoice[:15]}...")
        if self.mock_delay > 0:
            time.sleep(self.mock_delay) 
        logger.info("[MockProvider] ✅ HODL Invoice successfully funded.")
        return True

    def settle_to_fiat(self, agent_id: str, amount_sats: int) -> bool:
        btc_amount = amount_sats / 100_000_000
        usd_value = btc_amount * self.mock_btc_price
        logger.info(f"[MockProvider] Simulating payout of ${usd_value:.2f} USD to Agent {agent_id}")
        return True

# ==========================================
# 3. The Core Gateway 
# ==========================================
class FiatGateway:
    """
    Handles inbound enterprise webhooks, securely verifies them, 
    and orchestrates the conversion and escrow lock.
    """
    def __init__(self, provider: LiquidityProvider, escrow_manager, stripe_secret: str):
        self.provider = provider
        self.escrow_manager = escrow_manager 
        self.stripe_secret = stripe_secret
        self.max_task_usd = 500.00  # Hard sanity ceiling for task payouts

    def process_fleet_webhook(self, payload: bytes, sig_header: str) -> Tuple[bool, Optional[str]]:
        """
        Verifies the generic Fleet webhook and initiates the Lightning Escrow.
        Returns (Success_Boolean, Message)
        """
        # Step 1: Cryptographic Verification
        try:
            # construct_event does not require a globally set api_key
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.stripe_secret
            )
        except stripe.error.SignatureVerificationError:
            logger.error("🚨 CRITICAL: Invalid Stripe Webhook Signature detected!")
            return False, "Signature verification failed"
        except ValueError:
            logger.error("⚠️ Invalid payload format.")
            return False, "Invalid payload"

        # Step 2: Route the Event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            usd_paid = session.get('amount_total', 0) / 100.0
            metadata = session.get('metadata', {})
            task_id = metadata.get('task_id')
            
            # Step 3: Bounds and Sanity Checking
            if not task_id or not (0 < usd_paid <= self.max_task_usd):
                logger.warning(f"⚠️ Invalid webhook data: Amount ${usd_paid} | Task: {task_id}")
                return False, "Invalid amount or missing task_id"

            # Step 4: Idempotency Check
            if task_id in self.escrow_manager.task_map:
                logger.info(f"♻️ Task {task_id} already escrowed. Ignoring duplicate webhook.")
                return True, "Duplicate event ignored"

            logger.info(f"✅ Verified ${usd_paid:.2f} payment from Fleet for Task {task_id}")

            # Step 5: Get Satoshi Quote
            sats_required = self.provider.get_quote(usd_paid)
            
            # Step 6: Generate Internal HODL Invoice
            try:
                invoice_data = self.escrow_manager.create_hodl_invoice(
                    agent_id="pending", 
                    task_id=task_id, 
                    amount=sats_required
                )
                bolt11 = invoice_data['bolt11']
            except Exception as e:
                logger.error(f"Failed to generate HODL invoice: {e}")
                return False, "Internal Escrow generation failed"

            # Step 7: Liquidity Provider funds the invoice, locking the HTLC
            funding_success = self.provider.fund_hodl_invoice(bolt11)
            
            if funding_success:
                logger.info(f"🚀 TASK {task_id} IS NOW LIVE AND ESCROWED.")
                return True, "Task successfully escrowed"
            else:
                logger.error(f"Failed to fund HODL invoice for Task {task_id}")
                return False, "Liquidity provision failed"

        return True, "Event ignored"