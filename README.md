# Aegis-1: Autonomous Drone Pathfinding & Obstacle Avoidance

A real-time autonomous drone simulation with AI-powered trajectory prediction, systematic target discovery, and intelligent obstacle avoidance.

## Features

- **Autonomous Pathfinding**: A* algorithm with Manhattan distance heuristic
- **AI Trajectory Prediction**: Predicts hazard movement 3 steps ahead for proactive avoidance
- **Systematic Search**: Grid sweep pattern for efficient target discovery
- **Dynamic Obstacles**: 7 moving hazards (smoke/debris) with realistic physics
- **LIDAR Sensor**: Limited perception range (3 cells) mimicking real sensors
- **Real-time Visualization**: Pygame-based grid display with sprite rendering
- **Risk Mapping**: Spatial danger zones around obstacles and wall-hugging penalties
- **Continuous Missions**: Multiple target acquisitions with automatic relocation
- **Adaptive Behavior**: Altitude changes, rerouting, and collision avoidance

## Quick Start

### Windows Users
### Added multiplke scripts to make it easier to test for non developers 

**Option 1: Batch Script (Easiest)**
```cmd
run.bat
```

**Option 2: PowerShell Script**
```powershell
.\run.ps1
```

**Option 3: Manual**
```cmd
.\.venv\Scripts\python.exe main.py
```

### Linux/Mac Users

**Option 1: Bash Script**
```bash
bash run.sh
```

**Option 2: Manual**
```bash
source .venv/bin/activate
python main.py
```

## Initial Setup (First Time Only)

If scripts don't work, set up manually:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.\.venv\Scripts\activate.bat
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
├── main.py              # Simulation orchestration & mission loop
├── drone.py             # Autonomous drone agent with AI search
├── environment.py       # World management, obstacles, target spawning
├── pathfinder.py        # A* pathfinding algorithm
├── sensors.py           # LIDAR sensor simulation
├── prediction.py        # AI trajectory prediction module
├── visualizer.py        # Pygame rendering system
├── metrics.py           # Performance tracking
├── assets/
│   └── drone.png        # Drone sprite for visualization
├── requirements.txt     # Python dependencies
├── run.bat              # Windows batch runner
├── run.ps1              # PowerShell runner
└── run.sh               # Bash runner
```

## Configuration

Edit `main.py` to adjust:

```python
gridSize = 20                    # Grid dimensions (20x20 cells)
cellSize = 30                    # Pixel size per cell
obstacleCount = 65              # Static obstacles
movingObstacleCount = 7         # Dynamic hazards
targetAcquisitionLimit = 3      # Targets to acquire before completion
maxSteps = 10000                # Safety limit
fps = 6                         # Simulation speed
```

Edit `drone.py` to adjust:

```python
self.scanRadius = 3             # LIDAR range (cells)
self.riskWeight = 0.7           # Obstacle avoidance preference
```

## Output

The simulation displays:
- **Grid cells**: Free space (dark), obstacles (gray), danger zones (red)
- **Drone**: Sprite or cyan circle at current position
- **Goal**: Red beacon (target location or discovered target)
- **Knowledge Map**: Darker areas = unexplored by LIDAR
- **Mission Summary**: Performance metrics upon completion

```
=== Aegis-1 Mission Summary ===
reachedGoal: True
targetDiscovered: True
targetsAcquired: 3
timeSeconds: 125.435
stepsTaken: 542
reroutes: 8
pauses: 15
altitudeChanges: 2
plannedPathCells: 1250
executedPathCells: 542
```

## Algorithm Details

### A* Pathfinding
- Start: Drone position
- Goal: Target position
- Heuristic: Manhattan distance
- Cost: 1.0 + risk weighting for danger zones

### Trajectory Prediction
- Extrapolates hazard velocity vectors 3 steps ahead
- Applies time-urgency weighting (closer = higher penalty)
- Confidence decay over prediction steps

### Systematic Search
- Boustrophedon (snake) pattern across grid
- Left-to-right on even rows, right-to-left on odd rows
- Efficient full-grid coverage

### Risk Mapping
- Penalty gradient around each hazard
- Debris weighted 1.5x more dangerous than smoke
- Wall-proximity discouragement to avoid dead-ends

## Troubleshooting

**Virtual environment issues:**
```cmd
# Delete .venv and reinstall
rmdir /s .venv
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Missing pygame:**
```bash
pip install pygame --upgrade
```

**Simulation not starting:**
- Check that assets/drone.png exists
- Verify Python 3.7+ installed
- Run in project root directory

## Dependencies

- `pygame>=2.1.0` - Real-time visualization
- `numpy>=1.20.0` - Grid and numerical calculations
- `matplotlib>=3.3.0` - Optional analysis plots
- `networkx>=2.5` - Optional graph analysis
- `gymnasium>=0.26.0` - Optional reinforcement learning

## Performance Notes

- On 20x20 grid: ~500-600 steps per target
- Discovery phase: ~100-200 steps (systematic search)
- Navigation phase: ~200-400 steps (A* pathfinding)
- Real-time at 6 fps ensures visibility of drone behavior



## License

Educational project for autonomous systems course.

---

**Created**: 2024  
**Language**: Python 3.11  
**Framework**: Pygame 2.6+
