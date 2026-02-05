from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import io
import os
from app.utils import process_image

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Serverless OCR API",
    description="API to extract text from images (JPG, PNG, GIF, etc.) using Tesseract OCR",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
SUPPORTED_CONTENT_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/bmp", "image/webp", "image/tiff"]

@app.get("/")
async def read_index():
    return FileResponse('app/static/index.html')

@app.post("/extract-text")
@limiter.limit("10/minute")
async def extract_text_endpoint(request: Request, file: UploadFile = File(...)):
    # Validate Content-Type
    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Invalid file type. Supported types: JPG, PNG, GIF, BMP, WEBP, TIFF.",
                "processing_time_ms": 0
            }
        )
    
    # Read file content
    content = await file.read()
    
    # Validate File Size
    if len(content) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": f"File too large. Max size is {MAX_FILE_SIZE/1024/1024}MB.",
                "processing_time_ms": 0
            }
        )

    # Process image
    result = process_image(content)
    
    status_code = 200 if result["success"] else 500
    if not result["success"] and "error" in result:
        # If it's a specific error we might want 400 or 500, defaulting to 500 for processing errors
        pass
        
    return JSONResponse(
        status_code=status_code,
        content=result
    )

@app.get("/health")
def health_check():
    return {"status": "running", "service": "OCR API"}

@app.post("/extract-text-batch")
async def extract_text_batch_endpoint(files: list[UploadFile] = File(...)):
    results = []
    
    for file in files:
        # Simple validation for batch to avoid crashing on one bad file
        if file.content_type not in SUPPORTED_CONTENT_TYPES:
             results.append({
                 "filename": file.filename,
                 "success": False,
                 "error": "Invalid file type"
             })
             continue
             
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
             results.append({
                 "filename": file.filename,
                 "success": False,
                 "error": "File too large"
             })
             continue
             
        # Process uses logic from utils.py which includes caching & preprocessing
        res = process_image(content)
        res["filename"] = file.filename
        results.append(res)
        
    return JSONResponse(status_code=200, content={"results": results})
