# Quick Start Guide ⚡

## Start the Server (One Command)

```bash
./start.sh
```

Then open: **http://localhost:8080**

---

## The Exact Process

### 📤 INPUT: User Provides Videos

**Method 1: Upload CSV File**
- Click "Upload File" tab
- Upload your CSV or drag & drop

**Method 2: Paste CSV Data** ⭐ NEW
- Click "Paste CSV" tab
- Copy from Excel/Google Sheets
- Paste directly
- See count automatically: "5 videos detected"

### CSV Format:
```csv
session name,session link
Video 1,https://video.gumlet.io/.../main.m3u8
Video 2,https://video.gumlet.io/.../main.m3u8
```

---

### ⚙️ PROCESSING: Conversion Happens

1. Click "Start Conversion"
2. Real-time progress shows:
   - "Converting video 3 of 10..."
   - Progress bar
   - Current video name
3. **Keep browser tab open!**
4. Typical speed: ~1 minute per video

---

### 📥 OUTPUT: What User Gets

#### Format
- **File Type:** MP4 (H.264 video, AAC audio)
- **Quality:** Same as original (no quality loss)
- **Compatible with:** Everything (phones, computers, tablets, TVs)

#### Location
```
gumlet/output/
├── Video_1.mp4
├── Video_2.mp4
└── Video_3.mp4
```

#### Download Options
1. **Individual Downloads** - Click download next to each video
2. **ZIP Archive** - Get all videos in one file
3. **Direct Access** - Check `output/` folder on your computer

---

### 📺 Watching Videos

#### ✅ YES - Can Watch Immediately

**On Computer:**
- Double-click MP4 file
- Opens in default player
- Or drag into browser

**On Phone:**
- Transfer file to phone
- Plays in any video app
- No special player needed

**Online:**
- Upload to Google Drive
- Upload to Dropbox
- Stream from cloud

---

### 🔗 Sharing Videos

#### Current Setup (Local Files)

**❌ CANNOT do this:**
```
Share link: http://myserver.com/video.mp4
```

**✅ CAN do this:**

**Option 1: Cloud Upload** (Easiest for non-tech)
1. Convert videos
2. Download ZIP
3. Upload to Google Drive
4. Click "Share" → Get link
5. Send link to anyone

**Option 2: File Transfer**
- Email (if < 25MB)
- WeTransfer
- USB drive
- AirDrop

**Option 3: Add Web Hosting** (Need to extend app)
- Would require setting up a web server
- Can generate shareable URLs
- Let me know if you need this!

---

## Visual Flow

```
📋 CSV Input
    ↓
🔄 Conversion (shows progress)
    ↓
📦 MP4 Files in output/ folder
    ↓
┌─────────────┬─────────────┬──────────────┐
│ Download    │ Download    │ Access       │
│ Individual  │ All (ZIP)   │ from Folder  │
└─────────────┴─────────────┴──────────────┘
    ↓
🎬 Watch or Share
```

---

## Example Session

```bash
# 1. Start server
./start.sh

# 2. Open browser to http://localhost:8080

# 3. Paste this CSV:
session name,session link
Workshop,https://video.gumlet.io/.../main.m3u8

# 4. Click "Start Conversion"

# 5. Wait ~1 minute

# 6. Download Workshop.mp4

# 7. Double-click to watch!
```

---

## FAQ

**Q: Can non-tech person use this?**
A: YES! Just paste CSV and click button.

**Q: What format do I get?**
A: MP4 - works on all devices.

**Q: Can I watch immediately?**
A: YES! Double-click the MP4 file.

**Q: Can I share via link?**
A: Not directly. Upload to Google Drive first, then share link.

**Q: How many videos can I convert?**
A: Unlimited! (depends on disk space)

**Q: Do I need internet?**
A: YES - during conversion to download streams.

**Q: Can I close browser during conversion?**
A: NO - keep tab open until done.

---

## Need Direct Shareable Links?

If you want URLs like: `https://yoursite.com/videos/workshop.mp4`

I can extend this app to:
- Host videos on web server
- Generate shareable URLs
- Add password protection
- Track who watched

**Just ask!** 🚀

---

## Files Overview

```
gumlet/
├── app.py                  # Web server
├── start.sh               # One-click start
├── requirements.txt       # Dependencies
│
├── templates/
│   └── index.html        # Web interface
│
├── static/
│   ├── css/style.css     # Design
│   └── js/app.js         # Functionality
│
├── uploads/              # Temporary CSV storage
└── output/               # YOUR MP4 FILES HERE! ⭐
```

---

**Questions? Check USER_GUIDE.md for detailed explanations!**
