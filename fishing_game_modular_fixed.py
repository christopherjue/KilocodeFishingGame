"""
2D Pygame Fishing Timing Game - Complete Enhanced Implementation
Complete implementation with all critical fixes, spacebar controls, moving target system, and enhanced difficulty

Author: AI Assistant
Based on structured implementation plan with 5-stage fishing process,
rod upgrades, and rarity system
"""

import pygame
import random
import math
import time

# ============================================================================
# PHASE 1: PROJECT FOUNDATION - Constants and Game States
# ============================================================================

# Initialize Pygame
pygame.init()

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

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

class GameState:
    MAIN_MENU = "main_menu"
    GUIDE = "guide"
    SHOP = "shop"
    CASTING = "casting"
    FISHING = "fishing"
    SELLING = "selling"
    INVENTORY = "inventory"
    FISH_DISPLAY = "fish_display"
    FISH_INDEX = "fish_index"

# ============================================================================
# PHASE 1: PROJECT FOUNDATION - Game Data and Button Class
# ============================================================================

class GameData:
    def __init__(self):
        self.gold = 5000  # Starting gold (updated for new economy)
        self.current_rod = "Basic Rod"
        self.rod_luck = {"Basic Rod": 0, "Novice Rod": 20, "Master Rod": 45}
        self.cheat_mode = False
        self.price_cheat = False  # New cheat for increased prices
        self.caught_fish = None
        self.cheat_buffer = ""
        self.fullscreen = False  # Fullscreen mode flag
        self.background = None  # Background image path
        # Inventory system
        self.inventory = []  # List to store caught fish
        self.inventory_capacity = 20  # Maximum inventory capacity

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font, image_path=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.image_path = image_path
        self.image = None
        self.image_rect = None
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False

        # Load image if provided
        if image_path:
            try:
                self.image = pygame.image.load(image_path)
                # Scale image to fit button size while maintaining aspect ratio
                original_width, original_height = self.image.get_size()
                aspect_ratio = original_width / original_height

                # Calculate scaled dimensions to fit within button size
                if aspect_ratio > 1:  # Landscape orientation
                    scaled_width = width
                    scaled_height = int(width / aspect_ratio)
                else:  # Portrait orientation
                    scaled_height = height
                    scaled_width = int(height * aspect_ratio)

                # Scale the image
                self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
                self.image_rect = self.image.get_rect(center=self.rect.center)
            except:
                # If image loading fails, fall back to text
                self.image = None
                self.image_rect = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        # Draw button background only if no image
        if not self.image:
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
            # Fall back to text if no image
            text_surface = self.font.render(self.text, True, BLACK)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        else:
            # Draw image if available
            screen.blit(self.image, self.image_rect)
            # Draw hover effect border for image buttons
            if self.is_hovered:
                pygame.draw.rect(screen, BLACK, self.rect, 2)

# ============================================================================
# PHASE 6: Quality and Rarity Systems - Fish Database and Spawning
# ============================================================================

# Fish Database - FIXED: Separated fish names properly
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
                  "Aurora Salmon", "Poseidon's Pike"],
    "Mythic": ["Abyssal Leviathan", "Celestial Megalodon", "Void Kraken"]
}

# Rarity Chances - Enhanced to include accessible mythic fish
RARITY_CHANCES_NORMAL = {"Common": 0.60, "Uncommon": 0.20, "Rare": 0.12, "Epic": 0.05, "Legendary": 0.025, "Mythic": 0.005}
RARITY_CHANCES_CHEAT = {"Legendary": 0.50, "Epic": 0.25, "Uncommon": 0.15, "Common": 0.05, "Rare": 0.04, "Mythic": 0.01}

# Base Prices - SIGNIFICANTLY INCREASED
BASE_PRICES = {"Common": 100, "Uncommon": 500, "Rare": 2000, "Epic": 10000, "Legendary": 50000, "Mythic": 500000}

def calculate_quality(stage_scores):
    """Calculate fish quality based on stage scores"""
    quality = sum(stage_scores) / len(stage_scores)
    
    if quality >= 95:
        return "Perfect"
    elif quality >= 80:
        return "Great"
    elif quality >= 60:
        return "Good"
    elif quality >= 40:
        return "Fair"
    else:
        return "Poor"

def spawn_fish(rod_luck, cheat_mode):
    """Spawn a fish based on rarity probabilities"""
    base_chances = RARITY_CHANCES_CHEAT if cheat_mode else RARITY_CHANCES_NORMAL
    
    # Adjust probabilities based on rod luck (excluding Mythic which is fixed at 0.5%)
    luck_bonus = rod_luck / 1000
    adjusted_chances = {}
    
    for rarity, chance in base_chances.items():
        if rarity == "Mythic":
            adjusted_chances[rarity] = max(0.002, chance + luck_bonus * 0.5)  # Enhanced mythic chances
        elif rarity in ["Rare", "Epic", "Legendary"]:
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
    
    # Select specific fish from rarity - ADDED BOUNDS CHECKING
    if selected_rarity in FISH_DATABASE and FISH_DATABASE[selected_rarity]:
        fish_name = random.choice(FISH_DATABASE[selected_rarity])
    else:
        fish_name = "Common Fish"  # Fallback
    
    return {"name": fish_name, "rarity": selected_rarity}

