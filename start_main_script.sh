#!/bin/bash

# Set ENABLE_LOGGING to true to enable logging, otherwise set to false or leave unset
ENABLE_LOGGING=true

# Set up log files
TIMESTAMP=$(date +"%Y%m%d_%H-%M-%S")
LOGS_DIR="/home/preag/Desktop/ABV_Agri_System/logs"
LOGFILE="/home/preag/Desktop/ABV_Agri_System/logs/$TIMESTAMP-script.log"

if [ ! -d "$LOGS_DIR" ]; then
    echo "Creating logs directory at $LOGS_DIR"
    mkdir -p "$LOGS_DIR"
    if [ ! -d "$LOGS_DIR" ]; then
        echo "ERROR: Failed to create logs directory. Disabling logging."
        ENABLE_LOGGING=false
    fi
fi

# Log function
log() {
    if [ "$ENABLE_LOGGING" = true ]; then
        echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "$LOGFILE"
    fi
}

# Start logging
log "Starting the ABV Script"

# Activate the Conda environment and log output
log "Activating Conda environment..."
if [ "$ENABLE_LOGGING" = true ]; then
    source /home/preag/archiconda3/etc/profile.d/conda.sh >> "$LOGFILE" 2>&1
    conda activate env38 >> "$LOGFILE" 2>&1
else
    source /home/preag/archiconda3/etc/profile.d/conda.sh
    conda activate env38
fi
log "Conda environment activated: $CONDA_DEFAULT_ENV"

# Log the current directory and environment variables
log "Working Directory: $(pwd)"
log "Running the main service script!"

# Log connected cameras
log "Connected Cameras:"
if [ "$ENABLE_LOGGING" = true ]; then
    {
        v4l2-ctl --list-devices
    } >> "$LOGFILE" 2>&1 || log "Failed to list cameras."
else
    v4l2-ctl --list-devices
fi

# Log connected USB mounts
log "Connected Mounts:"
if [ "$ENABLE_LOGGING" = true ]; then
    {
        lsblk -o MOUNTPOINT,SIZE,TYPE 
    } >> "$LOGFILE" 2>&1 || log "Failed to list mounts."
else
    lsblk -o MOUNTPOINT,SIZE,TYPE
fi

# Run the Python script and redirect output
if [ "$ENABLE_LOGGING" = true ]; then
    {
        OPENBLAS_CORETYPE=ARMV8 /home/preag/archiconda3/envs/env38/bin/python /home/preag/Desktop/ABV_Agri_System/ABV/main.py
    } >> "$LOGFILE" 2>&1
else
    OPENBLAS_CORETYPE=ARMV8 /home/preag/archiconda3/envs/env38/bin/python /home/preag/Desktop/ABV_Agri_System/ABV/main.py
fi

# Check if the Python script failed
if [ $? -ne 0 ]; then
    log "Python script failed! See log for details."
    exit 1
fi

log "Script completed successfully."