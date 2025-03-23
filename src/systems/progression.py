from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import json
import os
import time

class MetaUpgradeType(Enum):
    DAMAGE_BOOST = "damage_boost"
    XP_GAIN = "xp_gain"
    GOLD_GAIN = "gold_gain"
    STARTING_LEVEL = "starting_level"
    MAX_HEALTH = "max_health"

@dataclass
class MetaUpgrade:
    type: MetaUpgradeType
    name: str
    description: str
    base_cost: int
    max_level: int
    effect_value: float  # e.g., 0.05 for 5% boost

class RunData:
    def __init__(self, run_number: int, player_class: str, 
                 enemies_defeated: int, experience_gained: int,
                 gold_earned: int, duration: float):
        self.run_number = run_number
        self.player_class = player_class
        self.enemies_defeated = enemies_defeated
        self.experience_gained = experience_gained
        self.gold_earned = gold_earned
        self.duration = duration
        self.timestamp = time.time()

class ProgressionSystem:
    def __init__(self):
        self.current_run: Optional[RunData] = None
        self.run_number = 0
        self.total_gold = 0
        self.meta_upgrades: Dict[MetaUpgradeType, int] = {
            upgrade_type: 0 for upgrade_type in MetaUpgradeType
        }
        
        # Define available meta upgrades
        self.available_upgrades = {
            MetaUpgradeType.DAMAGE_BOOST: MetaUpgrade(
                type=MetaUpgradeType.DAMAGE_BOOST,
                name="Damage Boost",
                description="Increase all damage dealt by 5%",
                base_cost=100,
                max_level=10,
                effect_value=0.05
            ),
            MetaUpgradeType.XP_GAIN: MetaUpgrade(
                type=MetaUpgradeType.XP_GAIN,
                name="Experience Boost",
                description="Gain 10% more experience",
                base_cost=150,
                max_level=8,
                effect_value=0.10
            ),
            MetaUpgradeType.GOLD_GAIN: MetaUpgrade(
                type=MetaUpgradeType.GOLD_GAIN,
                name="Gold Boost",
                description="Earn 10% more gold",
                base_cost=200,
                max_level=6,
                effect_value=0.10
            ),
            MetaUpgradeType.STARTING_LEVEL: MetaUpgrade(
                type=MetaUpgradeType.STARTING_LEVEL,
                name="Starting Level",
                description="Start each run 1 level higher",
                base_cost=300,
                max_level=5,
                effect_value=1.0
            ),
            MetaUpgradeType.MAX_HEALTH: MetaUpgrade(
                type=MetaUpgradeType.MAX_HEALTH,
                name="Max Health",
                description="Increase maximum health by 10%",
                base_cost=250,
                max_level=8,
                effect_value=0.10
            )
        }
        
        # Load saved progress
        self.load_progress()
    
    def start_new_run(self, player_class: str) -> None:
        """Start a new run."""
        self.run_number += 1
        self.current_run = RunData(
            run_number=self.run_number,
            player_class=player_class,
            enemies_defeated=0,
            experience_gained=0,
            gold_earned=0,
            duration=0.0
        )
    
    def end_run(self, enemies_defeated: int, experience_gained: int,
                gold_earned: int, duration: float) -> None:
        """End the current run and calculate rewards."""
        if self.current_run:
            # Apply gold gain boost
            gold_multiplier = 1.0 + (self.meta_upgrades[MetaUpgradeType.GOLD_GAIN] * 
                                   self.available_upgrades[MetaUpgradeType.GOLD_GAIN].effect_value)
            gold_earned = int(gold_earned * gold_multiplier)
            
            # Update run data
            self.current_run.enemies_defeated = enemies_defeated
            self.current_run.experience_gained = experience_gained
            self.current_run.gold_earned = gold_earned
            self.current_run.duration = duration
            
            # Add gold to total
            self.total_gold += gold_earned
            
            # Save progress
            self.save_progress()
    
    def get_upgrade_cost(self, upgrade_type: MetaUpgradeType) -> int:
        """Calculate the cost of the next level of an upgrade."""
        current_level = self.meta_upgrades[upgrade_type]
        if current_level >= self.available_upgrades[upgrade_type].max_level:
            return -1  # Max level reached
        
        base_cost = self.available_upgrades[upgrade_type].base_cost
        return int(base_cost * (1.5 ** current_level))
    
    def purchase_upgrade(self, upgrade_type: MetaUpgradeType) -> bool:
        """Purchase the next level of an upgrade."""
        cost = self.get_upgrade_cost(upgrade_type)
        if cost == -1 or self.total_gold < cost:
            return False
        
        self.total_gold -= cost
        self.meta_upgrades[upgrade_type] += 1
        self.save_progress()
        return True
    
    def get_upgrade_effect(self, upgrade_type: MetaUpgradeType) -> float:
        """Get the total effect value of an upgrade."""
        current_level = self.meta_upgrades[upgrade_type]
        return current_level * self.available_upgrades[upgrade_type].effect_value
    
    def get_difficulty_multiplier(self) -> float:
        """Calculate difficulty multiplier based on run number."""
        return 1.0 + (self.run_number * 0.1)  # 10% increase per run
    
    def save_progress(self) -> None:
        """Save progression data to a file."""
        data = {
            'run_number': self.run_number,
            'total_gold': self.total_gold,
            'meta_upgrades': {k.value: v for k, v in self.meta_upgrades.items()}
        }
        
        try:
            with open('progress.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def load_progress(self) -> None:
        """Load progression data from file."""
        try:
            if os.path.exists('progress.json'):
                with open('progress.json', 'r') as f:
                    data = json.load(f)
                    self.run_number = data.get('run_number', 0)
                    self.total_gold = data.get('total_gold', 0)
                    self.meta_upgrades = {
                        MetaUpgradeType(k): v 
                        for k, v in data.get('meta_upgrades', {}).items()
                    }
        except Exception as e:
            print(f"Error loading progress: {e}") 