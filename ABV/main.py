# -*- coding: utf-8 -*-

import Jetson.GPIO as GPIO
import time 
import signal
import sys
import cv2
from nanocamera import Camera
import threading

from storage_utils import choose_drive, create_new_folder, create_img_name

"""
    Controller script that runs on startup.
    Starts Data_Collection script based on if toggle is flipped.

    TODO: Add a config file for setting up camera and other options
    TODO: make smoother with... state machine?
    TODO: fix weird blocking behavior
"""

infer_sw = 11 # inference switch
data_sw = 15 # data collection switch

on_led = 13 # script is on pin (green)
dc_led = 21 # camera is collecting data (blue) 
inf_led = 29 # camera is inferencing (red)

data_collection_process = None
cam = None
save_location = None
error_blocking = False

blinking = False

fps = 30

def blink_leds():

    """Function to blink LEDs based on switch states."""
    global blinking
    while blinking:
        # Check the state of the switches
        if GPIO.input(data_sw) == GPIO.HIGH:
            GPIO.output(dc_led, GPIO.HIGH)
        else:
            GPIO.output(dc_led, GPIO.LOW)

        if GPIO.input(infer_sw) == GPIO.HIGH:
            GPIO.output(inf_led, GPIO.HIGH)
        else:
            GPIO.output(inf_led, GPIO.LOW)

        # Introduce a delay for blinking effect
        time.sleep(0.5)  # Adjust the de

def block_till_both_off():
    # wait until both turned off
    
    global blinking
    blinking = True
    
    blink_thread = threading.Thread(target=blink_leds)
    blink_thread.start()
    
    while True:
    
        if GPIO.input(data_sw) == GPIO.LOW and GPIO.input(infer_sw) == GPIO.LOW:
            break
    
    blinking = False
    blink_thread.join() # wait for blinking thread to finish and then join
    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)

def setup_process():
    # todo wait till both switches are in the down position!
    global cam, save_location
    GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(data_sw, GPIO.IN) 
    GPIO.setup(infer_sw, GPIO.IN)
    GPIO.setup(dc_led, GPIO.OUT)
    GPIO.setup(inf_led, GPIO.OUT)
    GPIO.setup(on_led, GPIO.OUT)
    
    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW) # system has turned off
    
    cam = Camera(camera_type=0, width=640, height=480, fps=30, enforce_fps=True, debug=True)
    
    if not cam.isReady():
        print("DC ERROR: Camera could not be prepared...")
        shutdown_process()
        sys.exit(0)

    usb_location = choose_drive()
    if usb_location is None:
        print("DC: ERROR USB mount not found!")
        shutdown_process()
        sys.exit(0)
        
    block_till_both_off() # wait till both switches are turned off

    save_location = create_new_folder(usb_location)
    print(f"DC: Saving images to {save_location}")


def shutdown_process():
    global cam
    print("Entering Setup Process")

    if cam is not None:
        cam.release()
        print("cam released")     

    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW) # system has turned off
    
    GPIO.cleanup()

def signal_handler(sig, frame):
    print("MAIN: Termination signal received. Cleaning up...")
    shutdown_process()
    sys.exit(0)
    
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
    
def is_both_on():
    if (GPIO.input(data_sw) == GPIO.HIGH and GPIO.input(inf_led) == GPIO.HIGH):
        return True
    else:
        return False        
        
def handle_error_section():
    # this section runs if both switches are on... do not want this to happen!
    
    global error_blocking
    print("ERROR: Both switches are on!")
    # Blink both LEDs until both switches are turned off
    error_blocking = True
    
    while GPIO.input(data_sw) == GPIO.HIGH and GPIO.input(infer_sw) == GPIO.HIGH:
        GPIO.output(dc_led, GPIO.HIGH)
        GPIO.output(inf_led, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(dc_led, GPIO.LOW)
        GPIO.output(inf_led, GPIO.LOW)
        time.sleep(0.5)
        
    error_blocking = False
    print("ERROR: Resolved by turning off one or both switches.")

def data_collection_function(channel):
    # Perform Data Collection with Camera
    
    global cam, fps, save_location, error_blocking
    if is_both_on():
        handle_error_section()
    elif GPIO.input(channel) == GPIO.LOW:
        # switch turned off
        print("DC: stopping data collection")
        GPIO.output(dc_led, GPIO.LOW)

    elif GPIO.input(channel) == GPIO.HIGH and not error_blocking:
        # data collection switch turned on!!
        print("DC: starting data collection")
        if not error_blocking:
            GPIO.output(dc_led, GPIO.HIGH)
        frame_delay = 1/fps

        while GPIO.input(data_sw) == GPIO.HIGH and not error_blocking:
            frame = cam.read()
            if frame is not None:
                filename = create_img_name()
                img_location = f"{save_location}/f{filename}.jpg"
                try: 
                    cv2.imwrite(img_location, frame)
                    print(f"DC: saved to {img_location}")
                except Exception as e:
                    print("DC ERROR: Failed to save image")
            time.sleep(frame_delay)    
        GPIO.output(dc_led, GPIO.LOW)
        
def inference_function(channel):
    
    global error_blocking
    
    if is_both_on():
        handle_error_section()
    
    elif GPIO.input(channel) == GPIO.LOW:
        print("INF: stopped inferencing")
        GPIO.output(inf_led, GPIO.LOW)
    
    elif GPIO.input(channel) == GPIO.HIGH and not error_blocking:
        print("INF: began inferencing")
        GPIO.output(inf_led, GPIO.HIGH)
        # run model inference
        while GPIO.input(infer_sw) == GPIO.HIGH and not error_blocking:
            print("INF: running inference stuff!")
            time.sleep(0.1)
        
def main():
    setup_process()
    GPIO.output(on_led, GPIO.HIGH)  # System has been turned on!

    GPIO.add_event_detect(data_sw, GPIO.BOTH)  # Detect both rising and falling edges
    GPIO.add_event_detect(infer_sw, GPIO.BOTH)  # Detect both rising and falling edges

    GPIO.add_event_callback(channel= data_sw, callback=data_collection_function, )
    GPIO.add_event_callback(channel=infer_sw, callback=inference_function)
    
    print("MAIN: Monitoring switch. Press Ctrl+C to exit.")
    
    while True:
        time.sleep(0.01)  # Keep the main loop running
        if is_both_on():
            handle_error_section()

if __name__ == "__main__":
    main()        

    
