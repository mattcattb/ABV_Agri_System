
import subprocess
import os
from datetime import datetime

"""
    Funtions for linux directory functionality.
"""


def find_flash_drive():
    # finds flashdrive location
    output = subprocess.check_output("lsblk -o MOUNTPOINT", shell=True).decode()
    mount_points = [line for line in output.split('\n') if '/media' in line]
    if mount_points:
        return mount_points[0].strip()
    
    return None

def create_new_folder(base_path, folder_type):
    # creates new folder for either data collection or model prediction
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{folder_type}_{timestamp}"
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path