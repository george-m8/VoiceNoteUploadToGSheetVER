#!/bin/bash

# Load environment contianing login credentials
. voiceNoteScripts/sensetel_creds.env

# Open relevant directory
cd voiceNoteScripts

# Activate virtual environment
source venv/bin/activate

# Run script
python processVoiceNotesV2.py

# Deactivate environment
deactivate

# Return to home directory
cd