from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class GearSlot(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"

@dataclass
class GearItem:
    name: str
    slot: GearSlot
    stats: Dict[str, float]  # e.g., {'attack': 5, 'defense': 3}
    description: str
    level: int = 1
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    
    def get_stat_bonus(self, stat: str) -> float:
        """Get the bonus value for a specific stat."""
        return self.stats.get(stat, 0.0)
    
    def get_total_stats(self) -> Dict[str, float]:
        """Get all stat bonuses, including level scaling."""
        scaled_stats = {}
        for stat, value in self.stats.items():
            scaled_stats[stat] = value * (1 + (self.level - 1) * 0.1)
        return scaled_stats

class GearSystem:
    def __init__(self):
        self.equipped_items: Dict[GearSlot, Optional[GearItem]] = {
            slot: None for slot in GearSlot
        }
        self.inventory: List[GearItem] = []
        self.max_inventory_size = 20
        
    def equip_item(self, item: GearItem) -> bool:
        """Equip an item to its slot."""
        if item.slot in self.equipped_items:
            # Unequip current item if any
            if self.equipped_items[item.slot]:
                self.unequip_item(item.slot)
            
            self.equipped_items[item.slot] = item
            return True
        return False
    
    def unequip_item(self, slot: GearSlot) -> Optional[GearItem]:
        """Unequip an item from a slot."""
        if slot in self.equipped_items:
            item = self.equipped_items[slot]
            self.equipped_items[slot] = None
            return item
        return None
    
    def add_to_inventory(self, item: GearItem) -> bool:
        """Add an item to inventory if there's room."""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False
    
    def remove_from_inventory(self, item: GearItem) -> bool:
        """Remove an item from inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def get_equipped_item(self, slot: GearSlot) -> Optional[GearItem]:
        """Get the item equipped in a slot."""
        return self.equipped_items.get(slot)
    
    def get_total_stats(self) -> Dict[str, float]:
        """Get total stats from all equipped items."""
        total_stats = {}
        
        for item in self.equipped_items.values():
            if item:
                item_stats = item.get_total_stats()
                for stat, value in item_stats.items():
                    total_stats[stat] = total_stats.get(stat, 0.0) + value
        
        return total_stats
    
    def get_item_by_name(self, name: str) -> Optional[GearItem]:
        """Find an item by name in inventory or equipped items."""
        # Check equipped items
        for item in self.equipped_items.values():
            if item and item.name == name:
                return item
        
        # Check inventory
        for item in self.inventory:
            if item.name == name:
                return item
        
        return None 