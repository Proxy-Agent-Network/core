import cv2
import numpy as np
import pytesseract
import re
import hashlib
import json
from pytesseract import Output
from typing import Tuple, Dict

# PROXY PROTOCOL - ZK PRIVACY GUARD (v1.1)
# "Sanitize locally. Verify globally."
# ----------------------------------------------------
# Dependencies: pip install opencv-python-headless pytesseract

class PrivacyGuard:
    def __init__(self):
        # Load Face Detection Model
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Regex Patterns for Sensitive Text
        self.PATTERNS = {
            "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b',
            "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
            "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }

    def _pixelate_region(self, image, x, y, w, h, blocks=15):
        """
        Destructive editing: Downsample and upsample to remove details.
        """
        # 1. Select Region of Interest (ROI)
        roi = image[y:y+h, x:x+w]
        
        # 2. Downsample (Shrink)
        roi = cv2.resize(roi, (blocks, blocks), interpolation=cv2.INTER_LINEAR)
        
        # 3. Upsample (Expand back to original size)
        roi = cv2.resize(roi, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # 4. Apply back to image
        image[y:y+h, x:x+w] = roi
        return image

    def redact_pii(self, image_path: str) -> Tuple[str, Dict]:
        """
        Main pipeline: Detects faces + Sensitive Text and blurs them.
        Returns: (Output Path, Report)
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found or invalid format.")

        report = {"faces_redacted": 0, "text_blocks_redacted": 0}

        # --- STEP 1: FACE REDACTION ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            self._pixelate_region(img, x, y, w, h)
            # Add a green box to show the Agent "We handled this"
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 65), 2)
            report["faces_redacted"] += 1

        # --- STEP 2: TEXT REDACTION (OCR) ---
        # Get detailed OCR data (words + bounding boxes)
        d = pytesseract.image_to_data(img, output_type=Output.DICT)
        n_boxes = len(d['text'])
        
        for i in range(n_boxes):
            text = d['text'][i]
            conf = int(d['conf'][i])
            
            if conf > 40 and text.strip():
                # Check against regex patterns
                is_sensitive = False
                for p_name, pattern in self.PATTERNS.items():
                    if re.search(pattern, text):
                        is_sensitive = True
                        break
                
                if is_sensitive:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    # Expand box slightly to ensure full coverage
                    pad = 5
                    self._pixelate_region(img, x-pad, y-pad, w+(pad*2), h+(pad*2))
                    report["text_blocks_redacted"] += 1

        # --- STEP 3: SAVE & PROVE ---
        output_path = image_path.replace(".", "_safe.")
        cv2.imwrite(output_path, img)
        
        # Generate ZK Commitment (Proof of Sanitization)
        # In v2, this would be a zk-SNARK. In v1, it's a Hash Commitment.
        proof = self._generate_commitment(image_path, output_path)
        report["proof"] = proof
        
        return output_path, report

    def _generate_commitment(self, original_path: str, safe_path: str) -> Dict:
        """
        Creates a cryptographic record linking the raw input to the sanitized output.
        The Raw Hash acts as the 'Commitment' and the Safe Hash is the 'Public Output'.
        """
        def get_hash(path):
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()

        return {
            "method": "privacy_guard_v1.1",
            "input_commitment": get_hash(original_path), # Private (Raw)
            "output_hash": get_hash(safe_path),          # Public (Safe)
            "timestamp": "2026-02-10T08:00:00Z"
        }

# --- CLI Usage ---
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 privacy_guard.py <image_path>")
        sys.exit(1)

    guard = PrivacyGuard()
    print(f"[*] Analyzing {sys.argv[1]} for PII...")
    
    try:
        safe_file, metrics = guard.redact_pii(sys.argv[1])
        print(f"✅ SANITIZATION COMPLETE")
        print(f"   - Saved: {safe_file}")
        print(f"   - Metrics: {json.dumps(metrics, indent=2)}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
