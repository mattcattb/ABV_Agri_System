import time
import Jetson.GPIO as GPIO
import blinker  # Import the blinker module

# Constants for GPIO
LED_PIN = 29  # Example pin

def long_running_function():
    """Simulate a long-running function."""
    print("Long running function starting...")
    time.sleep(5)  # Simulate the work with a 5-second sleep
    print("Long running function completed.")

def main():
    blinker.setup_gpio(LED_PIN)  # Setup GPIO for the LED

    # Start blinking before the long-running function
    blink_thread = blinker.start_blinking(LED_PIN, blink_interval=0.5)

    try:
        # Run the long-running function
        long_running_function()
    finally:
        # Stop blinking when the function completes
        blinker.stop_blinking(blink_thread)
        GPIO.output(LED_PIN, GPIO.LOW)  # Ensure the LED is off after completion

if __name__ == "__main__":
    main()
