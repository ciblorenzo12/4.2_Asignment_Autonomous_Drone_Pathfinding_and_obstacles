from environment import Environment
from drone import Drone
from metrics import Metrics
from visualizer import Visualizer


def main():
    # Entry point for the Aegis-1 autonomous drone simulation
    gridSize = 20
    cellSize = 30

    # Configure simulation parameters for environment complexity
    obstacleCount = 65
    movingObstacleCount = 7

    metrics = Metrics()

    # Initialize simulation environment with static debris and dynamic hazards
    env = Environment(
        gridSize=gridSize,
        obstacleCount=obstacleCount,
        movingObstacleCount=movingObstacleCount,
        seed=42,
    )

    startPos = (0, 0)

    drone = Drone(
        startPos=startPos,
        gridSize=gridSize,
        metrics=metrics,
        initialGoal=None,  # Target discovered during exploration
    )

    # Initialize real-time visualization system
    viz = Visualizer(gridSize=gridSize, cellSize=cellSize)

    # Configure continuous mission parameters
    reachedGoal = False
    running = True
    targetAcquisitionLimit = 3  # Acquire this many targets before stopping
    maxSteps = 10000  # Safety limit to prevent infinite loops

    while running:
        # Check for window close event
        if viz.handleQuitEvents():
            running = False
            break

        # Safety limit to prevent infinite loops
        if metrics.stepsTaken >= maxSteps:
            running = False
            break

        # Update positions of moving obstacles
        env.stepMovingObstacles()

        # Retrieve current state of the environment including all obstacles
        realGrid = env.getCombinedGrid()

        # Calculate spatial risk map using AI trajectory prediction to anticipate hazards
        riskMap = env.buildPredictiveRiskMap(riskRadius=2, predictions=3)

        # Execute drone behavior loop: sense, plan, and move
        drone.decideAndAct(realGrid=realGrid, riskMap=riskMap, targetPos=env.getTargetPos())

        # Render current simulation state with sensor data and risk visualization
        displayGoal = drone.goal if drone.goal is not None else env.getTargetPos()
        viz.draw(
            staticGrid=env.staticGrid,
            movingObstacles=env.movingObstacles,
            dronePos=drone.position,
            goalPos=displayGoal,
            knownGrid=drone.knownGrid,
            riskMap=riskMap,
        )

        # Control simulation frame rate
        viz.tick(fps=6)

        # Check if drone has reached the current target (continuous mission mode)
        if drone.targetFound and drone.hasReachedGoal():
            # Target acquired! Increment counter and prepare for next target
            metrics.targetsAcquired += 1

            # Check if mission is complete
            if metrics.targetsAcquired >= targetAcquisitionLimit:
                reachedGoal = True
                running = False
            else:
                # Relocate target to random location for next acquisition
                env.relocateTarget()
                # Reset drone for new target search
                drone.goal = None
                drone.targetFound = False
                drone.currentPath = []

    metrics.markFinished()
    viz.shutdown()

    summary = metrics.buildSummary(reachedGoal=reachedGoal)

    # Output mission performance summary
    print("\n=== Aegis-1 Mission Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()