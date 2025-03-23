from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Stats:
    level: int = 1
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    speed: int = 1
    
    @classmethod
    def create_warrior(cls) -> 'Stats':
        return cls(
            level=1,
            hp=120,
            max_hp=120,
            attack=15,
            defense=8,
            speed=1
        )
    
    @classmethod
    def create_rogue(cls) -> 'Stats':
        return cls(
            level=1,
            hp=80,
            max_hp=80,
            attack=20,
            defense=3,
            speed=2
        )
    
    @classmethod
    def create_mage(cls) -> 'Stats':
        return cls(
            level=1,
            hp=60,
            max_hp=60,
            attack=25,
            defense=2,
            speed=1
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'level': self.level,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed
        } 