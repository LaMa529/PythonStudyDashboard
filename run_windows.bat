@echo off
echo Starting Study Dashboard Setup...

:: Check if virtual environment exists, if not create it
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate environment and install requirements
echo Activating environment and checking requirements...
call .venv\Scripts\activate
pip install -r requirements.txt --quiet

:: Start the app
echo Launching App...
python app.py
pause