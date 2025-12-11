# UI Screens Implementation

## Phase 2: Main Menu System + Phase 3: Guide Screen + Phase 4: Shop System + Phase 7: Selling System + Phase 8: Visual Design

### 2.1 Main Menu Implementation
```python
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
```

### 3.1 Guide Content
```python
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
```

### 4.1 Shop Interface
```python
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
    
    # Purchase instructions
    purchase_text = font.render("Press 1 for Novice Rod, 2 for Master Rod", True, BLACK)
    screen.blit(purchase_text, (50, y_offset + 20))
    
    back_text = font.render("Press ESC to return to menu", True, BLACK)
    screen.blit(back_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 50))
```

### 8.1 Top-Down Layout + 7.1 Selling System
```python
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