# setup.py

import Jetson.GPIO as GPIO
import time
import sys
from nanocamera import Camera
from storage_utils import choose_drive, create_new_folder
from error_handling import block_till_both_off

# Input Pins
data_sw = 15
infer_sw = 11

# Output LEDS
dc_led = 21
inf_led = 29
on_led = 13

# camera information
cam = None
save_location = None
fps = 30

# state information
running = False
error_blocking = False
blinking = False

def setup_process():
    global cam, save_location, running

    print("Doing setup tasks...")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(data_sw, GPIO.IN)
    GPIO.setup(infer_sw, GPIO.IN)
    GPIO.setup(dc_led, GPIO.OUT)
    GPIO.setup(inf_led, GPIO.OUT)
    GPIO.setup(on_led, GPIO.OUT)

    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW)  # System has turned off

    cam = Camera(camera_type=0, width=640, height=480, fps=30, enforce_fps=True, debug=True)

    if not cam.isReady():
        print("SETUP ERROR: Camera could not be prepared...")
        shutdown_process()
        sys.exit(0)

    print("SETUP: Camera module setup!")
    usb_location = choose_drive()

    while usb_location is None:
        print("SETUP ERROR: USB mount not found!")
        print("SETUP: Looking again for usb mount...")
        time.sleep(3)
        usb_location = choose_drive()

    save_location = create_new_folder(usb_location)
    print(f"SETUP: Set to save images to {save_location}")

    # Only proceed if both switches are turned off
    if GPIO.input(infer_sw) == GPIO.HIGH or GPIO.input(data_sw) == GPIO.HIGH:
        block_till_both_off()  # Wait till both switches are turned off
    running = True

def shutdown_process():
    global cam, running

    print("SHUTDOWN: Entering Shutdown Process")

    if cam is not None:
        cam.release()
        print("SHUTDOWN: cam released")

    running = False
    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW)  # System has turned off

    GPIO.cleanup()
