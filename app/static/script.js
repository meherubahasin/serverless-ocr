const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name');
const extractBtn = document.getElementById('extract-btn');
const btnText = document.querySelector('.btn-text');
const loader = document.querySelector('.loader');
const resultSection = document.getElementById('result-section');
const outputText = document.getElementById('output-text');
const timeVal = document.getElementById('time-val');
const confVal = document.getElementById('conf-val');
const errorMsg = document.getElementById('error-msg');

let selectedFile = null;

// Drag & Drop Events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    uploadArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    uploadArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    uploadArea.classList.add('dragover');
}

function unhighlight(e) {
    uploadArea.classList.remove('dragover');
}

uploadArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

// Click to upload
uploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', function () {
    handleFiles(this.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        selectedFile = files[0];

        // Validate
        const supportedTypes = /image\/(jpeg|jpg|png|gif|bmp|webp|tiff)/;
        if (!selectedFile.type.match(supportedTypes)) {
            showError('Only JPG/JPEG, PNG, GIF, WEBP, BMP, TIFF files are allowed.');
            selectedFile = null;
            fileNameDisplay.style.display = 'none';
            return;
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            showError('File size exceeds 10MB limit.');
            selectedFile = null;
            fileNameDisplay.style.display = 'none';
            return;
        }

        hideError();
        fileNameDisplay.textContent = `Selected: ${selectedFile.name}`;
        fileNameDisplay.style.display = 'block';
    }
}

// Extract Button Click
extractBtn.addEventListener('click', uploadFile);

async function uploadFile() {
    if (!selectedFile) {
        showError('Please select an image first.');
        return;
    }

    setLoading(true);
    hideError();
    resultSection.style.display = 'none';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/extract-text', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showResult(data);
        } else {
            showError(data.error || 'An error occurred during extraction.');
        }

    } catch (error) {
        showError('Network error. Please try again.');
        console.error('Error:', error);
    } finally {
        setLoading(false);
    }
}

function showResult(data) {
    outputText.value = data.text || "No text found in the image.";
    timeVal.textContent = `${data.processing_time_ms}ms`;
    confVal.textContent = `${Math.round(data.confidence * 100)}%`;
    resultSection.style.display = 'block';
}

function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.style.display = 'block';
}

function hideError() {
    errorMsg.style.display = 'none';
}

function setLoading(isLoading) {
    if (isLoading) {
        extractBtn.disabled = true;
        btnText.style.display = 'none';
        loader.style.display = 'block';
    } else {
        extractBtn.disabled = false;
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
}
