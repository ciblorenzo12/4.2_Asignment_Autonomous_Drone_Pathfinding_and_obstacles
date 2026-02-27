import time


class Metrics:
    def __init__(self):
        # Initialize performance tracking and start mission timer
        self.startTime = time.time()
        self.endTime = None

        self.stepsTaken = 0
        self.reroutes = 0
        self.pauses = 0
        self.altitudeChanges = 0

        self.pathLengthPlanned = 0
        self.pathLengthExecuted = 0
        
        # Track target discovery and acquisition phases
        self.targetDiscovered = False
        self.targetDiscoveryTime = None
        self.targetsAcquired = 0  # Count completed target acquisitions

    def markFinished(self):
        # Record mission completion timestamp
        if self.endTime is None:
            self.endTime = time.time()

    def getElapsedSeconds(self):
        # Calculate elapsed time from mission start to finish
        if self.endTime is None:
            return time.time() - self.startTime
        return self.endTime - self.startTime

    def buildSummary(self, reachedGoal):
        # Compile performance metrics into report dictionary
        return {
            "reachedGoal": reachedGoal,
            "targetDiscovered": self.targetDiscovered,
            "targetsAcquired": self.targetsAcquired,
            "timeSeconds": round(self.getElapsedSeconds(), 3),
            "stepsTaken": self.stepsTaken,
            "reroutes": self.reroutes,
            "pauses": self.pauses,
            "altitudeChanges": self.altitudeChanges,
            "plannedPathCells": self.pathLengthPlanned,
            "executedPathCells": self.pathLengthExecuted,
        }