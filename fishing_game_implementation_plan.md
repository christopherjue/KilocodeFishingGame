# 2D Pygame Fishing Timing Game - Implementation Plan

## Project Overview
This document outlines the technical implementation plan for a 2D top-down fishing timing game built with Pygame. The game features a 5-stage fishing process, rarity-based fish system, rod upgrades, and a quality-based selling mechanism.

## Core Architecture

### Game Structure
- **Window Size**: 800x600 pixels
- **Frame Rate**: 60 FPS
- **Game States**: MAIN_MENU, GUIDE, SHOP, FISHING, SELLING
- **Key Libraries**: pygame, random, math, time

### Main Game Loop Structure
```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    current_state = MAIN_MENU
    
    while running:
        events = pygame.event.get()
        
        if current_state == MAIN_MENU:
            current_state = handle_main_menu(events)
        elif current_state == FISHING:
            current_state, fish_caught = handle_fishing_sequence(events)
            if fish_caught:
                current_state = SELLING
        
        screen.fill(BLUE)
        draw_current_state(screen, current_state)
        pygame.display.flip()
        clock.tick(60)
```

## Implementation Phases

### Phase 1: Project Foundation

#### 1.1 Basic Pygame Setup
- Initialize pygame with proper configuration
- Create main window and game loop
- Implement basic event handling system
- Set up color constants and basic drawing functions

#### 1.2 State Management System
```python
class GameState:
    MAIN_MENU = "main_menu"
    GUIDE = "guide"
    SHOP = "shop"
    FISHING = "fishing"
    SELLING = "selling"

class GameData:
    def __init__(self):
        self.gold = 0
        self.current_rod = "Basic Rod"
        self.rod_luck = {"Basic Rod": 0, "Novice Rod": 20, "Master Rod": 45}
        self.cheat_mode = False
        self.caught_fish = None
```

### Phase 2: Main Menu System

#### 2.1 Main Menu Implementation
- Create background with water/land theme
- Design menu buttons (Start, Guide, Shop, Quit)
- Implement button hover and click detection
- Add typing detection for "lucknow" cheat code

#### 2.2 Cheat Code System
```python
def handle_cheat_code(events):
    cheat_buffer = ""
    for event in events:
        if event.type == pygame.KEYDOWN:
            cheat_buffer += event.unicode.lower()
            if "lucknow" in cheat_buffer:
                game_data.cheat_mode = not game_data.cheat_mode
                cheat_buffer = ""
```

### Phase 3: Guide Screen

#### 3.1 Guide Content
- Create text display for each fishing stage explanation
- Design stage instruction layout
- Add visual diagrams for each stage mechanics
- Implement escape key return to menu

### Phase 4: Shop System

#### 4.1 Shop Interface
```python
ROD_UPGRADES = {
    "Novice Rod": {"price": 300, "luck": 20},
    "Master Rod": {"price": 1000, "luck": 45}
}

def draw_shop_screen(screen):
    # Display available rods and prices
    # Show current gold amount
    # Handle purchase logic
```

#### 4.2 Rod System Implementation
- Rod selection affects fish rarity probabilities
- Implement rod luck bonuses
- Add rod visualization in UI

### Phase 5: Core Fishing Mechanics

#### 5.1 Stage 1 - Cast Timing
```python
class CastTimingStage:
    def __init__(self):
        self.marker_x = 0
        self.marker_direction = 1
        self.bar_width = 600
        self.score = 0
        
    def update(self, dt):
        self.marker_x += self.marker_direction * 200 * dt
        if self.marker_x >= self.bar_width or self.marker_x <= 0:
            self.marker_direction *= -1
            
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.score = int((self.marker_x / self.bar_width) * 100)
                return True
        return False
```

#### 5.2 Stage 2 - Depth Control
```python
class DepthControlStage:
    def __init__(self):
        self.marker_y = 0
        self.ideal_zone_start = 200
        self.ideal_zone_end = 300
        self.score = 0
        
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                zone_center = (self.ideal_zone_start + self.ideal_zone_end) / 2
                distance = abs(self.marker_y - zone_center)
                max_distance = 300  # Assuming 600px height
                self.score = max(0, 100 - (distance / max_distance) * 100)
                return True
        return False
```

#### 5.3 Stage 3 - Bite Reaction
```python
class BiteReactionStage:
    def __init__(self):
        self.bite_time = time.time() + random.uniform(1, 4)
        self.bite_triggered = False
        self.reaction_start = 0
        self.score = 0
        
    def update(self):
        if not self.bite_triggered and time.time() >= self.bite_time:
            self.bite_triggered = True
            self.reaction_start = time.time()
            
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.bite_triggered:
                    reaction_time = time.time() - self.reaction_start
                    if reaction_time <= 1.0:  # 1 second window
                        self.score = 100 - (reaction_time * 50)
                    return True
                else:
                    self.score = 0  # Early press
                    return True
        return False
```

#### 5.4 Stage 4 - Reeling Rhythm
```python
class ReelingRhythmStage:
    def __init__(self):
        self.arrow_sequence = []
        self.current_index = 0
        self.correct_presses = 0
        self.total_presses = 5
        
    def generate_sequence(self):
        directions = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
        self.arrow_sequence = [random.choice(directions) for _ in range(self.total_presses)]
        
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    if event.key == self.arrow_sequence[self.current_index]:
                        self.correct_presses += 1
                    self.current_index += 1
                    if self.current_index >= len(self.arrow_sequence):
                        self.score = (self.correct_presses / self.total_presses) * 100
                        return True
        return False
```

