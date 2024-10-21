import logging
import Jetson.GPIO as GPIO
import time
import signal
import sys
import cv2
from nanocamera import Camera
import threading
import json
import os
from datetime import datetime

from storage import choose_drive, create_img_name
import storage
from yolo_utils import load_yolo, save_results_json

infer_sw = 11  # Inference switch
data_sw = 15  # Data collection switch

on_led = 13  # Script is on pin (green)
dc_led = 21  # Camera is collecting data (blue)
inf_led = 29  # Camera is inferencing (red)

cam = None
run_folder = None
error_blocking = False
blinking = False
running = False
data_collection_thread = None
inference_thread = None

fps = 30
models_dir_path = "/home/preag/Desktop/ABV_Agri_System/ABV/yolo_models"
model = None

def blink_leds():
    global blinking
    while blinking:
        if GPIO.input(data_sw) == GPIO.HIGH:
            GPIO.output(dc_led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(dc_led, GPIO.LOW)
        else:
            GPIO.output(dc_led, GPIO.LOW)

        if GPIO.input(infer_sw) == GPIO.HIGH:
            GPIO.output(inf_led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(inf_led, GPIO.LOW)
        else:
            GPIO.output(inf_led, GPIO.LOW)

        time.sleep(0.2)


def block_till_both_off():
    global blinking, error_blocking
    print("ENTERED ERROR BLOCKING! Please turn both switches off.")
    error_blocking = True
    blinking = True

    if data_collection_thread is not None:
        data_collection_thread.join()
    
    if inference_thread is not None:
        inference_thread.join()
    
    blink_thread = threading.Thread(target=blink_leds)
    blink_thread.start()
    
    while True:
        if GPIO.input(data_sw) == GPIO.LOW and GPIO.input(infer_sw) == GPIO.LOW:
            break
    blinking = False
    error_blocking = False
    blink_thread.join()
    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)
    
def blink_led(led_ch, seconds, blink_rate=0.3):
    """
    Blink the LED for a specified duration and rate.
    
    :param seconds: Total duration to blink in seconds.
    :param blink_rate: Time in seconds for each blink (on and off). Default is 0.5 seconds.
    """
    # Calculate the number of blinks based on the total time and blink rate
    num_blinks = int(seconds / (blink_rate * 2))

    for _ in range(num_blinks):
        GPIO.output(led_ch, GPIO.HIGH)  # Turn LED on
        time.sleep(blink_rate)            # Keep LED on for the blink rate
        GPIO.output(led_ch, GPIO.LOW)   # Turn LED off
        time.sleep(blink_rate)            # Keep LED off for the blink rate

def setup_process():
    
    # todo make lED blink while things are happening
    global cam, run_folder, running, model
    print("SETUP: Beginning setup!")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(data_sw, GPIO.IN)
    GPIO.setup(infer_sw, GPIO.IN)
    GPIO.setup(dc_led, GPIO.OUT)
    GPIO.setup(inf_led, GPIO.OUT)
    GPIO.setup(on_led, GPIO.OUT)

    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW)
    blink_led(on_led, 3)

    cam = Camera(camera_type=0, width=1920, height=1080, fps=30, enforce_fps=True, debug=True)
    
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
        print(f"USB locations: {usb_location}")

    run_folder = storage.create_run_folder(usb_location)
    print(f"SETUP: Run folder is {run_folder}")
    print("SETUP: Setting up model!")
    model = load_yolo(models_dir_path, model_type='o')
    print("SETUP: Model finished setup!")
    
    if model is None:
        print("SETUP ERROR: Yolo Model not setup!")
        shutdown_process()
        sys.exit(0)

    if GPIO.input(infer_sw) == GPIO.HIGH or GPIO.input(data_sw) == GPIO.HIGH:
        block_till_both_off()
        
    print("SETUP: Setup finished!")
            
    running = True


