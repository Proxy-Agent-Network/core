import grpc
import os
import sys
import logging
import codecs
from typing import Dict, Optional

# 🌟 INFRASTRUCTURE FIX: Python Path Injection
# Generated gRPC files try to directly import each other. We force Python 
# to look in both the root folder and the grpc folder to guarantee it finds them.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, '../../')))    # Looks in /app
sys.path.append(os.path.abspath(os.path.join(CURRENT_DIR, '../grpc')))   # Looks in /app/backend/grpc

# --- PROTOCOL BUFFERS ---
try:
    import rpc_pb2 as ln
    import rpc_pb2_grpc as lnrpc
    import router_pb2 as router
    import router_pb2_grpc as routerrpc
except ImportError as e:
    ln = None
    lnrpc = None
    router = None
    routerrpc = None
    print(f"\n[CRITICAL WARN] ⚠️ LND gRPC modules failed to load!")
    print(f"Exact Python Error: {e}\n")

logger = logging.getLogger("LightningEngine")

class LightningEngine:
    def __init__(self):
        self.connected = False
        
        # 🟢 THE FIX: Fail-closed credential loading. No defaults.
        self.host = os.getenv('LND_GRPC_HOST')
        self.port = os.getenv('LND_GRPC_PORT', '10009')
        self.cert_path = os.getenv('LND_TLS_CERT_PATH')
        self.macaroon_path = os.getenv('LND_MACAROON_PATH')
        self.expected_network = os.getenv('LND_NETWORK', 'mainnet')

        if not all([self.host, self.cert_path, self.macaroon_path]):
            logger.critical("🛑 FATAL: Missing LND Credentials. Cannot initialize Mainnet M2H payments.")
            return

        self.connect()

    def connect(self) -> bool:
        """Establishes secure gRPC channels using TLS and Macaroons."""
        if lnrpc is None or routerrpc is None or ln is None:
            logger.critical("🛑 LND gRPC modules not loaded. Cannot connect.")
            return False

        try:
            # 1. Load TLS Cert
            with open(self.cert_path, 'rb') as f:
                cert_credentials = grpc.ssl_channel_credentials(f.read())

            # 2. Load Macaroon
            with open(self.macaroon_path, 'rb') as f:
                macaroon_bytes = f.read()
                macaroon = codecs.encode(macaroon_bytes, 'hex')

            def metadata_callback(context, callback):
                callback([('macaroon', macaroon)], None)

            auth_credentials = grpc.metadata_call_credentials(metadata_callback)
            combined_credentials = grpc.composite_channel_credentials(cert_credentials, auth_credentials)

            # 3. Establish Channel
            self.channel = grpc.secure_channel(f"{self.host}:{self.port}", combined_credentials)
            self.stub = lnrpc.LightningStub(self.channel)
            self.router_stub = routerrpc.RouterStub(self.channel)
            
            # 4. Verify Node State (Synced & Correct Network)
            self._verify_node_state()
            
            self.connected = True
            return True

        except Exception as e:
            logger.error(f"❌ LND Connection Failed: {e}")
            self.connected = False
            return False

    def _verify_node_state(self):
        """
        Strictly enforces that we are on Mainnet and fully synced 
        before allowing any Escrow operations to proceed.
        """
        req = ln.GetInfoRequest()
        res = self.stub.GetInfo(req)
        
        # Check Network
        active_networks = [net.network for net in res.networks]
        if self.expected_network not in active_networks:
            logger.critical(f"🛑 FATAL NETWORK MISMATCH: Expected {self.expected_network}, but node is on {active_networks}")
            raise RuntimeError("LND Node is on the wrong chain. Halting to prevent loss of funds.")
            
        # Check Sync Status
        if not res.synced_to_chain:
            logger.warning("⚠️ LND Node is currently catching up to the Bitcoin blockchain. Payments may fail.")
            
        logger.info(f"⚡ LND Engine Online | Alias: {res.alias} | Network: {active_networks[0]} | Synced: {res.synced_to_chain}")

    def get_balances(self) -> Optional[Dict[str, int]]:
        if not self.connected and not self.connect():
            return None
            
        try:
            wallet_req = ln.WalletBalanceRequest()
            wallet_resp = self.stub.WalletBalance(wallet_req)
            
            channel_req = ln.ChannelBalanceRequest()
            channel_resp = self.stub.ChannelBalance(channel_req)
            
            return {
                "onchain_sats": wallet_resp.total_balance,
                "channel_sats": channel_resp.balance,
                "pending_channel_sats": channel_resp.pending_open_balance
            }
        except Exception as e:
            logger.error(f"❌ Balance Fetch Error: {e}")
            return None

    def check_outbound_liquidity(self, required_sats: int) -> bool:
        """
        Checks active channels to ensure we have enough total outbound 
        capacity across all channels (MPP) to route the payload.
        """
        if not self.connected and not self.connect():
            return False
            
        try:
            req = ln.ListChannelsRequest(active_only=True)
            res = self.stub.ListChannels(req)
            
            total_outbound = sum(c.local_balance for c in res.channels)
            
            if total_outbound < required_sats:
                logger.error(f"💸 LIQUIDITY CRISIS: Need {required_sats} sats, but total channel outbound is {total_outbound} sats.")
                return False
                
            return True
        except Exception as e:
            logger.error(f"❌ Outbound Liquidity Check Error: {e}")
            return False

    def create_invoice(self, amount_sats: int, memo: str, expiry: int = 3600) -> Optional[Dict]:
        """
        🟢 THE FIX: B2B INBOUND PAYMENTS
        Generates an L402 Lightning Invoice for Fleet AI API fees.
        """
        if not self.connected and not self.connect():
            return None
            
        try:
            req = ln.Invoice(
                memo=memo,
                value=amount_sats,
                expiry=expiry
            )
            response = self.stub.AddInvoice(req)
            
            # r_hash is required to verify the payment later
            r_hash_hex = codecs.encode(response.r_hash, 'hex').decode('utf-8')
            
            logger.info(f"🧾 Generated Invoice for {amount_sats} sats: {memo}")
            return {
                "payment_request": response.payment_request,
                "r_hash": r_hash_hex
            }
        except Exception as e:
            logger.error(f"❌ Invoice Creation Error: {e}")
            return None

    def pay_invoice(self, payment_request: str, max_fee_sats: int = 50) -> Dict:
        """
        Executes an L402 M2H payout to an Agent's Lightning Wallet.
        Enforces strict routing fee limits.
        """
        if not self.connected and not self.connect():
            return {"status": "FAILED", "error": "LND Disconnected"}
            
        try:
            # 1. Decode invoice to check amount before paying
            decode_req = ln.PayReqString(pay_req=payment_request)
            decoded = self.stub.DecodePayReq(decode_req)
            
            amount_sats = decoded.num_satoshis
            
            # 2. Check Liquidity
            if not self.check_outbound_liquidity(amount_sats):
                return {"status": "FAILED", "error": "Insufficient outbound channel liquidity."}
            
            # 3. Dispatch Payment with strict fee limits
            logger.info(f"💸 Routing {amount_sats} sats to Agent... (Max Fee: {max_fee_sats} sats)")
            req = router.SendPaymentRequest(
                payment_request=payment_request,
                timeout_seconds=30,
                fee_limit_sat=max_fee_sats
            )
            
            for response in self.router_stub.SendPaymentV2(req):
                if response.status == ln.Payment.SUCCEEDED:
                    logger.info(f"✅ M2H Payout Settled! Preimage: {response.payment_preimage}")
                    return {
                        "status": "SETTLED", 
                        "preimage": response.payment_preimage,
                        "fee_paid_sats": response.fee_sat
                    }
                elif response.status == ln.Payment.FAILED:
                    logger.error(f"❌ Payment Route Failed: {response.failure_reason}")
                    return {"status": "FAILED", "error": f"Routing Failure Code: {response.failure_reason}"}
                    
            return {"status": "TIMEOUT", "error": "Payment timed out during routing."}

        except Exception as e:
            logger.error(f"❌ Payment Execution Error: {e}")
            return {"status": "FAILED", "error": str(e)}

    def verify_payment_hash(self, r_hash_hex: str) -> bool:
        """Used by the Escrow Smart Contract to verify a bounty was actually paid."""
        if not self.connected and not self.connect():
            return False
            
        try:
            request = ln.PaymentHash(r_hash_str=r_hash_hex)
            invoice = self.stub.LookupInvoice(request, timeout=10)
            
            # State 1 = SETTLED
            if invoice.state == 1:
                return True
            return False
                
        except Exception as e:
            logger.error(f"❌ Invoice Lookup Error: {e}")
            return False