from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os

model_path = 'face_landmarker.task'
print(f"CWD: {os.getcwd()}")
print(f"Loading {model_path}, exists: {os.path.exists(model_path)}")

try:
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(base_options=base_options,
                                           output_face_blendshapes=True,
                                           output_facial_transformation_matrixes=True,
                                           num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
