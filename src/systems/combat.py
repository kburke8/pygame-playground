from typing import List, Tuple, Dict, Any
from entities.player import Player
from entities.enemy import Enemy
from systems.progression import MetaUpgradeType
import random
import time
import pygame

class CombatSystem:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player = None
        self.enemies: List[Enemy] = []
        self.battle_active = False
        self.current_wave = 0
        self.enemies_per_wave = 3
        self.wave_spacing = 100  # pixels between enemies
        
        # Turn-related attributes
        self.battle_duration = 0
        self.last_turn_time = 0
        self.last_turn_processed = 0
        self.turn_delay = 0.2  # seconds between turns
        self.turn_order = []
        self.battle_state = 'preparation'  # 'preparation', 'battle', 'rewards'
        self.exp_gained = 0
        self.gold_earned = 0
        self.enemies_defeated = 0
        
    def start_battle(self, player: Player, enemies: List[Enemy]):
        """Start a new battle with the given player and enemies."""
        self.player = player
        self.enemies = enemies.copy()  # Make a copy of the enemies list
        self.battle_active = True
        self.current_wave = 0
        self.battle_start_time = time.time()
        self._spawn_wave()
        
    def _spawn_wave(self):
        """Spawn a new wave of enemies."""
        # Determine enemy types based on wave number
        enemy_types = ['basic']
        if self.current_wave >= 2:
            enemy_types.append('ranged')
        if self.current_wave >= 4:
            enemy_types.append('tank')
            
        # Spawn enemies in a line
        start_x = self.screen_width // 2 - (self.enemies_per_wave * self.wave_spacing) // 2
        for i in range(self.enemies_per_wave):
            enemy_type = random.choice(enemy_types)
            enemy = Enemy(start_x + i * self.wave_spacing, 100, enemy_type)
            self.enemies.append(enemy)
            
    def update(self) -> bool:
        """Update the battle state. Returns True if battle is still active."""
        if not self.battle_active:
            return False
            
        # Update player
        self.player.update()
        
        # Update enemies
        for enemy in self.enemies[:]:  # Use slice copy to avoid modification during iteration
            enemy.update()
            
            # Check if enemy is in range to attack player
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance <= enemy.attack_range:
                enemy.attack(self.player)
                
            # Check if player is in range to attack enemy
            if distance <= self.player.attack_range:
                self.player.attack(enemy)
                
            # Remove dead enemies
            if enemy.stats.hp <= 0:
                self.enemies.remove(enemy)
                
        # Check if wave is complete
        if not self.enemies:
            self.current_wave += 1
            self._spawn_wave()
            
        # Check if player is dead
        if self.player.stats.hp <= 0:
            self.battle_active = False
            return False
            
        return True
        
    def draw(self, screen: pygame.Surface):
        """Draw the battle state."""
        # Draw player
        self.player.draw(screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)
            
        # Draw wave number
        wave_text = f"Wave {self.current_wave + 1}"
        wave_surface = pygame.font.Font(None, 36).render(wave_text, True, (255, 255, 255))
        screen.blit(wave_surface, (10, 10))
        
    def is_battle_active(self) -> bool:
        """Check if a battle is currently active."""
        return self.battle_active
        
    def get_battle_rewards(self) -> dict:
        """Calculate and return battle rewards."""
        if not self.battle_active:
            return {}
            
        # Base rewards
        gold = self.current_wave * 10
        experience = self.current_wave * 5
        
        # Bonus rewards for surviving longer
        if self.current_wave >= 5:
            gold *= 2
            experience *= 2
            
        return {
            'gold': gold,
            'experience': experience,
            'wave': self.current_wave
        }
    
    def _get_enemy_exp(self, enemy: Enemy) -> int:
        """Get experience value for enemy type."""
        exp_values = {
            'basic': 10,
            'ranged': 15,
            'tank': 20
        }
        return exp_values.get(enemy.enemy_type, 10)
        
    def _get_enemy_gold(self, enemy: Enemy) -> int:
        """Get gold value for enemy type."""
        gold_values = {
            'basic': 5,
            'ranged': 8,
            'tank': 12
        }
        return gold_values.get(enemy.enemy_type, 5)
        
    def process_turn(self, player: Player, enemies: List[Enemy], current_time: float) -> List[str]:
        """Process a single turn of combat."""
        log_entries = []
        
        # Update battle duration
        self.battle_duration = current_time
        
        # Process player's turn
        if current_time - self.last_turn_time >= self.turn_delay:
            # Player attacks nearest enemy
            if self.enemies:  # Only proceed if there are enemies
                nearest_enemy = min(self.enemies, 
                                 key=lambda e: ((e.x - player.x)**2 + 
                                              (e.y - player.y)**2)**0.5)
                
                # Calculate distance to nearest enemy
                dx = nearest_enemy.x - player.x
                dy = nearest_enemy.y - player.y
                distance = (dx**2 + dy**2)**0.5
                
                if distance <= player.attack_range:
                    # Player attacks enemy
                    if player.attack(nearest_enemy):
                        log_entries.append(f"Player attacks {nearest_enemy.enemy_type} for {player.stats.attack} damage")
                        
                        # Check if enemy died
                        if nearest_enemy.stats.hp <= 0:
                            # Add rewards
                            exp_gained = self._get_enemy_exp(nearest_enemy)
                            gold_gained = self._get_enemy_gold(nearest_enemy)
                            self.exp_gained += exp_gained
                            self.gold_earned += gold_gained
                            self.enemies_defeated += 1
                            
                            # Give experience to player
                            player.gain_experience(exp_gained)
                            
                            # Remove dead enemy
                            self.enemies.remove(nearest_enemy)
                            log_entries.append(f"{nearest_enemy.enemy_type} defeated! +{exp_gained} XP, +{gold_gained} Gold")
                            
                            # Check if all enemies are defeated
                            if not self.enemies:
                                self.battle_active = False
                                log_entries.append("Wave complete!")
            
            # Process enemy turns
            for enemy in self.enemies[:]:  # Use slice copy to avoid modification during iteration
                # Calculate distance to player
                dx = player.x - enemy.x
                dy = player.y - enemy.y
                distance = (dx**2 + dy**2)**0.5
                
                # Enemy attacks player if in range
                if distance <= enemy.attack_range:
                    if enemy.attack(player):
                        log_entries.append(f"{enemy.enemy_type} attacks player for {enemy.stats.attack} damage")
                        
                        # Check if player died
                        if player.stats.hp <= 0:
                            self.battle_active = False
                            log_entries.append("Player defeated!")
                            break
            
            self.last_turn_time = current_time
        
        return log_entries
    
    def get_battle_stats(self) -> Dict[str, Any]:
        """Get current battle statistics."""
        return {
            'duration': round(self.battle_duration, 1),
            'exp_gained': self.exp_gained,
            'gold_earned': self.gold_earned,
            'enemies_defeated': len([e for e in self.enemies if e.stats.hp <= 0])
        } 