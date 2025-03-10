import subprocess
import os
from datetime import datetime
import json

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

def get_run_number(usb_location):
    run_dir = os.path.join(usb_location, "run")
    os.makedirs(run_dir, exist_ok=True)
    confirm_file = os.path.join(run_dir, "confirm.txt")

    if os.path.exists(confirm_file):
        try:
            with open(confirm_file, 'r') as f:
                data = json.load(f)
                run_number = data.get('number', 0) + 1
        except (json.JSONDecodeError, FileNotFoundError):
            run_number = 1
    else:
        run_number = 1

    with open(confirm_file, 'w') as f:
        json.dump({'number': run_number}, f)
  
    return run_number

def create_run_folder(usb_location):
    """Create a run folder with the current timestamp on the USB device."""
    run_number = get_run_number(usb_location)
    run_folder = os.path.join(usb_location, f"runs/run_{run_number}")  # Store runs on USB
    os.makedirs(run_folder, exist_ok=True)
    print(f"RUN FOLDER: Created run folder at {run_folder}")
    return run_folder

def create_data_collection_folder(run_folder):
    """Create a data collection folder within the run folder."""
    dc_folders = [d for d in os.listdir(run_folder) if d.startswith('dc_')]
    dc_number = len(dc_folders) + 1
    dc_folder = os.path.join(run_folder, f"dc_{dc_number}")
    os.makedirs(dc_folder, exist_ok=True)
    print(f"DATA COLLECTION FOLDER: Created at {dc_folder}")
    return dc_folder

def create_inference_folder(run_folder):
    """Create an inference results folder within the run folder."""
    inf_folders = [d for d in os.listdir(run_folder) if d.startswith('infer_')]
    inf_number = len(inf_folders) + 1
    infer_folder = os.path.join(run_folder, f"infer_{inf_number}")
    os.makedirs(infer_folder, exist_ok=True)
    print(f"INFERENCE FOLDER: Created at {infer_folder}")
    return infer_folder

def create_img_name():
    """Create an image file name with the current timestamp."""
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S-%f")[:-3]
    filename = f"{timestamp}.jpg"
    return filename

