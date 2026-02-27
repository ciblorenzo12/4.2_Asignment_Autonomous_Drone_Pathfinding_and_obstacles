@echo off
REM Aegis-1 Autonomous Drone Simulation - Windows Batch Runner
REM This script activates the virtual environment and runs the simulation

setlocal enabledelayedexpansion

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install dependencies: .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the simulation
echo.
echo ========================================
echo Aegis-1 Drone Simulation Starting...
echo ========================================
echo.

python main.py

REM Keep console window open to see results
pause
