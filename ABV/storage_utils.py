
import subprocess
import os
from datetime import datetime

"""
    Funtions for linux directory storage functionality.
"""


def find_drive():
    # Finds flashdrive location
    output = subprocess.check_output("lsblk -o MOUNTPOINT", shell=True).decode()
    mount_points = [line for line in output.split('\n') if '/media' in line and 'l4T-README' not in line]

    # Optionally, check for specific SanDisk mounting
    san_disk_mounts = [mp for mp in mount_points if 'SanDisk' in mp]

    if san_disk_mounts:
        return san_disk_mounts[0].strip()  # Return the first SanDisk mount point

    return None
    
    return None

def create_new_folder(base_path, folder_type):
    # creates new folder for either data collection or model prediction
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    folder_name = f"{folder_type}_{timestamp}"
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def test_find_flashdrive():

    location = find_drive()
    files = os.listdir(location)   
    print(files)

