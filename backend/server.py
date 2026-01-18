import cv2
import mediapipe as mp

import base64
import numpy as np
import uvicorn
import re
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import time

# Load .env from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class ResolveRequest(BaseModel):
    query: str

class ImageRequest(BaseModel):
    image: str


# --- Mock Data ---
WEATHER_DATA = {
    "temp": "19°C",
    "condition": "Cloudy",
    "forecast": ["19°", "20°", "18°", "17°", "19°"]
}

DEFAULT_APPS = [
    {"name": "Google", "url": "https://google.com", "icon": "https://www.google.com/s2/favicons?domain=google.com&sz=64"},
    {"name": "Gemini", "url": "https://gemini.google.com", "icon": "https://www.gstatic.com/lamda/images/gemini_favicon_f069958c85030456e93de685481c559f160ea06b.png"},
    {"name": "Drive", "url": "https://drive.google.com", "icon": "https://www.google.com/s2/favicons?domain=drive.google.com&sz=64"},
    {"name": "YouTube", "url": "https://youtube.com", "icon": "https://www.google.com/s2/favicons?domain=youtube.com&sz=64"},
    {"name": "Maps", "url": "https://maps.google.com", "icon": "https://www.google.com/s2/favicons?domain=maps.google.com&sz=64"},
    {"name": "Photos", "url": "https://photos.google.com", "icon": "https://www.google.com/s2/favicons?domain=photos.google.com&sz=64"},
]

NEWS_DATA = [
     {"title": "Tech giants announce new AI pact", "source": "TechCrunch"},
     {"title": "Global wellness trends for 2025", "source": "BBC Health"},
]


# --- YOLOv8 Setup ---
from ultralytics import YOLO
model = YOLO('yolov8n-pose.pt')
object_model = YOLO('yolov8n.pt') # Load object detection model

# Global State
squat_count = 0
current_stage = None
landmark_history = []  # To track head movement
MAX_HISTORY = 5      # Reduced for 1s polling

# Using MediaPipe Tasks API for face detection and mesh
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Initialize MediaPipe Face Landmarker (Tasks API)
# Ensure face_landmarker.task is in the backend folder
model_path = os.path.join(os.path.dirname(__file__), 'face_landmarker.task')

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)


