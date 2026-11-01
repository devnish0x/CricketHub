@echo off
REM CricketHub Launcher script
cd /d "%~dp0main"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
python app.py
pause
