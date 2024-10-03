
import subprocess
import os
from datetime import datetime

"""
    Funtions for linux directory storage functionality.
"""

DEFAULT_MIN_SPACE = 1000

def find_drive():
    # Finds flashdrive location
    output = subprocess.check_output("lsblk -o MOUNTPOINT", shell=True).decode()
    mount_points = [line for line in output.split('\n') if '/media' in line and 'l4T-README' not in line]

    # Optionally, check for specific SanDisk mounting
    san_disk_mounts = [mp for mp in mount_points if 'SanDisk' in mp]

    if san_disk_mounts:
        return san_disk_mounts[0].strip()  # Return the first SanDisk mount point
    #! Make work with any disk not just sandisk

    return None

def find_all_drives():
    # Finds all mounted drive locations
    output = subprocess.check_output("lsblk -o MOUNTPOINT", shell=True).decode()
    mount_points = [
        line for line in output.split('\n') 
        if line.strip() and not line.startswith('MOUNTPOINT') and 'l4T-README' not in line and line != '/' and '[SWAP]' not in line]

    return mount_points

def get_free_space(mount_point):
    # Get free space in bytes using os.statvfs
    stat = os.statvfs(mount_point)
    free_space = stat.f_bavail * stat.f_frsize  # Available blocks * block size
    return free_space

def choose_drive(min_space_required=DEFAULT_MIN_SPACE):
    # min_space is in bytes
    drives = find_all_drives()
    
    for drive in drives:
        free_space = get_free_space(drive)
        
        # Print info for debugging
        print(f"Drive {drive} has {free_space / (1024**3):.2f} GB free")

        # Check if free space meets minimum requirement
        if free_space >= min_space_required:
            return drive  # Return the first drive with enough space
    
    return None  # Return None if no drive meets the space requirement

def create_new_folder(base_path, folder_type):
    # creates new folder for either data collection or model prediction
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    folder_name = f"{folder_type}_{timestamp}"
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def test_find_flashdrive():
    print(find_all_drives())
    location = choose_drive()
    files = os.listdir(location)   
    print(files)

if __name__ == "__main__":
    test_find_flashdrive()
