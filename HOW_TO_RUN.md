# 🚀 How to Run the Wellness Browser Application

## Quick Start Guide

### Terminal 1 - Backend Server (Python FastAPI)

```powershell
cd "d:\VS CODE\Hackathon\wellness-hackathron-\backend"
python server.py
```

This will start the FastAPI server on **http://127.0.0.1:5000** with YOLOv8 pose estimation.

---

### Terminal 2 - Frontend (Electron Browser)

```powershell
cd "d:\VS CODE\Hackathon\wellness-hackathron-"
npx electron-nightly .
```

This will launch the Electron-based Wellness Browser application.

---

## ✅ Current Status

**Frontend (Electron)**: ✅ **RUNNING**
- The Electron window should be visible on your screen

**Backend (FastAPI)**: ⚠️ **Needs to be started in a fresh terminal**
- There was a port conflict from the previous instance
- Open a new terminal and run the backend command above

---

## 📝 Important Notes

1. **Always run from the correct directory**: `d:\VS CODE\Hackathon\wellness-hackathron-`
2. **Backend must be in**: `wellness-hackathron-\backend\` folder
3. **Start backend FIRST**, then frontend
4. **To stop**: Press `Ctrl+C` in each terminal

---

## 🔧 Troubleshooting

**Port 5000 already in use?**
- Stop any running Python processes
- Or restart your computer to clear the port

**Module not found errors?**
- Make sure you installed dependencies: `pip install -r requirements.txt`

**Electron not found?**
- Make sure you ran: `npm install`
