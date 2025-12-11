"""
2D Pygame Fishing Timing Game
Complete implementation with , rod upgrades, and rarity5-stage fishing process system
"""

import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
LIGHT_BLUE = (135, 206, 250)
DARK_BLUE = (0, 50, 150)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

# Game States
class GameState:
    MAIN_MENU = "main_menu"
    GUIDE = "guide"
    SHOP = "shop"
    FISHING = "fishing"
    SELLING = "selling"

# Fish Database
FISH_DATABASE = {
    "Common": ["Cod", "Carp", "Minnow", "Perch", "Sunfish", "Tilapia", "Catfish", 
               "Goldfish", "Bluegill", "Troutlet"],
    "Uncommon": ["Rainbow Trout", "Bass", "Pike", "Mackerel", "Flounder", 
                "Walleye", "Rockfish", "Perch King", "Small Snapper", "Eel"],
    "Rare": ["Salmon", "Swordfish", "Barracuda", "Marlin", "Bluefin Tuna",
             "Sturgeon", "Grouper", "Lionfish", "Golden Trout", "Red Snapper"],
    "Epic": ["Anglerfish", "Giant Catfish", "Ocean Sunfish", "Tarpon",
             "King Mackerel", "Giant Salmon", "Peacock Bass", "Rainbow Marlin",
             "Electric Eel", "Swordfin"],
    "Legendary": ["Kraken Carp", "Mythical Koi", "Leviathan Cod", "Golden Barracuda",
                  "Celestial Tuna", "Phantom Marlin", "Titan Sturgeon", "Dragonfish",
                  "Aurora Salmon", "Poseidon's Pike"]
}

# Rarity Chances
RARITY_CHANCES_NORMAL = {"Common": 0.65, "Uncommon": 0.20, "Rare": 0.10, "Epic": 0.04, "Legendary": 0.01}
RARITY_CHANCES_CHEAT = {"Legendary": 0.65, "Epic": 0.20, "Uncommon": 0.10, "Common": 0.04, "Rare": 0.01}

# Base Prices
BASE_PRICES = {"Common": 10, "Uncommon": 25, "Rare": 50, "Epic": 100, "Legendary": 250}

# Rod Upgrades
ROD_UPGRADES = {
    "Novice Rod": {"price": 300, "luck": 20},
    "Master Rod": {"price": 1000, "luck": 45}
}

class GameData:
    def __init__(self):
        self.gold = 100  # Starting gold
        self.current_rod = "Basic Rod"
        self.rod_luck = {"Basic Rod": 0, "Novice Rod": 20, "Master Rod": 45}
        self.cheat_mode = False
        self.caught_fish = None
        self.cheat_buffer = ""

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
    
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class CastTimingStage:
    def __init__(self):
        self.marker_x = 0
        self.marker_direction = 1
        self.bar_width = 600
        self.bar_x = 100
        self.bar_y = 400
        self.score = 0
        self.completed = False
        self.stage_time = 0
        
    def update(self, dt):
        if not self.completed:
            self.marker_x += self.marker_direction * 200 * dt
            if self.marker_x >= self.bar_width or self.marker_x <= 0:
                self.marker_direction *= -1
            self.stage_time += dt
            
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.completed:
                    self.score = int((self.marker_x / self.bar_width) * 100)
                    self.completed = True
                    return True
        return False
    
    def draw(self, screen, font):
        # Draw timing bar
        pygame.draw.rect(screen, GRAY, (self.bar_x, self.bar_y, self.bar_width, 20))
        pygame.draw.rect(screen, GREEN, (self.bar_x + self.bar_width * 0.8, self.bar_y, self.bar_width * 0.2, 20))
        
        # Draw moving marker
        marker_x = self.bar_x + self.marker_x
        pygame.draw.rect(screen, RED, (marker_x - 5, self.bar_y - 5, 10, 30))
        
        # Instructions
        instruction = font.render("Stage 1: CAST TIMING - Press SPACE when marker is in green zone!", True, BLACK)
        screen.blit(instruction, (50, 350))
        
        if self.completed:
            score_text = font.render(f"Cast Score: {self.score}", True, BLACK)
            screen.blit(score_text, (50, 430))