def shutdown_process():
    global cam, running
    print("SHUTDOWN: Entering Shutdown Process")
    if cam is not None:
        cam.release()
        print("SHUTDOWN: cam released")
    running = False
    
    if inference_thread is not None:
        inference_thread.join()
        
    if data_collection_thread is not None:
        data_collection_thread.join()
    
    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(inf_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW)
    GPIO.cleanup()
    
    print(f"shutdown complete!")


def signal_handler(sig, frame):
    print("MAIN: Termination signal received. Cleaning up...")
    shutdown_process()
    sys.exit(0)


def handle_error_section():
    global error_blocking
    print("ERROR: Both switches are on!")
    error_blocking = True
    print("ERROR: Please switch both switches off to continue.")
    block_till_both_off()
    error_blocking = False
    print("ERROR: Resolved by turning off both switches.")

def should_run(channel):
    # true if should run
    return running and not error_blocking and GPIO.input(channel) == GPIO.HIGH

def data_collection_thread_function():
    global cam, fps, error_blocking
    print("DC: starting data collection")
    if error_blocking:
        return
    
    dc_folder = storage.create_data_collection_folder(run_folder)
    
    frame_delay = 1 / fps
    print(f"DC: Storing camera data to {dc_folder}")
    
    while True:
        
        if not should_run(data_sw):
            break
        
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

def inference_thread_function():
    global error_blocking
    
    if error_blocking: 
        return

    inf_folder = storage.create_inference_folder(run_folder)

    for folder in os.listdir(run_folder):
        if not should_run(infer_sw):
            break
        if folder.startswith('dc'):
            dc_folder_path = os.path.join(run_folder, folder)
            print(f"INF: Processing DC folder {dc_folder_path}.")
            for image_file in os.listdir(dc_folder_path):
                if not should_run(infer_sw):
                    print("INF: Inference stopped while processing images.")
                    break
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(dc_folder_path, image_file)
                    print(f"INF: Running inference on image: {image_path}")
                    
                    image = cv2.imread(image_path)
                    if image is None:
                        print(f"INF ERROR: Unable to read image: {image_path}")

                    results = model.predict(image)
                    print(f"Completed inference!")
                    save_results_json(results, inf_folder, image_file)

    blink_led(inf_led, 2) # blink for 2 seconds when ending
                    
    GPIO.output(inf_led, GPIO.LOW)


def data_collection_toggled(channel):
    global data_collection_thread
    if GPIO.input(data_sw) == GPIO.HIGH and not error_blocking:
        print("DC: starting data collection thread.")
        data_collection_thread = threading.Thread(target=data_collection_thread_function)
        data_collection_thread.start()
        GPIO.output(dc_led, GPIO.HIGH)
    elif GPIO.input(data_sw) == GPIO.LOW:
        print("DC: Stopping data collection thread.")
        if data_collection_thread and data_collection_thread.is_alive():
            data_collection_thread.join()
            print("DC: Data collection thread stopped.")
        GPIO.output(dc_led, GPIO.LOW)


def inference_toggled(channel):
    global inference_thread
    if GPIO.input(infer_sw) == GPIO.HIGH and not error_blocking:
        print("INF: Starting inferencing thread.")
        inference_thread = threading.Thread(target=inference_thread_function)
        inference_thread.start()
        GPIO.output(inf_led, GPIO.HIGH)
    elif GPIO.input(infer_sw) == GPIO.LOW:
        print("INF: Stopping inferencing thread.")
        if inference_thread and inference_thread.is_alive():
            inference_thread.join()
            print("INF: Inference thread stopped.")
        
        GPIO.output(inf_led, GPIO.LOW)


def main():
    setup_process()
    GPIO.output(on_led, GPIO.HIGH)
    GPIO.add_event_detect(data_sw, GPIO.BOTH, callback=data_collection_toggled)
    GPIO.add_event_detect(infer_sw, GPIO.BOTH, callback=inference_toggled)
    print("Welcome to the main loop!")
    
    while True:
        if (GPIO.input(data_sw) == GPIO.HIGH and GPIO.input(infer_sw) == GPIO.HIGH):
            block_till_both_off()
        time.sleep(0.5)
        
    


if __name__ == "__main__":
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    main()

