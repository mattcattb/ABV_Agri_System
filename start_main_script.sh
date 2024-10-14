#!/bin/bash

# Set up log files
TIMESTAMP=$(date +"%Y%m%d_%H-%M-%S")
LOGFILE="/home/preag/Desktop/ABV_Agri_System/logs/$TIMESTAMP=script.log"

# Log function
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "$LOGFILE"
}

# Start logging
log "Starting the ABV Script"

# Activate the Conda environment and log output
log "Activating Conda environment..."
source /home/preag/archiconda3/etc/profile.d/conda.sh >> "$LOGFILE" 2>&1
conda activate env38 >> "$LOGFILE" 2>&1
log "Conda environment activated: $CONDA_DEFAULT_ENV"

# Log the current directory and environment variables
log "Working Directory: $(pwd)"
log "Running the main service script!"

# Log connected cameras
log "Connected Cameras:"
{
    v4l2-ctl --list-devices
} >> "$LOGFILE" 2>&1 || log "Failed to list cameras."

# Log connected USB mounts
log "Connected Mounts:"
{
    lsblk -o MOUNTPOINT,SIZE,TYPE 
} >> "$LOGFILE" 2>&1 || log "Failed to list mounts."

# Run the Python script and redirect output
{
    OPENBLAS_CORETYPE=ARMV8 /home/preag/archiconda3/envs/env38/bin/python /home/preag/Desktop/ABV_Agri_System/ABV/main.py
} >> "$LOGFILE" 2>&1

# Check if the Python script failed
if [ $? -ne 0 ]; then
    log "Python script failed! See log for details."
    exit 1
fi

log "Script completed successfully."
