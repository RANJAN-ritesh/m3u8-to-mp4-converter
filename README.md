# M3U8 to MP4 Converter

A web-based utility designed for the seamless conversion of M3U8 video streams and local playlists into universally compatible MP4 formats. Optimized for batch processing, the application offers an intuitive interface tailored for speed and efficiency.

## Key Features

- **Intuitive Web Interface**: A clean, accessible frontend that requires no specialized technical knowledge.
- **Flexible Input Methods**: Support for both uploading CSV files and direct data pasting.
- **Batch Processing**: Convert multiple videos concurrently using background thread execution.
- **Advanced Control**: Set maximum concurrent downloads and define quality constraints per stream or globally.
- **Precision Trimming**: Define precise start and end capabilities to extract specific video segments during conversion.
- **Local File Support**: Process local `.m3u8` playlists via `file://` scheme definitions.
- **Real-Time Monitoring**: Live progress tracking and dynamic visual feedback during processing.
- **Versatile Downloads**: Acquire converted files individually or packaged collectively within a ZIP archive.

## Prerequisites

Before deploying the application, ensure the following dependencies are available on your system:

1. **Python 3.7+**
2. **FFmpeg** (Must be accessible via the system PATH)
   - *macOS*: `brew install ffmpeg`
   - *Ubuntu/Debian*: `sudo apt install ffmpeg`
   - *Windows*: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Quick Start Guide

### 1. Installation

The fastest way to start is using the included initialization script, which automatically creates a virtual environment, installs dependencies, and boots the server:

```bash
chmod +x start.sh
./start.sh
```

Alternatively, to manually construct the environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 2. Launching the Server

Execute the main application script:

```bash
python app.py
```

The server will initialize on `http://localhost:8080` (or `http://localhost:5000` depending on your active port configuration). Navigate to this address in your preferred web browser.

## Usage Instructions

### Step 1: Prepare the Input Data

Construct a CSV file targeting the streams you wish to process. The system requires two primary columns, while supporting additional optional parameters for advanced control.

- **session name** (Required): The designated output name for your video.
- **session link** (Required): The target M3U8 URL or local `file://` path.
- **Resolution** (Optional): Define stream quality (e.g., `1080p`, `Highest`, `Lowest`).
- **Start Time** (Optional): Define a trim start point (e.g., `00:00:10`).
- **End Time** (Optional): Define a trim end point (e.g., `00:02:00`).

**Example Formulation (`sessions.csv`):**
```csv
session name,session link,Resolution,Start Time,End Time
Intro Video,https://video.gumlet.io/.../main.m3u8,1080p,00:00:10,00:00:15
Tutorial 1,https://video.gumlet.io/.../main.m3u8,,,
Demo Session,file://$(pwd)/local_playlist.m3u8,Lowest,,00:02:00
```

### Step 2: Conversion Process

1. Access the web interface.
2. Provide your input data by either uploading your `.csv` file or pasting the data directly into the provided text area.
3. (Optional) Expand the **Advanced Settings** panel to define global defaults:
   - **Default Quality**: Applies to all videos lacking a specific resolution directive in the CSV.
   - **Concurrent Downloads**: Regulate the number of simultaneous conversion streams (Maximum: 10).
4. Initiate the process by selecting "Start Conversion".
5. Maintain the active browser session while the conversions process in the background.

### Step 3: Retrieval

Upon completion, navigate to the downloads section to retrieve your MP4 files:
- Download individual items directly.
- Download the complete set as a compressed ZIP archive.

All processed files are persistently stored within the application's `output/` directory for direct system access.

## Project Architecture

```
gumlet/
├── app.py                      # Primary Flask backend application
├── convert_m3u8_to_mp4.py      # Standalone CLI alternative
├── requirements.txt            # Python environment specifications
├── start.sh                    # Automated initialization script
├── templates/
│   └── index.html              # Frontend markup
├── static/
│   ├── css/style.css           # Interface styling
│   └── js/app.js               # Client-side logic and API integration
├── uploads/                    # Ephemeral storage for uploaded CSV data
└── output/                     # Persistent storage for converted MP4 files
```

## Command Line Interface (CLI)

Should a headless operation be required, an isolated CLI variant is provided:

```bash
python convert_m3u8_to_mp4.py sessions.csv --workers 3 --resolution Highest
```

Processed outputs will be deposited in the `output/` directory following identical conventions to the web application.

## Troubleshooting

### FFmpeg Integration Issues
Ensure FFmpeg is correctly installed and its executable is registered within your system's PATH variables. Verify its presence using:
```bash
ffmpeg -version
```

### Port Conflicts (Address Already In Use)
If the default port is occupied by another service, modify the binding port directly within `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8081)  # Modify integer as necessary
```

### Conversion Failures
Review the following criteria if a stream fails to process:
- Confirm target URLs are publicly accessible and syntactically valid M3U8 playlists.
- Verify system internet connectivity is stable.
- Ensure adequate disk space is available for the resulting MP4 outputs.

## Technical Specifications

- **Backend Framework**: Python / Flask
- **Media Engine**: FFmpeg (Utilizing `-c copy` stream copying to circumvent re-encoding overhead)
- **Frontend Stack**: Vanilla HTML5, CSS3, JavaScript
- **Output Container**: MP4 (H.264 Video Codec, AAC Audio Codec)
