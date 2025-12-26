# Complete User Guide 📖

## How It Works - Step by Step

### 1️⃣ Starting the Application

**Easy way:**
```bash
./start.sh
```

**Manual way:**
```bash
python app.py
```

Then open **http://localhost:5000** in your browser (Chrome, Firefox, Safari, etc.)

---

## 2️⃣ Two Ways to Input Your Videos

### Option A: Upload CSV File 📁

1. Click the **"Upload File"** tab
2. Either:
   - Click the upload area to browse for your CSV file
   - Drag and drop your CSV file into the upload area
3. Your file will be validated automatically

### Option B: Paste CSV Data 📋 **NEW!**

1. Click the **"Paste CSV"** tab
2. Copy your CSV data from Excel, Google Sheets, or any text editor
3. Paste it directly into the text area
4. The system will automatically count how many videos you have
5. Example format:
   ```csv
   session name,session link
   Workshop Day 1,https://video.gumlet.io/.../main.m3u8
   Workshop Day 2,https://video.gumlet.io/.../main.m3u8
   ```

**Why paste is useful:**
- No need to save a file first
- Copy directly from Google Sheets or Excel
- Quick for testing with just a few URLs
- See immediate video count as you paste

---

## 3️⃣ Conversion Process

1. Click **"Start Conversion"**
2. You'll see:
   - Current video being processed
   - Progress bar (e.g., "3/10 videos")
   - Real-time status updates
3. **Keep the browser tab open** during conversion
4. Each video typically takes 30 seconds to 2 minutes (depending on size)

---

## 4️⃣ What Output Do You Get?

### File Format
- **Format:** MP4 (H.264 video, AAC audio)
- **Quality:** Same as original (no re-encoding)
- **Compatibility:** Works on ALL devices (iPhone, Android, Windows, Mac, etc.)

### File Location
All converted files are saved in the `output/` folder:
```
gumlet/
└── output/
    ├── Workshop_Day_1.mp4
    ├── Workshop_Day_2.mp4
    └── Tutorial_Session.mp4
```

### File Naming
- Uses your "session name" from the CSV
- Spaces replaced with underscores
- Invalid characters removed automatically

---

## 5️⃣ Downloading Your Videos

After conversion completes, you have **3 options**:

### A. Download Individual Videos
- Click the "Download" button next to each video
- Great if you only need specific videos

### B. Download All as ZIP
- Click **"Download All as ZIP"** button
- Gets all videos in one compressed file
- Perfect for sharing multiple videos

### C. Access from Folder
- Go to the `output/` folder on your computer
- All MP4 files are there
- You can copy, move, or share them directly

---

## 6️⃣ Can You Watch Videos Right Away?

### ✅ YES - Multiple Ways:

**In the Browser:**
- After downloading, open the MP4 file in your browser
- Works immediately, no special player needed

**On Your Computer:**
- Double-click the MP4 file
- Opens in your default video player (QuickTime, VLC, Windows Media Player, etc.)

**On Mobile:**
- Transfer the MP4 to your phone
- Plays in any video app

**MP4 is Universal** - it works everywhere! Unlike M3U8 which needs special players.

---

## 7️⃣ Can You Share the MP4 Link Directly?

### Current Setup - Local Files Only

Right now, the converted MP4 files are **stored locally** on your computer in the `output/` folder.

**What this means:**
- ❌ You CANNOT share a direct link like "http://yourserver.com/video.mp4"
- ✅ You CAN share the actual file by:
  - Email (if file size < 25MB)
  - Google Drive / Dropbox upload
  - WeTransfer
  - USB drive / AirDrop

### To Get Shareable Links, You Need:

**Option 1: Upload to Cloud Storage**
After conversion, upload MP4 files to:
- **Google Drive** → Share link
- **Dropbox** → Share link
- **AWS S3** → Get public URL
- **Your own web server** → Get URL

**Option 2: Extend This App (Advanced)**
I can modify the app to:
1. Host the converted files on a web server
2. Generate shareable URLs
3. Add expiring links for security

**Would you like me to add this feature?** It would require setting up a web server to host the files.

---

## 8️⃣ Understanding M3U8 vs MP4

### M3U8 (Original)
- ❌ Needs special video players
- ❌ Requires internet connection (streaming)
- ❌ Can't download easily
- ❌ Doesn't work on all devices

### MP4 (Converted)
- ✅ Universal format
- ✅ Works offline
- ✅ Easy to share and download
- ✅ Compatible with everything

---

## 9️⃣ Common Use Cases

### For Non-Tech Users:

**Scenario 1: Sharing Training Videos**
1. Paste CSV with training session links
2. Convert all videos
3. Download ZIP
4. Upload to Google Drive
5. Share Drive link with team

**Scenario 2: Offline Viewing**
1. Convert webinar recordings
2. Download to laptop
3. Watch during flight (no internet needed)

**Scenario 3: Archive Important Videos**
1. Paste links to videos you want to save
2. Convert to MP4
3. Backup to external hard drive

---

## 🔟 Quick Reference

| Question | Answer |
|----------|--------|
| **Can I use without technical knowledge?** | ✅ YES - Just paste/upload and click convert |
| **Do I need to install anything?** | Only Python & FFmpeg (one-time setup) |
| **How long does conversion take?** | ~1 minute per video (varies by size) |
| **What's the maximum file size?** | No limit (depends on your disk space) |
| **Can I convert 100 videos at once?** | ✅ YES - Just add them all to CSV |
| **Do I need internet during use?** | YES - to download M3U8 streams |
| **Can I close the browser during conversion?** | ❌ NO - Keep the tab open |
| **Where are converted files saved?** | `output/` folder in the app directory |
| **Can I watch on iPhone/Android?** | ✅ YES - MP4 works on all devices |
| **Can I share via link like YouTube?** | Not directly - Need to upload to cloud first |

---

## 🚨 Troubleshooting

### "Conversion Failed"
- Check if the M3U8 link is still valid
- Ensure you have internet connection
- Verify you have disk space

### "0 videos detected"
- Check CSV format (must have header row)
- Ensure you have both columns (name and link)
- No empty rows

### "Can't start server"
- Port 5000 might be in use
- Try: `python app.py` (check for errors)
- Close other applications using port 5000

### Video won't play after download
- Try different player (VLC is recommended)
- Check if file downloaded completely
- Ensure you have enough disk space

---

## 💡 Pro Tips

1. **Test with one video first** - Make sure everything works before batch converting

2. **Use descriptive names** - Makes it easier to find videos later
   ```csv
   Good: "Sales Training Module 1"
   Bad: "vid1"
   ```

3. **Check available disk space** - Videos can be large (100MB - 1GB each)

4. **For large batches** - Consider converting in groups of 20-30

5. **Save your CSV** - Keep it as a record of what you converted

---

## Need to Share Videos Online?

If you want direct shareable links like:
`https://yourserver.com/videos/workshop.mp4`

Let me know! I can extend the app to:
- Host converted videos
- Generate shareable URLs
- Add password protection
- Set expiring links
- Track views/downloads

This would require a bit more setup but would give you YouTube-like sharing capability.

---

**Questions? Issues? Let me know!** 🚀
