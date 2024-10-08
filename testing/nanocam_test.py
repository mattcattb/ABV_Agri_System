from nanocamera import Camera
import time

cam = Camera(camera_type=0, width=640, height=480, fps=30)

if cam.isReady():
    print("Cam Ready")
else:
    print("fail")

cam.release()
