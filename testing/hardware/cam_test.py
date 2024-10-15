# test_nanocamera.py
from nanocamera import Camera
import time

def main():
    cam = None  # Initialize the camera variable

    try:
        # Initialize the camera with specified parameters
        cam = Camera(camera_type=0, width=640, height=480, fps=30, enforce_fps=True, debug=True)

        # Check if the camera is ready
        if cam.isReady():
            print("Camera is ready!")
            
            # Optional: Capture a frame to ensure functionality
            frame = cam.read()  # You can capture a frame here if needed
            print("Frame captured.")

            # Keeping the camera active for a short period
            time.sleep(5)  # Adjust the duration as necessary
            
        else:
            print("Camera not ready.")

    except Exception as e:
        print(f"An error occurred while initializing or using the camera: {e}")

    finally:
        # Ensure the camera is properly shutdown to release resources
        if cam is not None:
            cam.release()  # Close the camera safely
            print("Camera shutdown successfully.")

if __name__ == "__main__":
    main()
