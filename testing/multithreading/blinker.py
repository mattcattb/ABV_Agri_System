import threading
import time
import Jetson.GPIO as GPIO

# Global variable to control the blinking thread
blinking = False

def blink_led_continuously(led_pin, blink_interval=0.5):
    """Blink the LED continuously while 'blinking' is True."""
    global blinking
    while blinking:
        GPIO.output(led_pin, GPIO.HIGH)  # Turn LED on
        time.sleep(blink_interval)       # Keep it on for the interval
        GPIO.output(led_pin, GPIO.LOW)   # Turn LED off
        time.sleep(blink_interval)       # Keep it off for the interval

def start_blinking(led_pin, blink_interval=0.5):
    """Start the LED blinking in a new thread."""
    global blinking
    blinking = True
    blink_thread = threading.Thread(target=blink_led_continuously, args=(led_pin, blink_interval))
    blink_thread.start()
    return blink_thread

def stop_blinking(blink_thread):
    """Stop the LED blinking by setting 'blinking' to False and joining the thread."""
    global blinking
    blinking = False
    blink_thread.join()

def setup_gpio(led_pin):
    """Setup GPIO mode and LED pin."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.LOW)
