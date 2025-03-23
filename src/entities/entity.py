import pygame
import math
from typing import Optional, Tuple, List

class Projectile:
    def __init__(self, x: float, y: float, target_x: float, target_y: float, 
                 speed: float, damage: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.damage = damage
        self.color = color
        self.size = 8
        
        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        length = math.sqrt(dx*dx + dy*dy)
        self.dx = dx / length
        self.dy = dy / length
        
    def update(self) -> None:
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        
    def draw(self, screen: pygame.Surface, world) -> None:
        pygame.draw.circle(screen, self.color, 
                         (int(self.x), int(self.y)), self.size)
        
    def is_off_screen(self, width: int, height: int) -> bool:
        return (self.x < 0 or self.x > width or 
                self.y < 0 or self.y > height)

class Entity:
    def __init__(self, x: float, y: float, width: int, height: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.target_x = x
        self.target_y = y
        self.movement_speed = 2
        
        # Attack properties
        self.attacking = False
        self.attack_frame = 0
        self.attack_duration = 20  # frames
        self.attack_range = 50  # pixels
        self.attack_cooldown = 0
        self.attack_cooldown_max = 30  # frames
        
        # Projectiles
        self.projectiles: List[Projectile] = []
        
    def set_target(self, x: float, y: float) -> None:
        self.target_x = x
        self.target_y = y
        
    def update(self) -> None:
        # Update position
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1:
            self.x += (dx / distance) * self.movement_speed
            self.y += (dy / distance) * self.movement_speed
        else:
            self.x = self.target_x
            self.y = self.target_y
            
        # Update attack animation
        if self.attacking:
            self.attack_frame += 1
            if self.attack_frame >= self.attack_duration:
                self.attacking = False
                self.attack_frame = 0
                
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.is_off_screen(800, 600):  # Use screen dimensions
                self.projectiles.remove(projectile)
                
    def draw(self, screen: pygame.Surface, world) -> None:
        # Draw entity
        pygame.draw.rect(screen, self.color, 
                        (int(self.x - self.width/2), 
                         int(self.y - self.height/2),
                         self.width, self.height))
        
        # Draw attack animation
        if self.attacking:
            # Calculate attack animation offset based on frame
            progress = self.attack_frame / self.attack_duration
            if progress < 0.5:
                # Forward slash
                offset = int(progress * 2 * self.attack_range)
                pygame.draw.line(screen, (255, 255, 0),  # Yellow slash
                               (self.x, self.y),
                               (self.x + offset, self.y - offset), 3)
            else:
                # Backward slash
                offset = int((1 - progress) * 2 * self.attack_range)
                pygame.draw.line(screen, (255, 255, 0),
                               (self.x, self.y),
                               (self.x - offset, self.y - offset), 3)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen, world)
            
    def can_attack(self) -> bool:
        return not self.attacking and self.attack_cooldown <= 0
        
    def start_attack(self) -> None:
        if self.can_attack():
            self.attacking = True
            self.attack_frame = 0
            self.attack_cooldown = self.attack_cooldown_max
            
    def shoot_projectile(self, target_x: float, target_y: float, 
                        speed: float, damage: int) -> None:
        if self.can_attack():
            self.projectiles.append(Projectile(
                self.x, self.y, target_x, target_y,
                speed, damage, self.color
            ))
            self.attack_cooldown = self.attack_cooldown_max 