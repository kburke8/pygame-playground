from dataclasses import dataclass
from typing import List, Dict, Optional
import time

@dataclass
class Skill:
    name: str
    damage: int
    cooldown: float  # in seconds
    description: str
    last_used: float = 0
    
    def can_use(self) -> bool:
        """Check if the skill is off cooldown."""
        return time.time() - self.last_used >= self.cooldown
    
    def use(self) -> bool:
        """Use the skill if it's off cooldown."""
        if self.can_use():
            self.last_used = time.time()
            return True
        return False

@dataclass
class Passive:
    name: str
    description: str
    effect_type: str  # 'crit_chance', 'life_steal', 'damage_bonus', etc.
    value: float
    trigger_chance: float = 1.0  # 0.0 to 1.0

class AbilitySystem:
    def __init__(self):
        self.skills: List[Skill] = []
        self.passives: List[Passive] = []
        self.max_skills = 4  # Maximum number of skills that can be equipped
        
    def add_skill(self, skill: Skill) -> bool:
        """Add a skill if there's room."""
        if len(self.skills) < self.max_skills:
            self.skills.append(skill)
            return True
        return False
    
    def remove_skill(self, skill_name: str) -> bool:
        """Remove a skill by name."""
        for skill in self.skills:
            if skill.name == skill_name:
                self.skills.remove(skill)
                return True
        return False
    
    def add_passive(self, passive: Passive) -> bool:
        """Add a passive trait."""
        self.passives.append(passive)
        return True
    
    def remove_passive(self, passive_name: str) -> bool:
        """Remove a passive by name."""
        for passive in self.passives:
            if passive.name == passive_name:
                self.passives.remove(passive)
                return True
        return False
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name."""
        for skill in self.skills:
            if skill.name == skill_name:
                return skill
        return None
    
    def get_passive(self, passive_name: str) -> Optional[Passive]:
        """Get a passive by name."""
        for passive in self.passives:
            if passive.name == passive_name:
                return passive
        return None
    
    def get_passives_by_type(self, effect_type: str) -> List[Passive]:
        """Get all passives of a specific type."""
        return [p for p in self.passives if p.effect_type == effect_type]
    
    def apply_passive_effects(self, base_damage: int, is_critical: bool = False) -> Dict[str, float]:
        """Apply passive effects to damage calculation."""
        effects = {
            'damage_multiplier': 1.0,
            'life_steal': 0.0,
            'crit_chance': 0.0,
            'crit_multiplier': 1.0
        }
        
        for passive in self.passives:
            if passive.effect_type == 'damage_bonus':
                effects['damage_multiplier'] += passive.value
            elif passive.effect_type == 'life_steal':
                effects['life_steal'] += passive.value
            elif passive.effect_type == 'crit_chance':
                effects['crit_chance'] += passive.value
            elif passive.effect_type == 'crit_multiplier':
                effects['crit_multiplier'] += passive.value
        
        return effects 