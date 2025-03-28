import pygame

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

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
PLAYER_SPEED = 6
PLAYER_ACCELERATION = 0.5
PLAYER_FRICTION = 0.85
GRAVITY = 0.6
JUMP_FORCE = -12
JUMP_SPEED = 15
MAX_FALL_SPEED = 15
COYOTE_TIME = 6

# Platform settings
PLATFORM_HEIGHT = 40
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 200
MIN_PLATFORM_SPACING = 200
MAX_PLATFORM_SPACING = 350
SHRINK_RATE = 0.05
PLATFORM_COLORS = [BLUE, PURPLE, CYAN, GREEN, ORANGE, PINK]

# Jetpack settings
JETPACK_FORCE = -0.4
JETPACK_MAX_SPEED = -6
JETPACK_FUEL = 100
JETPACK_FUEL_CONSUMPTION = 0.5
JETPACK_HORIZONTAL_BOOST = 1.2

# Shop items
SHOP_ITEMS = [
    {"name": "Burger", "price": 5, "effect": "burger", "description": "Speed boost + double jump (1 min)"},
    {"name": "Jetpack", "price": 10, "effect": "jetpack", "description": "Fly and move smoothly (permanent)"},
    {"name": "Speed Boost", "price": 15, "effect": "speed_boost", "description": "2x speed (20 min)"},
    {"name": "Shield", "price": 20, "effect": "shield", "description": "Invincibility (30 sec)"},
    {"name": "Magnet", "price": 25, "effect": "magnet", "description": "Attract coins (1 min)"},
    {"name": "Rainbow Trail", "price": 30, "effect": "trail", "description": "Leave a rainbow trail (permanent)"}
]

# Powerup settings
SPEED_BOOST_MULTIPLIER = 2.0
SPEED_BOOST_DURATION = 1200
BURGER_SPEED_MULTIPLIER = 1.5
BURGER_DURATION = 3600
SHIELD_DURATION = 1800
MAGNET_DURATION = 3600
MAGNET_RANGE = 150

# RGB Color cycling
RGB_CYCLE_SPEED = 2
RGB_TEXT_ENABLED = True 