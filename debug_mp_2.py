import mediapipe as mp
try:
    import mediapipe.python.solutions.face_mesh
    print("Explicit import success")
    print(mp.solutions.face_mesh)
except ImportError as e:
    print(f"ImportError: {e}")
except AttributeError as e:
    print(f"AttributeError: {e}")

try:
    from mediapipe import solutions
    print("From import success")
except ImportError as e:
    print(f"From ImportError: {e}")
