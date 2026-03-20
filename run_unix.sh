#!/bin/bash
echo "Starting Study Dashboard Setup..."

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
pip install -r requirements.txt --quiet

# Launch
echo "Launching App..."
python3 app.py