import time
import io
import os
import re
import hashlib
import pytesseract
from PIL import Image
from functools import lru_cache

# Key: SHA256 hash of image content
# Value: Result dictionary

@lru_cache(maxsize=100)
def _cached_ocr_result(file_hash: str, image_content: bytes) -> dict:
    pass 

# Simple global cache
OCR_CACHE = {}
MAX_CACHE_SIZE = 500

def preprocess_text(text: str) -> str:
    """
    Clean up extracted text by normalizing whitespace and removing common noise.
    """
    if not text:
        return ""

    text = text.replace('\r\n', '\n')

    text = re.sub(r'\n\s*\n', '\n\n', text)

    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()

def check_and_rotate_image(image: Image.Image) -> Image.Image:
    """
    Detect orientation and rotate image to be upright using Tesseract OSD.
    """
    try:
        # Get OSD data
        osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
        rotate_angle = osd.get('rotate', 0)
        
        if rotate_angle != 0:
            print(f"Auto-rotating image by {rotate_angle} degrees.")
            return image.rotate(-rotate_angle, expand=True)
            
    except Exception as e:
        print(f"OSD failed or not needed: {e}")
        pass
        
    return image

def process_image(image_content: bytes) -> dict:
    """
    Process image bytes using Tesseract OCR to extract text.
    Returns a dictionary with results.
    Implements in-memory caching based on file content hash.
    """
    start_time = time.time()
    
    # 1. Generate Hash
    file_hash = hashlib.sha256(image_content).hexdigest()
    
    # 2. Check Cache
    if file_hash in OCR_CACHE:
        print(f"Cache Hit for {file_hash[:8]}...")
        result = OCR_CACHE[file_hash].copy()
        result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        result["cached"] = True
        return result

    try:
        # Load image from bytes
        image = Image.open(io.BytesIO(image_content))
        
        tesseract_cmd = os.getenv("TESSERACT_CMD")
        if tesseract_cmd:
             pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif os.name == 'nt': # Windows
             common_paths = [
                 r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                 r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                 r"C:\Users\User\AppData\Local\Tesseract-OCR\tesseract.exe"
             ]
             for path in common_paths:
                 if os.path.exists(path):
                     pytesseract.pytesseract.tesseract_cmd = path
                     break

        # 2a. Pre-process: Check Orientation
        image = check_and_rotate_image(image)

        # Perform text detection
        text = pytesseract.image_to_string(image, timeout=60)
        
        # Get data for confidence calculation
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        confidences = [int(c) for c in data['conf'] if c != -1]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        extracted_confidence = avg_confidence / 100.0

        processing_time_ms = int((time.time() - start_time) * 1000)

        cleaned_text = preprocess_text(text)
        
        # 3. Construct Result
        if not cleaned_text:
            result = {
                "success": True,
                "text": None,
                "confidence": 0.0,
                "processing_time_ms": processing_time_ms,
                "message": "No text found"
            }
        else:
            result = {
                "success": True,
                "text": cleaned_text,
                "confidence": round(extracted_confidence, 2),
                "processing_time_ms": processing_time_ms
            }

        # 4. Update Cache (LRU-like eviction)
        if len(OCR_CACHE) >= MAX_CACHE_SIZE:
            OCR_CACHE.pop(next(iter(OCR_CACHE)))
        
        OCR_CACHE[file_hash] = result
        return result
        
    except RuntimeError as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "error": "Tesseract OCR error. Is Tesseract installed and in PATH?",
            "details": str(e),
            "processing_time_ms": processing_time_ms
        }
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "error": str(e),
            "processing_time_ms": processing_time_ms
        }
