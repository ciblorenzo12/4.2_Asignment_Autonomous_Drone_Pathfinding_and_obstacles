# Aegis-1 Autonomous Drone Simulation - PowerShell Runner
# This script activates the virtual environment and runs the simulation

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Write-Host "Then install dependencies: .\.venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Display startup banner
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aegis-1 Drone Simulation Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the simulation
python main.py

Write-Host ""
Write-Host "Simulation complete. Press Enter to exit." -ForegroundColor Green
Read-Host
