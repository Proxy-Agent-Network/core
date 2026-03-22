import grpc
import os
import sys
import codecs
import logging
import base64
import urllib.parse
import requests 
import qrcode
import io

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
except ImportError as e:
    ln = None
    lnrpc = None
    print(f"\n[CRITICAL WARN] ⚠️ LND gRPC modules failed to load!")
    print(f"Exact Python Error: {e}\n")

# --- SECURE DOCKER CONFIGURATION ---
LND_HOST = os.getenv('LND_GRPC_HOST', 'lnd')
LND_PORT = os.getenv('LND_GRPC_PORT', '10009')

HOME = os.path.expanduser("~")
CERT_PATH = os.getenv('LND_TLS_CERT_PATH', f'{HOME}/.lnd/tls.cert')
MACAROON_PATH = os.getenv('LND_MACAROON_PATH', f'{HOME}/.lnd/data/chain/bitcoin/regtest/admin.macaroon')

class LightningEngine:
    def __init__(self):
        self.stub = None
        self.connected = False
        self.pending_invoices = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("LND-gRPC")

    def _generate_qr_base64(self, data_string):
        """Helper: Generates a QR code base64 string locally in memory."""
        if not data_string:
            return ""
            
        try:
            # 1. Configure the QR Code matrix
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data_string)
            qr.make(fit=True)

            # 2. Render the image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 3. Save to an in-memory byte buffer (No disk I/O)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            
            # 4. Encode to base64 for frontend consumption
            base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{base64_img}"
            
        except Exception as e:
            self.logger.error(f"❌ Local QR Generation Error: {e}")
            return ""

    def connect(self):
        """Establishes secure mTLS connection to the LND Container."""
        if not ln or not lnrpc:
            self.logger.error("❌ gRPC modules missing. Cannot connect.")
            return False

        try:
            if not os.path.exists(CERT_PATH) or not os.path.exists(MACAROON_PATH):
                self.logger.info(f"⏳ Missing Keys: Checked {CERT_PATH}")
                return False

            self.logger.info(f"🔑 Loading credentials from {CERT_PATH}...")

            with open(CERT_PATH, 'rb') as f:
                cert_creds = grpc.ssl_channel_credentials(f.read())

            with open(MACAROON_PATH, 'rb') as f:
                macaroon_bytes = f.read()
                macaroon = codecs.encode(macaroon_bytes, 'hex')

            def metadata_callback(context, callback):
                callback([('macaroon', macaroon)], None)

            auth_creds = grpc.metadata_call_credentials(metadata_callback)
            combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)

            self.logger.info(f"🔌 Connecting to LND at {LND_HOST}:{LND_PORT}...")
            
            channel = grpc.secure_channel(
                f"{LND_HOST}:{LND_PORT}", 
                combined_creds
            )

            self.stub = lnrpc.LightningStub(channel)
            
            info = self.stub.GetInfo(ln.GetInfoRequest())
            self.connected = True
            self.pubkey = info.identity_pubkey
            
            self.logger.info(f"⚡ CONNECTED to {info.alias} (Testnet)")
            self.logger.info(f"🔑 Pubkey: {info.identity_pubkey}")
            
            return True

        except Exception as e:
            self.logger.error(f"⚠️ LND Connection Failed: {e}")
            return False

    def create_invoice(self, sats, memo):
        if not self.connected:
            if not self.connect(): 
                return None
        try:
            request = ln.Invoice(value=int(sats), memo=memo)
            response = self.stub.AddInvoice(request, timeout=10)
            payment_request = response.payment_request
            r_hash_hex = response.r_hash.hex()
            
            self.pending_invoices[r_hash_hex] = {
                'amount': sats,
                'memo': memo,
                'payment_request': payment_request
            }
            
            qr_code = self._generate_qr_base64(payment_request)
            
            self.logger.info(f"🧾 Invoice Created: {sats} sats | Hash: {r_hash_hex[:8]}...")
            
            return {
                'payment_request': payment_request,
                'r_hash': r_hash_hex,
                'amount': sats,
                'qr_code': qr_code
            }
        except Exception as e:
            self.logger.error(f"❌ Invoice Creation Error: {e}")
            return None
        
    def get_balances(self):
        if not self.connected:
            if not self.connect(): 
                return None
        try:
            wallet_req = ln.WalletBalanceRequest()
            wallet_resp = self.stub.WalletBalance(wallet_req)
            
            channel_req = ln.ChannelBalanceRequest()
            channel_resp = self.stub.ChannelBalance(channel_req)
            
            self.logger.info("💰 Successfully fetched node balances.")
            
            return {
                "onchain_sats": wallet_resp.total_balance,
                "channel_sats": channel_resp.balance,
                "pending_channel_sats": channel_resp.pending_open_balance
            }
        except Exception as e:
            self.logger.error(f"❌ Balance Fetch Error: {e}")
            return None
        
    def verify_payment(self, r_hash_hex):
        if not self.connected:
            if not self.connect(): 
                return False
        try:
            request = ln.PaymentHash(r_hash_str=r_hash_hex)
            invoice = self.stub.LookupInvoice(request, timeout=10)
            
            if invoice.state == 1:
                self.logger.info(f"✅ Payment Verified for hash: {r_hash_hex[:8]}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Payment Verification Error: {e}")
            return False

lnd = LightningEngine()