class DepthControlStage:
    def __init__(self):
        self.marker_y = 0
        self.marker_direction = 1
        self.ideal_zone_start = 200
        self.ideal_zone_end = 300
        self.score = 0
        self.completed = False
        self.bar_height = 400
        self.bar_x = 150
        self.bar_y = 150
        
    def update(self, dt):
        if not self.completed:
            self.marker_y += self.marker_direction * 150 * dt
            if self.marker_y >= self.bar_height or self.marker_y <= 0:
                self.marker_direction *= -1
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.completed:
                    zone_center = (self.ideal_zone_start + self.ideal_zone_end) / 2
                    distance = abs(self.marker_y - zone_center)
                    max_distance = self.bar_height / 2
                    self.score = max(0, 100 - (distance / max_distance) * 100)
                    self.completed = True
                    return True
        return False
    
    def draw(self, screen, font):
        # Draw depth bar
        pygame.draw.rect(screen, GRAY, (self.bar_x, self.bar_y, 20, self.bar_height))
        
        # Draw ideal zone
        ideal_y = self.bar_y + self.ideal_zone_start
        pygame.draw.rect(screen, GREEN, (self.bar_x - 5, ideal_y, 30, self.ideal_zone_end - self.ideal_zone_start))
        
        # Draw moving marker
        marker_y = self.bar_y + self.marker_y
        pygame.draw.circle(screen, RED, (self.bar_x + 10, marker_y), 8)
        
        # Instructions
        instruction = font.render("Stage 2: DEPTH CONTROL - Press SPACE when marker is in green zone!", True, BLACK)
        screen.blit(instruction, (50, 100))
        
        if self.completed:
            score_text = font.render(f"Depth Score: {int(self.score)}", True, BLACK)
            screen.blit(score_text, (50, 450))

class BiteReactionStage:
    def __init__(self):
        self.bite_time = time.time() + random.uniform(2, 5)
        self.bite_triggered = False
        self.reaction_start = 0
        self.score = 0
        self.completed = False
        self.show_waiting = True
        
    def update(self, dt):
        if not self.completed and not self.bite_triggered:
            if time.time() >= self.bite_time:
                self.bite_triggered = True
                self.reaction_start = time.time()
                self.show_waiting = False
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.completed:
                    if self.bite_triggered:
                        reaction_time = time.time() - self.reaction_start
                        if reaction_time <= 1.0:  # 1 second window
                            self.score = max(0, 100 - (reaction_time * 50))
                        else:
                            self.score = max(0, 50 - (reaction_time - 1) * 25)
                    else:
                        self.score = 0  # Early press
                    self.completed = True
                    return True
        return False
    
    def draw(self, screen, font):
        instruction = font.render("Stage 3: BITE REACTION - Wait for fish bite, then press SPACE!", True, BLACK)
        screen.blit(instruction, (50, 200))
        
        if self.show_waiting:
            waiting_text = font.render("Waiting for fish bite...", True, ORANGE)
            screen.blit(waiting_text, (50, 250))
        
        if self.bite_triggered and not self.completed:
            bite_text = font.render("FISH BITES! Press SPACE NOW!", True, RED)
            screen.blit(bite_text, (50, 300))
        
        if self.completed:
            score_text = font.render(f"Reaction Score: {int(self.score)}", True, BLACK)
            screen.blit(score_text, (50, 350))

class ReelingRhythmStage:
    def __init__(self):
        self.arrow_sequence = []
        self.current_index = 0
        self.correct_presses = 0
        self.total_presses = 5
        self.score = 0
        self.completed = False
        self.generate_sequence()
        
    def generate_sequence(self):
        directions = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
        self.arrow_sequence = [random.choice(directions) for _ in range(self.total_presses)]
        
    def get_arrow_text(self, key):
        arrows = {
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT", 
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN"
        }
        return arrows.get(key, "?")
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    if not self.completed:
                        if event.key == self.arrow_sequence[self.current_index]:
                            self.correct_presses += 1
                        self.current_index += 1
                        if self.current_index >= len(self.arrow_sequence):
                            self.score = (self.correct_presses / self.total_presses) * 100
                            self.completed = True
                            return True
        return False
    
    def draw(self, screen, font):
        instruction = font.render("Stage 4: REELING RHYTHM - Follow the arrow sequence!", True, BLACK)
        screen.blit(instruction, (50, 150))
        
        # Show sequence progress
        sequence_text = "Sequence: "
        for i, key in enumerate(self.arrow_sequence):
            if i < self.current_index:
                if key == self.arrow_sequence[i]:
                    sequence_text += f"[{self.get_arrow_text(key)}] "
                else:
                    sequence_text += f"({self.get_arrow_text(key)}) "
            else:
                sequence_text += f"{self.get_arrow_text(key)} "
        screen.blit(font.render(sequence_text, True, BLACK), (50, 200))
        
        progress_text = f"Progress: {self.current_index}/{self.total_presses} | Correct: {self.correct_presses}"
        screen.blit(font.render(progress_text, True, BLACK), (50, 250))
        
        if self.completed:
            score_text = font.render(f"Rhythm Score: {int(self.score)}", True, BLACK)
            screen.blit(score_text, (50, 300))

