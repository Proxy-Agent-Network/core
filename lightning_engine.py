import time
import random
import hashlib
import logging
import qrcode
import os
from io import BytesIO
import base64

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LND_Engine")

class LightningEngine:
    def __init__(self, mode="SIMULATION"):
        self.mode = mode
        self.pending_invoices = {}
        logger.info(f"⚡ Lightning Engine Initialized [Mode: {self.mode}]")

    def create_invoice(self, amount_sats: int, memo: str) -> dict:
        """
        Generates a Lightning Invoice (BOLT11).
        In SIMULATION mode, creates a dummy hash and QR code.
        """
        invoice_hash = hashlib.sha256(f"{memo}{time.time()}{random.random()}".encode()).hexdigest()
        
        # Simulate a BOLT11 string (Mock data)
        bolt11 = f"lnbc{amount_sats}n1{invoice_hash[:50]}..."

        # Generate QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(bolt11)
        qr.make(fit=True)
        
        img_buffer = BytesIO()
        qr.make_image(fill='black', back_color='white').save(img_buffer)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        invoice_data = {
            "r_hash": invoice_hash,
            "payment_request": bolt11,
            "amount": amount_sats,
            "memo": memo,
            "qr_image": f"data:image/png;base64,{img_str}",
            "status": "OPEN",
            "created_at": time.time()
        }
        
        self.pending_invoices[invoice_hash] = invoice_data
        logger.info(f"🧾 Invoice Created: {amount_sats} sats | Hash: {invoice_hash[:8]}...")
        return invoice_data

    def check_status(self, r_hash: str) -> str:
        """
        Checks if an invoice has been paid.
        In SIMULATION mode, this auto-settles based on the invoice's specific duration.
        """
        if r_hash not in self.pending_invoices:
            return "UNKNOWN"
        
        invoice = self.pending_invoices[r_hash]
        
        if invoice['status'] == 'SETTLED':
            return "SETTLED"
        
        # SIMULATION LOGIC: Dynamic Delay
        if self.mode == "SIMULATION":
            elapsed = time.time() - invoice['created_at']
            
            # Get duration from invoice, default to 8 if not found
            target_duration = invoice.get('duration', 8)
            
            if elapsed > target_duration:
                invoice['status'] = 'SETTLED'
                logger.info(f"💰 Payment Detected! {invoice['amount']} sats [SIMULATED]")
                return "SETTLED"
        
        return "OPEN"

# Singleton Instance
lnd = LightningEngine()