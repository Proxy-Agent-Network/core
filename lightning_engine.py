import grpc
import os
import codecs
import logging
import base64
import urllib.parse
import requests 

# --- PROTOCOL BUFFERS ---
# These are generated automatically by the Dockerfile during build
try:
    import rpc_pb2 as ln
    import rpc_pb2_grpc as lnrpc
except ImportError:
    ln = None
    lnrpc = None
    print(" [WARN] ⚠️  LND gRPC modules not found. They will be generated during Docker build.")

# CONFIGURATION
# In Docker, the host is the service name 'lnd_node'
LND_HOST = os.getenv('LND_GRPC_HOST', 'lnd_node')
LND_PORT = os.getenv('LND_GRPC_PORT', '10009')

# PATHS (Mapped via Docker Volume)
# These files exist inside the container, mounted from the LND node
CERT_PATH = '/root/.lnd/tls.cert'
MACAROON_PATH = '/root/.lnd/data/chain/bitcoin/testnet/admin.macaroon'

class LightningEngine:
    def __init__(self):
        self.stub = None
        self.connected = False
        self.pending_invoices = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("LND-gRPC")

    def _generate_qr_base64(self, data_string):
        """
        Helper: Generates a QR code base64 string using a utility API.
        This provides the visual QR for the dashboard escrow.
        """
        try:
            # Encode the payment request for the URL
            safe_data = urllib.parse.quote(data_string)
            # Fetch QR blob from a standard QR server
            url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={safe_data}"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Convert binary image -> Base64 string for HTML display
                b64_img = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/png;base64,{b64_img}"
        except Exception as e:
            self.logger.error(f"⚠️ QR Generation failed: {e}")
        
        return "" 

    def connect(self):
        """Establishes secure mTLS connection to the LND Container."""
        if not ln or not lnrpc:
            self.logger.error("❌ gRPC modules missing. Cannot connect.")
            return False

        try:
            if not os.path.exists(CERT_PATH) or not os.path.exists(MACAROON_PATH):
                self.logger.info(f"⏳ LND is initializing... Waiting for key generation at {MACAROON_PATH}")
                return False

            # 1. Load TLS Cert (Server Authentication)
            with open(CERT_PATH, 'rb') as f:
                cert_creds = grpc.ssl_channel_credentials(f.read())

            # 2. Load Macaroon (Client Authorization)
            with open(MACAROON_PATH, 'rb') as f:
                macaroon_bytes = f.read()
                macaroon = codecs.encode(macaroon_bytes, 'hex')

            # 3. Build Auth Metadata Interceptor
            def metadata_callback(context, callback):
                callback([('macaroon', macaroon)], None)

            auth_creds = grpc.metadata_call_credentials(metadata_callback)
            combined_creds = grpc.composite_channel_credentials(cert_creds, auth_creds)

            # 4. Connect to the Container
            self.logger.info(f"🔌 Connecting to LND at {LND_HOST}:{LND_PORT}...")
            channel = grpc.secure_channel(f"{LND_HOST}:{LND_PORT}", combined_creds)
            self.stub = lnrpc.LightningStub(channel)
            
            # 5. Verify Connection with GetInfo
            info = self.stub.GetInfo(ln.GetInfoRequest())
            self.connected = True
            
            self.logger.info(f"⚡ CONNECTED to {info.alias} (Testnet)")
            self.logger.info(f"🔑 Pubkey: {info.identity_pubkey}")
            self.logger.info(f"⛓️  Synced to Block: {info.block_height}")
            
            return True

        except Exception as e:
            self.logger.error(f"⚠️ LND Connection Failed: {e}")
            return False

    def create_invoice(self, sats, memo):
        """Creates a Lightning Invoice and returns formatting for UI."""
        if not self.connected:
            if not self.connect(): 
                return None
            
        try:
            # Create Invoice Request
            request = ln.Invoice(value=int(sats), memo=memo)
            response = self.stub.AddInvoice(request)
            
            # Extract Data
            payment_request = response.payment_request
            r_hash_hex = response.r_hash.hex()
            
            # Store for tracking
            self.pending_invoices[r_hash_hex] = {
                'amount': sats,
                'memo': memo,
                'payment_request': payment_request,
                'r_hash': r_hash_hex
            }
            
            # Generate Visual QR
            qr_image = self._generate_qr_base64(payment_request)
            
            self.logger.info(f"🧾 Invoice Created: {sats} sats | Hash: {r_hash_hex[:8]}...")
            
            return {
                'payment_request': payment_request,
                'r_hash': r_hash_hex,
                'amount': sats,
                'qr_image': qr_image
            }
        except Exception as e:
            self.logger.error(f"❌ Invoice Creation Error: {e}")
            return None

    def check_status(self, r_hash):
        """Checks if a specific invoice hash has been paid."""
        if not self.connected: 
            return "OFFLINE"
            
        try:
            # LND expects bytes for the hash lookup
            r_hash_bytes = bytes.fromhex(r_hash)
            
            request = ln.PaymentHash(r_hash=r_hash_bytes)
            response = self.stub.LookupInvoice(request)
            
            if response.state == ln.Invoice.SETTLED:
                return "SETTLED"
            elif response.state == ln.Invoice.OPEN:
                return "OPEN"
            elif response.state == ln.Invoice.CANCELED:
                return "EXPIRED"
            else:
                return "UNKNOWN"
        except Exception as e:
            return "ERROR"

# Singleton Instance
lnd = LightningEngine()