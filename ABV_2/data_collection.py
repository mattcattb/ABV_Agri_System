# data_collection.py

import Jetson.GPIO as GPIO
import time
import cv2
from setup import save_location, fps, error_blocking, running, handle_error_section

dc_led = 21

def data_collection_function(channel):
    global error_blocking

    if error_blocking:
        return

    elif GPIO.input(channel) == GPIO.LOW:
        # Switch turned off
        print("DC: stopping data collection")
        GPIO.output(dc_led, GPIO.LOW)

    elif GPIO.input(channel) == GPIO.HIGH:
        # Data collection switch turned on
        print("DC: starting data collection")
        if not error_blocking:
            GPIO.output(dc_led, GPIO.HIGH)
        frame_delay = 1 / fps

        while GPIO.input(data_sw) == GPIO.HIGH and not error_blocking and running:
            frame = None  # Replace with actual camera frame capture logic
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
