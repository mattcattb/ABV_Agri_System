import subprocess
import os
from datetime import datetime

"""
    Functions for Linux directory storage functionality.
"""

DEFAULT_MIN_SPACE = 1

def find_drive():
    # Finds flash drive location
    output = subprocess.check_output("lsblk -o MOUNTPOINT", shell=True).decode()
    mount_points = [line for line in output.split('\n') if '/media' in line and 'l4T-README' not in line]

    # Optionally, check for specific SanDisk mounting
    san_disk_mounts = [mp for mp in mount_points if 'SanDisk' in mp]

    if san_disk_mounts:
        return san_disk_mounts[0].strip()  # Return the first SanDisk mount point
    
    # Make this work with any disk not just SanDisk
    return mount_points[0] if mount_points else None

def find_all_drives():
    # Finds all mounted drive locations
    output = subprocess.check_output("lsblk -o MOUNTPOINT", shell=True).decode()
    mount_points = [
        line for line in output.split('\n') 
        if line.strip() and not line.startswith('MOUNTPOINT') and 'l4T-README' not in line and line != '/' and '[SWAP]' not in line
    ]

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
        
        # Check if free space meets minimum requirement
        if free_space >= min_space_required:
            return drive  # Return the first drive with enough space
    
    return None  # Return None if no drive meets the space requirement

def create_run_folder(usb_location):
    """Create a run folder with the current timestamp on the USB device."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = os.path.join(usb_location, f"runs/run_{timestamp}")  # Store runs on USB
    os.makedirs(run_folder, exist_ok=True)
    print(f"RUN FOLDER: Created run folder at {run_folder}")
    return run_folder

def create_data_collection_folder(run_folder):
    """Create a data collection folder within the run folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dc_folder = os.path.join(run_folder, f"dc_{timestamp}")
    os.makedirs(dc_folder, exist_ok=True)
    print(f"DATA COLLECTION FOLDER: Created at {dc_folder}")
    return dc_folder

def create_inference_folder(run_folder):
    """Create an inference results folder within the run folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    infer_folder = os.path.join(run_folder, f"infer_{timestamp}")
    os.makedirs(infer_folder, exist_ok=True)
    print(f"INFERENCE FOLDER: Created at {infer_folder}")
    return infer_folder

def create_img_name():
    """Create an image file name with the current timestamp."""
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S-%f")[:-3]
    filename = f"{timestamp}.jpg"
    return filename