def get_all_fish_list():
    """Get a list of all fish in the database"""
    all_fish = []
    for rarity in FISH_DATABASE:
        for fish_name in FISH_DATABASE[rarity]:
            all_fish.append({
                'name': fish_name,
                'rarity': rarity
            })
    return all_fish

def get_missing_fish_counts(inventory):
    """Count missing fish by rarity class"""
    caught_fish_names = {fish['info']['name'] for fish in inventory}
    missing_counts = {}

    for rarity in FISH_DATABASE:
        total_in_rarity = len(FISH_DATABASE[rarity])
        caught_in_rarity = sum(1 for fish in inventory if fish['info']['rarity'] == rarity and fish['info']['name'] in FISH_DATABASE[rarity])
        missing_counts[rarity] = total_in_rarity - caught_in_rarity

    return missing_counts


def calculate_selling_price(fish_rarity, quality_percentage, game_data=None):
    """Calculate selling price based on fish rarity and quality"""
    if fish_rarity not in BASE_PRICES:
        fish_rarity = "Common"  # Fallback for unknown rarities

    base_price = BASE_PRICES[fish_rarity]
    quality_multiplier = quality_percentage / 100

    # Apply 10x multiplier if price cheat is active
    if game_data and game_data.price_cheat:
        base_price *= 10

    return int(base_price * (quality_multiplier ** 1.5))

# ============================================================================
# PHASE 4: Shop System - Rod Upgrades
# ============================================================================

# Rod Upgrades - UPDATED PRICES FOR NEW ECONOMY
ROD_UPGRADES = {
    "Novice Rod": {"price": 5000, "luck": 20},
    "Master Rod": {"price": 50000, "luck": 45}
}

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

