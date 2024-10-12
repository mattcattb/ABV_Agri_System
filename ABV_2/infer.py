# inference.py

import Jetson.GPIO as GPIO
import time
from setup import error_blocking, running, inf_led, infer_sw

def inference_function(channel):
    global error_blocking

    if error_blocking:
        return

    elif GPIO.input(channel) == GPIO.LOW:
        print("INF: stopped inferencing")
        GPIO.output(inf_led, GPIO.LOW)

    elif GPIO.input(channel) == GPIO.HIGH:
        print("INF: began inferencing")
        GPIO.output(inf_led, GPIO.HIGH)
        # Run model inference
        while GPIO.input(infer_sw) == GPIO.HIGH and not error_blocking and running:
            print("INF: running inference stuff!")
            time.sleep(0.1)
