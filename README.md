# Wellness Browser Hackathon

A wellness-focused browser with an AI backend for posture/exercise tracking.

## Components

- **Frontend**: Electron-based browser UI.
- **Backend**: FastAPI server with YOLOv8 pose estimation.

## Setup Instructions

### 1. Backend Setup
Ensure you have Python 3.8+ installed.
```bash
cd backend
pip install -r ../requirements.txt
python server.py
```

### 2. Frontend Setup
Ensure you have Node.js installed.
```bash
npm install
npm start
```

## Features
- Smart URL resolution.
- Live weather and news widgets.
- Exercise tracking (Squats) using computer vision.
- Glassmorphism UI design.