# ============================================================================
# PHASE 5: Core Fishing Mechanics - Enhanced All 5 Fishing Stages
# ============================================================================

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
        
        # ENHANCED DIFFICULTY: Tighter timing windows, faster indicators
        self.marker_speed = 300  # Increased from 250 to 300 px/s
        self.target_zone_size = 0.10  # Reduced from 0.15 to 0.10 (tighter timing)
        
    def update(self, dt):
        if not self.completed:
            self.marker_x += self.marker_direction * self.marker_speed * dt
            if self.marker_x >= self.bar_width or self.marker_x <= 0:
                self.marker_direction *= -1
            self.stage_time += dt
            
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.completed:
                    self.score = max(0, min(100, int((self.marker_x / self.bar_width) * 100)))
                    self.completed = True
                    return True
        return False
    
    def draw(self, screen, font):
        # Draw timing bar
        pygame.draw.rect(screen, GRAY, (self.bar_x, self.bar_y, self.bar_width, 20))
        
        # Draw smaller target zone for enhanced difficulty
        target_start = self.bar_width * (0.5 - self.target_zone_size/2)
        target_end = self.bar_width * (0.5 + self.target_zone_size/2)
        pygame.draw.rect(screen, GREEN, (self.bar_x + target_start, self.bar_y, target_end - target_start, 20))
        
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
        # ENHANCED DIFFICULTY: Smaller sweet spot, more sensitive
        self.ideal_zone_start = 235  # Tightened from 220-260 to 235-265
        self.ideal_zone_end = 265
        self.score = 0
        self.completed = False
        self.bar_height = 400
        self.bar_x = 150
        self.bar_y = 150
        self.marker_speed = 180  # Increased from 150
        
    def update(self, dt):
        if not self.completed:
            self.marker_y += self.marker_direction * self.marker_speed * dt
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
        
        # Draw smaller ideal zone for enhanced difficulty
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
        # ENHANCED DIFFICULTY: Faster bites, shorter reaction window
        self.bite_time = time.time() + random.uniform(1.0, 2.5)  # Reduced from 1.5-3.5 to 1.0-2.5
        self.bite_triggered = False
        self.reaction_start = 0
        self.score = 0
        self.completed = False
        self.show_waiting = True
        self.reaction_window = 0.6  # Reduced from 0.8 to 0.6
        
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
                        if reaction_time <= self.reaction_window:
                            self.score = max(0, 100 - (reaction_time * 100))  # More punishing
                        else:
                            self.score = max(0, 20 - (reaction_time - self.reaction_window) * 40)
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
        # ENHANCED DIFFICULTY: Longer sequence, less forgiveness
        self.total_presses = 8  # Increased from 7 to 8
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
    
    def update(self, dt):
        # ReelingRhythmStage doesn't need continuous updates - only input handling
        pass
    
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
        # Enhanced LineTensionStage with spacebar controls and moving target system
        self.bobber_y = 250  # Start bobber higher for natural falling motion
        self.safe_zone_start = 350  # Y position for safe zone
        self.safe_zone_end = 450
        self.in_safe_zone_time = 0
        self.total_time = 5.0  # 5 second stage
        self.score = 0
        self.completed = False
        self.elapsed_time = 0
        
        # FIXED SPACEBAR CONTROL SYSTEM
        self.space_held = False
        self.bobber_velocity = 0
        self.gravity = 200  # Natural downward pull (positive = down)
        self.lift_force = -300  # Upward force when holding space (negative = up)
        self.max_up_speed = -200  # Maximum upward speed (negative = up)
        self.max_down_speed = 300  # Maximum downward speed (positive = down)
        
        # SIMPLIFIED TARGET SQUARE SYSTEM - Vertical movement only for stability
        self.target_square_size = 80  # Keep same size as original for better visibility
        self.target_square_x = WINDOW_WIDTH // 2 - self.target_square_size // 2  # Center horizontally
        self.target_square_y = 300  # Start at middle height
        self.target_square_direction = 1  # Vertical movement only (1 = down, -1 = up)
        self.target_square_speed = 80  # Slower speed for better playability
        
        # Time tracking for target square
        self.time_in_target = 0
        self.time_out_target = 0
        
    def update(self, dt):
        if not self.completed:
            # FIXED SPACEBAR PHYSICS: HOLD SPACE TO GO UP, RELEASE TO GO DOWN
            if self.space_held:
                # Spacebar held = apply upward force (negative velocity)
                self.bobber_velocity += self.lift_force * dt
            else:
                # Spacebar released = apply gravity (positive velocity)
                self.bobber_velocity += self.gravity * dt

            # Limit velocity to reasonable bounds
            self.bobber_velocity = max(self.max_down_speed, min(self.max_up_speed, self.bobber_velocity))

            # Update bobber position (positive Y = down, negative Y = up)
            self.bobber_y += self.bobber_velocity * dt

            # Keep bobber within reasonable bounds
            self.bobber_y = max(150, min(550, self.bobber_y))
            
            # SIMPLIFIED TARGET SQUARE MOVEMENT - Vertical only for stability
            self.target_square_y += self.target_square_direction * self.target_square_speed * dt

            # Bounce off vertical boundaries (keep in water area)
            if self.target_square_y <= 150:  # Top boundary
                self.target_square_direction = 1  # Move down
                self.target_square_y = 150
            elif self.target_square_y >= 450:  # Bottom boundary
                self.target_square_direction = -1  # Move up
                self.target_square_y = 450
            
            # FIXED: Simplified bobber position calculation
            bobber_screen_x = WINDOW_WIDTH // 2
            bobber_screen_y = self.bobber_y  # Direct Y position
            
            # Check if bobber is inside target square with bounds checking
            target_left = max(0, self.target_square_x)
            target_right = min(WINDOW_WIDTH, self.target_square_x + self.target_square_size)
            target_top = max(0, self.target_square_y)
            target_bottom = min(WINDOW_HEIGHT, self.target_square_y + self.target_square_size)

            in_target = (target_left <= bobber_screen_x <= target_right and
                        target_top <= bobber_screen_y <= target_bottom)

            if in_target:
                self.time_in_target += dt
            else:
                self.time_out_target += dt

            self.elapsed_time += dt
            if self.elapsed_time >= self.total_time:
                # FIXED: Score based on time spent in target square (0-100%)
                target_ratio = self.time_in_target / self.total_time
                self.score = target_ratio * 100  # 100% based on time in target
                self.completed = True
    
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.completed:
                    self.space_held = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.space_held = False
        return False
        
    def finish_stage(self):
        if not self.completed:
            self.score = (self.in_safe_zone_time / self.total_time) * 100
            self.completed = True
    
    def draw(self, screen, font):
        instruction = font.render("Stage 5: LINE TENSION - Hold SPACE to lift bobber, release to let it fall!", True, BLACK)
        screen.blit(instruction, (50, 80))
        
        # Draw tension bar
        pygame.draw.rect(screen, GRAY, (50, 150, 20, 400))
        
        # Draw safe zone
        safe_y = 150 + (600 - self.safe_zone_end)
        pygame.draw.rect(screen, GREEN, (45, safe_y, 30, self.safe_zone_end - self.safe_zone_start))
        
        # Draw tension marker (bobber)
        bobber_x = 80  # Move further left as requested
        bobber_y = self.bobber_y
        
        # Visual feedback for speed and power level
        speed_intensity = abs(self.bobber_velocity) / self.max_up_speed
        if self.space_held:
            # Bright colors when holding spacebar
            if speed_intensity > 0.8:
                bobber_color = RED
            elif speed_intensity > 0.5:
                bobber_color = ORANGE
            elif speed_intensity > 0.2:
                bobber_color = YELLOW
            else:
                bobber_color = BLACK
        else:
            # Gray when not holding spacebar
            bobber_color = GRAY
            
        pygame.draw.circle(screen, bobber_color, (bobber_x, bobber_y), 15)
        # Add yellow outline for better visibility
        pygame.draw.circle(screen, YELLOW, (bobber_x, bobber_y), 16, 2)
        
        # Draw moving target square (SIMPLIFIED: vertical movement only)
        pygame.draw.rect(screen, DARK_GREEN, (self.target_square_x, self.target_square_y,
                                             self.target_square_size, self.target_square_size), 2)

        # Check if bobber is in target square
        in_target = (self.target_square_x <= bobber_x <= self.target_square_x + self.target_square_size and
                    self.target_square_y <= bobber_y <= self.target_square_y + self.target_square_size)

        if in_target:
            pygame.draw.circle(screen, GOLD, (bobber_x, bobber_y), 10)
            # Draw indicator when in target
            pygame.draw.circle(screen, GREEN, (bobber_x, bobber_y), 15, 2)
        
        # Draw time tracking info
        time_info = font.render(f"In Target: {self.time_in_target:.1f}s | Out: {self.time_out_target:.1f}s", True, BLACK)
        screen.blit(time_info, (300, 100))
        
        # Draw enhanced speed/power indicator
        power_level = int(speed_intensity * 100)
        speed_text = font.render(f"Power: {power_level}% | Speed: {abs(int(self.bobber_velocity))}", True, BLACK)
        screen.blit(speed_text, (300, 130))
        
        # Draw spacebar status
        if self.space_held:
            space_text = font.render("SPACE: HOLDING (Lifting!)", True, GREEN)
        else:
            space_text = font.render("SPACE: Released (Falling)", True, RED)
        screen.blit(space_text, (300, 160))
        
        # Draw time remaining
        remaining_time = max(0, self.total_time - self.elapsed_time)
        time_text = font.render(f"Time Remaining: {remaining_time:.1f}s", True, BLACK)
        screen.blit(time_text, (300, 500))
        
        if self.completed:
            score_text = font.render(f"Tension Score: {int(self.score)}", True, BLACK)
            screen.blit(score_text, (300, 530))

