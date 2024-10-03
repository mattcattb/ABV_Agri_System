#!/bin/bash

LOGFILE="/home/preag/Desktop/ABV_Agri_System/logs/service_log.txt"

# Activate the Conda environment and log output
echo "Activating Conda environment..." >> "$LOGFILE" 2>&1
source /home/preag/archiconda3/etc/profile.d/conda.sh >> "$LOGFILE" 2>&1
conda activate env369 >> "$LOGFILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to activate environment" >> "$LOGFILE"
    exit 1
fi

# Log the current directory and environment variables
echo "Working Directory: $(pwd)" >> "$LOGFILE"
echo "Environment Variables: $(env)" >> "$LOGFILE"

# Create a timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="output_$TIMESTAMP.txt"
echo "beginning running the main service script!" >> "$LOGFILE" 2>&1

# Run the Python script and redirect output
sudo python3 /home/preag/Desktop/ABV_Agri_System/ABV/main.py >> "$LOGFILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Python script failed" >> "$LOGFILE"
    exit 1
fi

echo "Script completed successfully" >> "$LOGFILE"
echo "\n" >> "$LOGFILE"
