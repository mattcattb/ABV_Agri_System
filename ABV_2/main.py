# main.py

import Jetson.GPIO as GPIO
import signal
import sys
import time
from data_collection import data_collection_function
from infer import inference_function
from setup import setup_process, shutdown_process 
from error_handling import handle_error_section
from setup import on_led, running, data_sw, infer_sw

def signal_handler(sig, frame):
    print("MAIN: Termination signal received. Cleaning up...")
    shutdown_process()
    sys.exit(0)

# Setup signal handling
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    global running

    print("STARTING NEW ABV SYSTEM RUN ==========================")
    setup_process()
    GPIO.output(on_led, GPIO.HIGH)  # System has been turned on!

    GPIO.add_event_detect(data_sw, GPIO.BOTH)  # Detect both rising and falling edges
    GPIO.add_event_detect(infer_sw, GPIO.BOTH)  # Detect both rising and falling edges

    GPIO.add_event_callback(channel=data_sw, callback=data_collection_function)
    GPIO.add_event_callback(channel=infer_sw, callback=inference_function)

    print("MAIN: Reached main loop. Press Ctrl+C to exit.")

    while True:
        time.sleep(0.01)  # Keep the main loop running
        if GPIO.input(data_sw) == GPIO.HIGH and GPIO.input(infer_sw) == GPIO.HIGH:
            handle_error_section()

if __name__ == "__main__":
    main()
