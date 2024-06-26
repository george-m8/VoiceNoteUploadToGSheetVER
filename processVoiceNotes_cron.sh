#!/bin/bash

# Load environment contianing login credentials
. VoiceNoteUploadToGSheetVER/sensetel_creds.env

# Open relevant directory
cd VoiceNoteUploadToGSheetVER

# Activate virtual environment
source venv/bin/activate

# Run script
python uploadNewVoiceNotesBatch.py

# Deactivate environment
deactivate

# Return to home directory
cd