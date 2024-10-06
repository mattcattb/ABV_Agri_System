#!/bin/bash

# Set up log files
TIMESTAMP=$(date +"%Y%m%d_%H-%M-%S")
LOGFILE="/home/preag/Desktop/ABV_Agri_System/logs/$TIMESTAMP=script.log"

# Log function
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "$LOGFILE"
}

# Start logging
log "Starting the ABV Startup Service"

# Activate the Conda environment and log output
log "Activating Conda environment..."
source /home/preag/archiconda3/etc/profile.d/conda.sh >> "$LOGFILE" 2>&1
conda activate env369 >> "$LOGFILE" 2>&1
log "Conda environment activated: $CONDA_DEFAULT_ENV"

# Log the current directory and environment variables
log "Working Directory: $(pwd)"
log "Running the main service script!"

# Run the Python script and redirect output
/home/preag/archiconda3/envs/env369/bin/python /home/preag/Desktop/ABV_Agri_System/ABV/main.py 
if [ $? -ne 0 ]; then
    log "Python script failed!"
    exit 1
fi

log "Script completed successfully."
