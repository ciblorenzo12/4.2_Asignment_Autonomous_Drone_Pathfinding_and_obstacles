import numpy as np
import random


class Environment:
    def __init__(self, gridSize=20, obstacleCount=60, movingObstacleCount=6, seed=42):
        # Initialize random number generators with seed for reproducibility
        random.seed(seed)
        np.random.seed(seed)

        # Set grid dimensions
        self.gridSize = gridSize

        # Grid cell values: 0 = free space, 1 = blocked (static obstacle)
        self.staticGrid = np.zeros((gridSize, gridSize), dtype=np.int8)

        # Track dynamic obstacles (moving hazards)
        self.movingObstacles = []

        # Store simulation configuration
        self.obstacleCount = obstacleCount
        self.movingObstacleCount = movingObstacleCount

        # Target location (discovered through exploration)
        self.targetPos = None

        # Generate initial environment state
        self._generateStaticObstacles()
        self._spawnMovingObstacles()
        self._spawnTarget()

    def _generateStaticObstacles(self):
        # Randomly scatter static obstacles, avoiding start and goal corners
        forbidden = {(0, 0), (self.gridSize - 1, self.gridSize - 1)}
        placed = 0
        attempts = 0

        while placed < self.obstacleCount and attempts < self.obstacleCount * 40:
            attempts += 1
            x = random.randint(0, self.gridSize - 1)
            y = random.randint(0, self.gridSize - 1)

            if (x, y) in forbidden:
                continue

            if self.staticGrid[x, y] == 0:
                self.staticGrid[x, y] = 1
                placed += 1

    def _spawnMovingObstacles(self):
        # Initialize moving hazards at random positions
        forbidden = {(0, 0), (self.gridSize - 1, self.gridSize - 1)}
        self.movingObstacles = []

        tries = 0
        while len(self.movingObstacles) < self.movingObstacleCount and tries < 5000:
            tries += 1
            x = random.randint(0, self.gridSize - 1)
            y = random.randint(0, self.gridSize - 1)

            if (x, y) in forbidden:
                continue

            if self.staticGrid[x, y] == 1:
                continue

            # Create hazard with random movement pattern and type
            hazard = {
                "pos": (x, y),
                "kind": random.choice(["smoke", "debris"]),
                "cooldown": random.randint(0, 2),
                "history": [(x, y)],  # Track position history for trajectory prediction
            }
            self.movingObstacles.append(hazard)

    def _spawnTarget(self):
        # Place target at random free location for drone to discover
        forbidden = {(0, 0), (self.gridSize - 1, self.gridSize - 1)}
        placed = False
        attempts = 0

        while not placed and attempts < 1000:
            attempts += 1
            x = random.randint(0, self.gridSize - 1)
            y = random.randint(0, self.gridSize - 1)

            if (x, y) in forbidden:
                continue

            if self.staticGrid[x, y] == 1:
                continue

            # Check if hazards occupy this position
            occupied = False
            for hazard in self.movingObstacles:
                if hazard["pos"] == (x, y):
                    occupied = True
                    break

            if not occupied:
                self.targetPos = (x, y)
                placed = True

    def getTargetPos(self):
        # Return target location if it exists
        return self.targetPos

    def relocateTarget(self):
        # Spawn target at new random free location for continuous missions
        forbidden = {(0, 0), (self.gridSize - 1, self.gridSize - 1)}
        placed = False
        attempts = 0

        while not placed and attempts < 1000:
            attempts += 1
            x = random.randint(0, self.gridSize - 1)
            y = random.randint(0, self.gridSize - 1)

            if (x, y) in forbidden:
                continue

            if self.staticGrid[x, y] == 1:
                continue

            # Check if hazards occupy this position
            occupied = False
            for hazard in self.movingObstacles:
                if hazard["pos"] == (x, y):
                    occupied = True
                    break

            if not occupied:
                self.targetPos = (x, y)
                placed = True

    def getCombinedGrid(self):
        # Merge static and dynamic obstacles into single grid representation
        combined = self.staticGrid.copy()

        for hazard in self.movingObstacles:
            x, y = hazard["pos"]
            combined[x, y] = 1

        return combined

    def stepMovingObstacles(self):
        # Update positions of all moving hazards
        for hazard in self.movingObstacles:

            if hazard["cooldown"] > 0:
                hazard["cooldown"] -= 1
                continue

            hazard["cooldown"] = random.randint(0, 2)

            x, y = hazard["pos"]

            # Select movement pattern based on hazard type
            if hazard["kind"] == "smoke":
                # Smoke can drift in all directions including pause
                moveChoices = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
            else:
                # Debris moves only orthogonally
                moveChoices = [(1, 0), (-1, 0), (0, 1), (0, -1)]

            dx, dy = random.choice(moveChoices)
            nx, ny = x + dx, y + dy

            # Check bounds
            if not (0 <= nx < self.gridSize and 0 <= ny < self.gridSize):
                continue

            # Prevent movement through static obstacles
            if self.staticGrid[nx, ny] == 1:
                continue

            # Record previous position and update to new location
            if len(hazard["history"]) > 5:
                hazard["history"].pop(0)  # Keep only recent history
            hazard["history"].append((nx, ny))
            hazard["pos"] = (nx, ny)

    def buildRiskMap(self, riskRadius=2):
        # Calculate spatial danger map based on proximity to moving hazards
        riskMap = np.zeros((self.gridSize, self.gridSize), dtype=np.float32)

        for hazard in self.movingObstacles:
            hx, hy = hazard["pos"]

            # Apply penalty gradient around hazard position
            for dx in range(-riskRadius, riskRadius + 1):
                for dy in range(-riskRadius, riskRadius + 1):
                    x = hx + dx
                    y = hy + dy

                    if not (0 <= x < self.gridSize and 0 <= y < self.gridSize):
                        continue

                    # Penalty decreases with distance from hazard
                    dist = abs(dx) + abs(dy)
                    penalty = max(0.0, (riskRadius + 1) - dist)

                    # Apply hazard-type specific weighting
                    if hazard["kind"] == "debris":
                        penalty *= 1.5

                    riskMap[x, y] += penalty

        # Add penalty for proximity to static debris walls (dead-end discouragement)
        for x in range(self.gridSize):
            for y in range(self.gridSize):
                if self.staticGrid[x, y] == 1:
                    continue

                nearDebris = 0
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize:
                        if self.staticGrid[nx, ny] == 1:
                            nearDebris += 1

                riskMap[x, y] += nearDebris * 0.35

        return riskMap

    def buildPredictiveRiskMap(self, riskRadius=2, predictions=3):
        # Build risk map using AI trajectory prediction for proactive avoidance
        from prediction import buildPredictiveRiskMap as predictRisk
        
        riskMap = predictRisk(
            self.movingObstacles,
            self.gridSize,
            riskRadius=riskRadius,
            predictions=predictions
        )

        # Add wall-proximity penalty (same as regular risk map)
        for x in range(self.gridSize):
            for y in range(self.gridSize):
                if self.staticGrid[x, y] == 1:
                    continue

                nearDebris = 0
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.gridSize and 0 <= ny < self.gridSize:
                        if self.staticGrid[nx, ny] == 1:
                            nearDebris += 1

                riskMap[x, y] += nearDebris * 0.35

        return riskMap