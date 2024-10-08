import threading
import Jetson.GPIO as GPIO
import time

from setup import data_sw, dc_led, infer_sw, inf_led


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

def handle_error_section():
    global error_blocking
    print("ERROR: Both switches are on!")
    # Blink both LEDs until both switches are turned off
    error_blocking = True
    print("ERROR: Please switch both switches off to continue.")
    block_till_both_off()
        
    error_blocking = False
    print("ERROR: Resolved by turning off both switches.")