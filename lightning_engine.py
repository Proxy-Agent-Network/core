"""
lightning_engine.py
-------------------
Connects the Proxy Agent to a local LND node via REST API.
Now includes QR Code generation for the dashboard.
"""
import requests
import json
import base64
import os
import logging
import urllib.parse

# CONFIGURATION
LND_HOST = os.getenv("LND_HOST", "https://host.docker.internal:8081")
MACAROON_HEX = os.getenv("LND_MACAROON", "")

class LightningClient:
    def __init__(self):
        self.base_url = LND_HOST
        self.headers = {
            "Grpc-Metadata-macaroon": MACAROON_HEX
        }
        self.verify_ssl = False 
        self.pending_invoices = {} 

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("LND")
        self.logger.info(f"🔌 LND Client initializing at {self.base_url}...")

    def _generate_qr_base64(self, data_string):
        """
        Helper: Generates a QR code base64 string using a utility API.
        This avoids needing to install the 'qrcode' library inside Docker.
        """
        try:
            # Encode the payment request for the URL
            safe_data = urllib.parse.quote(data_string)
            # Fetch QR blob from a standard QR server
            url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={safe_data}"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Convert binary image -> Base64 string
                b64_img = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/png;base64,{b64_img}"
        except Exception as e:
            self.logger.error(f"⚠️ QR Generation failed: {e}")
        
        return "" # Return empty string if generation fails

    def create_invoice(self, amount_sats, memo="Proxy Task Service"):
        endpoint = f"{self.base_url}/v1/invoices"
        data = {"value": amount_sats, "memo": memo}
        
        try:
            response = requests.post(
                endpoint, 
                json=data, 
                headers=self.headers, 
                verify=self.verify_ssl
            )
            
            if response.status_code == 200:
                res_json = response.json()
                
                # 1. Decode Hash
                r_hash_base64 = res_json['r_hash']
                payment_hash = base64.b64decode(r_hash_base64).hex()
                
                # 2. Get Payment Request (BOLT11)
                payment_request = res_json['payment_request']

                # --- ADD THIS BLOCK ---
                print(f"\n{'='*60}")
                print(f"👉 COPY THIS INVOICE FOR BOB:\n{payment_request}")
                print(f"{'='*60}\n")
                # ----------------------

                # 3. Generate QR Code
                qr_image = self._generate_qr_base64(payment_request)
                
                self.pending_invoices[payment_hash] = {
                    "amount": amount_sats,
                    "memo": memo,
                    "status": "OPEN",
                    "r_hash": payment_hash,
                    "payment_request": payment_request
                }
                
                self.logger.info(f"⚡ Real Invoice Created: {amount_sats} sats | Hash: {payment_hash[:8]}...")
                
                return {
                    "payment_request": payment_request,
                    "r_hash": payment_hash,
                    "amount": amount_sats,
                    "qr_image": qr_image  # Dashboard needs this to complete the popup!
                }
            else:
                self.logger.error(f"❌ LND Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Connection Failed: {e}")
            return None

    def check_status(self, r_hash):
        endpoint = f"{self.base_url}/v1/invoice/{r_hash}"
        try:
            response = requests.get(endpoint, headers=self.headers, verify=self.verify_ssl)
            if response.status_code == 200:
                data = response.json()
                return "SETTLED" if data.get("settled") else "OPEN"
            return "UNKNOWN"
        except Exception as e:
            self.logger.error(f"Status Check Failed: {e}")
            return "ERROR"

if MACAROON_HEX:
    lnd = LightningClient()
else:
    print(" [WARN] No Macaroon found. LND Client disabled.")
    lnd = None