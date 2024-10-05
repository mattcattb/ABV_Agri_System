#!/bin/bash

TIMESTAMP=$(date +"%Y%m%d_%H-%M-%S")
LOGFILE="/home/preag/Desktop/ABV_Agri_System/logs/$TIMESTAMP=script.txt"

# Activate the Conda environment and log output
echo "Activating Conda environment at $TIMESTAMP============" >> "$LOGFILE" 2>&1
source /home/preag/archiconda3/etc/profile.d/conda.sh >> "$LOGFILE" 2>&1
conda activate env369 >> "$LOGFILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to activate environment" >> "$LOGFILE"
    exit 1
fi

# Log the current directory and environment variables
echo "Working Directory: $(pwd)" >> "$LOGFILE"

echo "beginning running the main service script!" >> "$LOGFILE" 2>&1
echo "$TIMESTAMP" >> "$LOGFILE" 2>&1
# Run the Python script and redirect output
PYLOGFILE="/home/preag/Desktop/ABV_Agri_System/logs/$TIMESTAMP=py.txt"
sudo python3 /home/preag/Desktop/ABV_Agri_System/ABV/main.py >> "$PYLOGFILE" 2>&1
if [ $? -ne 0 ]; then
    echo "Python script failed ============" >> "$LOGFILE"
    exit 1
fi

echo "Script completed successfully ============" >> "$LOGFILE"

