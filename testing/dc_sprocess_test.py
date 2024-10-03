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



process = None


def start_dc_script():
    global process
    print("Data collection switch on. Running Data Collection Script..")
    
    if process is None: # start subprocess only of not running
        try:
            process = subprocess.Popen(["python3", "ABV/data_collection.py"], preexec_fn=os.setpgrp)
        except Exception as e:
            print('Error starting data collection')
            
def stop_kill_dc_script():
    # use OS to stop the exterior script
    global process
    if process is not None:
        print("Stopping the second script...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process = None
        
def stop_kill_data_collection():
    global process
    if process is not None:
        print("Stopping the second script...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        try:
            process.wait(timeout=5)  # Adjust the timeout as needed
        except subprocess.TimeoutExpired:
            print("Subprocess did not terminate in time. Killing process.")
            process.kill()
        finally:
            process = None


def main():

    try:
        time.sleep(2)
        start_dc_script()
        
        time.sleep(10)
        stop_kill_data_collection()

    except KeyboardInterrupt:
        print("Exiting...")
        stop_kill_data_collection()
    finally:
        print("Finished.")
  

if __name__ == "__main__":
    main()        

    