class LineTensionStage:
    def __init__(self):
        self.tension_position = 300  # Start in middle of 600px bar
        self.safe_zone_start = 250
        self.safe_zone_end = 350
        self.in_safe_zone_time = 0
        self.total_time = 5.0  # 5 second stage
        self.score = 0
        self.completed = False
        self.elapsed_time = 0
        
    def update(self, dt):
        if not self.completed:
            # Erratic movement simulation
            movement = random.uniform(-80, 80) * dt
            self.tension_position += movement
            self.tension_position = max(0, min(600, self.tension_position))
            
            # Track safe zone time
            if self.safe_zone_start <= self.tension_position <= self.safe_zone_end:
                self.in_safe_zone_time += dt
            
            self.elapsed_time += dt
            if self.elapsed_time >= self.total_time:
                self.score = (self.in_safe_zone_time / self.total_time) * 100
                self.completed = True
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.completed:
                    self.tension_position -= 40  # Nudge up
                    self.tension_position = max(0, self.tension_position)
        return False
        
    def finish_stage(self):
        if not self.completed:
            self.score = (self.in_safe_zone_time / self.total_time) * 100
            self.completed = True
    
    def draw(self, screen, font):
        instruction = font.render("Stage 5: LINE TENSION - Keep marker in green zone! Press SPACE to adjust.", True, BLACK)
        screen.blit(instruction, (50, 100))
        
        # Draw tension bar
        pygame.draw.rect(screen, GRAY, (100, 150, 20, 400))
        
        # Draw safe zone
        safe_y = 150 + (600 - self.safe_zone_end)
        pygame.draw.rect(screen, GREEN, (95, safe_y, 30, self.safe_zone_end - self.safe_zone_start))
        
        # Draw tension marker
        tension_y = 150 + (600 - self.tension_position)
        pygame.draw.circle(screen, RED, (110, tension_y), 10)
        
        # Draw time remaining
        remaining_time = max(0, self.total_time - self.elapsed_time)
        time_text = font.render(f"Time Remaining: {remaining_time:.1f}s", True, BLACK)
        screen.blit(time_text, (200, 500))
        
        if self.completed:
            score_text = font.render(f"Tension Score: {int(self.score)}", True, BLACK)
            screen.blit(score_text, (200, 530))

def calculate_quality(stage_scores):
    """Calculate fish quality based on stage scores"""
    quality = sum(stage_scores) / len(stage_scores)
    
    if quality >= 90:
        return "Perfect"
    elif quality >= 70:
        return "Great"
    elif quality >= 40:
        return "Fine"
    elif quality >= 10:
        return "Rough"
    else:
        return "Trash"

def spawn_fish(rod_luck, cheat_mode):
    """Spawn a fish based on rarity probabilities"""
    base_chances = RARITY_CHANCES_CHEAT if cheat_mode else RARITY_CHANCES_NORMAL
    
    # Adjust probabilities based on rod luck
    luck_bonus = rod_luck / 1000
    adjusted_chances = {}
    
    for rarity, chance in base_chances.items():
        if rarity in ["Rare", "Epic", "Legendary"]:
            adjusted_chances[rarity] = min(0.8, chance + luck_bonus)
        else:
            adjusted_chances[rarity] = max(0.01, chance - luck_bonus * 0.5)
    
    # Normalize probabilities
    total = sum(adjusted_chances.values())
    for rarity in adjusted_chances:
        adjusted_chances[rarity] /= total
    
    # Select rarity
    random_value = random.random()
    cumulative = 0
    selected_rarity = "Common"
    for rarity, chance in adjusted_chances.items():
        cumulative += chance
        if random_value <= cumulative:
            selected_rarity = rarity
            break
    
    # Select specific fish from rarity
    fish_name = random.choice(FISH_DATABASE[selected_rarity])
    return {"name": fish_name, "rarity": selected_rarity}

