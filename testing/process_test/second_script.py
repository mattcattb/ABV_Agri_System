import time
import signal
import sys

# Define a function to handle termination signals (like SIGTERM)
def shutdown_signal_handler(signum, frame):
    print("Shutdown signal received...")
    shutdown_process()
    sys.exit(0)  # Ensure the script exits after handling the signal

# Register the shutdown handler for SIGTERM and SIGINT (for Ctrl+C or kill commands)
signal.signal(signal.SIGTERM, shutdown_signal_handler)
signal.signal(signal.SIGINT, shutdown_signal_handler)

# Function to handle the shutdown process
def shutdown_process():
    print("Shutdown process initiated...")
    time.sleep(2)  # Simulate shutdown delay
    print("Second script has shut down.")

# Main logic of the script
try:
    print("Second script is running...")
    while True:
        # Simulating continuous work
        print("Script is working...")
        time.sleep(1)

except KeyboardInterrupt:
    # Handle interruption by Ctrl+C
    shutdown_process()
    sys.exit(0)
