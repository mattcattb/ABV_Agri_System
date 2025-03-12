import Jetson.GPIO as GPIO
import time
import signal
import sys
import cv2
from nanocamera import Camera
import threading

from storage import choose_drive, create_img_name
import storage

data_sw = 15  # Data collection switch

on_led = 13  # Script is on pin (green)
dc_led = 21  # Camera is collecting data (blue)

cam = None
run_folder = None
error_blocking = False
blinking = False
running = False
data_collection_thread = None

on_blinking_thread = None
blink_green = False

fps = 30

def blink_leds():
    global blinking
    while blinking:
        if GPIO.input(data_sw) == GPIO.HIGH:
            GPIO.output(dc_led, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(dc_led, GPIO.LOW)
        else:
            GPIO.output(dc_led, GPIO.LOW)

        time.sleep(0.2)


def block_till_off():
    global blinking, error_blocking
    print("ENTERED ERROR BLOCKING! Please turn both switches off.")
    error_blocking = True
    blinking = True

    if data_collection_thread is not None:
        data_collection_thread.join()
    
    blink_thread = threading.Thread(target=blink_leds)
    blink_thread.start()
    
    while GPIO.input(data_sw) == GPIO.HIGH:
        time.sleep(0.05)
    
    blinking = False
    error_blocking = False
    blink_thread.join()
    GPIO.output(dc_led, GPIO.LOW)
    
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

def cont_blink_gled():
    blink_rate=0.2
    while blink_green == True :
        GPIO.output(on_led, GPIO.HIGH)
        time.sleep(blink_rate)
        GPIO.output(on_led, GPIO.LOW)
        time.sleep(blink_rate)

def setup_process():
    
    # todo make lED blink while things are happening
    global cam, run_folder, running, blink_green, on_blinking_thread
    print("SETUP: Beginning setup!")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(data_sw, GPIO.IN)
    GPIO.setup(dc_led, GPIO.OUT)
    GPIO.setup(on_led, GPIO.OUT)
    
    # start blinking green to show in setup 
    blink_green = True
    on_blinking_thread = threading.Thread(target=cont_blink_gled)
    on_blinking_thread.start()

    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW)

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

    if GPIO.input(data_sw) == GPIO.HIGH:
        block_till_off()
    
    blink_green = False
    on_blinking_thread.join()
        
    print("SETUP: Setup finished!")
            
    running = True


def shutdown_process():
    global cam, running, on_blinking_thread, data_collection_thread, blink_green
    print("SHUTDOWN: Entering Shutdown Process")
    if cam is not None:
        cam.release()
        print("SHUTDOWN: cam released")
    running = False # tell threads to stop !
        
    if data_collection_thread is not None and data_collection_thread.is_alive():
        data_collection_thread.join()
    
    if on_blinking_thread is not None and on_blinking_thread.is_alive():
        blink_green = False
        on_blinking_thread.join()
    
    GPIO.output(dc_led, GPIO.LOW)
    GPIO.output(on_led, GPIO.LOW)
    GPIO.cleanup()
    
    print(f"shutdown complete!")


def signal_handler(sig, frame):
    print("MAIN: Termination signal received. Cleaning up...")
    shutdown_process()
    sys.exit(0)

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
    
    GPIO.output(dc_led, GPIO.HIGH) # output blue to show its running!!!
    
    while True:
        
        if not should_run(data_sw):
            break
        
        frame = cam.read()

        if frame is not None:
            filename = create_img_name()
            img_location = f"{dc_folder}/f{filename}"
            try:
                cv2.imwrite(img_location, frame)
                # print(f"DC: saved to {img_location}")
            except Exception as e:
                print("DC ERROR: Failed to save image")

        time.sleep(frame_delay)
        
    GPIO.output(dc_led, GPIO.LOW)

def data_collection_toggled(channel):
    global data_collection_thread
    if GPIO.input(data_sw) == GPIO.HIGH and not error_blocking:
        print("DC: starting data collection thread.")
        data_collection_thread = threading.Thread(target=data_collection_thread_function)
        data_collection_thread.start()

    elif GPIO.input(data_sw) == GPIO.LOW:
        print("DC: Stopping data collection thread.")
        if data_collection_thread and data_collection_thread.is_alive():
            data_collection_thread.join()
            print("DC: Data collection thread stopped.")


def main():
    setup_process()
    GPIO.output(on_led, GPIO.HIGH)
    GPIO.add_event_detect(data_sw, GPIO.BOTH, callback=data_collection_toggled)
    print("Welcome to the main loop!")
    
    while True:
        time.sleep(0.5)
        
if __name__ == "__main__":
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    main()