def calculate_selling_price(fish_rarity, quality_percentage):
    """Calculate selling price based on fish rarity and quality"""
    base_price = BASE_PRICES[fish_rarity]
    quality_multiplier = quality_percentage / 100
    return int(base_price * (quality_multiplier ** 1.5))

def draw_main_menu(screen, font, buttons, cheat_mode, gold):
    """Draw the main menu screen"""
    screen.fill(LIGHT_BLUE)
    
    # Title
    title = font.render("FISHING MASTERY", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
    screen.blit(title, title_rect)
    
    # Draw buttons
    for button in buttons:
        button.draw(screen)
    
    # Display gold
    gold_text = font.render(f"Gold: {gold}", True, BLACK)
    screen.blit(gold_text, (10, 10))
    
    # Display cheat mode status
    if cheat_mode:
        cheat_text = font.render("CHEAT MODE ACTIVE", True, RED)
        screen.blit(cheat_text, (10, 40))
    
    # Instructions
    instruction = font.render("Type 'lucknow' for enhanced fishing!", True, BLACK)
    screen.blit(instruction, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 50))

def draw_guide_screen(screen, font):
    """Draw the guide screen explaining fishing stages"""
    screen.fill(LIGHT_BLUE)
    
    title = font.render("FISHING GUIDE", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
    screen.blit(title, title_rect)
    
    guide_texts = [
        "Stage 1 - CAST TIMING: Press SPACE when the moving marker is in the green zone",
        "Stage 2 - DEPTH CONTROL: Press SPACE when the marker is in the ideal depth range", 
        "Stage 3 - BITE REACTION: Wait for the fish to bite, then press SPACE quickly",
        "Stage 4 - REELING RHYTHM: Follow the arrow sequence using arrow keys",
        "Stage 5 - LINE TENSION: Keep the tension marker in the safe zone using SPACE",
        "",
        "FISH QUALITY affects selling price: Perfect > Great > Fine > Rough > Trash",
        "Upgrade your rod for better chances at rare fish!",
        "Type 'lucknow' in the main menu for enhanced fish rarity!"
    ]
    
    y_offset = 120
    for text in guide_texts:
        if text:
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (50, y_offset))
        y_offset += 40
    
    back_text = font.render("Press ESC to return to menu", True, BLACK)
    screen.blit(back_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 50))

def draw_shop_screen(screen, font, current_rod, gold):
    """Draw the shop screen for rod upgrades"""
    screen.fill(LIGHT_BLUE)
    
    title = font.render("FISHING SHOP", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
    screen.blit(title, title_rect)
    
    # Current rod info
    current_text = font.render(f"Current Rod: {current_rod}", True, BLACK)
    screen.blit(current_text, (50, 120))
    
    # Gold display
    gold_text = font.render(f"Gold: {gold}", True, BLACK)
    screen.blit(gold_text, (50, 160))
    
    # Available rods
    y_offset = 220
    for rod_name, rod_info in ROD_UPGRADES.items():
        if rod_name != current_rod:
            rod_text = font.render(f"{rod_name}: {rod_info['price']} gold (Luck +{rod_info['luck']})", True, BLACK)
            screen.blit(rod_text, (50, y_offset))
            y_offset += 40
    
    back_text = font.render("Press ESC to return to menu", True, BLACK)
    screen.blit(back_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 50))

