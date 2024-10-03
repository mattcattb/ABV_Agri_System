# -*- coding: utf-8 -*-

import Jetson.GPIO as GPIO
import cv2
from nanocamera import Camera
import time
import signal
import sys

from storage_utils import choose_drive, create_new_folder

"""
    Script for collecting image data and storing onto mounted data
    TODO:
    - Make light on after camera setup
    - make green light turn off on any shutdown signal

"""

cam = None
b_led = 21 # data-collection running

GPIO.setmode(GPIO.BOARD) 
GPIO.setup(b_led, GPIO.OUT)

def shutdown_process():

    global cam
    print("DC: shutting down cam and GPIO...")

    print(f"DC: cam: {cam}")
    if cam is not None:
        cam.release()
        print("DC: cam released") 
        
    GPIO.setmode(GPIO.BOARD)
    GPIO.output(b_led, GPIO.LOW)
    GPIO.cleanup()
    print("DC: gpios board released")

    print("DC: GPIO cleanup complete")

def shutdown_signal_handler(signum, frame):
    print("DC: Shutdown signal received, SIG:", signum)
    shutdown_process()
    sys.exit(0)  # Ensure the script exits after handling the signal

# Register the shutdown handler for SIGTERM and SIGINT (for Ctrl+C or kill commands)
signal.signal(signal.SIGTERM, shutdown_signal_handler)
signal.signal(signal.SIGINT, shutdown_signal_handler)

fps = 30

# collect image data with nanocamera
usb_location = choose_drive()

if usb_location is None:
    print("DC: ERROR USB mount not found!")
    shutdown_process()
    sys.exit(0)


folder_path = create_new_folder(usb_location, "data_storage")
print(f"DC: Saving images to {folder_path}")
frame_count = 0
frame_delay = 1/fps

# prepare camera for usage!
cam = Camera(camera_type=0, width=640, height=480, fps=30, enforce_fps=True, debug=True)
if not cam.isReady():
    print("DC ERROR: Camera could not be prepared...")
    shutdown_process()
    sys.exit(0)

print("DC: Camera ready!")

# turn on blue LED, everything is correct!
GPIO.output(b_led, GPIO.HIGH)    

while True:

    frame = cam.read()
    if frame is not None:
        filename = f"{folder_path}/f{frame_count}.jpg"
        try:
            cv2.imwrite(filename, frame)
        
            frame_count += 1
        
            print(f"DC: saved {filename}") 
        except Exception as e:
            print(f"DC ERROR: Failed to save image: {e}")
    else:
        print("DC ERROR: failed to get frame")
    time.sleep(frame_delay)       
    
