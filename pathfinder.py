import heapq


def manhattanDistance(a, b):
    # Calculate Manhattan distance heuristic for A* algorithm
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def aStarSearch(start, goal, grid, riskMap=None, riskWeight=0.7):
    # Compute optimal path using A* algorithm with risk-weighted costs
    if riskMap is None:
        riskMap = None

    openSet = []
    heapq.heappush(openSet, (0.0, start))

    cameFrom = {}
    gScore = {start: 0.0}

    visited = set()

    while openSet:
        _, current = heapq.heappop(openSet)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            # Reconstruct path by backtracking through parents
            path = []
            node = current
            while node in cameFrom:
                path.append(node)
                node = cameFrom[node]
            path.reverse()
            return path

        # Explore 4-directional neighbors (no diagonals)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbor = (current[0] + dx, current[1] + dy)

            # Check bounds
            if not (0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]):
                continue

            # Skip blocked cells
            if grid[neighbor[0], neighbor[1]] == 1:
                continue

            stepCost = 1.0

            # Apply risk penalty to discourage traversing hazard zones
            if riskMap is not None:
                stepCost += float(riskMap[neighbor[0], neighbor[1]]) * riskWeight

            tentative = gScore[current] + stepCost

            if neighbor not in gScore or tentative < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tentative

                h = manhattanDistance(neighbor, goal)
                f = tentative + h
                heapq.heappush(openSet, (f, neighbor))

    # Return empty list if no path exists
    return []