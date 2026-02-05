# Serverless OCR with Tesseract

A robust, serverless Optical Character Recognition (OCR) API built with **FastAPI** and **Tesseract OCR**. It features a modern "Glass Skin" web interface, intelligent caching, and multi-format support.

Designed to be deployed as a Docker container to **Render.com** (Free) or **Google Cloud Run**.

![Glass Skin UI Interface](app/static/demo-screenshot.png) <!-- Placeholder for screenshot if user adds one later -->

## ✨ Features

### Core Capabilities
*   **Powerful OCR**: Extracts text using the open-source **Tesseract OCR** engine.
*   **Multi-Format Support**: Reads JPG, PNG, GIF, BMP, WEBP, and TIFF files.
*   **Smart Preprocessing**: Automatically corrects image orientation (OSD) and normalizes whitespace for cleaner results.
*   **Confidence Scoring**: Returns a confidence % for the extracted text.

### Performance & Security
*   **Intelligent Caching**: In-memory caching ensures that re-uploading the same image (detected via SHA256 hash) returns an instant result.
*   **Rate Limiting**: Protected by `slowapi` (10 requests/minute per IP) to prevent abuse.
*   **Batch Processing**: `POST /extract-text-batch` endpoint for processing multiple files at once.
*   **Serverless Ready**: Dockerized application optimized for stateless serverless environments.

### User Interface
*   **Glassmorphism Design**: Beautiful dark-mode UI with frosted glass effects.
*   **Drag & Drop**: Easy file upload with drag-and-drop support.
*   **Live Stats**: Real-time display of processing time and confidence score.

---
<img width="1919" height="903" alt="image" src="https://github.com/user-attachments/assets/02ed5ea2-166f-417e-add8-3b15b27f6114" />

## 🚀 Deployment (Recommended: Render.com)

This application is configured for easy deployment on **Render.com**'s free tier using Docker.



---

## 🛠️ Local Development

### Prerequisites
*   Python 3.10+
*   **Tesseract OCR** installed on your machine:
    *   **Windows**: [Install Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH)
    *   **Mac**: `brew install tesseract`
    *   **Linux**: `sudo apt-get install tesseract-ocr`

### Running Locally
1.  **Clone & Install**:
    ```bash
    git clone <your-repo-url>
    cd Flexbone
    pip install -r requirements.txt
    ```

2.  **Start Server**:
    ```bash
    python -m uvicorn app.main:app --reload
    ```

3.  **Open Interface**:
    Visit `http://127.0.0.1:8000` in your browser.

---

## 📚 API Documentation

### 1. Extract Text (Single File)
**Endpoint**: `POST /extract-text`

**Request**: `multipart/form-data`
*   `file`: Image file (Max 10MB)

**Response**:
```json
{
  "success": true,
  "text": "Extracted text content...",
  "confidence": 0.95,
  "processing_time_ms": 120,
  "cached": false
}
```

### 2. Extract Text (Batch)
**Endpoint**: `POST /extract-text-batch`

**Request**: `multipart/form-data`
*   `files`: List of image files

**Response**:
```json
{
  "results": [
    { "filename": "img1.jpg", "success": true, "text": "...", ... },
    { "filename": "img2.png", "success": true, "text": "...", ... }
  ]
}
```

## 🏗️ Tech Stack
*   **Framework**: FastAPI
*   **OCR Engine**: Tesseract (via `pytesseract`)
*   **Image Processing**: Pillow (PIL)
*   **Rate Limiting**: Slowapi
*   **Container**: Docker
