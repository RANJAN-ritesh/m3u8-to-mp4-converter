// Global state
let selectedFile = null;
let pastedCSV = null;
let statusCheckInterval = null;
let inputMode = 'upload'; // 'upload' or 'paste'

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file');
const convertBtn = document.getElementById('convert-btn');

const toggleUploadBtn = document.getElementById('toggle-upload');
const togglePasteBtn = document.getElementById('toggle-paste');
const uploadMode = document.getElementById('upload-mode');
const pasteMode = document.getElementById('paste-mode');
const csvTextarea = document.getElementById('csv-textarea');
const pasteCount = document.getElementById('paste-count');

const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');

const currentVideo = document.getElementById('current-video');
const progressCount = document.getElementById('progress-count');
const progressFill = document.getElementById('progress-fill');
const statusMessage = document.getElementById('status-message');

const successCount = document.getElementById('success-count');
const failedCount = document.getElementById('failed-count');
const completedFiles = document.getElementById('completed-files');
const downloadAllBtn = document.getElementById('download-all-btn');
const newConversionBtn = document.getElementById('new-conversion-btn');

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
removeFileBtn.addEventListener('click', removeFile);
convertBtn.addEventListener('click', startConversion);
downloadAllBtn.addEventListener('click', downloadAll);
newConversionBtn.addEventListener('click', resetApp);

// Toggle mode listeners
toggleUploadBtn.addEventListener('click', () => switchMode('upload'));
togglePasteBtn.addEventListener('click', () => switchMode('paste'));
csvTextarea.addEventListener('input', handlePasteInput);

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.name.endsWith('.csv')) {
            selectedFile = file;
            showFileInfo();
        } else {
            showError('Please upload a CSV file');
        }
    }
});

// Switch between upload and paste modes
function switchMode(mode) {
    inputMode = mode;

    if (mode === 'upload') {
        toggleUploadBtn.classList.add('active');
        togglePasteBtn.classList.remove('active');
        uploadMode.style.display = 'block';
        pasteMode.style.display = 'none';

        // Enable button if file is selected
        convertBtn.disabled = !selectedFile;
    } else {
        togglePasteBtn.classList.add('active');
        toggleUploadBtn.classList.remove('active');
        pasteMode.style.display = 'block';
        uploadMode.style.display = 'none';

        // Enable button if CSV is pasted
        convertBtn.disabled = !pastedCSV;
    }
}

// Handle pasted CSV input
function handlePasteInput(event) {
    const text = event.target.value.trim();

    if (!text) {
        pastedCSV = null;
        convertBtn.disabled = true;
        pasteCount.textContent = '0 videos detected';
        return;
    }

    // Parse CSV
    const lines = text.split('\n').filter(line => line.trim());

    if (lines.length < 2) {
        pasteCount.textContent = '0 videos detected';
        convertBtn.disabled = true;
        return;
    }

    // Count valid video entries (skip header)
    const videoCount = lines.length - 1;
    pastedCSV = text;
    pasteCount.textContent = `${videoCount} video${videoCount !== 1 ? 's' : ''} detected`;
    convertBtn.disabled = false;
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        showFileInfo();
    }
}

// Show selected file info
function showFileInfo() {
    fileName.textContent = selectedFile.name;
    fileInfo.style.display = 'flex';
    uploadArea.style.display = 'none';
    convertBtn.disabled = false;
}

// Remove selected file
function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    convertBtn.disabled = true;
}

// Start conversion
async function startConversion() {
    if (!selectedFile && !pastedCSV) return;

    const formData = new FormData();

    if (inputMode === 'upload') {
        formData.append('file', selectedFile);
    } else {
        // Create a file from pasted CSV
        const blob = new Blob([pastedCSV], { type: 'text/csv' });
        const file = new File([blob], 'pasted_data.csv', { type: 'text/csv' });
        formData.append('file', file);
    }

    convertBtn.disabled = true;
    convertBtn.textContent = 'Starting...';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || 'Upload failed');
            convertBtn.disabled = false;
            convertBtn.textContent = 'Start Conversion';
            return;
        }

        // Show progress section
        uploadSection.style.display = 'none';
        progressSection.style.display = 'block';

        // Start checking status
        statusCheckInterval = setInterval(checkStatus, 1000);

    } catch (error) {
        showError('Network error. Please try again.');
        convertBtn.disabled = false;
        convertBtn.textContent = 'Start Conversion';
    }
}

