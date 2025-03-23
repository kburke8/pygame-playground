import pygame
from typing import Tuple

class World:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.camera_x = 0
        self.camera_y = 0
        
    def handle_input(self, keys):
        """Handle camera movement input."""
        pass  # Removed camera movement
        
    def world_to_screen(self, world_x: float, world_y: float) -> tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        # Handle screen wrapping
        screen_x = world_x % self.width
        screen_y = world_y % self.height
        return screen_x, screen_y
        
    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        return screen_x, screen_y
        
    def draw(self, screen: pygame.Surface):
        """Draw the world."""
        # Draw a simple background grid
        grid_size = 32
        for x in range(0, self.width, grid_size):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, self.height))
        for y in range(0, self.height, grid_size):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (self.width, y)) 