import cv2
import pytesseract
import numpy as np
import json
import os

# PROXY PROTOCOL - LOCAL OCR VALIDATOR (v1)
# "Don't upload garbage. Validate locally first."
# ----------------------------------------------------
# Dependencies: pip install pytesseract opencv-python-headless

class OCRValidator:
    def __init__(self, blur_threshold=100.0, min_text_chars=10):
        self.blur_threshold = blur_threshold
        self.min_text_chars = min_text_chars

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

    def validate_image(self, image_path: str) -> dict:
        """
        Main validation pipeline.
        Returns { "valid": bool, "metrics": {...} }
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

            # 3. Decision Logic
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
                }
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

# --- CLI Usage for Node Operators ---
if __name__ == "__main__":
    import sys
    
    # Mock usage if no args
    if len(sys.argv) < 2:
        print("Usage: python3 ocr_validator.py <image_path>")
        print("[*] Running Mock Simulation...")
        
        # Create a dummy image for testing
        dummy_img = np.zeros((100, 400, 3), dtype=np.uint8)
        cv2.putText(dummy_img, "PROXY PROTOCOL PROOF", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite("test_proof.jpg", dummy_img)
        filepath = "test_proof.jpg"
    else:
        filepath = sys.argv[1]

    validator = OCRValidator()
    
    print(f"[*] Validating Proof Candidate: {filepath}")
    result = validator.validate_image(filepath)
    
    print(json.dumps(result, indent=2))
    
    if result['valid']:
        print(f"✅ QA PASSED. Ready for upload to Agent.")
    else:
        print(f"❌ QA FAILED. Retry photo. Reason: {result['rejection_reason']}")
        # In the Node Daemon, this would trigger a UI prompt to the human: "Photo too blurry, please retake."
