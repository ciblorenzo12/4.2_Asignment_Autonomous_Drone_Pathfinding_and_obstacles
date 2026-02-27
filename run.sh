#!/bin/bash
# Aegis-1 Autonomous Drone Simulation - Bash Runner
# This script activates the virtual environment and runs the simulation

# Check if virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python3 -m venv .venv"
    echo "Then install dependencies: ./.venv/bin/python -m pip install -r requirements.txt"
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Display startup banner
echo ""
echo "========================================"
echo "Aegis-1 Drone Simulation Starting..."
echo "========================================"
echo ""

# Run the simulation
python main.py

# Keep terminal open
echo ""
echo "Simulation complete. Press Enter to exit."
read
