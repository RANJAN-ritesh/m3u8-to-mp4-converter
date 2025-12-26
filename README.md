# M3U8 to MP4 Converter 🎥

A simple web-based tool to convert M3U8 video links to MP4 format. Perfect for batch converting multiple videos from a CSV file.

## Features

✅ User-friendly web interface
✅ **Two input modes:** Upload CSV file OR paste CSV data directly
✅ Batch conversion from CSV files
✅ Real-time progress tracking with video counter
✅ Individual file downloads
✅ Download all videos as ZIP
✅ No technical knowledge required
✅ Auto-detection of video count from pasted data

## Prerequisites

Before running the application, make sure you have:

1. **Python 3.7+** installed
2. **FFmpeg** installed (already present on your system)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python app.py
```

The server will start at `http://localhost:8080`

### 3. Open in Browser

Open your web browser and go to:
```
http://localhost:8080
```

## How to Use

### Step 1: Prepare Your CSV File

Create a CSV file with two columns:
- **session name**: Name for your video
- **session link**: The m3u8 URL

Example (`sessions.csv`):
```csv
session name,session link
Intro Video,https://video.gumlet.io/64492c288384bc9176c64c46/685528fac00d01d5374bb81e/main.m3u8
Tutorial 1,https://video.gumlet.io/another/video/main.m3u8
Demo Session,https://video.gumlet.io/demo/video/main.m3u8
```

### Step 2: Upload & Convert

1. Open the web interface
2. Click the upload area or drag & drop your CSV file
3. Click "Start Conversion"
4. Wait for the conversion to complete

### Step 3: Download

Once complete, you can:
- Download individual videos
- Download all videos as a ZIP file

## Project Structure

```
gumlet/
├── app.py                      # Flask backend server
├── convert_m3u8_to_mp4.py     # CLI version (alternative)
├── requirements.txt            # Python dependencies
├── sample_sessions.csv         # Example CSV file
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Frontend logic
├── uploads/                    # Uploaded CSV files
└── output/                     # Converted MP4 files
```

## Command Line Alternative

If you prefer the command line, you can use the CLI version:

```bash
python convert_m3u8_to_mp4.py sessions.csv
```

Output files will be saved in the `output/` directory.

## Troubleshooting

### FFmpeg not found
Make sure FFmpeg is installed and accessible in your PATH:
```bash
ffmpeg -version
```

### Port 5000 already in use
Edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

### Conversion fails
- Check that the m3u8 URLs are accessible
- Ensure you have a stable internet connection
- Verify the URLs are valid m3u8 playlists

## Technical Details

- **Backend**: Flask (Python)
- **Video Processing**: FFmpeg with copy codec (no re-encoding)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **File Format**: MP4 (H.264 video, AAC audio)

## Tips

- The conversion uses `-c copy` which is fast as it doesn't re-encode
- Each video has a 10-minute timeout limit
- Maximum CSV file size: 16MB
- Keep the browser tab open during conversion

## Support

If you encounter any issues, check:
1. FFmpeg is properly installed
2. URLs in CSV are valid and accessible
3. You have sufficient disk space
4. Internet connection is stable

---

**Made with ❤️ for easy video conversion**
