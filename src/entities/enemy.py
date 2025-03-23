from .entity import Entity
from .stats import Stats
import pygame
from typing import Tuple
import random

class Enemy(Entity):
    def __init__(self, x: float, y: float, enemy_type: str = 'basic'):
        # Set color based on enemy type
        color_map = {
            'basic': (255, 165, 0),    # Orange
            'ranged': (255, 0, 255),   # Magenta
            'tank': (128, 128, 128)    # Gray
        }
        color = color_map.get(enemy_type, (255, 165, 0))
        
        super().__init__(x, y, 32, 32, color)
        
        # Set enemy type and stats
        self.enemy_type = enemy_type
        self.stats = self._create_stats()
        
        # Set attack properties based on type
        if enemy_type == 'basic':
            self.attack_range = 40  # Very close range
            self.attack_duration = 20  # frames
            self.attack_cooldown_max = 30  # frames
            self.projectile_speed = 0  # No projectiles
        elif enemy_type == 'ranged':
            self.attack_range = 150  # Medium range
            self.attack_duration = 15  # frames
            self.attack_cooldown_max = 25  # frames
            self.projectile_speed = 6  # Medium speed projectiles
        else:  # tank
            self.attack_range = 40  # Very close range
            self.attack_duration = 25  # frames
            self.attack_cooldown_max = 40  # frames
            self.projectile_speed = 0  # No projectiles
        
        # Movement properties
        self.target_x = x
        self.target_y = y
        self.movement_speed = 1.5
        
    def _create_stats(self) -> Stats:
        """Create stats based on enemy type."""
        if self.enemy_type == 'basic':
            return Stats(level=1, hp=30, max_hp=30, attack=3, defense=2, speed=3)
        elif self.enemy_type == 'ranged':
            return Stats(level=1, hp=25, max_hp=25, attack=5, defense=1, speed=4)
        else:  # tank
            return Stats(level=1, hp=50, max_hp=50, attack=2, defense=4, speed=2)
        
    def attack(self, target: Entity) -> bool:
        """Attack a target."""
        if not self.can_attack():
            return False
            
        # Calculate distance to target
        dx = target.x - self.x
        dy = target.y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        # Only attack if in range
        if distance <= self.attack_range:
            # Calculate damage
            damage = self.stats.attack
            
            # Handle different attack types
            if self.enemy_type == 'ranged':
                # Ranged attack
                self.shoot_projectile(target.x, target.y, 
                                    self.projectile_speed, int(damage))
            else:
                # Close range attack
                self.start_attack()
                target.stats.hp -= int(damage)
            
            return True
        return False
        
    def update(self):
        """Update enemy state."""
        super().update()
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Update attack animation
        if self.attacking:
            self.attack_frame += 1
            if self.attack_frame >= self.attack_duration:
                self.attacking = False
                self.attack_frame = 0
                
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.is_dead():
                self.projectiles.remove(projectile)
                
    def draw(self, screen: pygame.Surface, world):
        """Draw the enemy and its projectiles."""
        # Convert world coordinates to screen coordinates
        screen_x, screen_y = world.world_to_screen(self.x, self.y)
        
        # Draw base enemy
        pygame.draw.rect(screen, self.color, 
                        (screen_x, screen_y, self.width, self.height))
        
        # Draw health bar
        health_width = (self.width * self.stats.hp) // self.stats.max_hp
        pygame.draw.rect(screen, (255, 0, 0), 
                        (screen_x, screen_y - 10, self.width, 5))
        pygame.draw.rect(screen, (0, 255, 0), 
                        (screen_x, screen_y - 10, health_width, 5))
        
        # Draw enemy type
        type_text = self.enemy_type.capitalize()
        type_surface = pygame.font.Font(None, 20).render(type_text, True, (255, 255, 255))
        screen.blit(type_surface, (screen_x, screen_y - 25))
        
        # Draw attack animation
        if self.attacking:
            # Calculate offset based on attack frame
            offset = (self.attack_frame / self.attack_duration) * 20
            # Draw attack effect
            pygame.draw.circle(screen, (255, 0, 0),
                             (int(screen_x + self.width/2 + offset),
                              int(screen_y + self.height/2)),
                             5)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen, world) 