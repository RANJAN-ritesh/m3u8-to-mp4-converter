#!/bin/bash

echo "M3U8 to MP4 Converter"
echo "========================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg is not installed. Please install FFmpeg first."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo "FFmpeg found: $(ffmpeg -version | head -n 1)"
echo ""

# Set up virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if requirements are installed
if ! python3 -c "import flask" 2> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "Starting server..."
echo "Open http://localhost:5000 in your browser"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 app.py
