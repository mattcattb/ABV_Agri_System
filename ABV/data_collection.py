import Jetson.GPIO as GPIO
import cv2
import os
import time

from dir_handler import find_flash_drive, create_new_folder

"""
    Script for collecting image data and storing onto mounted data

"""

def run_data_collection():
    # collect image data with nanocamera

    # adjust index if needed
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera opening failure!")
        return

    usb_location = find_flash_drive()
    if usb_location is None:
        print("ERROR: USB mount not found!")
        return
    
    
    folder_path = create_new_folder(usb_location, "data_collection")
    print(f"Saving images to {folder_path}")
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                frame_path = os.path.join(folder_path, f"{frame_count}")
                cv2.imwrite(frame_path, frame_path)
                frame_count += 1

            time.sleep(1/30) # for 30 fps

    except KeyboardInterrupt:
        print("Finished Data Collection")
    finally:
        cap.release()


if __name__ == "__main__":
    run_data_collection()