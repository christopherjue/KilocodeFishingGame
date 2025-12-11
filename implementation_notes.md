# Implementation Notes and Guidelines

## Phase 9: Polish and Testing

### 9.1 Audio Implementation (Optional)
- Water splash sounds
- Bite detection sounds
- Button click sounds
- Background ambient music

### 9.2 Animation and Effects
- Smooth transitions between stages
- Particle effects for water splashes
- Visual feedback for successful actions
- Progress bar animations

### 9.3 Balance Testing
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

## Main Game Loop Template
```python
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
```

## Development Timeline Suggestion

1. **Week 1**: Phases 1-2 (Foundation + Menu)
   - Set up basic Pygame framework
   - Implement main menu with buttons and cheat codes

2. **Week 2**: Phase 3-4 (Guide + Shop)
   - Create guide screen with stage explanations
   - Implement shop system with rod upgrades

3. **Week 3**: Phase 5 (Core Fishing Mechanics)
   - Implement all 5 fishing stages
   - Add timing and scoring systems

4. **Week 4**: Phase 6-7 (Quality + Selling Systems)
   - Create fish database and spawning
   - Implement quality calculation and selling

5. **Week 5**: Phase 8 (Visual Design + UI)
   - Design top-down interface
   - Polish UI elements and visual feedback

6. **Week 6**: Phase 9 (Polish + Testing + Bug Fixes)
   - Add audio and animations
   - Balance game mechanics
   - Comprehensive testing

This plan provides a structured approach to implementing your fishing game with clear technical specifications for each component.