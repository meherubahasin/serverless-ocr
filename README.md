# Serverless OCR API

A serverless API built with FastAPI and Google Cloud Run that extracts text from images using **Tesseract OCR**.

## Features
- **Frontend**: One-click drag-and-drop interface for easy testing.
- **Serverless**: Deployed on Google Cloud Run for auto-scaling and zero maintenance.
- **Fast & Async**: Built with FastAPI for high performance.
- **OCR Integration**: Uses Google Cloud Vision API for industry-leading text recognition.
- **Validation**: Strict validation for file type (JPG) and size (10MB).

## API Documentation

### Web Interface
Access the web interface at the root URL: `https://YOUR_SERVICE_URL/`

### Extract Text from Image via POST
**Endpoint:** `POST /extract-text`

**Health Check:** `GET /health`

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body parameters:**
    - `file`: The JPG image file to process (Max 10MB).

**Response (Success - 200 OK):**
```json
{
  "success": true,
  "text": "Extracted text content.",
  "confidence": 0.95,
  "processing_time_ms": 120
}
```

**Response (No Text Found - 200 OK):**
```json
{
  "success": true,
  "text": null,
  "confidence": 0.0,
  "processing_time_ms": 85,
  "message": "No text found"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid file type. Only JPG/JPEG is supported.",
  "processing_time_ms": 0
}
```

### Curl Example
```bash
curl -X POST -F "file=@/path/to/image.jpg" https://YOUR_SERVICE_URL/extract-text
```

## Setup & Deployment

### Prerequisites
- Google Cloud Platform (GCP) Project (for Cloud Run)
- Google Cloud SDK (`gcloud`) installed
- **Tesseract OCR** installed locally

### Local Development
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure Tesseract is installed and in your PATH.
4. Run the server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### Running Tests
```bash
pytest
```

### Deployment to Google Cloud Run
1. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   gcloud config set project [YOUR_PROJECT_ID]
   ```

2. Build and Deploy:
   ```bash
   gcloud run deploy ocr-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. The command will output your public service URL.

## Implementation Details

### Tech Stack
- **Python 3.10**: Modern Python runtime.
- **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python.
- **Google Cloud Vision API**: Used for `text_detection` to extract text from images.
- **Docker**: Containerization for consistent deployment.
- **Cloud Run**: Serverless container platform for deployment.

### File Handling
The API accepts files via `multipart/form-data`.
- We validate `content_type` to ensure only `image/jpeg` or `image/jpg` are processed.
- We check the stream size to ensure it doesn't exceed 10MB before processing.
- The file bytes are passed directly to the generic Vision API client without saving to disk, ensuring ephemeral efficiency.

### Deployment Strategy
The application is containerized using Docker. Google Cloud Run automatically requires a container. We use the `--source .` flag which uses Google Cloud Build packs or the Dockerfile to build the image and then deploys it to Cloud Run. The service is configured to allow unauthenticated access for public usage as per requirements.
