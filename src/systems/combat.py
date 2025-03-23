from typing import List, Tuple, Dict, Any
from entities.player import Player
from entities.enemy import Enemy
import random
import time

class CombatSystem:
    def __init__(self):
        self.battle_state = 'preparation'  # 'preparation', 'battle', 'rewards'
        self.turn_order = []
        self.battle_duration = 0  # Time in seconds
        self.last_turn_time = 0
        self.last_turn_processed = 0
        self.turn_delay = 0.2  # Reduced delay between turns
        self.battle_start_time = 0
        self.exp_gained = 0
        self.enemies = []  # Track current enemies
        
    def start_battle(self, player: Player, enemies: List[Enemy]):
        """Initialize a new battle."""
        self.battle_state = 'battle'
        self.battle_duration = 0
        self.last_turn_time = 0
        self.last_turn_processed = 0
        self.battle_start_time = time.time()
        self.exp_gained = 0
        self.enemies = enemies
        self.turn_order = self._determine_turn_order(player, enemies)
        
    def _determine_turn_order(self, player: Player, enemies: List[Enemy]) -> List[Tuple[str, object]]:
        """Determine the order of turns based on speed."""
        # Create list of (speed, entity) tuples
        entities = [(player.stats.speed, 'player', player)]
        entities.extend([(enemy.stats.speed, 'enemy', enemy) for enemy in enemies])
        
        # Sort by speed (highest first)
        entities.sort(key=lambda x: x[0], reverse=True)
        
        # Return list of (type, entity) tuples
        return [(entity_type, entity) for _, entity_type, entity in entities]
    
    def process_turn(self, player: Player, enemies: List[Enemy], current_time: float) -> List[str]:
        """Process a single turn of combat."""
        battle_log = []
        
        # Update battle duration
        if self.last_turn_time > 0:
            self.battle_duration += current_time - self.last_turn_time
        self.last_turn_time = current_time
        
        # Check if enough time has passed since last turn
        if current_time - self.last_turn_processed < self.turn_delay:
            return battle_log
            
        self.last_turn_processed = current_time
        
        # Process each entity's turn
        for entity_type, entity in self.turn_order:
            if entity_type == 'player':
                # Player's turn
                if enemies:
                    # Find nearest enemy
                    target = min(enemies, 
                              key=lambda e: ((e.x - player.x)**2 + (e.y - player.y)**2)**0.5)
                    if entity.attack(target):
                        damage = max(1, entity.stats.attack - target.stats.defense)
                        target.stats.hp -= damage
                        battle_log.append(f"Player deals {damage} damage to {target.enemy_type}")
                        
                        if target.stats.hp <= 0:
                            battle_log.append(f"{target.enemy_type} defeated!")
                            enemies.remove(target)
                            # Give experience
                            exp_gained = self._calculate_exp(target)
                            player.gain_experience(exp_gained)
                            self.exp_gained += exp_gained  # Track total exp gained
                            battle_log.append(f"Player gained {exp_gained} experience!")
            else:
                # Enemy's turn
                if entity.stats.hp > 0:  # Only act if alive
                    if player.stats.hp > 0:  # Only attack if player is alive
                        if entity.attack(player):
                            damage = max(1, entity.stats.attack - player.stats.defense)
                            player.stats.hp -= damage
                            battle_log.append(f"{entity.enemy_type} deals {damage} damage to Player")
        
        # Check battle end conditions
        if player.stats.hp <= 0:
            self.battle_state = 'rewards'
            battle_log.append("Game Over!")
        elif not enemies:
            self.battle_state = 'rewards'
            battle_log.append("Victory!")
            
        return battle_log
    
    def _calculate_exp(self, enemy: Enemy) -> int:
        """Calculate experience gained from defeating an enemy."""
        base_exp = {
            'goblin': 10,
            'skeleton': 15,
            'slime': 5
        }
        return base_exp.get(enemy.enemy_type, 10)
    
    def is_battle_active(self) -> bool:
        """Check if the battle is still active."""
        return self.battle_state == 'battle'
    
    def get_battle_stats(self) -> Dict[str, Any]:
        """Get current battle statistics."""
        return {
            'duration': round(self.battle_duration, 1),
            'exp_gained': self.exp_gained,
            'enemies_defeated': len([e for e in self.enemies if e.stats.hp <= 0])
        } 