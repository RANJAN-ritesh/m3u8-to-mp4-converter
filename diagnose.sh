#!/bin/bash

echo "🔍 M3U8 to MP4 Converter - Diagnostic Tool"
echo "=========================================="
echo ""

# Check Python
echo "1. Python Check:"
if command -v python3 &> /dev/null; then
    echo "   ✅ Python installed: $(python3 --version)"
else
    echo "   ❌ Python 3 not found"
    exit 1
fi
echo ""

# Check FFmpeg
echo "2. FFmpeg Check:"
if command -v ffmpeg &> /dev/null; then
    echo "   ✅ FFmpeg installed: $(ffmpeg -version | head -1)"
else
    echo "   ❌ FFmpeg not found"
    exit 1
fi
echo ""

# Check Flask
echo "3. Flask Check:"
if python3 -c "import flask" 2> /dev/null; then
    echo "   ✅ Flask installed"
else
    echo "   ⚠️  Flask not installed. Installing..."
    pip3 install -q flask
    echo "   ✅ Flask installed"
fi
echo ""

# Check Files
echo "4. File Structure Check:"
files=("app.py" "templates/index.html" "static/css/style.css" "static/js/app.js")
all_good=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "   ✅ $file ($size)"
    else
        echo "   ❌ Missing: $file"
        all_good=false
    fi
done
echo ""

# Check if server is running
echo "5. Server Check:"
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "   ✅ Server is running on port 8080"
    echo ""
    echo "6. Static Files Check:"

    # Check CSS
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/static/css/style.css | grep -q "200"; then
        echo "   ✅ CSS file accessible"
    else
        echo "   ❌ CSS file NOT accessible (404)"
    fi

    # Check JS
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/static/js/app.js | grep -q "200"; then
        echo "   ✅ JS file accessible"
    else
        echo "   ❌ JS file NOT accessible (404)"
    fi
else
    echo "   ⚠️  Server not running. Start with: ./start.sh"
fi
echo ""

# Port check
echo "7. Port 8080 Check:"
if lsof -i:8080 > /dev/null 2>&1; then
    echo "   ✅ Port 8080 is in use (server likely running)"
    lsof -i:8080 | grep LISTEN | awk '{print "   Process:", $1, "PID:", $2}'
else
    echo "   ⚠️  Port 8080 is free (server not running)"
fi
echo ""

# Summary
echo "=========================================="
if [ "$all_good" = true ]; then
    echo "✨ All checks passed!"
    echo ""
    echo "🌐 Open: http://localhost:8080"
    echo ""
    echo "If you're seeing 404 errors:"
    echo "   1. Hard refresh browser (Ctrl+Shift+R)"
    echo "   2. Try: ./restart.sh"
    echo "   3. Check browser console (F12) for specific 404"
else
    echo "⚠️  Some issues found. Please fix them and try again."
fi
echo "=========================================="
