from .entity import Entity
from .stats import Stats
import pygame
import random

class Enemy(Entity):
    def __init__(self, x: float, y: float, enemy_type: str = 'goblin'):
        # Set color based on enemy type
        color_map = {
            'goblin': (0, 255, 0),     # Green
            'skeleton': (200, 200, 200), # Gray
            'slime': (0, 255, 255)      # Cyan
        }
        color = color_map.get(enemy_type, (255, 0, 0))
        
        super().__init__(x, y, 24, 24, color)
        
        # Set enemy type and stats
        self.enemy_type = enemy_type
        self.stats = self._create_stats()
        
        # Animation properties
        self.attacking = False
        self.attack_frame = 0
        self.attack_duration = 20  # frames
        self.attack_range = 30  # pixels
        
        # Movement properties
        self.target_x = x
        self.target_y = y
        self.movement_speed = 1
        
    def _create_stats(self) -> Stats:
        """Create stats based on enemy type."""
        if self.enemy_type == 'goblin':
            return Stats(level=1, hp=80, max_hp=80, attack=5, defense=3, speed=3)
        elif self.enemy_type == 'skeleton':
            return Stats(level=1, hp=60, max_hp=60, attack=8, defense=2, speed=4)
        elif self.enemy_type == 'slime':
            return Stats(level=1, hp=100, max_hp=100, attack=3, defense=4, speed=2)
        return Stats()  # Default stats if type not found
        
    def update(self):
        super().update()
        
        # Update attack animation
        if self.attacking:
            self.attack_frame += 1
            if self.attack_frame >= self.attack_duration:
                self.attacking = False
                self.attack_frame = 0
        
        # Move towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 1:
            # Move one step at a time
            step_x = (dx / distance) * self.movement_speed
            step_y = (dy / distance) * self.movement_speed
            
            # Update position
            self.x += step_x
            self.y += step_y
        
    def set_target(self, x: float, y: float):
        """Set movement target."""
        self.target_x = x
        self.target_y = y
        
    def attack(self, target: Entity) -> bool:
        """Attack a target."""
        # Calculate distance to target
        dx = target.x - self.x
        dy = target.y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance <= self.attack_range:
            self.attacking = True
            self.attack_frame = 0
            # Apply damage
            target.stats.hp -= self.stats.attack
            return True
        return False
        
    def draw(self, screen: pygame.Surface, world):
        # Draw base enemy
        super().draw(screen, world)
        
        # Draw health bar
        screen_x, screen_y = world.world_to_screen(self.x, self.y)
        health_width = (self.stats.hp / self.stats.max_hp) * self.width
        pygame.draw.rect(screen, (0, 255, 0), 
                        (screen_x, screen_y - 10, health_width, 5))
        
        # Draw enemy type
        type_text = self.enemy_type.capitalize()
        type_surface = pygame.font.Font(None, 20).render(type_text, True, (255, 255, 255))
        screen.blit(type_surface, (screen_x, screen_y - 25))
        
        # Draw attack animation
        if self.attacking:
            # Calculate attack animation offset
            progress = self.attack_frame / self.attack_duration
            offset = int(20 * (1 - (2 * progress - 1)**2))  # Quadratic easing
            
            # Draw attack effect
            pygame.draw.circle(screen, (255, 0, 0),
                             (int(screen_x + self.width/2 + offset),
                              int(screen_y + self.height/2)),
                             5) 