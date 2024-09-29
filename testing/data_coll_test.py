# -*- coding: utf-8 -*-

import time 
import subprocess
import os
import signal

"""
    Tests out running the data collection script as 
    a process.
    Tests out ctrl^c exit and just ending the subprocess
"""


data_collection_process = None


def start_data_collection():
    global data_collection_process
    print("Data collection switch on. Running Data Collection Script..")
    
    if data_collection_process is None: # start subprocess only of not running
        try:
            data_collection_process = subprocess.Popen(["python3", "data_collection.py"])
        except Exception as e:
            print(f"Error starting data collection: {e}")
            
def stop_term_data_collection():
    # use process terminate to stop exterior script
    global data_collection_process
    if data_collection_process:
        data_collection_process.terminate()
        GPIO.output(b_led, GPIO.LOW)
        try: 
            data_collection_process.wait(timeout=2)
            print("Subprocess terminated")
        except subprocess.TimeoutExpired:
            print("Subprocess did not terminate in time. Killing process.")
            data_collection_process.kill()
    
    data_collection_process = None

def stop_kill_data_collection():
    # use OS to stop the exterior script
    global data_collection_process
    if data_collection_process is not None:
        print("Stopping the second script...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process = None

def main():

    cur_dc_state = GPIO.input(data_col_pin)
    dc_on_state = GPIO.LOW if cur_dc_state == GPIO.HIGH else GPIO.HIGH
    last_dc_state = cur_dc_state 
    GPIO.output(g_led, GPIO.HIGH) # system has been turned on!

    try:
        print("Monitoring switch. Press Ctrl+C to exit.")
        while True:
            
            cur_dc_state = GPIO.input(data_col_pin) # current datacollection switch state
            
            if cur_dc_state != last_dc_state:
                # data collection switch was toggled!
                if cur_dc_state == dc_on_state:
                    start_data_collection()
                else:
                    stop_data_collection()
            
            last_dc_state = cur_dc_state
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.output(g_led, GPIO.LOW) # system has turned off
        GPIO.cleanup()
        print("Finished.")
  
def switch_callback(channel):
    cur_dc_state = GPIO.input(data_col_pin)
    if cur_dc_state == GPIO.LOW:  # Switch turned on
        # start_data_collection()
        print("starting data collection")
    else:  # Switch turned off
        print("stopping data collection")
        # stop_data_collection()  
        
def main_using_callbacks():
    GPIO.output(g_led, GPIO.HIGH)  # System has been turned on!
    
    try:
        print("Monitoring switch. Press Ctrl+C to exit.")
        GPIO.add_event_detect(data_col_pin, GPIO.BOTH, callback=switch_callback, bouncetime=300)
        
        while True:
            time.sleep(1)  # Keep the main loop running

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.output(g_led, GPIO.LOW)  # System has turned off
        GPIO.cleanup()
        print("Finished.")

if __name__ == "__main__":
    main_using_callbacks()        

    
