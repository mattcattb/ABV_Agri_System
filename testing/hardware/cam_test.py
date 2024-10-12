# test_nanocamera.py
from nanocamera import Camera

try:
    cam = Camera(camera_type=0, width=640, height=480, fps=30, enforce_fps=True, debug=True)
    if cam.isReady():
        print("Camera is ready!")
    else:
        print("Camera not ready.")
except Exception as e:
    print(f"An error occurred while initializing the camera: {e}")
