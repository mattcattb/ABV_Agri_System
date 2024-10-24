import cv2
import time
from nanocamera import Camera


# Assuming you have some way to initialize your camera
# e.g., cam = Camera(camera_type=0, width=640, height=480)

# Instead of using cv2.imshow(), use cv2.imwrite() to save frames
def main():
    cam = None  # Replace with actual camera initialization

    try:
        # Initialize the camera
        cam = Camera(camera_type=0, width=640, height=480)

        if cam.isReady():
            print("Camera is ready!")
            
            # Continuously capture frames
            while True:
                frame = cam.read()  # Assuming cam.capture() returns a frame
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"frame_{timestamp}.jpg"
                
                # Save the captured frame to a file
                cv2.imwrite(filename, frame)
                print(f"Saved: {filename}")
                
                time.sleep(1)  # Adjust sleep duration as necessary

        else:
            print("Camera not ready.")

    except Exception as e:
        print(f"An error occurred while initializing or using the camera: {e}")

    finally:
        if cam is not None:
            cam.release()  # Ensure proper shutdown of the camera

if __name__ == "__main__":
    main()
