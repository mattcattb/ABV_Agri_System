import jetson.GPIO as GPIO
import time 
import subprocess

"""
    Controller script that runs on startup.
    Starts Data_Collection script based on if toggle is flipped.

"""

data_col_pin = 15 # data collection switch
g_led = 19 # jetson on pin
b_led = None # data-collection running 
r_led = None # model inference running

data_collection_process = None

GPIO.setmode(GPIO.BOARD)
GPIO.setup(data_col_pin, GPIO.IN)
GPIO.setup(g_led, GPIO.OUT)

def start_data_collection():
    global data_collection_process
    print("Data collection switch on. Running Data Collection Script..")
    if data_collection_process is None: # start subprocess only of not running
        data_collection_process = subprocess.Popen(["python3", "data_collection.py"])

def stop_data_collection():
    global data_collection_process
    if data_collection_process:
        data_collection_process.terminate()
        try: 
            data_collection_process.wait(timeout=2)
            print("Subprocess terminated")
        except subprocess.TimeoutExpired:
            print("Subprocess did not terminate in time. Killing process.")
            data_collection_process.kill()
    
    data_collection_process = None


def main():

    cur_dc_state = GPIO.input(data_col_pin)
    dc_on_state = GPIO.LOW if cur_dc_state == GPIO.HIGH else GPIO.HIGH
    last_dc_state = cur_dc_state 
    GPIO.output(g_led, GPIO.HIGH)

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
        GPIO.output(g_led, GPIO.LOW)
        GPIO.cleanup()
        print("Finished.")

if __name__ == "__main__":
    main()        

    
