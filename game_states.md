# Game States and Constants

## Phase 1: Project Foundation

### 1.1 Basic Pygame Setup
- Initialize pygame with proper configuration
- Create main window and game loop
- Implement basic event handling system
- Set up color constants and basic drawing functions

### 1.2 State Management System
```python
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
    FISHING = "fishing"
    SELLING = "selling"

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