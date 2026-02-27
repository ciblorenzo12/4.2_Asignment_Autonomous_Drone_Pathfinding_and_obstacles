import pygame
import os


class Visualizer:
    def __init__(self, gridSize, cellSize=30):
        # Initialize pygame display and load drone sprite asset
        pygame.init()
        self.gridSize = gridSize
        self.cellSize = cellSize

        self.width = gridSize * cellSize
        self.height = gridSize * cellSize

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Aegis-1: Autonomous Drone Search-and-Rescue Simulation")

        # Load drone sprite from assets folder
        assetPath = os.path.join("assets", "drone.png")
        if os.path.exists(assetPath):
            self.droneImage = pygame.image.load(assetPath).convert_alpha()
            # Scale sprite to match grid cell dimensions
            self.droneImage = pygame.transform.scale(
                self.droneImage,
                (int(cellSize * 1.0), int(cellSize * 1.0))
            )
        else:
            self.droneImage = None

        self.clock = pygame.time.Clock()

    def handleQuitEvents(self):
        # Process window events and detect quit command
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def draw(self, staticGrid, movingObstacles, dronePos, goalPos, knownGrid=None, riskMap=None):
        # Render complete simulation state to display
        self.screen.fill((18, 18, 28))

        cellSize = self.cellSize

        for x in range(self.gridSize):
            for y in range(self.gridSize):
                rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)

                # Render static obstacles in gray
                if staticGrid[x, y] == 1:
                    pygame.draw.rect(self.screen, (110, 110, 120), rect)

                # Visualize danger zones based on proximity to moving hazards
                if riskMap is not None and staticGrid[x, y] == 0:
                    danger = float(riskMap[x, y])
                    if danger > 0:
                        intensity = min(120, int(danger * 25))
                        pygame.draw.rect(self.screen, (50 + intensity, 40, 40), rect)

                # Display unexplored areas in darker shade
                if knownGrid is not None and knownGrid[x, y] == 0 and staticGrid[x, y] == 0:
                    pygame.draw.rect(self.screen, (22, 22, 34), rect)

                pygame.draw.rect(self.screen, (35, 35, 55), rect, 1)

        # Render moving hazards with type-specific colors
        for hazard in movingObstacles:
            x, y = hazard["pos"]
            rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
            if hazard["kind"] == "smoke":
                pygame.draw.rect(self.screen, (70, 80, 95), rect)
            else:
                pygame.draw.rect(self.screen, (140, 95, 60), rect)

        # Render drone sprite or fallback circle
        dx, dy = dronePos
        if self.droneImage is not None:
            # Render sprite at drone position
            rect = self.droneImage.get_rect(center=(dx * cellSize + cellSize // 2, dy * cellSize + cellSize // 2))
            self.screen.blit(self.droneImage, rect)
        else:
            # Use cyan circle if sprite unavailable
            pygame.draw.circle(
                self.screen,
                (0, 240, 240),
                (dx * cellSize + cellSize // 2, dy * cellSize + cellSize // 2),
                8,
            )

        # Render goal location as red beacon
        gx, gy = goalPos
        pygame.draw.circle(
            self.screen,
            (255, 85, 85),
            (gx * cellSize + cellSize // 2, gy * cellSize + cellSize // 2),
            8,
        )

        pygame.display.flip()

    def tick(self, fps=6):
        # Regulate simulation speed by controlling frame rate
        self.clock.tick(fps)

    def shutdown(self):
        # Cleanup pygame resources
        pygame.quit()
