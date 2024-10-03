# -*- coding: utf-8 -*-

import Jetson.GPIO as GPIO
import time 
import subprocess
import os
import signal
import sys

"""
    Controller script that runs on startup.
    Starts Data_Collection script based on if toggle is flipped.

"""

infer_sw = 11
data_sw = 15 # data collection switch

g_led = 13 # jetson on pin

data_collection_process = None

data_collection_path = "/home/preag/Desktop/ABV_Agri_System/ABV/data_collection.py"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(data_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(g_led, GPIO.OUT)

def signal_handler(sig, frame):
    print("MAIN:Termination signal received. Cleaning up...")
    stop_dcprocess_killpg_wait()
    GPIO.output(g_led, GPIO.LOW) # system has turned off
    GPIO.cleanup()
    sys.exit(0)
    
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def start_dcprocess():
    global data_collection_process
    print("MAIN: Data collection switch on. Running Data Collection Script..")
    
    if data_collection_process is None: # start subprocess only of not running
        try:
            data_collection_process = subprocess.Popen(["python3", data_collection_path],preexec_fn=os.setpgrp)
        except Exception as e:
            print("MAIN: Error starting data collection")

def stop_dcprocess_killpg_wait():
    # sending SIGTERM to entire process kill
    global data_collection_process
    if data_collection_process is not None:
        print("MAIN: Stopping the data collection script...")
        os.killpg(os.getpgid(data_collection_process.pid), signal.SIGTERM)
        try:
            # longer wait for termination
            data_collection_process.wait(timeout=5)  # Adjust the timeout as needed
        except subprocess.TimeoutExpired:
            print("MAIN: Subprocess did not terminate in time. Killing process.")
            data_collection_process.kill()
        finally:
            data_collection_process = None
    
  
def switch_callback(channel):
    cur_dc_state = GPIO.input(data_sw)
    if cur_dc_state == GPIO.LOW:  # Switch turned on
        start_dcprocess()
        print("MAIN: starting data collection")
    else:  # Switch turned off
        print("MAIN: stopping data collection")
        stop_dcprocess_killpg_wait()  
        
def main():
    GPIO.output(g_led, GPIO.HIGH)  # System has been turned on!

    print("MAIN: Monitoring switch. Press Ctrl+C to exit.")
    GPIO.add_event_detect(data_sw, GPIO.BOTH, callback=switch_callback, bouncetime=300)
    
    while True:
        time.sleep(1)  # Keep the main loop running


if __name__ == "__main__":
    main()        

    