#### 5.5 Stage 5 - Line Tension Control
```python
class LineTensionStage:
    def __init__(self):
        self.tension_position = 300  # Start in middle of 600px bar
        self.safe_zone_start = 250
        self.safe_zone_end = 350
        self.in_safe_zone_time = 0
        self.total_time = 5.0  # 5 second stage
        
    def update(self, dt):
        # Erratic movement simulation
        movement = random.uniform(-100, 100) * dt
        self.tension_position += movement
        self.tension_position = max(0, min(600, self.tension_position))
        
        # Track safe zone time
        if self.safe_zone_start <= self.tension_position <= self.safe_zone_end:
            self.in_safe_zone_time += dt
            
    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.tension_position -= 50  # Nudge up
        return False
        
    def finish_stage(self):
        self.score = (self.in_safe_zone_time / self.total_time) * 100
```

### Phase 6: Quality and Rarity Systems

#### 6.1 Quality Calculation
```python
def calculate_quality(stage_scores):
    # stage_scores = [stage1_score, stage2_score, stage3_score, stage4_score, stage5_score]
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
```

#### 6.2 Fish Database and Spawning
```python
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

RARITY_CHANCES_NORMAL = {"Common": 0.65, "Uncommon": 0.20, "Rare": 0.10, "Epic": 0.10, "Legendary": 0.05}
RARITY_CHANCES_CHEAT = {"Legendary": 0.65, "Epic": 0.20, "Uncommon": 0.10, "Common": 0.05, "Rare": 0.00}

def spawn_fish(rod_luck, cheat_mode):
    # Adjust probabilities based on rod luck
    base_chances = RARITY_CHANCES_CHEAT if cheat_mode else RARITY_CHANCES_NORMAL
    
    # Simple luck adjustment (can be more sophisticated)
    luck_bonus = rod_luck / 1000  # Convert to percentage
    adjusted_chances = {}
    
    for rarity, chance in base_chances.items():
        if rarity in ["Rare", "Epic", "Legendary"]:
            adjusted_chances[rarity] = chance + luck_bonus
        else:
            adjusted_chances[rarity] = chance - luck_bonus
    
    # Normalize probabilities
    total = sum(adjusted_chances.values())
    for rarity in adjusted_chances:
        adjusted_chances[rarity] /= total
    
    # Select rarity
    random_value = random.random()
    cumulative = 0
    for rarity, chance in adjusted_chances.items():
        cumulative += chance
        if random_value <= cumulative:
            selected_rarity = rarity
            break
    
    # Select specific fish from rarity
    fish_name = random.choice(FISH_DATABASE[selected_rarity])
    return {"name": fish_name, "rarity": selected_rarity}
```

### Phase 7: Selling System

#### 7.1 Price Calculation
```python
BASE_PRICES = {"Common": 10, "Uncommon": 25, "Rare": 50, "Epic": 100, "Legendary": 250}

def calculate_selling_price(fish_rarity, quality_percentage, use_exponential=False):
    base_price = BASE_PRICES[fish_rarity]
    quality_multiplier = quality_percentage / 100
    
    if use_exponential:
        return int(base_price * (quality_multiplier ** 1.5))
    else:
        return int(base_price * quality_multiplier)
```

### Phase 8: Visual Design and UI

#### 8.1 Top-Down Layout
```python
def draw_fishing_interface(screen, stage_info):
    # Player character at top
    pygame.draw.circle(screen, GREEN, (400, 50), 20)
    
    # Water area
    pygame.draw.rect(screen, BLUE, (0, 100, 800, 500))
    
    # Hook line
    hook_x, hook_y = get_hook_position()
    pygame.draw.line(screen, BLACK, (400, 70), (hook_x, hook_y), 2)
    pygame.draw.circle(screen, RED, (hook_x, hook_y), 5)
    
    # Stage-specific interface
    if current_stage == 1:
        draw_cast_timing_bar(screen)
    # ... other stages
```

#### 8.2 UI Elements
- Gold display in top-left corner
- Current rod display in top-right corner
- Stage progress indicator
- Fish quality and rarity display after catch
- Score displays for each stage

### Phase 9: Polish and Testing

#### 9.1 Audio Implementation (Optional)
- Water splash sounds
- Bite detection sounds
- Button click sounds
- Background ambient music

#### 9.2 Animation and Effects
- Smooth transitions between stages
- Particle effects for water splashes
- Visual feedback for successful actions
- Progress bar animations

#### 9.3 Balance Testing
- Adjust difficulty of timing sequences
- Fine-tune probability distributions
- Test rod upgrade progression
- Validate selling price calculations

## Key Implementation Notes

1. **Event Handling**: Use pygame.event.get() for input detection
2. **Timing**: Use pygame.time.get_ticks() for precise timing
3. **Drawing**: Optimize drawing operations for 60 FPS performance
4. **State Transitions**: Ensure smooth transitions between game states
5. **Error Handling**: Add input validation and edge case handling
6. **Code Organization**: Use classes for each major component
7. **Constants**: Define all game constants at the top of the file
8. **Comments**: Add comprehensive comments for complex logic

## Development Timeline Suggestion

1. **Week 1**: Phases 1-2 (Foundation + Menu)
2. **Week 2**: Phase 3-4 (Guide + Shop)
3. **Week 3**: Phase 5 (Core Fishing Mechanics)
4. **Week 4**: Phase 6-7 (Quality + Selling Systems)
5. **Week 5**: Phase 8 (Visual Design + UI)
6. **Week 6**: Phase 9 (Polish + Testing + Bug Fixes)

This plan provides a structured approach to implementing your fishing game with clear technical specifications for each component.