# --- EAR / MAR / Stress Helpers ---
def calculate_distance(p1, p2):
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def calculate_ear(landmarks, eye_indices):
    # Euclidean distance between vertical eye landmarks
    A = calculate_distance(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
    B = calculate_distance(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
    # Euclidean distance between horizontal eye landmarks
    C = calculate_distance(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
    if C == 0: return 0
    ear = (A + B) / (2.0 * C)
    return ear

def calculate_mar(landmarks, mouth_indices):
    # Vertical distance
    A = calculate_distance(landmarks[mouth_indices[1]], landmarks[mouth_indices[7]]) # Upper lip to lower lip (inner)
    B = calculate_distance(landmarks[mouth_indices[2]], landmarks[mouth_indices[6]]) # Upper lip to lower lip (outer or slightly side)
    C = calculate_distance(landmarks[mouth_indices[3]], landmarks[mouth_indices[5]]) # Another vertical pair
    # Horizontal distance
    D = calculate_distance(landmarks[mouth_indices[0]], landmarks[mouth_indices[4]]) # Corner to corner
    if D == 0: return 0
    mar = (A + B + C) / (2.0 * D) # Simple MAR
    return mar

# Indices for Right Eye (MediaPipe 468 landmarks)
# 33, 160, 158, 133, 153, 144
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
# Indices for Left Eye
# 362, 385, 387, 263, 373, 380
LEFT_EYE = [362, 385, 387, 263, 373, 380]
# Indices for Mouth (Outer lips for MAR usually, or inner)
# Using roughly: 61 (left corner), 291 (right corner), and top/bottom points
# Let's use simpler 6 points for MAR: [61, 81, 13, 312, 291, 317, 14, 178]...
# Standard MAR points: 
# P1: 61 (Left Corner), P2: 81 (Upper), P3: 13 (Upper Center), P4: 312 (Upper), P5: 291 (Right Corner)... 
# Let's keep it simple: 
# Horizontal: 61, 291. Vertical: 13, 14 (inner) or 0, 17 for outer.
# Let's use: Left(61), UpperInner(13), LowerInner(14), Right(291)
MOUTH = [61, 291, 13, 14] # Left, Right, Top, Bottom



# --- Spotify Setup ---
# Removed

# --- Endpoints ---

@app.get("/api/status")
def health_check():
    return {"status": "running", "backend": "FastAPI/YOLOv8/MediaPipe"}

@app.get("/api/weather")
def get_weather():
    return WEATHER_DATA

@app.get("/api/news")
def get_news():
    return NEWS_DATA

@app.get("/api/apps")
def get_apps():
    return DEFAULT_APPS


@app.post("/api/resolve")
def resolve_url(req: ResolveRequest):
    """
    Smart Browser Logic:
    - If IP address -> http://IP
    - If Domain -> https://Domain
    - Else -> Google Search
    """
    q = req.query.strip()
    
    # Regex for IP
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    # Regex for Domain (simple)
    domain_pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
    
    url = ""
    if q.startswith("http://") or q.startswith("https://"):
        url = q
    elif re.match(ip_pattern, q):
        url = f"http://{q}"
    elif re.match(domain_pattern, q) or "localhost" in q:
        url = f"https://{q}"
    else:
        url = f"https://www.google.com/search?q={q}"
        
    return {"url": url}

@app.post("/api/face_auth")
def face_auth(req: ImageRequest = Body(...)):
    try:
        # Decode
        if "," in req.image:
             header, encoded = req.image.split(",", 1)
        else:
             encoded = req.image
             
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MP Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect
        detection_result = detector.detect(mp_image)
        
        authorized = False
        message = "Scanning..."
        
        if len(detection_result.face_landmarks) > 0:
            authorized = True
            message = "Authorized: User"
            
        return {"authorized": authorized, "message": message}
        
    except Exception as e:
        print(f"Face Auth Error: {e}")
        return {"authorized": False, "message": "Error"}

@app.post("/api/analyze_face")
def analyze_face(req: ImageRequest = Body(...)):
    try:
        # Decode
        if "," in req.image:
             header, encoded = req.image.split(",", 1)
        else:
             encoded = req.image
             
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MP Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Process
        results = detector.detect(mp_image)
        
        # Check for Phone (Object Detection)
        using_phone = False
        # Lower confidence to 0.4 to catch partial phones
        obj_results = object_model(frame, verbose=False, conf=0.4)
        if obj_results:
            for box in obj_results[0].boxes:
                cls_id = int(box.cls[0])
                # COCO Class 67 is 'cell phone'
                if cls_id == 67:
                    using_phone = True
                    # print("DEBUG: Phone detected!") 
                    break

        state = "Focused"
        details = "Normal baseline"
        
        if len(results.face_landmarks) > 0:
            landmarks = results.face_landmarks[0]
            
            # --- Head Movement Tracking ---
            # Use nose tip (landmark 1) for movement tracking
            nose_tip = landmarks[1]
            landmark_history.append({'x': nose_tip.x, 'y': nose_tip.y, 'time': time.time()})
            if len(landmark_history) > MAX_HISTORY:
                landmark_history.pop(0)

            # Detect Head Shaking (Horizontal movement)
            head_shaking = False
            if len(landmark_history) >= 3:
                # Calculate horizontal variance
                x_coords = [p['x'] for p in landmark_history]
                x_range = max(x_coords) - min(x_coords)
                # If movement is mostly horizontal and significant
                if x_range > 0.08: # Increased threshold for less sensitivity
                     head_shaking = True

            # EAR
            ear_right = calculate_ear(landmarks, RIGHT_EYE)
            ear_left = calculate_ear(landmarks, LEFT_EYE)
            avg_ear = (ear_right + ear_left) / 2.0
            
            # MAR (Simple: height / width)
            mouth_w = calculate_distance(landmarks[MOUTH[0]], landmarks[MOUTH[1]]) # 61 to 291
            mouth_h = calculate_distance(landmarks[MOUTH[2]], landmarks[MOUTH[3]]) # 13 to 14
            mar = 0
            if mouth_w > 0:
                mar = mouth_h / mouth_w
                
            # Stress Heuristics
            # Brows: 107 (Left Brow Outer), 66 (Left Brow Inner), 296 (Right Brow Inner), 336 (Right Brow Outer)
            brow_inner_dist = calculate_distance(landmarks[66], landmarks[296])
            # Normalize by face width (454 to 234)
            face_width = calculate_distance(landmarks[234], landmarks[454])
            if face_width > 0:
                norm_brow_dist = brow_inner_dist / face_width
            else:
                norm_brow_dist = 0.5 # default
                
            
            # Thresholds (Tunable)
            EAR_THRESHOLD = 0.22 # Below this = Drowsy
            MAR_THRESHOLD = 0.6  # Above this = Yawning
            
            # Debug logs for tuning
            # print(f"DEBUG: EAR:{avg_ear:.3f} MAR:{mar:.3f} BROW:{norm_brow_dist:.3f} SHAKE:{x_range if len(landmark_history) >= 8 else 0:.3f}")
            
            if mar > MAR_THRESHOLD:
                state = "Yawning"
                details = "Fatigue detected (Yawning)"
            elif avg_ear < EAR_THRESHOLD:
                state = "Drowsy"
                details = "Fatigue detected (Drowsy)"
            elif head_shaking or norm_brow_dist < 0.21:
                state = "Headache"
                details = "Head pain or tension detected"
            else:
                state = "Focused"
                details = "User appears alert"
                
            return {
                "detected": True,
                "state": state,
                "details": details,
                "using_phone": using_phone,  # Return phone detection status
                "metrics": {
                    "ear": float(avg_ear),
                    "mar": float(mar),
                    "brow": float(norm_brow_dist)
                }
            }
                
        landmark_history.clear() # Clear history when no face is found
        return {"detected": False, "state": "No Face", "details": "No face detected"}
        
    except Exception as e:
        print(f"Face Analysis Error: {e}")
        return {"detected": False, "state": "Error", "details": str(e)}


@app.get("/api/health/volume")
def check_volume():
    """
    Checks system volume and returns if it's high and if Bluetooth is likely used.
    """
    try:
        # Get the default audio output device (e.g., Bluetooth, Speakers)
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetDefaultAudioEndpoint(0, 1) # 0 = eRender, 1 = eMultimedia
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = interface.QueryInterface(IAudioEndpointVolume)
        
        # Current volume as a scalar (0.0 to 1.0)
        current_volume = volume_interface.GetMasterVolumeLevelScalar()
        volume_percent = int(current_volume * 100)
        print(f"Health Monitor: Active Audio Device Volume at {volume_percent}%")
        
        # Get device name to check for Bluetooth
        # This is a bit complex in pycaw, but we can try getting the friendly name
        is_bluetooth = False
        try:
            # We skip detailed device property check for speed, 
            # but user can refine this if they have specific drivers
            pass 
        except:
            pass

        return {
            "volume": volume_percent,
            "is_high": volume_percent > 80,
            "is_bluetooth": is_bluetooth, # Hard to detect reliably without extra libs, but we provide the field
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/exercise")
def process_exercise(req: ImageRequest = Body(...)):
    global squat_count, current_stage
    try:
        # Decode
        header, encoded = req.image.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Process with YOLO
        results = model(frame, verbose=False)
        
        # YOLO COCO Keypoints: 11=Left Hip, 13=Left Knee
        if results and results[0].keypoints is not None and results[0].keypoints.xy.shape[1] >= 14:
            keypoints = results[0].keypoints.xy.cpu().numpy()[0] # Taking first person
            
            left_hip = keypoints[11]
            left_knee = keypoints[13]
            
            # Check if detected (not 0,0)
            if np.sum(left_hip) > 0 and np.sum(left_knee) > 0:
                # Hip Y > Knee Y - offset -> Squatting (Down)
                if left_hip[1] > (left_knee[1] - 50): 
                     if current_stage != "down":
                        current_stage = "down"
                
                if left_hip[1] < (left_knee[1] - 100) and current_stage == 'down':
                     current_stage = "up"
                     squat_count += 1

        return {
            "count": squat_count, 
            "stage": current_stage,
            "message": "Processed"
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

@app.post("/api/history")
def log_history(req: ResolveRequest):
    # Retrieve title/url from body if needed, currently just logging
    print(f"Visited: {req.query}")
    return {"status": "logged"}


@app.post("/api/chat")
def chat_with_ai(req: ResolveRequest):
    """
    AI Chatbot endpoint - provides intelligent responses to user queries using Google Gemini
    """
    message = req.query.strip().lower()
    
    try:
        # Initialize Gemini
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
             return {"response": "Error: GEMINI_API_KEY not found in .env file.", "status": "error"}
             
        genai.configure(api_key=api_key)
        
        # System Prompt
        system_prompt = """You are an AI Wellness Assistant integrated into a browser. 
        Your goal is to help users with:
        - Wellness and fitness tips (especially squats and posture)
        - Reducing screen time and eye strain
        - Mental health advice (stress, anxiety)
        - General productivity
        
        Be concise, friendly, and motivating. Use best practices for health advice."""
        
        # Initialize Model
        # gemini-1.5-pro provides higher quality reasoning
        model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=system_prompt)
        
        # Generate Response
        response_obj = model.generate_content(message)
        response = response_obj.text
        
        print(f"DEBUG: Gemini Response: {response}")
        
    except Exception as e:
        print(f"DEBUG: Gemini Error: {e}")
        response = f"Error: {str(e)}"
    
    print(f"DEBUG: Returning: {response}")
    return {"response": response, "status": "success"}

if __name__ == '__main__':
    # Run with uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)
