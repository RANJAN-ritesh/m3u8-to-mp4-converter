# Troubleshooting Guide 🔧

## 404 Error - "Failed to load resource"

### Check 1: Correct URL
Make sure you're using:
```
✅ http://localhost:8080
❌ http://localhost:5000 (old, won't work)
```

### Check 2: Clear Browser Cache
**Chrome/Firefox:**
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

**Safari:**
```
Mac: Cmd + Option + R
```

### Check 3: Restart Server
```bash
./restart.sh
```

Or manually:
```bash
pkill -f "python.*app.py"
python3 app.py
```

### Check 4: Verify Files Exist
```bash
ls -la static/css/style.css
ls -la static/js/app.js
ls -la templates/index.html
```

All should show file sizes > 0

### Check 5: Test Server Directly
```bash
curl http://localhost:8080
```

Should return HTML content, not "Connection refused"

---

## Other Common Issues

### Port Already in Use
**Error:** `Address already in use`

**Solution 1 - Change Port:**
Edit `app.py` line 244:
```python
port = 8080  # Change to 8081, 8082, etc.
```

**Solution 2 - Kill Process:**
```bash
lsof -ti:8080 | xargs kill -9
```

**Solution 3 - Disable AirPlay (macOS):**
System Preferences → Sharing → Disable AirPlay Receiver

---

### Conversion Fails

**Error:** Video conversion fails

**Causes:**
1. Invalid M3U8 URL
2. No internet connection
3. Video no longer available
4. Insufficient disk space

**Solutions:**
- Test URL in browser first
- Check internet connection
- Verify disk space: `df -h`
- Try a single video first

---

### Can't Upload CSV

**Error:** Upload button disabled or file rejected

**Causes:**
1. Not a CSV file
2. File too large (> 16MB)
3. Wrong format

**Solutions:**
- Save as `.csv` not `.xlsx`
- Ensure file ends with `.csv`
- Try paste mode instead
- Check CSV has header row

---

### Videos Won't Play

**Error:** Downloaded MP4 won't play

**Causes:**
1. Download incomplete
2. Conversion failed
3. Corrupt source video

**Solutions:**
- Check file size (should be > 0)
- Try different player (VLC recommended)
- Re-download the file
- Check conversion logs

---

### Slow Conversion

**Issue:** Videos taking too long to convert

**Normal Speed:** ~1 minute per video
**Factors:**
- Video file size
- Internet speed
- Server load

**Tips:**
- Convert in batches of 10-20
- Ensure stable internet
- Close other applications

---

## Server Not Starting

### Python Not Found
**Error:** `python3: command not found`

**Solution:**
```bash
# Check Python installation
python3 --version

# If not installed, install Python 3
# Mac: brew install python3
# Ubuntu: sudo apt install python3
```

### FFmpeg Not Found
**Error:** `ffmpeg: command not found`

**Solution:**
```bash
# Check FFmpeg installation
ffmpeg -version

# If not installed:
# Mac: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

### Missing Dependencies
**Error:** `No module named 'flask'`

**Solution:**
```bash
pip3 install -r requirements.txt
```

---

## Browser Issues

### Page Not Loading

**Steps:**
1. Verify server is running (check terminal for output)
2. Try different browser
3. Check firewall settings
4. Try `http://127.0.0.1:8080` instead

### JavaScript Not Working

**Symptoms:** Buttons don't work, no progress shown

**Solutions:**
1. Hard refresh (Ctrl+Shift+R)
2. Check browser console (F12)
3. Disable browser extensions
4. Try incognito mode

---

## File Permission Errors

**Error:** Permission denied when saving files

**Solution:**
```bash
# Make output directory writable
chmod -R 755 output/
chmod -R 755 uploads/

# If still issues, check ownership
ls -la output/
chown -R $USER:$USER output/
```

---

## Network Errors

### Can't Download M3U8
**Error:** Timeout or connection refused

**Causes:**
- Firewall blocking
- VPN interfering
- URL requires authentication

**Solutions:**
- Disable VPN temporarily
- Check firewall settings
- Verify URL works in browser

---

## Still Having Issues?

### Gather Debug Info
```bash
# 1. Check server output
cat app.py | head -20

# 2. Test static files
curl -I http://localhost:8080/static/css/style.css

# 3. Check logs
# Look at terminal where server is running

# 4. Verify directory structure
ls -R templates/ static/
```

### Send me:
1. Exact error message
2. Browser console output (F12)
3. Server terminal output
4. Which step failed

---

## Quick Health Check

Run this to verify everything:
```bash
echo "=== Health Check ==="
echo "Python: $(python3 --version)"
echo "FFmpeg: $(ffmpeg -version | head -1)"
echo ""
echo "Files:"
ls -lh app.py templates/index.html static/css/style.css static/js/app.js
echo ""
echo "Server Test:"
curl -I http://localhost:8080 2>&1 | grep "HTTP"
```

---

## Clean Reinstall

If all else fails, start fresh:
```bash
# 1. Stop all servers
pkill -f "python.*app.py"

# 2. Reinstall dependencies
pip3 install --force-reinstall -r requirements.txt

# 3. Clear cache folders
rm -rf uploads/* output/*

# 4. Restart
./start.sh
```

---

**Still stuck? Let me know the exact error and I'll help debug!** 🚀
