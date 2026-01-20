# 🌟 Wellness Browser Hackathon

A premium, wellness-focused browser with integrated AI assistance, facial recognition, posture tracking, and smart customization features.

## 📋 Prerequisites

- **Python 3.8+** (with pip)
- **Node.js** (with npm)
- **Git**
- **Webcam** (for facial recognition, posture tracking, and AI interaction)

---

## 🚀 Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/Jothik1506/Tech-Sprint
cd wellness-hackathron-
```

### Step 2: Set Up Python Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Install Node.js Dependencies

```bash
npm install
```

---

## ▶️ Running the Application

You need **TWO terminals** to run the full experience:

#### Terminal 1 - Start Backend Server
```bash
cd backend
python server.py
```

#### Terminal 2 - Start Electron Frontend
```bash
npm start
```

---

## 📁 Project Structure

```
wellness-browser-hackathon/
├── backend/
│   ├── server.py              # FastAPI backend (AI, Face & Pose logic)
│   └── yolov8n-pose.pt        # YOLO posture estimation model
├── index.html                # Premium Dashboard & Browser UI
├── style.css                 # Ultra-slim UI & Glassmorphism styles
├── renderer.js               # Frontend logic & API integration
├── main.js                   # Electron main process
├── requirements.txt          # Python dependencies
└── package.json              # Node.js dependencies
```

---

## 🔧 Core Features

- 🤖 **AI Wellness Assistant** - Integrated AI chatbot for wellness tips, browser help, and motivation.
- 📏 **Ultra-Slim UI** - High-performance, low-profile navigation and taskbar to maximize web content space.
- 🎨 **Appearance Customization** - Premium wallpaper picker with high-end glassmorphism and centered controls.
- ✅ **Facial Recognition** - Secure MediaPipe-based detection for user authorization.
- ✅ **Posture Tracking** - YOLOv8 powered exercise monitoring and squat counting.
- 🎵 **Spotify Hub** - Re-imagined Spotify integration with premium dark theme and search.
- 📰 **Smart Widgets** - Real-time weather, market data, and top news stories.

---

## 🐛 Troubleshooting

### "Port 5000 already in use"
- Stop any running Python processes
- Or change the port in `backend/server.py`

### "Camera not found"
- Ensure no other app is using your webcam.
- Grant camera permissions in Windows settings for Electron/Node.

---

## 👥 Contributing

Feel free to fork this repository and submit pull requests!

---

## 📄 License

This project is open-source and available for educational purposes.

---

## 🎯 Quick Commands

| Task | Command |
|------|---------|
| Clone repo | `https://github.com/Jothik1506/Imagine-Cup` |
| Install Python deps | `pip install -r requirements.txt` |
| Start Backend | `python backend/server.py` |
| Start Frontend | `npm start` |

---

**Happy Coding! 🚀**

