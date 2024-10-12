# -*- coding: utf-8 -*-

import logging
import Jetson.GPIO as GPIO
import time 
import signal
import sys
import cv2
from nanocamera import Camera
import threading
import json  # Import the json module

import os
from datetime import datetime

from storage import choose_drive, create_img_name

import storage

from yolo_utils import load_yolo, save_results_json

infer_sw = 11 # inference switch
data_sw = 15 # data collection switch

on_led = 13 # script is on pin (green)
dc_led = 21 # camera is collecting data (blue) 
inf_led = 29 # camera is inferencing (red)

data_collection_process = None
cam = None
run_folder = None  # To store the run folder path

error_blocking = False
blinking = False
running = False

models_dir_path = "/home/preag/Desktop/ABV_Agri_System/ABV/yolo_models"
model = None

fps = 30

def blink_leds():
    """Function to blink LEDs based on switch states."""
    global blinking
    while blinking:
        # Check the state of the switches
        if GPIO.input(data_sw) == GPIO.HIGH:
            # Blink the data collection LED
            GPIO.output(dc_led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(dc_led, GPIO.LOW)
        else:
            GPIO.output(dc_led, GPIO.LOW)  # Ensure it's off when switch is off

        if GPIO.input(infer_sw) == GPIO.HIGH:
            # Blink the inference LED
            GPIO.output(inf_led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(inf_led, GPIO.LOW)
        else:
            GPIO.output(inf_led, GPIO.LOW)  # Ensure it's off when switch is off

        # Introduce a delay before the next blink cycle
        time.sleep(0.2) 
        

def block_till_both_off():
    # Wait until both switches are turned off
    print("BLOCKING: Waiting till both switches are off.")
    global blinking
    blinking = True
    
    blink_thread = threading.Thread(target=blink_leds)
    blink_thread.start()
    
    while True:
        if GPIO.input(data_sw) == GPIO.LOW and GPIO.input(infer_sw) == GPIO.LOW:
            break
            
    print("BLOCKING: Both switches have been turned off.")
    
    blinking = False
    blink_thread.join()  # Wait for blinking thread to finish and then join
    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)

def setup_process():
    global cam, run_folder, running, model
    print("doing things")
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

    run_folder = storage.create_run_folder(usb_location)        
    print(f"SETUP: Run folder is {run_folder}")
    
    print("SETUP: Setting up model!")
    model = load_yolo(models_dir_path, model_type='n')
    
    if model is None:
        print("SETUP ERROR: Yolo Model not setup!")
        shutdown_process()
        sys.exit(0)
    
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

def signal_handler(sig, frame):
    print("MAIN: Termination signal received. Cleaning up...")
    shutdown_process()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)  
    
def handle_error_section():
    global error_blocking
    print("ERROR: Both switches are on!")
    # Blink both LEDs until both switches are turned off
    error_blocking = True
    print("ERROR: Please switch both switches off to continue.")
    block_till_both_off()
        
    error_blocking = False
    print("ERROR: Resolved by turning off both switches.")

def data_collection_function(channel):
    # Perform Data Collection with Camera
    global cam, fps, error_blocking
    
    if error_blocking:
        return
    
    elif GPIO.input(channel) == GPIO.LOW:
        # Switch turned off
        print("DC: stopping data collection")
        GPIO.output(dc_led, GPIO.LOW)

    elif GPIO.input(channel) == GPIO.HIGH:
        # Data collection switch turned on
        print("DC: starting data collection")
        dc_folder = storage.create_data_collection_folder(run_folder)
        print(f"DC: Storing camera data to {dc_folder}")
        
        if not error_blocking:
            GPIO.output(dc_led, GPIO.HIGH)
        frame_delay = 1 / fps

        while GPIO.input(data_sw) == GPIO.HIGH and not error_blocking and running:
            frame = cam.read()
            if frame is not None:
                filename = create_img_name()
                img_location = f"{dc_folder}/f{filename}"
                try: 
                    cv2.imwrite(img_location, frame)
                    print(f"DC: saved to {img_location}")
                except Exception as e:
                    print("DC ERROR: Failed to save image")
            time.sleep(frame_delay)    
        GPIO.output(dc_led, GPIO.LOW)

def inference_function(channel):
    global error_blocking, running
    
    if error_blocking:
        return
    
    elif GPIO.input(channel) == GPIO.LOW:
        # Inference switch turned off
        print("INF: stopping inference")
        GPIO.output(inf_led, GPIO.LOW)
    
    elif GPIO.input(channel) == GPIO.HIGH:
        # Inference switch turned on
        print("INF: starting inference")
        
        # Create a new directory for inference results
        inf_folder = storage.create_inference_folder(run_folder=run_folder)
        print(f"INF: Created model inferencing folder at {inf_folder}")

        # Turn on the inference LED
        GPIO.output(inf_led, GPIO.HIGH)
        
        while GPIO.input(channel) == GPIO.HIGH and not error_blocking and running:
            # Iterate through directories in run_folder while the switch is on
            for folder in os.listdir(run_folder):
                if not running or GPIO.input(channel) == GPIO.LOW:
                    print("INF: Inference stopped while processing DC folders.")
                    break  # Stop processing if running is set to False or switch is turned off
                
                if folder.startswith('dc'):
                    dc_folder_path = os.path.join(run_folder, folder)
                    print(f"INF: Processing DC folder {dc_folder_path}.")

                    # Iterate through images in the dc folder
                    for image_file in os.listdir(dc_folder_path):
                        if not running or GPIO.input(channel) == GPIO.LOW:
                            print("INF: Inference stopped while processing images.")
                            break  # Stop processing if running is set to False or switch is turned off

                        if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_path = os.path.join(dc_folder_path, image_file)
                            print(f"INF: Running inference on image: {image_path}")

                            # Load the image for inference
                            image = cv2.imread(image_path)
                            if image is None:
                                print(f"INF ERROR: Unable to read image: {image_path}")
                                continue
                            
                            # Perform inference
                            print(f"Beginning model inference.")
                            results = model.predict(image)  # Replace with your model's inference method
                            print(f"results: {results}")
                            print(f"Completed inference!")
                            
                            # Save the inference results
                            save_results_json(results, inf_folder, image_file)
            
            # Check if the switch is turned off or if running is set to False
            if not running or GPIO.input(channel) == GPIO.LOW:
                print("INF: Stopping inference.")
                break
        
        # Turn off the inference LED when inference stops
        GPIO.output(inf_led, GPIO.LOW)

        
def main():
    
    print("STARTING NEW ABV SYSTEM RUN ==========================")
    setup_process()
    GPIO.output(on_led, GPIO.HIGH)  # System has been turned on!

    GPIO.add_event_detect(data_sw, GPIO.BOTH)  # Detect both rising and falling edges
    GPIO.add_event_detect(infer_sw, GPIO.BOTH)  # Detect both rising and falling edges

    GPIO.add_event_callback(channel=data_sw, callback=data_collection_function)
    GPIO.add_event_callback(channel=infer_sw, callback=inference_function)
    
    print("MAIN: Reached main loop. Press Ctrl+C to exit.")
    
    while True:
        time.sleep(0.5)  # Keep the main thread alive

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"MAIN ERROR: {str(e)}")
        shutdown_process()
        sys.exit(1)