# ============================================================================
# PHASE 2,3,4,7,8: UI Screens Implementation
# ============================================================================

def draw_main_menu(screen, font, buttons, cheat_mode, price_cheat, gold, game_data):
    """Draw the main menu screen"""
    # Load and draw background if available, otherwise use light blue
    background = load_background(game_data.background)
    if background:
        screen.blit(background, (0, 0))
    else:
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

    # Display price cheat status
    if price_cheat:
        price_cheat_text = font.render("PRICE CHEAT ACTIVE (10x)", True, RED)
        screen.blit(price_cheat_text, (10, 70))
    else:
        # Display cheat code typing feedback
        if game_data.cheat_buffer:
            typing_text = font.render(f"Typing: {game_data.cheat_buffer}", True, BLACK)
            screen.blit(typing_text, (10, 70))

    # Display fullscreen status
    fullscreen_text = font.render("F11: TOGGLE FULLSCREEN", True, BLACK)
    screen.blit(fullscreen_text, (10, 100))


def handle_cheat_code(events, game_data):
    """Handle cheat code detection"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isdigit():
                game_data.cheat_buffer += event.unicode.lower()
                if len(game_data.cheat_buffer) > 20:  # Keep buffer small
                    game_data.cheat_buffer = game_data.cheat_buffer[-20:]

                if "lucknow" in game_data.cheat_buffer:
                    game_data.cheat_mode = not game_data.cheat_mode
                    game_data.cheat_buffer = ""
                    return True
                elif "cheatprices" in game_data.cheat_buffer:
                    game_data.price_cheat = not game_data.price_cheat
                    game_data.cheat_buffer = ""
                    return True
                elif "background1" in game_data.cheat_buffer:
                    game_data.background = "assets/Background/Stormy.jpg"
                    game_data.cheat_buffer = ""
                    return True
                elif "background2" in game_data.cheat_buffer:
                    game_data.background = "assets/Background/Docs.jpg"
                    game_data.cheat_buffer = ""
                    return True
            elif event.key == pygame.K_DELETE:
                # Clear the cheat buffer when DELETE key is pressed
                game_data.cheat_buffer = ""
                return True
    return False

def draw_guide_screen(screen, font, game_data):
    """Draw the guide screen explaining fishing stages"""
    # Load and draw background if available, otherwise use light blue
    background = load_background(game_data.background)
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(LIGHT_BLUE)

    title = font.render("FISHING GUIDE", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
    screen.blit(title, title_rect)
    
    guide_texts = [
        "Stage 1 - CAST TIMING: Press SPACE when the moving marker is in the green zone",
        "Stage 2 - DEPTH CONTROL: Press SPACE when the marker is in the ideal depth range", 
        "Stage 3 - BITE REACTION: Wait for the fish to bite, then press SPACE quickly",
        "Stage 4 - REELING RHYTHM: Follow the arrow sequence using arrow keys",
        "Stage 5 - LINE TENSION: Hold SPACE to lift bobber, release to let it fall",
        "",
        "ENHANCED FEATURES:",
        "• Stage 5 includes a moving target square - stay in it for better quality!",
        "• Spacebar controls with acceleration - hold longer for more power!",
        "• Quality scoring: (Stage Scores × 0.7) + (Target Square Time × 0.3)",
        "• Enhanced difficulty across all stages for more challenging gameplay",
        "• Quality tiers: Perfect (95+) > Great (80+) > Good (60+) > Fair (40+) > Poor (<40)",
        "",
        "FISH QUALITY affects selling price based on performance",
        "Upgrade your rod for better chances at rare fish!",
        "Type 'lucknow' in the main menu for enhanced fish rarity!",
        "SPECIAL: Mythic fish (Abyssal Leviathan, Celestial Megalodon, Void Kraken) have enhanced chances!"
    ]
    
    y_offset = 120
    for text in guide_texts:
        if text:
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (50, y_offset))
        y_offset += 30
    
    back_text = font.render("Press ESC to return to menu", True, BLACK)
    screen.blit(back_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 50))

def draw_shop_screen(screen, font, current_rod, gold, game_data):
    """Draw the shop screen for rod upgrades"""
    # Load and draw background if available, otherwise use light blue
    background = load_background(game_data.background)
    if background:
        screen.blit(background, (0, 0))
    else:
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
    
    # Purchase instructions
    purchase_text = font.render("Press 1 for Novice Rod, 2 for Master Rod", True, BLACK)
    screen.blit(purchase_text, (50, y_offset + 20))
    
    back_text = font.render("Press ESC to return to menu", True, BLACK)
    screen.blit(back_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 50))

def draw_fishing_interface(screen, font, small_font, current_stage, stages, gold, current_rod):
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
        "Legendary": GOLD,
        "Mythic": (255, 0, 255)  # Bright magenta for mythic
    }
    color = rarity_colors.get(fish_info['rarity'], BLACK)
    pygame.draw.rect(screen, color, (500, 195, 30, 30))
    pygame.draw.rect(screen, BLACK, (500, 195, 30, 30), 2)

    # Load and display fish texture
    fish_texture = load_fish_texture(fish_info['name'])
    if fish_texture:
        # Display fish texture on the right side
        screen.blit(fish_texture, (450, 100))

    instruction = font.render("Press SPACE to sell fish and return to menu", True, BLACK)
    screen.blit(instruction, (100, 400))

def draw_inventory_screen(screen, font, inventory, gold, game_data):
    """Draw the inventory screen showing all caught fish"""
    # Load and draw background if available, otherwise use light blue
    background = load_background(game_data.background)
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(LIGHT_BLUE)

    # Title
    title = font.render("INVENTORY", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
    screen.blit(title, title_rect)

    # Gold display
    gold_text = font.render(f"Gold: {gold}", True, BLACK)
    screen.blit(gold_text, (10, 10))

    # Inventory capacity display
    capacity_text = font.render(f"Inventory: {len(inventory)}/{20}", True, BLACK)
    screen.blit(capacity_text, (WINDOW_WIDTH - 150, 10))

    # Inventory list header
    header_font = pygame.font.Font(None, 30)
    name_header = header_font.render("Name", True, BLACK)
    rarity_header = header_font.render("Rarity", True, BLACK)
    quality_header = header_font.render("Quality", True, BLACK)
    price_header = header_font.render("Price", True, BLACK)

    screen.blit(name_header, (50, 100))
    screen.blit(rarity_header, (250, 100))
    screen.blit(quality_header, (400, 100))
    screen.blit(price_header, (550, 100))

    # Draw inventory items
    y_offset = 140
    for i, fish in enumerate(inventory):
        # Fish name
        name_text = font.render(fish['info']['name'], True, BLACK)
        screen.blit(name_text, (50, y_offset))

        # Fish rarity
        rarity_text = font.render(fish['info']['rarity'], True, BLACK)
        screen.blit(rarity_text, (250, y_offset))

        # Fish quality
        quality_text = font.render(f"{fish['quality']} ({int(fish['quality_score'])}%)", True, BLACK)
        screen.blit(quality_text, (400, y_offset))

        # Fish price
        price_text = font.render(f"{fish['price']} gold", True, BLACK)
        screen.blit(price_text, (550, y_offset))

def draw_fish_index_screen(screen, font, inventory, game_data):
    """Draw the fish index screen showing all fish with caught/uncaught status"""
    # Load and draw background if available, otherwise use light blue
    background = load_background(game_data.background)
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(LIGHT_BLUE)

    # Title
    title = font.render("FISH INDEX", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
    screen.blit(title, title_rect)

    # Get missing fish counts
    missing_counts = get_missing_fish_counts(inventory)

    # Display missing fish counts in top left
    missing_texts = []
    for rarity in ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]:
        if missing_counts[rarity] > 0:
            missing_texts.append(f"Missing {missing_counts[rarity]} {rarity}")

    y_offset = 20
    for text in missing_texts:
        missing_text = font.render(text, True, BLACK)
        screen.blit(missing_text, (20, y_offset))
        y_offset += 30

    # Get all fish and display them in a grid
    all_fish = get_all_fish_list()
    caught_fish_names = {fish['info']['name'] for fish in inventory}

    # Display fish in a grid layout
    fish_per_row = 4
    fish_size = 100
    spacing = 20
    start_x = 50
    start_y = 150

    for i, fish in enumerate(all_fish):
        row = i // fish_per_row
        col = i % fish_per_row

        x = start_x + col * (fish_size + spacing)
        y = start_y + row * (fish_size + spacing + 40)  # Extra space for text

        # Draw fish slot
        pygame.draw.rect(screen, WHITE, (x, y, fish_size, fish_size), 2)

        # Check if fish is caught
        if fish['name'] in caught_fish_names:
            # Load and display fish texture
            fish_texture = load_fish_texture(fish['name'])
            if fish_texture:
                # Scale down the texture to fit
                scaled_texture = pygame.transform.scale(fish_texture, (fish_size - 10, fish_size - 10))
                screen.blit(scaled_texture, (x + 5, y + 5))
            else:
                # Display fish name if texture not found
                name_text = font.render(fish['name'], True, BLACK)
                screen.blit(name_text, (x + 10, y + 40))
        else:
            # Display question mark for uncaught fish
            question_text = font.render("?", True, BLACK)
            question_rect = question_text.get_rect(center=(x + fish_size // 2, y + fish_size // 2))
            screen.blit(question_text, question_rect)

        # Display fish name below
        name_text = font.render(fish['name'], True, BLACK)
        name_rect = name_text.get_rect(center=(x + fish_size // 2, y + fish_size + 20))
        screen.blit(name_text, name_rect)

        # Display rarity color indicator
        rarity_colors = {
            "Common": GRAY,
            "Uncommon": GREEN,
            "Rare": BLUE,
            "Epic": PURPLE,
            "Legendary": GOLD,
            "Mythic": (255, 0, 255)  # Bright magenta for mythic
        }
        color = rarity_colors.get(fish['rarity'], BLACK)
        pygame.draw.rect(screen, color, (x + fish_size - 25, y + fish_size - 25, 20, 20))
        pygame.draw.rect(screen, BLACK, (x + fish_size - 25, y + fish_size - 25, 20, 20), 1)

    # Back to menu instruction
    back_text = font.render("Press ESC to return to menu", True, BLACK)
    screen.blit(back_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 50))



# ============================================================================
# PHASE 8: Casting System Implementation
# ============================================================================

def draw_casting_screen(screen, font, game_data):
    """Draw the casting screen with instructions"""
    # Load and draw background if available, otherwise use light blue
    background = load_background(game_data.background)
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(LIGHT_BLUE)

    # Title
    title = font.render("CAST YOUR ROD", True, DARK_BLUE)
    title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
    screen.blit(title, title_rect)

    # Instructions
    instruction = font.render("Click anywhere to cast your rod!", True, BLACK)
    instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 250))
    screen.blit(instruction, instruction_rect)

    # Visual representation of fisher casting
    pygame.draw.circle(screen, GREEN, (WINDOW_WIDTH // 2, 150), 20)
    player_text = font.render("FISHER", True, BLACK)
    player_rect = player_text.get_rect(center=(WINDOW_WIDTH // 2, 190))
    screen.blit(player_text, player_rect)

    # Draw water area
    pygame.draw.rect(screen, BLUE, (0, 220, WINDOW_WIDTH, WINDOW_HEIGHT - 220))
    water_text = font.render("WATER", True, WHITE)
    screen.blit(water_text, (10, 230))

    # Draw fishing rod casting animation
    pygame.draw.line(screen, BROWN, (WINDOW_WIDTH // 2, 170), (WINDOW_WIDTH // 2 + 100, 300), 3)
    pygame.draw.circle(screen, RED, (WINDOW_WIDTH // 2 + 100, 300), 5)

    # Additional hint
    hint = font.render("Click to start fishing!", True, DARK_BLUE)
    hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, 400))
    screen.blit(hint, hint_rect)

    return True

def handle_casting_input(events):
    """Handle click detection for casting mechanism"""
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                return True
    return False

def handle_inventory_selling(events, inventory, gold):
    """Handle selling fish from inventory"""
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # Check if click is within inventory item area
            for i, fish in enumerate(inventory):
                item_y = 135 + (i * 40)  # Starting y position + offset per item
                if (50 <= mouse_x <= 600 and item_y <= mouse_y <= item_y + 30):
                    # Sell the fish
                    gold += fish['price']
                    inventory.pop(i)  # Remove the fish from inventory
                    return gold, True  # Return updated gold and success flag

    return gold, False

# ============================================================================
# PHASE 8: Background and Fish Texture System
# ============================================================================

def load_background(background_path):
    """Load background image or return None if not found"""
    if background_path:
        try:
            background = pygame.image.load(background_path)
            # Scale the background to fit the screen
            return pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            # Return None if background not found
            return None
    return None

def get_fish_texture_path(fish_name):
    """Convert fish name to texture filename"""
    # Remove spaces and special characters from fish name
    texture_name = fish_name.replace(" ", "").replace("'", "").replace(".", "")
    return f"assets/Fish Textures/{texture_name}.jpg"

def load_fish_texture(fish_name):
    """Load fish texture or return None if not found"""
    texture_path = get_fish_texture_path(fish_name)
    try:
        texture = pygame.image.load(texture_path)
        # Scale the texture to a reasonable size
        return pygame.transform.scale(texture, (200, 150))
    except:
        # Return None if texture not found
        return None

def draw_fish_display_screen(screen, font, fish_info, quality, quality_score, selling_price):
    """Draw the fish display screen showing caught fish (3-second notification)"""
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
        "Legendary": GOLD,
        "Mythic": (255, 0, 255)  # Bright magenta for mythic
    }
    color = rarity_colors.get(fish_info['rarity'], BLACK)
    pygame.draw.rect(screen, color, (500, 195, 30, 30))
    pygame.draw.rect(screen, BLACK, (500, 195, 30, 30), 2)

    # Load and display fish texture
    fish_texture = load_fish_texture(fish_info['name'])
    if fish_texture:
        # Display fish texture on the right side
        screen.blit(fish_texture, (450, 100))

    instruction = font.render("Fish added to inventory!", True, BLACK)
    screen.blit(instruction, (100, 400))

# ============================================================================
# PHASE 9: Main Game Loop
# ============================================================================

def main():
    """Main game function"""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Fishing Mastery - Enhanced 2D Timing Game")
    clock = pygame.time.Clock()
    
    # Game data
    game_data = GameData()
    
    # Fonts
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Buttons for main menu - using icons instead of text
    start_button = Button(WINDOW_WIDTH // 2 - 75, 200, 150, 40, "START FISHING", GREEN, DARK_GREEN, font, "assets/Main Menu Icons/STARTFISHING.png")
    guide_button = Button(WINDOW_WIDTH // 2 - 75, 260, 150, 40, "GUIDE", BLUE, DARK_BLUE, font, "assets/Main Menu Icons/GUIDE.png")
    shop_button = Button(WINDOW_WIDTH // 2 - 75, 320, 150, 40, "SHOP", ORANGE, BROWN, font, "assets/Main Menu Icons/SHOP.png")
    fish_index_button = Button(WINDOW_WIDTH // 2 - 75, 380, 150, 40, "FISH INDEX", (0, 150, 150), (0, 100, 100), font, "assets/Main Menu Icons/FISHINDEX.png")
    inventory_button = Button(WINDOW_WIDTH // 2 - 75, 440, 150, 40, "INVENTORY", PURPLE, (100, 0, 100), font, "assets/Main Menu Icons/INVENTORY.png")
    quit_button = Button(WINDOW_WIDTH // 2 - 75, 500, 150, 40, "QUIT", RED, (150, 0, 0), font, "assets/Main Menu Icons/QUIT.png")
    buttons = [start_button, guide_button, shop_button, fish_index_button, inventory_button, quit_button]
    
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
    fish_display_start_time = 0  # Timer for fish display state
    
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        events = pygame.event.get()
        
        # Handle quit event
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Handle fullscreen toggle (F11 key) - TEMPORARILY DISABLED
        # for event in events:
        #     if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
        #         game_data.fullscreen = not game_data.fullscreen
        #         if game_data.fullscreen:
        #             screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        #         else:
        #             screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Handle cheat code (only in main menu)
        if current_state == GameState.MAIN_MENU:
            handle_cheat_code(events, game_data)
        
        # State handling
        if current_state == GameState.MAIN_MENU:
            for event in events:
                for button in buttons:
                    if button.handle_event(event):
                        if button.text == "START FISHING":
                            current_state = GameState.CASTING
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
                        elif button.text == "FISH INDEX":
                            current_state = GameState.FISH_INDEX
                        elif button.text == "INVENTORY":
                            current_state = GameState.INVENTORY
                        elif button.text == "QUIT":
                            running = False

        elif current_state == GameState.CASTING:
            if handle_casting_input(events):
                current_state = GameState.FISHING

            # Handle escape to return to menu
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = GameState.MAIN_MENU
        
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

        elif current_state == GameState.FISH_INDEX:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = GameState.MAIN_MENU

        elif current_state == GameState.INVENTORY:
            # Handle inventory selling
            game_data.gold, sold_fish = handle_inventory_selling(events, game_data.inventory, game_data.gold)

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = GameState.MAIN_MENU
        
        elif current_state == GameState.FISHING:
            # Update current stage
            if current_stage <= 5:
                stage_index = current_stage - 1
                stages[stage_index].update(dt)

                # Handle input for current stage
                stages[stage_index].handle_input(events)

                # Check if stage completed
                if stages[stage_index].completed:
                    if current_stage < 5:
                        current_stage += 1
                    else:
                        # Calculate final results with enhanced quality system
                        stage_scores = [stage.score for stage in stages]
                        
                        # ENHANCED QUALITY SCORING: (stage_scores_avg * 0.7) + (target_square_time_ratio * 0.3)
                        stage_avg = sum(stage_scores) / len(stage_scores)
                        target_stage = stages[4]  # LineTensionStage
                        
                        # Calculate target square time ratio
                        total_time = target_stage.time_in_target + target_stage.time_out_target
                        if total_time > 0:
                            target_ratio = (target_stage.time_in_target / total_time) * 100
                        else:
                            target_ratio = 0
                        
                        # Final quality calculation
                        quality_score = (stage_avg * 0.7) + (target_ratio * 0.3)
                        quality = calculate_quality([quality_score])

                        # Spawn fish
                        fish_info = spawn_fish(game_data.rod_luck[game_data.current_rod], game_data.cheat_mode)
                        selling_price = calculate_selling_price(fish_info['rarity'], quality_score, game_data)

                        # Create fish data
                        caught_fish = {
                            'info': fish_info,
                            'quality': quality,
                            'quality_score': quality_score,
                            'price': selling_price
                        }

                        # Add to inventory if there's space
                        if len(game_data.inventory) < game_data.inventory_capacity:
                            game_data.inventory.append(caught_fish)
                            game_data.caught_fish = caught_fish
                            current_state = GameState.FISH_DISPLAY
                            fish_display_start_time = time.time()  # Start timer for fish display
                        else:
                            # Inventory full, go directly to selling
                            game_data.caught_fish = caught_fish
                            current_state = GameState.SELLING

            # Handle escape to return to menu
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = GameState.MAIN_MENU
        
        elif current_state == GameState.FISH_DISPLAY:
            # Check if 3 seconds have passed
            if time.time() - fish_display_start_time >= 3.0:
                current_state = GameState.MAIN_MENU
                game_data.caught_fish = None

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Skip the display and go to menu
                    current_state = GameState.MAIN_MENU
                    game_data.caught_fish = None

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
            draw_main_menu(screen, font, buttons, game_data.cheat_mode, game_data.price_cheat, game_data.gold, game_data)
        elif current_state == GameState.GUIDE:
            draw_guide_screen(screen, font, game_data)
        elif current_state == GameState.SHOP:
            draw_shop_screen(screen, font, game_data.current_rod, game_data.gold, game_data)
        elif current_state == GameState.CASTING:
            draw_casting_screen(screen, font, game_data)
        elif current_state == GameState.FISHING:
            draw_fishing_interface(screen, font, small_font, current_stage, stages, game_data.gold, game_data.current_rod)
        elif current_state == GameState.SELLING:
            draw_selling_screen(screen, font,
                              game_data.caught_fish['info'],
                              game_data.caught_fish['quality'],
                              game_data.caught_fish['quality_score'],
                              game_data.caught_fish['price'])

        elif current_state == GameState.FISH_DISPLAY:
            draw_fish_display_screen(screen, font,
                                  game_data.caught_fish['info'],
                                  game_data.caught_fish['quality'],
                                  game_data.caught_fish['quality_score'],
                                  game_data.caught_fish['price'])

        elif current_state == GameState.FISH_INDEX:
            draw_fish_index_screen(screen, font, game_data.inventory, game_data)

        elif current_state == GameState.INVENTORY:
            draw_inventory_screen(screen, font, game_data.inventory, game_data.gold, game_data)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()