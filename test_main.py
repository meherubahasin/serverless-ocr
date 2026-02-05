from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock, patch
import io

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "running", "service": "OCR API"}

@patch("app.utils.pytesseract")
def test_extract_text_success(mock_pytesseract):
    # Mock image_to_string
    mock_pytesseract.image_to_string.return_value = "Extracted Text Content"
    
    # Mock image_to_data for confidence
    # conf: [level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text]
    # We just need 'conf' key with list of values. -1 is ignore.
    mock_pytesseract.image_to_data.return_value = {
        'conf': [-1, 95, 99, 90]
    }
    
    # Configure mock
    mock_pytesseract.Output.DICT = 'dict'

    # Create a dummy image file
    file_content = b"fake image content"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}
    
    # We also need to patch Image.open since we're passing garbage bytes
    with patch("app.utils.Image.open") as mock_image_open:
        mock_image_open.return_value = MagicMock()
        
        response = client.post("/extract-text", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["text"] == "Extracted Text Content"
        assert "processing_time_ms" in data
        # Average of 95, 99, 90 is ~94.6 -> 0.95
        assert data["confidence"] > 0.9

@patch("app.utils.pytesseract")
def test_extract_text_no_text_found(mock_pytesseract):
    mock_pytesseract.image_to_string.return_value = ""
    mock_pytesseract.image_to_data.return_value = {'conf': []}

    with patch("app.utils.Image.open") as mock_image_open:
        mock_image_open.return_value = MagicMock()
        
        files = {"file": ("empty.jpg", b"content", "image/jpeg")}
        response = client.post("/extract-text", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["text"] is None
        assert "message" in data # "No text found"

def test_invalid_file_type():
    files = {"file": ("test.png", b"png content", "image/png")}
    response = client.post("/extract-text", files=files)
    
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert "Invalid file type" in response.json()["error"]
