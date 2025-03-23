# Roguelike ARPG Autobattler

A Python-based roguelike ARPG with automated combat, featuring character classes, skills, passives, and gear systems.

## Features

### Core Gameplay
- Three unique character classes with distinct playstyles
- Automated combat system with turn-based mechanics
- Screen-wrapping movement (characters wrap around screen edges)
- Experience and leveling system
- Multiple enemy types with different stats and behaviors

### Character Classes
1. **Warrior**
   - High HP, balanced stats
   - Skill: Whirlwind (damage all nearby enemies)
   - Passive: Toughness (20% damage reduction)

2. **Rogue**
   - High Speed, High Damage
   - Skill: Backstab (massive damage from behind)
   - Passive: Critical Strike (15% chance for double damage)

3. **Mage**
   - High Damage, Low HP
   - Skill: Fireball (powerful ranged attack)
   - Passive: Arcane Power (25% increased damage)

### Combat System
- Turn-based combat with speed-based initiative
- Automatic targeting of nearest enemies
- Visual battle log showing actions and damage
- Experience gained from defeating enemies
- Victory/defeat conditions

### Enemy Types
1. **Goblin**
   - Balanced stats
   - 80 HP
   - Moderate attack and defense

2. **Skeleton**
   - High attack, low defense
   - 60 HP
   - Fast movement

3. **Slime**
   - High HP, low attack
   - 100 HP
   - Slow but tanky

### Skills & Passives
- Each class has unique skills with cooldowns
- Passive abilities that modify combat
- Visual cooldown tracking
- Skill effects displayed in battle log

### Gear System
- Three equipment slots:
  - Weapon
  - Armor
  - Accessory
- Items with stats and rarity levels
- Inventory management
- Level-scaling item stats

## Controls

### Character Selection
- `1`: Select Warrior
- `2`: Select Rogue
- `3`: Select Mage
- `ENTER`: Start game

### Gameplay
- `SPACE`: Start battle / Continue to next round
- `I`: Open/Close inventory
- `ESC`: Exit game

### Inventory
- `1`: Skills tab
- `2`: Passives tab
- `3`: Gear tab
- `SPACE`: Close inventory
- `ESC`: Exit game

## Game Flow

1. **Character Selection**
   - Choose your character class
   - Preview character appearance
   - Press ENTER to start

2. **Main Game**
   - Move around the screen (wraps at edges)
   - Press SPACE to start battle
   - Press I to check inventory

3. **Combat**
   - Automated turn-based combat
   - Watch battle log for actions
   - Press SPACE to continue

4. **Rewards**
   - View experience gained
   - Press SPACE for next round

5. **Inventory Management**
   - View skills and cooldowns
   - Check passive abilities
   - Manage equipped gear and inventory

## Requirements

- Python 3.8+
- Pygame 2.0+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/roguelike-arpg-autobattler.git
cd roguelike-arpg-autobattler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python src/main.py
```

## Project Structure

```
src/
├── main.py              # Main game loop and UI
├── game/
│   └── world.py        # World and screen management
├── entities/
│   ├── entity.py       # Base entity class
│   ├── player.py       # Player class and stats
│   └── enemy.py        # Enemy types and behaviors
└── systems/
    ├── combat.py       # Combat mechanics
    ├── abilities.py    # Skills and passives
    └── gear.py         # Equipment system
```

## Contributing

Feel free to submit issues and enhancement requests! 