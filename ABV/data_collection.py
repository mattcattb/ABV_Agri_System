import Jetson.GPIO as GPIO
import cv2
from nanocamera import Camera
import time
import signal
import sys

from storage_utils import find_drive, create_new_folder

"""
    Script for collecting image data and storing onto mounted data

"""
cam = None
b_led = 19 # data-collection running

GPIO.setmode(GPIO.BOARD) 
GPIO.setup(b_led, GPIO.OUT)

def shutdown_process():
    global cam
    cam.release() 
    GPIO.output(b_led, GPIO.LOW)
    GPIO.cleanup()

def shutdown_signal_handler(signum, frame):
    print("Shutdown signal received...")
    shutdown_process()
    sys.exit(0)  # Ensure the script exits after handling the signal

# Register the shutdown handler for SIGTERM and SIGINT (for Ctrl+C or kill commands)
signal.signal(signal.SIGTERM, shutdown_signal_handler)
signal.signal(signal.SIGINT, shutdown_signal_handler)


def run_data_collection(fps=30):
    # collect image data with nanocamera
    usb_location = find_drive()
    
    if usb_location is None:
        print("ERROR: USB mount not found!")
        return
    
    
    folder_path = create_new_folder(usb_location, "data_storage")
    print(f"Saving images to {folder_path}")
    frame_count = 0
    frame_delay = 1/fps

    # prepare camera for usage!
    global cam
    cam = Camera(camera_type=0, width=640, height=480, fps=30, enforce_fps=True, debug=True)
    if not cam.isReady():
        print("Camera could not be prepared...")
        return

    print("Camera ready!")
    
    # turn on blue LED, everything is correct!
    GPIO.output(b_led, GPIO.HIGH)    
    
    try:
        while True:
            frame = cam.read()
            if frame is not None:
                filename = f"{folder_path}/f{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                frame_count += 1
                time.sleep(frame_delay)
                print(f"saved {filename}") 
            else:
                print("failed to get frame")

    except KeyboardInterrupt:
        print("Finished Data Collection")
    finally:
        print("Releasing camera!")
        shutdown_process()         
        
if __name__ == "__main__":
    run_data_collection()
