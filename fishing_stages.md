# Fishing Stages Implementation

## Phase 5: Core Fishing Mechanics

### 5.1 Stage 1 - Cast Timing
```python
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
```

### 5.2 Stage 2 - Depth Control
```python
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
```

### 5.3 Stage 3 - Bite Reaction
```python
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
```

### 5.4 Stage 4 - Reeling Rhythm
```python
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
```

### 5.5 Stage 5 - Line Tension Control
```python
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