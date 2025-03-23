import pygame
import sys
from pathlib import Path
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
COUNTDOWN_TIME = 5  # seconds between rounds

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SEMI_TRANSPARENT = (0, 0, 0, 128)  # Black with 50% transparency
GOLD = (255, 215, 0)  # Color for gold text

# Import our game components
from game.world import World
from entities.player import Player
from entities.enemy import Enemy
from systems.combat import CombatSystem
from systems.gear import GearSlot
from systems.progression import ProgressionSystem, MetaUpgradeType

class Game:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Roguelike ARPG Autobattler")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = 'character_select'  # 'character_select', 'playing', 'battle', 'countdown', 'rewards', 'inventory', 'meta_upgrades'
        self.selected_class = 'warrior'
        self.inventory_page = 0  # 0: skills, 1: passives, 2: gear
        self.current_wave = 0  # Track current wave number
        
        # Initialize game world and entities
        self.world = World(self.screen_width, self.screen_height)  # Fixed screen size
        self.player = None
        self.enemies = []
        
        # Combat system
        self.combat = CombatSystem(self.screen_width, self.screen_height)
        
        # Progression system
        self.progression = ProgressionSystem()
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Battle log
        self.battle_log = []
        self.max_log_entries = 5
        
        # Create preview player
        self.preview_player = Player(self.screen_width // 2, self.screen_height // 2, self.selected_class, self.progression)
        
        # Game time and countdown
        self.start_time = time.time()
        self.countdown_start = 0
        self.countdown_remaining = COUNTDOWN_TIME
        
        # Meta-upgrades UI
        self.selected_upgrade = 0
        self.upgrade_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
        
    def start_game(self):
        # Create player at center
        self.player = Player(self.screen_width // 2, self.screen_height // 2, self.selected_class, self.progression)
        
        # Create some enemies
        self.enemies = []
        num_enemies = 3
        enemy_types = ['basic']
        if self.current_wave >= 2:
            enemy_types.append('ranged')
        if self.current_wave >= 4:
            enemy_types.append('tank')
            
        for _ in range(num_enemies):
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(100, self.screen_height - 100)
            enemy_type = random.choice(enemy_types)
            enemy = Enemy(x, y, enemy_type)
            self.enemies.append(enemy)
            
        # Start battle
        self.combat.start_battle(self.player, self.enemies)
        self.state = 'battle'
        self.battle_log = []
        self.start_time = time.time()

    def start_battle(self):
        self.state = 'battle'
        self.combat.start_battle(self.player, self.enemies)
        self.battle_log = []
        self.start_time = time.time()

    def start_countdown(self):
        self.state = 'countdown'
        self.countdown_start = time.time()
        self.countdown_remaining = COUNTDOWN_TIME

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 'inventory':
                        self.state = 'playing'
                    elif self.state == 'meta_upgrades':
                        self.state = 'character_select'
                    else:
                        self.running = False
                elif self.state == 'character_select':
                    if event.key == pygame.K_1:
                        self.selected_class = 'warrior'
                        self.preview_player = Player(self.screen_width // 2, self.screen_height // 2, self.selected_class, self.progression)
                    elif event.key == pygame.K_2:
                        self.selected_class = 'rogue'
                        self.preview_player = Player(self.screen_width // 2, self.screen_height // 2, self.selected_class, self.progression)
                    elif event.key == pygame.K_3:
                        self.selected_class = 'mage'
                        self.preview_player = Player(self.screen_width // 2, self.screen_height // 2, self.selected_class, self.progression)
                    elif event.key == pygame.K_m:
                        self.state = 'meta_upgrades'
                    elif event.key == pygame.K_RETURN:
                        self.progression.start_new_run(self.selected_class)
                        self.start_game()
                elif self.state == 'meta_upgrades':
                    if event.key in self.upgrade_keys:
                        upgrade_index = self.upgrade_keys.index(event.key)
                        upgrade_types = list(MetaUpgradeType)
                        if upgrade_index < len(upgrade_types):
                            upgrade_type = upgrade_types[upgrade_index]
                            if self.progression.purchase_upgrade(upgrade_type):
                                # Play a sound or show visual feedback
                                pass
                    elif event.key == pygame.K_RETURN:
                        # Start new run after viewing meta-upgrades
                        self.progression.start_new_run(self.selected_class)
                        self.start_game()
                elif self.state == 'playing':
                    if event.key == pygame.K_SPACE:
                        self.start_battle()
                    elif event.key == pygame.K_i:
                        self.state = 'inventory'
                elif self.state == 'battle':
                    # Remove space to continue during battle
                    pass
                elif self.state == 'rewards':
                    if event.key == pygame.K_SPACE:
                        self.state = 'meta_upgrades'  # Go to meta-upgrades after death
                elif self.state == 'inventory':
                    if event.key == pygame.K_1:
                        self.inventory_page = 0
                    elif event.key == pygame.K_2:
                        self.inventory_page = 1
                    elif event.key == pygame.K_3:
                        self.inventory_page = 2
                    elif event.key == pygame.K_SPACE:
                        self.state = 'playing'

    def update(self):
        if self.state in ['playing', 'battle', 'rewards']:
            # Update entities
            self.player.update()
            
            # Handle screen wrapping for player
            self.player.x = self.player.x % self.screen_width
            self.player.y = self.player.y % self.screen_height
            
            # Update enemies and remove dead ones
            for enemy in self.enemies[:]:  # Use slice copy to avoid modification during iteration
                enemy.update()
                # Handle screen wrapping for enemies
                enemy.x = enemy.x % self.screen_width
                enemy.y = enemy.y % self.screen_height
                
                # Remove dead enemies
                if enemy.stats.hp <= 0:
                    self.enemies.remove(enemy)
            
            # Check if all enemies are defeated
            if not self.enemies and self.state == 'battle':
                # Get battle stats
                battle_stats = self.combat.get_battle_stats()
                
                # End current run and save rewards
                self.progression.end_run(
                    enemies_defeated=battle_stats['enemies_defeated'],
                    experience_gained=battle_stats['exp_gained'],
                    gold_earned=battle_stats['gold_earned'],
                    duration=battle_stats['duration']
                )
                
                # Start next wave
                self.state = 'playing'
                self.spawn_enemies()
                self.battle_log = []  # Clear battle log for next wave
                self.start_time = time.time()
                
            # Move player towards nearest enemy if in battle
            if self.state == 'battle' and self.combat.is_battle_active():
                if self.enemies:  # Only proceed if there are enemies
                    nearest_enemy = min(self.enemies, 
                                     key=lambda e: ((e.x - self.player.x)**2 + 
                                                  (e.y - self.player.y)**2)**0.5)
                    
                    # Calculate distance to nearest enemy
                    dx = nearest_enemy.x - self.player.x
                    dy = nearest_enemy.y - self.player.y
                    distance = (dx**2 + dy**2)**0.5
                    
                    # If we're close enough to attack, stop moving and attack
                    if distance <= self.player.attack_range:
                        self.player.set_target(self.player.x, self.player.y)
                        self.player.attack(nearest_enemy)  # Attack when in range
                    else:
                        self.player.set_target(nearest_enemy.x, nearest_enemy.y)
                        
                    # Process combat turns
                    current_time = time.time() - self.start_time
                    new_log_entries = self.combat.process_turn(self.player, self.enemies, current_time)
                    self.battle_log.extend(new_log_entries)
                    # Keep only the last few entries
                    self.battle_log = self.battle_log[-self.max_log_entries:]
                    
                    # Check if battle is over
                    if not self.combat.is_battle_active():
                        # Get battle stats
                        battle_stats = self.combat.get_battle_stats()
                        
                        # End current run and save rewards
                        self.progression.end_run(
                            enemies_defeated=battle_stats['enemies_defeated'],
                            experience_gained=battle_stats['exp_gained'],
                            gold_earned=battle_stats['gold_earned'],
                            duration=battle_stats['duration']
                        )
                        
                        # Check if player died
                        if self.player.stats.hp <= 0:
                            self.state = 'rewards'
                        else:
                            # Start next wave
                            self.state = 'playing'
                            self.spawn_enemies()
                            self.battle_log = []  # Clear battle log for next wave
                            self.start_time = time.time()
        elif self.state == 'countdown':
            # Update countdown
            current_time = time.time()
            self.countdown_remaining = max(0, COUNTDOWN_TIME - (current_time - self.countdown_start))
            
            if self.countdown_remaining <= 0:
                # Start next round
                self.state = 'playing'
                self.spawn_enemies()
        else:
            # Update preview player
            self.preview_player.update()

    def render(self):
        self.screen.fill(BLACK)
        
        # Draw the world
        self.world.draw(self.screen)
        
        if self.state == 'character_select':
            # Draw preview player
            self.preview_player.draw(self.screen, self.world)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill(BLACK)
            overlay.set_alpha(64)  # Less dim overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw character selection UI
            title = self.font.render("Select Your Character", True, WHITE)
            warrior = self.font.render("1 - Warrior (High HP, Balanced)", True, WHITE)
            rogue = self.font.render("2 - Rogue (High Speed, High Damage)", True, WHITE)
            mage = self.font.render("3 - Mage (High Damage, Low HP)", True, WHITE)
            start = self.font.render("Press ENTER to Start", True, WHITE)
            meta = self.font.render("Press M for Meta-Upgrades", True, GOLD)
            
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            self.screen.blit(warrior, (self.screen_width//2 - warrior.get_width()//2, 200))
            self.screen.blit(rogue, (self.screen_width//2 - rogue.get_width()//2, 250))
            self.screen.blit(mage, (self.screen_width//2 - mage.get_width()//2, 300))
            self.screen.blit(start, (self.screen_width//2 - start.get_width()//2, 400))
            self.screen.blit(meta, (self.screen_width//2 - meta.get_width()//2, 450))
        elif self.state == 'meta_upgrades':
            self._render_meta_upgrades()
        else:
            # Draw game entities
            self.player.draw(self.screen, self.world)
            for enemy in self.enemies:
                enemy.draw(self.screen, self.world)
            
            # Draw battle UI
            if self.state == 'battle' and self.combat.is_battle_active():
                # Draw semi-transparent overlay
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.fill(BLACK)
                overlay.set_alpha(64)  # Less dim overlay
                self.screen.blit(overlay, (0, 0))
                
                # Draw battle log
                y = self.screen_height - 200
                for entry in self.battle_log[-5:]:  # Show last 5 entries
                    text = self.small_font.render(entry, True, WHITE)
                    self.screen.blit(text, (10, y))
                    y += 20
                
                # Draw instructions
                text = self.small_font.render("Press SPACE to continue", True, WHITE)
                self.screen.blit(text, (10, self.screen_height - 50))
            elif self.state == 'inventory':
                self._render_inventory()
            elif self.state == 'rewards':
                # Draw semi-transparent overlay
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.fill(BLACK)
                overlay.set_alpha(64)  # Less dim overlay
                self.screen.blit(overlay, (0, 0))
                
                # Draw rewards text
                text = self.font.render("Battle Complete!", True, WHITE)
                self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 100))
                
                # Draw experience gained
                battle_stats = self.combat.get_battle_stats()
                exp_gained = battle_stats.get('exp_gained', 0)
                exp_text = self.font.render(f"Experience Gained: {exp_gained}", True, WHITE)
                self.screen.blit(exp_text, (self.screen_width//2 - exp_text.get_width()//2, 200))
                
                # Draw gold earned
                gold_earned = battle_stats.get('gold_earned', 0)
                gold_text = self.font.render(f"Gold Earned: {gold_earned}", True, GOLD)
                self.screen.blit(gold_text, (self.screen_width//2 - gold_text.get_width()//2, 250))
                
                # Draw instructions
                text = self.small_font.render("Press SPACE to view Meta-Upgrades", True, WHITE)
                self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, self.screen_height - 50))
        
        pygame.display.flip()

    def _render_inventory(self):
        """Render the inventory UI with skills, passives, and gear."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill(BLACK)
        overlay.set_alpha(64)  # Less dim overlay
        self.screen.blit(overlay, (0, 0))
        
        # Draw inventory tabs
        tabs = ['Skills', 'Passives', 'Gear']
        for i, tab in enumerate(tabs):
            color = WHITE if i == self.inventory_page else (128, 128, 128)
            text = self.font.render(f"{i+1} - {tab}", True, color)
            self.screen.blit(text, (10 + i * 200, 10))
        
        # Draw content based on current page
        if self.inventory_page == 0:
            self._render_skills()
        elif self.inventory_page == 1:
            self._render_passives()
        else:
            self._render_gear()
        
        # Draw instructions
        instructions = [
            "Press 1-3 to switch tabs",
            "Press SPACE to close inventory",
            "Press ESC to exit game"
        ]
        for i, text in enumerate(instructions):
            text_surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(text_surface, (10, self.screen_height - 100 + i * 25))
    
    def _render_skills(self):
        """Render the skills page."""
        y = 60
        for skill in self.player.abilities.skills:
            # Draw skill name and cooldown
            name_text = self.font.render(skill.name, True, WHITE)
            cooldown_text = self.small_font.render(f"Cooldown: {skill.cooldown}s", True, WHITE)
            self.screen.blit(name_text, (20, y))
            self.screen.blit(cooldown_text, (20, y + 25))
            
            # Draw cooldown bar
            if not skill.can_use():
                cooldown_progress = (time.time() - skill.last_used) / skill.cooldown
                bar_width = 200
                bar_height = 5
                pygame.draw.rect(self.screen, (100, 100, 100),
                               (20, y + 50, bar_width, bar_height))
                pygame.draw.rect(self.screen, (0, 255, 0),
                               (20, y + 50, bar_width * cooldown_progress, bar_height))
            
            y += 100
    
    def _render_passives(self):
        """Render the passives page."""
        y = 60
        for passive in self.player.abilities.passives:
            # Draw passive name and description
            name_text = self.font.render(passive.name, True, WHITE)
            desc_text = self.small_font.render(passive.description, True, WHITE)
            self.screen.blit(name_text, (20, y))
            self.screen.blit(desc_text, (20, y + 25))
            y += 80
    
    def _render_gear(self):
        """Render the gear page."""
        y = 60
        # Draw equipped items
        for slot in GearSlot:
            item = self.player.gear.get_equipped_item(slot)
            slot_text = self.font.render(f"{slot.value.title()}:", True, WHITE)
            self.screen.blit(slot_text, (20, y))
            
            if item:
                name_text = self.small_font.render(item.name, True, WHITE)
                stats_text = self.small_font.render(str(item.stats), True, WHITE)
                self.screen.blit(name_text, (20, y + 25))
                self.screen.blit(stats_text, (20, y + 45))
            else:
                empty_text = self.small_font.render("Empty", True, (128, 128, 128))
                self.screen.blit(empty_text, (20, y + 25))
            
            y += 80
        
        # Draw inventory items
        y += 20
        inventory_text = self.font.render("Inventory:", True, WHITE)
        self.screen.blit(inventory_text, (20, y))
        y += 40
        
        for item in self.player.gear.inventory:
            name_text = self.small_font.render(item.name, True, WHITE)
            stats_text = self.small_font.render(str(item.stats), True, WHITE)
            self.screen.blit(name_text, (20, y))
            self.screen.blit(stats_text, (20, y + 20))
            y += 60

    def _render_meta_upgrades(self):
        """Render the meta-upgrades UI."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill(BLACK)
        overlay.set_alpha(64)  # Less dim overlay
        self.screen.blit(overlay, (0, 0))
        
        # Draw title and gold
        title = self.font.render("Meta-Upgrades", True, WHITE)
        gold_text = self.font.render(f"Gold: {self.progression.total_gold}", True, GOLD)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
        self.screen.blit(gold_text, (WINDOW_WIDTH//2 - gold_text.get_width()//2, 60))
        
        # Draw available upgrades
        y = 120
        for i, (upgrade_type, upgrade) in enumerate(self.progression.available_upgrades.items()):
            current_level = self.progression.meta_upgrades[upgrade_type]
            max_level = upgrade.max_level
            
            # Draw upgrade name and level
            name_text = self.font.render(f"{i+1} - {upgrade.name} (Level {current_level}/{max_level})", True, WHITE)
            self.screen.blit(name_text, (20, y))
            
            # Draw description
            desc_text = self.small_font.render(upgrade.description, True, WHITE)
            self.screen.blit(desc_text, (20, y + 30))
            
            # Draw cost
            cost = self.progression.get_upgrade_cost(upgrade_type)
            if cost == -1:
                cost_text = self.small_font.render("MAX LEVEL", True, (128, 128, 128))
            else:
                cost_text = self.small_font.render(f"Cost: {cost} gold", True, GOLD)
            self.screen.blit(cost_text, (20, y + 50))
            
            y += 100
        
        # Draw instructions
        instructions = [
            "Press 1-5 to purchase upgrades",
            "Press ESC to return to character select",
            "Press ENTER to start new run"
        ]
        for i, text in enumerate(instructions):
            text_surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(text_surface, (10, WINDOW_HEIGHT - 100 + i * 25))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

    def spawn_enemies(self):
        """Spawn new enemies for the next wave."""
        self.current_wave += 1
        self.enemies = []
        num_enemies = 3
        
        # Determine enemy types based on wave number
        enemy_types = ['basic']
        if self.current_wave >= 3:  # Changed from wave 2 to wave 3
            enemy_types.append('ranged')
        if self.current_wave >= 5:  # Changed from wave 4 to wave 5
            enemy_types.append('tank')
            
        for _ in range(num_enemies):
            x = random.randint(100, self.screen_width - 100)
            y = random.randint(100, self.screen_height - 100)
            enemy_type = random.choice(enemy_types)
            enemy = Enemy(x, y, enemy_type)
            self.enemies.append(enemy)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit() 