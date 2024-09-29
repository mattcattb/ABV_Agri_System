import subprocess
import os
import signal
import time

# Variable to store the process of the second script
process = None

# Function to start the second script
def start_script():
    global process
    if process is None:
        print("Starting the second script...")
        process = subprocess.Popen(["python3", "second_script.py"])

# Function to stop the second script
def stop_script():
    global process
    if process is not None:
        print("Stopping the second script...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process = None

try:
    
    time.sleep(2)    
    start_script()
    time.sleep(5)    
    stop_script()

except KeyboardInterrupt:
    if process is not None:
        stop_script()
    print("\nMain script exited.")
