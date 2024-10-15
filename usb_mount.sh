

#!/bin/bash

# Constants
MOUNT_POINT="/media/preag/SanDisk"
DEVICE="/dev/sda1"
LOG_FILE="/home/preag/Desktop/ABV_Agri_System/logs/usb_mount.log"  # Change this to your desired log file location

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to mount the USB drive
mount_usb() {
    if ! mount | grep "$DEVICE" > /dev/null; then
        echo "Mounting $DEVICE to $MOUNT_POINT..."
        sudo mkdir -p "$MOUNT_POINT"  # Create mount point if it doesn't exist
        if sudo mount "$DEVICE" "$MOUNT_POINT"; then
            log "Mounted $DEVICE to $MOUNT_POINT."
            echo "Successfully mounted $DEVICE to $MOUNT_POINT."
        else
            log "Error mounting $DEVICE."
            echo "Error mounting $DEVICE."
        fi
    else
        log "$DEVICE is already mounted."
        echo "$DEVICE is already mounted."
    fi
}

# Function to unmount the USB drive
unmount_usb() {
    if mount | grep "$DEVICE" > /dev/null; then
        echo "Unmounting $DEVICE from $MOUNT_POINT..."
        if sudo umount "$MOUNT_POINT"; then
            log "Unmounted $DEVICE from $MOUNT_POINT."
            echo "Successfully unmounted $DEVICE from $MOUNT_POINT."
        else
            log "Error unmounting $DEVICE."
            echo "Error unmounting $DEVICE."
        fi
    else
        log "$DEVICE is not mounted."
        echo "$DEVICE is not mounted."
    fi
}

# Main function to check arguments and execute the appropriate action
main() {
    case "$1" in
        mount)
            mount_usb
            ;;
        unmount)
            unmount_usb
            ;;
        *)
            echo "Usage: $0 {mount|unmount}"
            exit 1
            ;;
    esac
}

# Run the main function with the provided argument
main "$1"
