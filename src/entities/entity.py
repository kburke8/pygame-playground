import pygame
from typing import Tuple

class Entity:
    def __init__(self, x: float, y: float, width: int, height: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen: pygame.Surface, world):
        # Convert world coordinates to screen coordinates
        screen_x, screen_y = world.world_to_screen(self.x, self.y)
        pygame.draw.rect(screen, self.color, 
                        (screen_x, screen_y, self.width, self.height)) 