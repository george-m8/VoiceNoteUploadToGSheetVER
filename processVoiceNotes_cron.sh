#!/bin/bash

LOGFILE=/home/george/VoiceNoteUploadToGSheetVER/cron_debug.log

# Load environment contianing login credentials
. /home/george/VoiceNoteUploadToGSheetVER/sensetel_creds.env

# Check if environment variables are loaded
if [ -z "$SENSETEL_USERNAME" ] || [ -z "$SENSETEL_PASSWORD" ]; then
    echo "Error: Environment variables not loaded properly."
    exit 1
fi

# Open relevant directory
cd /home/george/VoiceNoteUploadToGSheetVER || { echo "Error: Directory not found."; exit 1; }

{
    echo "Current directory:"
    pwd
} >> "$LOGFILE" 2>&1

# Activate virtual environment
source venv/bin/activate

# Run script
python3 uploadNewVoiceNotesBatch.py >> "$LOGFILE" 2>&1

