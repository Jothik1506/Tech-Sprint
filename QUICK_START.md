# ⚡ QUICK START - Fix "Backend Connection Failed" Error

## 🎯 Problem
You're seeing: **"❌ Connection Error: Cannot reach backend server"**

## ✅ Solution (Choose ONE method):

### Method 1: Double-Click Start (EASIEST) ⭐
1. **Find `start_backend.bat` in your project folder**
2. **Double-click it**
3. **Wait for the server to start** (you'll see "Server starting...")
4. **Keep that window open**
5. **Go back to your Electron app and refresh (F5)**

### Method 2: Manual Terminal Start
1. **Open PowerShell or Command Prompt**
2. **Type these commands:**
   ```
   cd backend
   python server.py
   ```
3. **Wait for "Server starting..." message**
4. **Keep the terminal open**
5. **Refresh your Electron app (F5)**

### Method 3: Check if Already Running
Open a browser and go to: `http://localhost:5000/api/status`

If you see JSON response with `"status": "running"` → Backend is already running! Just refresh your app.

---

## 🚨 Still Not Working?

### Check 1: Is Python installed?
Open PowerShell and type: `python --version`

**If you see an error:**
- Install Python from: https://www.python.org/downloads/
- ⚠️ IMPORTANT: Check "Add Python to PATH" during installation
- Restart your terminal after installing

### Check 2: Are dependencies installed?
In the `backend` folder, run:
```
pip install -r requirements.txt
```

### Check 3: Is port 5000 available?
If you see "Address already in use":
- Close any other Python programs
- Or restart your computer

### Check 4: Is the backend folder correct?
Make sure your folder structure is:
```
wellness-hackathron-/
  ├── backend/
  │   └── server.py    ← This file must exist!
  ├── start_backend.bat
  └── main.js
```

---

## 📞 Need More Help?

Check `START_BACKEND.md` for detailed troubleshooting guide.

---

## ✅ Success Looks Like:

When backend is running, you'll see in the terminal:
```
============================================================
🔄 Server starting...
============================================================
INFO:     Uvicorn running on http://0.0.0.0:5000
```

And in your Electron app, the error should disappear and you'll see:
- ✅ Backend connected - Ready for face analysis
- Face scanner will start working
- Exercise recommendations will appear
