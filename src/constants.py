# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)

# Player settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
PLAYER_SPEED = 3
JUMP_FORCE = -15
GRAVITY = 0.5

# Platform settings
SHRINK_RATE = 0.05
PLATFORM_COLORS = [BLUE, PURPLE, CYAN, GREEN, ORANGE, PINK]

# Shop items
SHOP_ITEMS = [
    {"name": "Burger", "price": 5, "effect": "health"},
    {"name": "Jetpack", "price": 20, "effect": "double_jump"},
    {"name": "Car", "price": 30, "effect": "speed_boost"},
    {"name": "Shield", "price": 15, "effect": "invincibility"}
] 