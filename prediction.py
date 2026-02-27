import numpy as np


def predictTrajectories(hazards, predictions=3):
    """
    Predict future positions of moving hazards based on recent movement patterns.
    Extrapolates trajectories to anticipate collisions before they occur.
    
    Args:
        hazards: List of hazard dictionaries with position and movement history
        predictions: Number of time steps to predict ahead (default 3)
    
    Returns:
        List of predicted hazard occupancies for each future step
    """
    predictedTrajectories = []

    for step in range(1, predictions + 1):
        stepOccupancy = {}

        for hazard in hazards:
            # Extract movement history (if available)
            if "history" in hazard and len(hazard["history"]) >= 2:
                # Calculate velocity: direction and consistency of recent moves
                recentMoves = hazard["history"][-2:]
                prevPos = recentMoves[0]
                currPos = recentMoves[1]

                velocity = (
                    currPos[0] - prevPos[0],
                    currPos[1] - prevPos[1],
                )

                # Predict future position by extrapolating velocity
                predictedX = currPos[0] + (velocity[0] * step)
                predictedY = currPos[1] + (velocity[1] * step)
                predictedPos = (predictedX, predictedY)
            else:
                # If no history, assume current position (stationary)
                predictedPos = hazard["pos"]

            # Store predicted position with diminishing confidence
            confidence = 1.0 - (step * 0.15)  # Confidence decreases over time
            stepOccupancy[predictedPos] = {
                "confidence": max(0.3, confidence),
                "kind": hazard["kind"],
            }

        predictedTrajectories.append(stepOccupancy)

    return predictedTrajectories


def buildPredictiveRiskMap(hazards, gridSize, riskRadius=2, predictions=3):
    """
    Build risk map that accounts for predicted future hazard positions.
    Creates a dynamic danger zone that anticipates obstacle movement.
    
    Args:
        hazards: List of moving hazards
        gridSize: Size of the grid
        riskRadius: Radius of penalty around hazards
        predictions: Number of steps to predict ahead
    
    Returns:
        Risk map with penalties for current and predicted hazard positions
    """
    riskMap = np.zeros((gridSize, gridSize), dtype=np.float32)

    # Get predicted trajectories
    predictedTrajectories = predictTrajectories(hazards, predictions)

    # Apply penalties for predicted positions
    for stepIndex, stepOccupancy in enumerate(predictedTrajectories):
        # Earlier predictions have higher penalty (closer in time = more urgent)
        timeUrgency = 1.0 - (stepIndex / predictions) * 0.5

        for (hx, hy), hazardData in stepOccupancy.items():
            confidence = hazardData["confidence"]
            kind = hazardData["kind"]

            # Apply penalty around predicted position
            for dx in range(-riskRadius, riskRadius + 1):
                for dy in range(-riskRadius, riskRadius + 1):
                    x = int(hx) + dx
                    y = int(hy) + dy

                    if not (0 <= x < gridSize and 0 <= y < gridSize):
                        continue

                    # Distance-based penalty
                    dist = abs(dx) + abs(dy)
                    penalty = max(0.0, (riskRadius + 1) - dist)

                    # Apply type-specific weighting
                    if kind == "debris":
                        penalty *= 1.5

                    # Apply confidence and time urgency
                    penalty *= confidence * timeUrgency

                    riskMap[x, y] += penalty

    return riskMap
