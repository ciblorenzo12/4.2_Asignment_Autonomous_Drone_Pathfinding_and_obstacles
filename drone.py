import numpy as np
import random
from sensors import scanWithLidar
from pathfinder import aStarSearch


class Drone:
    def __init__(self, startPos, gridSize, metrics, initialGoal=None):
        # Initialize drone position and movement target
        self.position = startPos
        self.goal = initialGoal  # Goal can be None until target is discovered
        self.targetFound = False  # Track if drone has located the target
        # Track current heading for navigation
        self.facingDir = (1, 0)
        # Maintain knowledge map based on limited sensor data
        self.knownGrid = np.zeros((gridSize, gridSize), dtype=np.int8)

        # Store computed path waypoints
        self.currentPath = []

        # Configure sensor and decision-making parameters
        self.scanRadius = 3
        self.riskWeight = 0.7

        # Simulate altitude modulation for obstacle avoidance
        self.altitudeLevel = 1

        # Reference to performance tracking system
        self.metrics = metrics

        # Monitor consecutive detection of blocked movement
        self.stuckCounter = 0

        # Systematic search pattern for target discovery
        self.gridSize = gridSize
        self.searchPattern = self._generateSweepPattern(gridSize)
        self.searchIndex = 0

    def _generateSweepPattern(self, gridSize):
        # Create systematic sweep pattern covering entire grid
        pattern = []
        # Sweep from left to right, top to bottom in horizontal lines
        for y in range(gridSize):
            if y % 2 == 0:
                # Left to right on even rows
                for x in range(gridSize):
                    pattern.append((x, y))
            else:
                # Right to left on odd rows (boustrophedon - snake pattern)
                for x in range(gridSize - 1, -1, -1):
                    pattern.append((x, y))
        return pattern

    def scan(self, realGrid):
        # Update knowledge map using LIDAR sensor within scan radius
        self.knownGrid = scanWithLidar(
            dronePos=self.position,
            realGrid=realGrid,
            knownGrid=self.knownGrid,
            scanRadius=self.scanRadius,
        )

    def checkForTarget(self, targetPos):
        # Detect target location during sensor scan and set it as goal
        if targetPos is None or self.targetFound:
            return

        # Check if target is within sensor range
        tx, ty = targetPos
        dx = abs(self.position[0] - tx)
        dy = abs(self.position[1] - ty)

        if dx <= self.scanRadius and dy <= self.scanRadius:
            # Target discovered! Set it as the new goal
            self.goal = targetPos
            self.targetFound = True
            self.metrics.targetDiscovered = True

    def systematicSearch(self, realGrid, riskMap):
        # Execute systematic grid sweep pattern to find target efficiently
        # Skip to next valid waypoint if current is blocked
        attempts = 0
        maxAttempts = min(20, len(self.searchPattern))

        while attempts < maxAttempts and self.searchIndex < len(self.searchPattern):
            attempts += 1
            targetWaypoint = self.searchPattern[self.searchIndex]

            # Skip waypoints that are blocked
            if realGrid[targetWaypoint[0], targetWaypoint[1]] == 1:
                self.searchIndex += 1
                continue

            # Plan path to next search waypoint
            path = aStarSearch(
                start=self.position,
                goal=targetWaypoint,
                grid=self.knownGrid,
                riskMap=riskMap,
                riskWeight=self.riskWeight,
            )

            if path:
                # Found valid path to waypoint
                self.currentPath = path
                return

            # Path blocked, try next waypoint
            self.searchIndex += 1

        # If sweep pattern complete, reset to beginning
        if self.searchIndex >= len(self.searchPattern):
            self.searchIndex = 0

        # If no path found, pause
        self.metrics.pauses += 1

    def exploreRandomly(self, realGrid, riskMap):
        # Execute systematic search pattern instead of random exploration
        if not self.currentPath:
            self.systematicSearch(realGrid, riskMap)

        # Execute movement if path exists
        if self.currentPath:
            nextStep = self.currentPath[0]

            # Handle blocked path
            if realGrid[nextStep[0], nextStep[1]] == 1:
                self.metrics.pauses += 1
                self.currentPath = []
                self.stuckCounter += 1

                if self.stuckCounter >= 2:
                    self.searchIndex += 1
                    self.currentPath = []
                    self.stuckCounter = 0
                return

            # Execute safe movement
            self.currentPath.pop(0)
            self.position = nextStep
            self.metrics.stepsTaken += 1
            self.stuckCounter = 0

    def planPath(self, riskMap):
        # Compute optimal path using A* algorithm with risk weighting
        path = aStarSearch(
            start=self.position,
            goal=self.goal,
            grid=self.knownGrid,
            riskMap=riskMap,
            riskWeight=self.riskWeight,
        )
        self.currentPath = path
        self.metrics.pathLengthPlanned = len(path)

    def decideAndAct(self, realGrid, riskMap, targetPos=None):
        # Execute autonomous behavior cycle: perceive, decide, act
        self.scan(realGrid)

        # Check if target is within sensor range and update goal if found
        if targetPos is not None:
            self.checkForTarget(targetPos)

        # If no goal has been discovered yet, explore systematically
        if self.goal is None:
            self.exploreRandomly(realGrid, riskMap)
            return

        # Initiate path planning if no valid route exists
        if not self.currentPath:
            self.metrics.reroutes += 1
            self.planPath(riskMap)

        # Pause and retry next cycle if path planning failed
        if not self.currentPath:
            self.metrics.pauses += 1
            return

        nextStep = self.currentPath[0]

        # Handle blocked path by hazard
        if realGrid[nextStep[0], nextStep[1]] == 1:
            dangerHere = float(riskMap[nextStep[0], nextStep[1]])

            # Attempt altitude increase to evade high-danger obstacles
            if dangerHere >= 2.5 and self.altitudeLevel < 2:
                self.altitudeLevel += 1
                self.metrics.altitudeChanges += 1
                # Recalculate path at new altitude
                self.metrics.reroutes += 1
                self.planPath(riskMap)
                return

            # Pause instead of forcing movement into danger
            self.metrics.pauses += 1
            self.stuckCounter += 1

            # Force reroute after repeated blockage
            if self.stuckCounter >= 2:
                self.metrics.reroutes += 1
                self.planPath(riskMap)
                self.stuckCounter = 0
            return

        # Execute safe movement to next waypoint
        self.currentPath.pop(0)
        self.position = nextStep

        self.metrics.stepsTaken += 1
        self.metrics.pathLengthExecuted += 1
        self.stuckCounter = 0

    def hasReachedGoal(self):
        # Verify if current position matches goal location
        return self.position == self.goal