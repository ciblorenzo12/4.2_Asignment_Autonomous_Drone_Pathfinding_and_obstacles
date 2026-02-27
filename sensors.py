def scanWithLidar(dronePos, realGrid, knownGrid, scanRadius=3):
    # Update knowledge map by scanning environment within sensor range
    x0, y0 = dronePos
    gridSize = realGrid.shape[0]

    for dx in range(-scanRadius, scanRadius + 1):
        for dy in range(-scanRadius, scanRadius + 1):
            x = x0 + dx
            y = y0 + dy

            # Update knowledge map with real environment data
            if 0 <= x < gridSize and 0 <= y < gridSize:
                knownGrid[x, y] = realGrid[x, y]

    return knownGrid