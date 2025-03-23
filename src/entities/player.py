from .entity import Entity
from .stats import Stats
import pygame
from typing import Tuple
from dataclasses import dataclass
from systems.abilities import AbilitySystem, Skill, Passive
from systems.gear import GearSystem, GearItem, GearSlot
from systems.progression import MetaUpgradeType
import random

@dataclass
class Stats:
    def __init__(self, level: int = 1, hp: int = 0, max_hp: int = 0, 
                 attack: int = 0, defense: int = 0, speed: int = 0):
        self.level = level
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed

class Player(Entity):
    def __init__(self, x: float, y: float, character_class: str = 'warrior', progression_system=None):
        # Set color based on character class
        color_map = {
            'warrior': (255, 0, 0),    # Red
            'rogue': (0, 255, 0),      # Green
            'mage': (0, 0, 255)        # Blue
        }
        color = color_map.get(character_class, (255, 0, 0))
        
        super().__init__(x, y, 32, 32, color)
        
        # Store progression system reference
        self.progression = progression_system
        
        # Set character class and stats
        self.character_class = character_class
        self.stats = self._create_stats()
        
        # Initialize ability and gear systems
        self.abilities = AbilitySystem()
        self.gear = GearSystem()
        
        # Set attack properties based on class
        if character_class == 'warrior':
            self.attack_range = 50  # Close range
            self.attack_duration = 20  # frames
            self.attack_cooldown_max = 30  # frames
            self.projectile_speed = 0  # No projectiles
        elif character_class == 'rogue':
            self.attack_range = 150  # Medium range
            self.attack_duration = 15  # frames
            self.attack_cooldown_max = 25  # frames
            self.projectile_speed = 8  # Fast projectiles
        else:  # mage
            self.attack_range = 200  # Long range
            self.attack_duration = 10  # frames
            self.attack_cooldown_max = 35  # frames
            self.projectile_speed = 6  # Medium speed projectiles
        
        # Movement properties
        self.target_x = x
        self.target_y = y
        self.movement_speed = 2
        
        # Experience and leveling
        self.experience = 0
        self.level = 1
        self.experience_to_next_level = 100
        
        # Initialize class-specific skills and passives
        self._initialize_class_abilities()
        
    def _create_stats(self) -> Stats:
        """Create stats based on character class and meta-upgrades."""
        # Get base stats
        if self.character_class == 'warrior':
            base_stats = Stats(level=1, hp=50, max_hp=50, attack=8, defense=4, speed=4)
        elif self.character_class == 'rogue':
            base_stats = Stats(level=1, hp=40, max_hp=40, attack=12, defense=2, speed=5)
        elif self.character_class == 'mage':
            base_stats = Stats(level=1, hp=30, max_hp=30, attack=15, defense=1, speed=3)
        else:
            base_stats = Stats()
        
        # Apply meta-upgrade effects if available
        if self.progression:
            # Apply starting level
            starting_level = int(self.progression.get_upgrade_effect(MetaUpgradeType.STARTING_LEVEL))
            if starting_level > 0:
                base_stats.level = starting_level + 1
                base_stats.hp += starting_level * 10
                base_stats.max_hp += starting_level * 10
                base_stats.attack += starting_level * 2
                base_stats.defense += starting_level
                base_stats.speed += starting_level
            
            # Apply max health boost
            health_multiplier = 1.0 + self.progression.get_upgrade_effect(MetaUpgradeType.MAX_HEALTH)
            base_stats.hp = int(base_stats.hp * health_multiplier)
            base_stats.max_hp = int(base_stats.max_hp * health_multiplier)
        
        return base_stats
        
    def _initialize_class_abilities(self):
        """Initialize class-specific skills and passives."""
        if self.character_class == 'warrior':
            self.abilities.add_skill(Skill(
                name="Whirlwind",
                damage=20,
                cooldown=5.0,
                description="Spin and damage all nearby enemies"
            ))
            self.abilities.add_passive(Passive(
                name="Toughness",
                description="Take 20% less damage",
                effect_type="damage_bonus",
                value=0.2
            ))
        elif self.character_class == 'rogue':
            self.abilities.add_skill(Skill(
                name="Backstab",
                damage=30,
                cooldown=3.0,
                description="Deal massive damage from behind"
            ))
            self.abilities.add_passive(Passive(
                name="Critical Strike",
                description="15% chance to deal double damage",
                effect_type="crit_chance",
                value=0.15
            ))
        elif self.character_class == 'mage':
            self.abilities.add_skill(Skill(
                name="Fireball",
                damage=25,
                cooldown=4.0,
                description="Launch a powerful fireball"
            ))
            self.abilities.add_passive(Passive(
                name="Arcane Power",
                description="Deal 25% more damage",
                effect_type="damage_bonus",
                value=0.25
            ))
            
    def attack(self, target: Entity) -> bool:
        """Attack a target, applying skills, passives, and gear bonuses."""
        if not self.can_attack():
            return False
            
        # Check for critical hit
        is_critical = False
        crit_chance = self.abilities.apply_passive_effects(0)['crit_chance']
        if random.random() < crit_chance:
            is_critical = True
        
        # Calculate base damage
        base_damage = self.stats.attack
        
        # Apply gear bonuses
        gear_stats = self.gear.get_total_stats()
        base_damage += gear_stats.get('attack', 0)
        
        # Apply passive effects
        effects = self.abilities.apply_passive_effects(base_damage, is_critical)
        damage = base_damage * effects['damage_multiplier']
        
        if is_critical:
            damage *= effects['crit_multiplier']
        
        # Handle different attack types
        if self.character_class == 'warrior':
            # Close range attack
            self.start_attack()
            target.stats.hp -= int(damage)
        else:
            # Ranged attack (rogue or mage)
            self.shoot_projectile(target.x, target.y, 
                                self.projectile_speed, int(damage))
        
        # Apply life steal if any
        life_steal = effects['life_steal']
        if life_steal > 0:
            heal_amount = int(damage * life_steal)
            self.stats.hp = min(self.stats.max_hp, self.stats.hp + heal_amount)
        
        return True
        
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
        
    def gain_experience(self, amount: int):
        """Gain experience points and check for level up."""
        self.experience += amount
        while self.experience >= self.experience_to_next_level:
            self.level_up()
            
    def level_up(self):
        """Level up and increase stats."""
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        
        # Increase stats
        self.stats.max_hp += 10
        self.stats.hp = self.stats.max_hp
        self.stats.attack += 2
        self.stats.defense += 1
        self.stats.speed += 1
        
    def draw(self, screen: pygame.Surface, world):
        # Draw base player
        super().draw(screen, world)
        
        # Draw health bar
        screen_x, screen_y = world.world_to_screen(self.x, self.y)
        health_width = (self.stats.hp / self.stats.max_hp) * self.width
        pygame.draw.rect(screen, (0, 255, 0), 
                        (screen_x, screen_y - 10, health_width, 5))
        
        # Draw level and experience
        level_text = f"Lvl {self.level}"
        exp_text = f"EXP: {self.experience}/{self.experience_to_next_level}"
        level_surface = pygame.font.Font(None, 20).render(level_text, True, (255, 255, 255))
        exp_surface = pygame.font.Font(None, 20).render(exp_text, True, (255, 255, 255))
        screen.blit(level_surface, (screen_x, screen_y - 25))
        screen.blit(exp_surface, (screen_x, screen_y - 45))
        
        # Draw attack animation
        if self.attacking:
            # Calculate attack animation offset
            progress = self.attack_frame / self.attack_duration
            offset = int(20 * (1 - (2 * progress - 1)**2))  # Quadratic easing
            
            # Draw attack effect
            pygame.draw.circle(screen, (255, 255, 0),
                             (int(screen_x + self.width/2 + offset),
                              int(screen_y + self.height/2)),
                             5) 