def draw_fishing_interface(screen, font, current_stage, stages, gold, current_rod):
    """Draw the fishing interface with player, water, and stage UI"""
    screen.fill(LIGHT_BLUE)
    
    # Draw player at top
    pygame.draw.circle(screen, GREEN, (WINDOW_WIDTH // 2, 50), 20)
    player_text = font.render("FISHER", True, BLACK)
    player_rect = player_text.get_rect(center=(WINDOW_WIDTH // 2, 90))
    screen.blit(player_text, player_rect)
    
    # Draw water area
    pygame.draw.rect(screen, BLUE, (0, 120, WINDOW_WIDTH, WINDOW_HEIGHT - 120))
    water_text = font.render("WATER", True, WHITE)
    screen.blit(water_text, (10, 130))
    
    # Draw hook line
    hook_x = WINDOW_WIDTH // 2
    hook_y = 200  # Default hook position
    pygame.draw.line(screen, BLACK, (WINDOW_WIDTH // 2, 70), (hook_x, hook_y), 2)
    pygame.draw.circle(screen, RED, (hook_x, hook_y), 5)
    
    # UI Elements
    gold_text = font.render(f"Gold: {gold}", True, BLACK)
    screen.blit(gold_text, (10, 10))
    
    rod_text = font.render(f"Rod: {current_rod}", True, BLACK)
    screen.blit(rod_text, (WINDOW_WIDTH - 150, 10))
    
    # Stage progress
    stage_text = font.render(f"Stage {current_stage}/5", True, BLACK)
    screen.blit(stage_text, (10, 40))
    
    # Draw current stage interface
    if current_stage == 1:
        stages[0].draw(screen, font)
    elif current_stage == 2:
        stages[1].draw(screen, font)
    elif current_stage == 3:
        stages[2].draw(screen, font)
    elif current_stage == 4:
        stages[3].draw(screen, font)
    elif current_stage == 5:
        stages[4].draw(screen, font)

def draw_selling_screen(screen, font, fish_info, quality, quality_score, selling_price):
    """Draw the selling screen showing caught fish"""
    screen.fill(LIGHT_BLUE)
    
    title = font.render("FISH CAUGHT!", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
    screen.blit(title, title_rect)
    
    # Fish info
    fish_name = font.render(f"Fish: {fish_info['name']}", True, BLACK)
    fish_rarity = font.render(f"Rarity: {fish_info['rarity']}", True, BLACK)
    quality_text = font.render(f"Quality: {quality} ({int(quality_score)}%)", True, BLACK)
    price_text = font.render(f"Selling Price: {selling_price} gold", True, BLACK)
    
    screen.blit(fish_name, (100, 150))
    screen.blit(fish_rarity, (100, 200))
    screen.blit(quality_text, (100, 250))
    screen.blit(price_text, (100, 300))
    
    # Rarity color indicator
    rarity_colors = {
        "Common": GRAY,
        "Uncommon": GREEN, 
        "Rare": BLUE,
        "Epic": PURPLE,
        "Legendary": GOLD
    }
    color = rarity_colors.get(fish_info['rarity'], BLACK)
    pygame.draw.rect(screen, color, (500, 195, 30, 30))
    pygame.draw.rect(screen, BLACK, (500, 195, 30, 30), 2)
    
    instruction = font.render("Press SPACE to sell fish and return to menu", True, BLACK)
    screen.blit(instruction, (100, 400))

def handle_cheat_code(events, game_data):
    """Handle cheat code detection"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():
                game_data.cheat_buffer += event.unicode.lower()
                if len(game_data.cheat_buffer) > 10:  # Keep buffer small
                    game_data.cheat_buffer = game_data.cheat_buffer[-10:]
                
                if "lucknow" in game_data.cheat_buffer:
                    game_data.cheat_mode = not game_data.cheat_mode
                    game_data.cheat_buffer = ""
                    return True
    return False

def handle_shop_purchase(events, current_rod, gold):
    """Handle rod purchases in shop"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and current_rod != "Novice Rod":
                if gold >= ROD_UPGRADES["Novice Rod"]["price"]:
                    return "Novice Rod", gold - ROD_UPGRADES["Novice Rod"]["price"]
            elif event.key == pygame.K_2 and current_rod != "Master Rod":
                if gold >= ROD_UPGRADES["Master Rod"]["price"]:
                    return "Master Rod", gold - ROD_UPGRADES["Master Rod"]["price"]
    return current_rod, gold

def main():
    """Main game function"""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Fishing Mastery - 2D Timing Game")
    clock = pygame.time.Clock()
    
    # Game data
    game_data = GameData()
    
    # Fonts
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Buttons for main menu
    start_button = Button(WINDOW_WIDTH // 2 - 75, 200, 150, 40, "START FISHING", GREEN, DARK_GREEN, font)
    guide_button = Button(WINDOW_WIDTH // 2 - 75, 260, 150, 40, "GUIDE", BLUE, DARK_BLUE, font)
    shop_button = Button(WINDOW_WIDTH // 2 - 75, 320, 150, 40, "SHOP", ORANGE, BROWN, font)
    quit_button = Button(WINDOW_WIDTH // 2 - 75, 380, 150, 40, "QUIT", RED, (150, 0, 0), font)
    buttons = [start_button, guide_button, shop_button, quit_button]
    
    # Game stages
    stages = [
        CastTimingStage(),
        DepthControlStage(), 
        BiteReactionStage(),
        ReelingRhythmStage(),
        LineTensionStage()
    ]
    
    current_state = GameState.MAIN_MENU
    current_stage = 1
    running = True
    
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        events = pygame.event.get()
        
        # Handle quit event
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Handle cheat code (only in main menu)
        if current_state == GameState.MAIN_MENU:
            handle_cheat_code(events, game_data)
        
        # State handling
        if current_state == GameState.MAIN_MENU:
            for event in events:
                for button in buttons:
                    if button.handle_event(event):
                        if button.text == "START FISHING":
                            current_state = GameState.FISHING
                            current_stage = 1
                            # Reset stages
                            stages = [
                                CastTimingStage(),
                                DepthControlStage(),
                                BiteReactionStage(),
                                ReelingRhythmStage(),
                                LineTensionStage()
                            ]
                        elif button.text == "GUIDE":
                            current_state = GameState.GUIDE
                        elif button.text == "SHOP":
                            current_state = GameState.SHOP
                        elif button.text == "QUIT":
                            running = False
            
            # Handle escape key
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pass  # Already in main menu
        
        elif current_state == GameState.GUIDE:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = GameState.MAIN_MENU
        
        elif current_state == GameState.SHOP:
            new_rod, new_gold = handle_shop_purchase(events, game_data.current_rod, game_data.gold)
            game_data.current_rod = new_rod
            game_data.gold = new_gold
            
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = GameState.MAIN_MENU
        
        elif current_state == GameState.FISHING:
            # Update current stage
            if current_stage <= 5:
                stage_index = current_stage - 1
                stages[stage_index].update(dt)
                
                # Handle input for current stage
                if stages[stage_index].handle_input(events):
                    if current_stage < 5:
                        current_stage += 1
                    else:
                        # Calculate final results
                        stage_scores = [stage.score for stage in stages]
                        quality = calculate_quality(stage_scores)
                        quality_score = sum(stage_scores) / len(stage_scores)
                        
                        # Spawn fish
                        fish_info = spawn_fish(game_data.rod_luck[game_data.current_rod], game_data.cheat_mode)
                        selling_price = calculate_selling_price(fish_info['rarity'], quality_score)
                        
                        game_data.caught_fish = {
                            'info': fish_info,
                            'quality': quality,
                            'quality_score': quality_score,
                            'price': selling_price
                        }
                        
                        current_state = GameState.SELLING
            
            # Handle escape to return to menu
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = GameState.MAIN_MENU
        
        elif current_state == GameState.SELLING:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Sell fish and return to menu
                    game_data.gold += game_data.caught_fish['price']
                    game_data.caught_fish = None
                    current_state = GameState.MAIN_MENU
        
        # Drawing
        screen.fill(WHITE)
        
        if current_state == GameState.MAIN_MENU:
            draw_main_menu(screen, font, buttons, game_data.cheat_mode, game_data.gold)
        elif current_state == GameState.GUIDE:
            draw_guide_screen(screen, font)
        elif current_state == GameState.SHOP:
            draw_shop_screen(screen, font, game_data.current_rod, game_data.gold)
        elif current_state == GameState.FISHING:
            draw_fishing_interface(screen, font, current_stage, stages, game_data.gold, game_data.current_rod)
        elif current_state == GameState.SELLING:
            draw_selling_screen(screen, font, 
                              game_data.caught_fish['info'],
                              game_data.caught_fish['quality'],
                              game_data.caught_fish['quality_score'],
                              game_data.caught_fish['price'])
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()