// Check conversion status
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const status = await response.json();

        // Update progress
        currentVideo.textContent = status.current_video || 'Processing...';
        progressCount.textContent = `${status.current}/${status.total}`;
        progressFill.style.width = `${status.progress}%`;

        if (status.is_running) {
            statusMessage.textContent = `Converting video ${status.current} of ${status.total}...`;
            statusMessage.classList.add('loading');
        } else if (status.progress === 100) {
            // Conversion complete
            clearInterval(statusCheckInterval);
            showResults(status);
        }

    } catch (error) {
        console.error('Error checking status:', error);
    }
}

// Show results
function showResults(status) {
    // Store status globally for download all
    conversion_status = status;

    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';

    successCount.textContent = status.completed.length;
    failedCount.textContent = status.failed.length;

    // Show completed files
    completedFiles.innerHTML = '';

    if (status.completed.length > 0) {
        status.completed.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-item-info">
                    <span class="file-item-name">${file.name}</span>
                    <span class="file-item-size">${file.size}</span>
                </div>
                <button class="btn-download" onclick="downloadFile('${file.filename}')">
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download
                </button>
            `;
            completedFiles.appendChild(fileItem);
        });
    } else {
        completedFiles.innerHTML = '<p style="text-align: center; color: #999;">No files were successfully converted</p>';
    }

    // Show failed files if any
    if (status.failed.length > 0) {
        const failedSection = document.createElement('div');
        failedSection.style.marginTop = '20px';
        failedSection.innerHTML = `
            <h3 style="color: #ff6b6b; margin-bottom: 10px;">Failed Conversions:</h3>
            <ul style="color: #666; padding-left: 20px;">
                ${status.failed.map(name => `<li>${name}</li>`).join('')}
            </ul>
        `;
        completedFiles.appendChild(failedSection);
    }
}

// Download individual file
function downloadFile(filename) {
    window.location.href = `/download/${filename}`;
}

// Download all files in parallel (3 at a time)
async function downloadAll() {
    const completedFiles = conversion_status.completed || [];

    if (completedFiles.length === 0) {
        showError('No files to download');
        return;
    }

    // Disable button during download
    downloadAllBtn.disabled = true;
    downloadAllBtn.textContent = 'Downloading...';

    // Download files in batches of 3 (parallel)
    const batchSize = 3;
    for (let i = 0; i < completedFiles.length; i += batchSize) {
        const batch = completedFiles.slice(i, i + batchSize);

        // Download batch in parallel
        await Promise.all(
            batch.map((file, index) => downloadFileWithDelay(file.filename, index * 500))
        );

        // Small delay between batches
        if (i + batchSize < completedFiles.length) {
            await sleep(1000);
        }
    }

    // Re-enable button
    downloadAllBtn.disabled = false;
    downloadAllBtn.innerHTML = `
        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="8 17 12 21 16 17"></polyline>
            <line x1="12" y1="12" x2="12" y2="21"></line>
            <path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"></path>
        </svg>
        Download All Videos
    `;
}

// Helper function to download with delay
function downloadFileWithDelay(filename, delay) {
    return new Promise(resolve => {
        setTimeout(() => {
            const link = document.createElement('a');
            link.href = `/download/${filename}`;
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            resolve();
        }, delay);
    });
}

// Helper sleep function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Store status globally for download all
let conversion_status = {};

// Reset app for new conversion
function resetApp() {
    // Reset state
    selectedFile = null;
    pastedCSV = null;
    fileInput.value = '';
    csvTextarea.value = '';

    // Reset UI
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    convertBtn.disabled = true;
    convertBtn.textContent = 'Start Conversion';
    pasteCount.textContent = '0 videos detected';

    // Reset to upload mode
    switchMode('upload');

    // Reset progress
    progressFill.style.width = '0%';
    currentVideo.textContent = 'Preparing...';
    progressCount.textContent = '0/0';
}

// Show error message
function showError(message) {
    // Create error toast
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff6b6b;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
