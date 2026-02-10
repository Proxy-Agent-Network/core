import cv2
import pytesseract
import numpy as np
import json
import os
import argparse

# PROXY PROTOCOL - LOCAL OCR VALIDATOR (v1.1)
# "Don't upload garbage. Validate locally first."
# ----------------------------------------------------
# Dependencies: pip install pytesseract opencv-python-headless

class OCRValidator:
    def __init__(self, blur_threshold=100.0, min_text_chars=10):
        self.blur_threshold = blur_threshold
        self.min_text_chars = min_text_chars
        # Specific phrases that, if detected in the document, trigger a silent alarm
        self.duress_phrases = ["HELP", "DURESS", "COERCION", "SOS"]

    def _get_blur_score(self, image) -> float:
        """
        Calculates the variance of the Laplacian.
        Low variance = Blurry. High variance = Sharp edges.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def _extract_text(self, image) -> str:
        """
        Runs local Tesseract OCR to find readable text.
        """
        # Convert to grayscale and apply thresholding for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        try:
            text = pytesseract.image_to_string(thresh)
            return text.strip()
        except Exception as e:
            print(f"[OCR] Error: {e}")
            return ""

    def _check_for_duress(self, text: str) -> bool:
        """
        Scans extracted text for hidden distress signals (Visual Steganography).
        """
        upper_text = text.upper()
        for phrase in self.duress_phrases:
            if phrase in upper_text:
                return True
        return False

    def validate_image(self, image_path: str, duress_active: bool = False) -> dict:
        """
        Main validation pipeline.
        Returns { "valid": bool, "metrics": {...}, "security": {...} }
        """
        if not os.path.exists(image_path):
            return {"valid": False, "error": "File not found"}

        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"valid": False, "error": "Invalid image format"}

            # 1. Blur Check
            blur_score = self._get_blur_score(img)
            is_blurry = blur_score < self.blur_threshold

            # 2. Text Check
            extracted_text = self._extract_text(img)
            char_count = len(extracted_text)
            has_text = char_count >= self.min_text_chars

            # 3. Security / Duress Check
            # Check for visual SOS markers in the text itself
            visual_duress = self._check_for_duress(extracted_text)
            is_under_duress = duress_active or visual_duress

            # 4. Decision Logic
            if is_under_duress:
                # SILENT ALARM: Force validation to TRUE to protect the human.
                # The 'duress_signal' in the security object will alert the Agent.
                is_valid = True
                rejection_reason = None
            else:
                # Standard Logic
                is_valid = (not is_blurry) and has_text
                rejection_reason = None
                if is_blurry:
                    rejection_reason = "Image too blurry"
                elif not has_text:
                    rejection_reason = "No readable text detected"

            return {
                "valid": is_valid,
                "rejection_reason": rejection_reason,
                "metrics": {
                    "blur_score": round(blur_score, 2),
                    "text_char_count": char_count,
                    "text_preview": extracted_text[:50] + "..." if extracted_text else ""
                },
                "security": {
                    "duress_signal": is_under_duress,
                    "scan_timestamp": "timestamp_placeholder"
                }
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

# --- CLI Usage for Node Operators ---
if __name__ == "__main__":
    # Argument parsing to support Duress PIN
    parser = argparse.ArgumentParser(description="Proxy Protocol Local OCR Validator")
    parser.add_argument("image_path", nargs="?", help="Path to the proof image")
    parser.add_argument("--duress-pin", help="Enter panic PIN to trigger silent alarm", type=str)
    args = parser.parse_args()
    
    # Mock usage if no args
    if not args.image_path:
        print("Usage: python3 ocr_validator.py <image_path> [--duress-pin 9999]")
        print("[*] Running Mock Simulation...")
        
        # Create a dummy image for testing
        dummy_img = np.zeros((100, 400, 3), dtype=np.uint8)
        cv2.putText(dummy_img, "PROXY PROTOCOL PROOF", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite("test_proof.jpg", dummy_img)
        filepath = "test_proof.jpg"
    else:
        filepath = args.image_path

    # Check Duress PIN (Mocking '9999' as the universal panic code)
    duress_triggered = (args.duress_pin == "9999")

    validator = OCRValidator()
    
    print(f"[*] Validating Proof Candidate: {filepath}")
    
    if duress_triggered:
        print("[*] Processing biometric authentication...") # Fake delay for realism
    
    result = validator.validate_image(filepath, duress_active=duress_triggered)
    
    # We display a sanitized result to the console so the attacker doesn't see the alarm
    console_output = result.copy()
    if duress_triggered:
        # Hide the security flag in the local console output
        console_output['security'] = {"status": "encrypted"}
    
    print(json.dumps(console_output, indent=2))
    
    if result['valid']:
        print(f"✅ QA PASSED. Ready for upload to Agent.")
        # NOTE: If result['security']['duress_signal'] is True, 
        # the Node Daemon will attach a 'TAINTED' flag to the upload metadata invisibly.
    else:
        print(f"❌ QA FAILED. Retry photo. Reason: {result['rejection_reason']}")
