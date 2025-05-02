import pygame
from .player import Player
from .platform import Platform
from .coin import Coin
from .shop import Shop
from .treasure import TreasureChest, SuperChest
from .constants import *
import random
import math
import os
import time

# Global variables
music_initialized = False
music_loaded = False

class Game:
    def __init__(self, screen):
        global music_initialized
        
        self.screen = screen
        self.coins = []
        self.treasure_chests = []  # Initialize treasure_chests list
        self.super_chests = []  # Initialize super_chests list
        self.score = 0  # Initialize score
        self.reset_game()
        self.shop = Shop(self)
        self.show_shop = False
        self.show_skins = False  # Add skins menu flag
        self.game_over = False
        self.camera_offset = [0, 0]
        self.camera_target = [0, 0]
        self.background_color = 0
        # Position shop and home buttons right next to each other
        self.shop_button_rect = pygame.Rect(WINDOW_WIDTH - 120, 10, 100, 40)
        self.home_button_rect = pygame.Rect(WINDOW_WIDTH - 180, 10, 50, 40)  # Directly to the left of shop button
        self.skins_button_rect = pygame.Rect(10, 110, 100, 40)  # Add skins button below mute
        self.exit_button_rect = pygame.Rect(WINDOW_WIDTH - 120, WINDOW_HEIGHT - 50, 100, 40)
        self.music_button_rect = pygame.Rect(10, 60, 120, 40)
        self.music_muted = False
        self.show_purchase_message = False
        self.purchase_message = ""
        self.message_timer = 0
        self.active_items = []
        self.last_platform_x = WINDOW_WIDTH * 3
        self.fall_timer = 0
        self.max_fall_time = 300
        self.show_respawn = False
        self.music_restart_timer = 0
        self.teleport_available = False
        self.teleport_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 10, 200, 50)
        self.return_to_home = False
        
        # Save game confirmation dialog
        self.show_save_dialog = False
        self.save_dialog_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 125, 400, 250)
        self.save_yes_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50, 120, 50)
        self.save_no_rect = pygame.Rect(WINDOW_WIDTH // 2 + 30, WINDOW_HEIGHT // 2 + 50, 120, 50)
        
        # Play time tracking
        self.start_time = time.time()
        self.play_time = 0  # In seconds
        
        # Skins menu scrolling properties
        self.skins_scroll_y = 0  # Current scroll position
        self.skins_max_scroll = 0  # Will be calculated based on number of skins
        self.skins_scroll_speed = 20  # Scroll speed
        self.skins_visible_items = 5  # Number of items visible at once
        
        # Available skins with prices
        self.skins = [
            {"name": "Default", "price": 0, "color": (0, 255, 0), "unlocked": True, "pattern": "rgb", "anim_speed": 1.0},
            
            # Basic solid colors (1-10)
            {"name": "Azure", "price": 20, "color": (0, 127, 255), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Crimson", "price": 20, "color": (220, 20, 60), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Emerald", "price": 20, "color": (0, 201, 87), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Amethyst", "price": 20, "color": (153, 102, 204), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Amber", "price": 20, "color": (255, 191, 0), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Coral", "price": 20, "color": (255, 127, 80), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Teal", "price": 20, "color": (0, 128, 128), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Lavender", "price": 20, "color": (230, 230, 250), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Maroon", "price": 20, "color": (128, 0, 0), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            {"name": "Turquoise", "price": 20, "color": (64, 224, 208), "unlocked": False, "pattern": "solid", "anim_speed": 0},
            
            # Pulsing colors (11-20)
            {"name": "Pulse Red", "price": 40, "color": (255, 0, 0), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Blue", "price": 40, "color": (0, 0, 255), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Green", "price": 40, "color": (0, 128, 0), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Gold", "price": 40, "color": (255, 215, 0), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Silver", "price": 40, "color": (192, 192, 192), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Pink", "price": 40, "color": (255, 105, 180), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Cyan", "price": 40, "color": (0, 255, 255), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Orange", "price": 40, "color": (255, 165, 0), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Purple", "price": 40, "color": (128, 0, 128), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            {"name": "Pulse Lime", "price": 40, "color": (50, 205, 50), "unlocked": False, "pattern": "pulse", "anim_speed": 1.0},
            
            # Gradient patterns (21-30)
            {"name": "Sunset", "price": 60, "color": [(255, 0, 0), (255, 165, 0)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Ocean", "price": 60, "color": [(0, 0, 255), (0, 255, 255)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Forest", "price": 60, "color": [(0, 100, 0), (50, 205, 50)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Twilight", "price": 60, "color": [(75, 0, 130), (138, 43, 226)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Fire", "price": 60, "color": [(255, 0, 0), (255, 255, 0)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Ice", "price": 60, "color": [(0, 255, 255), (240, 248, 255)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Rose Gold", "price": 60, "color": [(255, 215, 0), (255, 192, 203)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Neon Nights", "price": 60, "color": [(255, 0, 255), (0, 0, 255)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Toxic", "price": 60, "color": [(0, 255, 0), (255, 255, 0)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            {"name": "Cotton Candy", "price": 60, "color": [(255, 192, 203), (135, 206, 235)], "unlocked": False, "pattern": "gradient", "anim_speed": 0.5},
            
            # Animated patterns (31-40)
            {"name": "Rainbow Wave", "price": 80, "color": None, "unlocked": False, "pattern": "rainbow_wave", "anim_speed": 1.5},
            {"name": "RGB Cycle", "price": 80, "color": None, "unlocked": False, "pattern": "rgb_cycle", "anim_speed": 1.0},
            {"name": "Matrix", "price": 80, "color": (0, 255, 0), "unlocked": False, "pattern": "matrix", "anim_speed": 1.0},
            {"name": "Glitch", "price": 80, "color": None, "unlocked": False, "pattern": "glitch", "anim_speed": 2.0},
            {"name": "Laser Show", "price": 80, "color": None, "unlocked": False, "pattern": "laser", "anim_speed": 1.5},
            {"name": "Digital Rain", "price": 80, "color": (0, 255, 255), "unlocked": False, "pattern": "digital_rain", "anim_speed": 1.0},
            {"name": "Plasma", "price": 80, "color": None, "unlocked": False, "pattern": "plasma", "anim_speed": 1.5},
            {"name": "Ripple", "price": 80, "color": (0, 191, 255), "unlocked": False, "pattern": "ripple", "anim_speed": 1.0},
            {"name": "Vortex", "price": 80, "color": None, "unlocked": False, "pattern": "vortex", "anim_speed": 1.2},
            {"name": "Scanline", "price": 80, "color": (255, 255, 255), "unlocked": False, "pattern": "scanline", "anim_speed": 1.0},
            
            # Particle effects (41-50)
            {"name": "Sparkle", "price": 100, "color": (220, 220, 220), "unlocked": False, "pattern": "sparkle", "anim_speed": 1.0},
            {"name": "Flames", "price": 100, "color": (255, 69, 0), "unlocked": False, "pattern": "flames", "anim_speed": 1.5},
            {"name": "Bubbles", "price": 100, "color": (30, 144, 255), "unlocked": False, "pattern": "bubbles", "anim_speed": 0.8},
            {"name": "Stardust", "price": 100, "color": (148, 0, 211), "unlocked": False, "pattern": "stardust", "anim_speed": 1.0},
            {"name": "Confetti", "price": 100, "color": None, "unlocked": False, "pattern": "confetti", "anim_speed": 1.2},
            {"name": "Fireflies", "price": 100, "color": (255, 255, 0), "unlocked": False, "pattern": "fireflies", "anim_speed": 0.7},
            {"name": "Smoke", "price": 100, "color": (105, 105, 105), "unlocked": False, "pattern": "smoke", "anim_speed": 0.5},
            {"name": "Snow", "price": 100, "color": (255, 250, 250), "unlocked": False, "pattern": "snow", "anim_speed": 0.6},
            {"name": "Electricity", "price": 100, "color": (255, 255, 0), "unlocked": False, "pattern": "electricity", "anim_speed": 2.0},
            {"name": "Pixels", "price": 100, "color": None, "unlocked": False, "pattern": "pixels", "anim_speed": 1.0},
            
            # Textured skins (51-60)
            {"name": "Metal", "price": 120, "color": (192, 192, 192), "unlocked": False, "pattern": "metal", "anim_speed": 0.3},
            {"name": "Wood", "price": 120, "color": (139, 69, 19), "unlocked": False, "pattern": "wood", "anim_speed": 0},
            {"name": "Glass", "price": 120, "color": (173, 216, 230), "unlocked": False, "pattern": "glass", "anim_speed": 0.5},
            {"name": "Stone", "price": 120, "color": (128, 128, 128), "unlocked": False, "pattern": "stone", "anim_speed": 0},
            {"name": "Lava", "price": 120, "color": (255, 69, 0), "unlocked": False, "pattern": "lava", "anim_speed": 0.8},
            {"name": "Ice Crystal", "price": 120, "color": (224, 255, 255), "unlocked": False, "pattern": "ice", "anim_speed": 0.4},
            {"name": "Diamond", "price": 120, "color": (185, 242, 255), "unlocked": False, "pattern": "diamond", "anim_speed": 0.7},
            {"name": "Rubber", "price": 120, "color": (30, 30, 30), "unlocked": False, "pattern": "rubber", "anim_speed": 0},
            {"name": "Leather", "price": 120, "color": (139, 69, 19), "unlocked": False, "pattern": "leather", "anim_speed": 0},
            {"name": "Tech", "price": 120, "color": (0, 0, 50), "unlocked": False, "pattern": "tech", "anim_speed": 1.0},
            
            # Themed skins (61-70)
            {"name": "Space", "price": 200, "color": (0, 0, 30), "unlocked": False, "pattern": "space", "anim_speed": 0.5},
            {"name": "Retro", "price": 200, "color": None, "unlocked": False, "pattern": "retro", "anim_speed": 0.8},
            {"name": "Neon", "price": 200, "color": (255, 0, 255), "unlocked": False, "pattern": "neon", "anim_speed": 1.2},
            {"name": "Cyberpunk", "price": 200, "color": None, "unlocked": False, "pattern": "cyberpunk", "anim_speed": 1.0},
            {"name": "Steampunk", "price": 200, "color": (184, 115, 51), "unlocked": False, "pattern": "steampunk", "anim_speed": 0.5},
            {"name": "Aquarium", "price": 200, "color": (0, 127, 255), "unlocked": False, "pattern": "aquarium", "anim_speed": 0.8},
            {"name": "Disco", "price": 200, "color": None, "unlocked": False, "pattern": "disco", "anim_speed": 1.5},
            {"name": "Zombie", "price": 200, "color": (69, 139, 0), "unlocked": False, "pattern": "zombie", "anim_speed": 0.7},
            {"name": "Ghost", "price": 200, "color": (220, 220, 255), "unlocked": False, "pattern": "ghost", "anim_speed": 0.5},
            {"name": "Robot", "price": 200, "color": (192, 192, 192), "unlocked": False, "pattern": "robot", "anim_speed": 0.8},
            
            # Premium skins (71-80)
            {"name": "Galaxy", "price": 300, "color": None, "unlocked": False, "pattern": "galaxy", "anim_speed": 0.8},
            {"name": "Void", "price": 300, "color": (0, 0, 0), "unlocked": False, "pattern": "void", "anim_speed": 1.0},
            {"name": "Hypnotic", "price": 300, "color": None, "unlocked": False, "pattern": "hypnotic", "anim_speed": 0.6},
            {"name": "Cosmic", "price": 300, "color": None, "unlocked": False, "pattern": "cosmic", "anim_speed": 1.0},
            {"name": "Hologram", "price": 300, "color": (0, 255, 255), "unlocked": False, "pattern": "hologram", "anim_speed": 1.2},
            {"name": "Nebula", "price": 300, "color": (138, 43, 226), "unlocked": False, "pattern": "nebula", "anim_speed": 0.5},
            {"name": "Fractal", "price": 300, "color": None, "unlocked": False, "pattern": "fractal", "anim_speed": 0.8},
            {"name": "Pixel Art", "price": 300, "color": None, "unlocked": False, "pattern": "pixel_art", "anim_speed": 0.5},
            {"name": "Quantum", "price": 300, "color": None, "unlocked": False, "pattern": "quantum", "anim_speed": 2.0},
            {"name": "Aurora", "price": 300, "color": None, "unlocked": False, "pattern": "aurora", "anim_speed": 0.7},
            
            # Elite skins (81-90)
            {"name": "Phoenix", "price": 500, "color": (255, 69, 0), "unlocked": False, "pattern": "phoenix", "anim_speed": 1.2},
            {"name": "Dragon", "price": 500, "color": (255, 0, 0), "unlocked": False, "pattern": "dragon", "anim_speed": 1.0},
            {"name": "Unicorn", "price": 500, "color": (255, 192, 203), "unlocked": False, "pattern": "unicorn", "anim_speed": 0.8},
            {"name": "Ninja", "price": 500, "color": (0, 0, 0), "unlocked": False, "pattern": "ninja", "anim_speed": 2.0},
            {"name": "Superhero", "price": 500, "color": (0, 0, 255), "unlocked": False, "pattern": "superhero", "anim_speed": 1.5},
            {"name": "Pirate", "price": 500, "color": (139, 69, 19), "unlocked": False, "pattern": "pirate", "anim_speed": 0.8},
            {"name": "Knight", "price": 500, "color": (192, 192, 192), "unlocked": False, "pattern": "knight", "anim_speed": 0.5},
            {"name": "Samurai", "price": 500, "color": (255, 0, 0), "unlocked": False, "pattern": "samurai", "anim_speed": 1.0},
            {"name": "Wizard", "price": 500, "color": (75, 0, 130), "unlocked": False, "pattern": "wizard", "anim_speed": 1.2},
            {"name": "Alien", "price": 500, "color": (0, 255, 0), "unlocked": False, "pattern": "alien", "anim_speed": 1.5},
            
            # Legendary skins (91-100)
            {"name": "Black Hole", "price": 1000, "color": (0, 0, 0), "unlocked": False, "pattern": "black_hole", "anim_speed": 1.0},
            {"name": "Supernova", "price": 1000, "color": None, "unlocked": False, "pattern": "supernova", "anim_speed": 2.0},
            {"name": "Time Warp", "price": 1000, "color": None, "unlocked": False, "pattern": "time_warp", "anim_speed": 1.5},
            {"name": "Singularity", "price": 1000, "color": (75, 0, 130), "unlocked": False, "pattern": "singularity", "anim_speed": 1.8},
            {"name": "Antimatter", "price": 1000, "color": None, "unlocked": False, "pattern": "antimatter", "anim_speed": 2.2},
            {"name": "Celestial", "price": 1000, "color": None, "unlocked": False, "pattern": "celestial", "anim_speed": 0.8},
            {"name": "Infinity", "price": 1000, "color": None, "unlocked": False, "pattern": "infinity", "anim_speed": 1.0},
            {"name": "Dimension", "price": 1000, "color": None, "unlocked": False, "pattern": "dimension", "anim_speed": 1.3},
            {"name": "Primordial", "price": 1000, "color": None, "unlocked": False, "pattern": "primordial", "anim_speed": 0.5},
            {"name": "Ultimate", "price": 1000, "color": None, "unlocked": False, "pattern": "ultimate", "anim_speed": 3.0}
        ]
        self.current_skin = 0  # Index of the current skin
        
        # Initialize background music
        self.initialize_music()
        
    def initialize_music(self):
        """Initialize music with better error handling"""
        global music_initialized, music_loaded
        
        # Skip if already initialized
        if music_initialized:
            return
        
        try:
            # Initialize mixer first
            pygame.mixer.quit()  # Reset mixer if it was active
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            
            # Set music path
            self.music_path = os.path.join(os.getcwd(), "music", "megalovania.mp3")
            
            print(f"\nDEBUG INFO:")
            print(f"Current directory: {os.getcwd()}")
            print(f"Looking for: {self.music_path}")
            
            # Ensure music directory exists
            music_dir = os.path.dirname(self.music_path)
            if not os.path.exists(music_dir):
                os.makedirs(music_dir, exist_ok=True)
                print(f"Created music directory: {music_dir}")
            
            print(f"Music directory exists: {os.path.exists(music_dir)}")
            print(f"Music file exists: {os.path.exists(self.music_path)}")
            
            # List directory contents
            try:
                if os.path.exists(music_dir):
                    print("Directory contents:")
                    for item in os.listdir(music_dir):
                        print(f"  - {item}")
            except Exception as e:
                print(f"Error listing directory: {str(e)}")
            
            # Load and play music if file exists
            music_initialized = True  # Mark as initialized even if loading fails
            
            if os.path.exists(self.music_path):
                try:
                    pygame.mixer.music.load(self.music_path)
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    pygame.mixer.music.set_volume(0.3)
                    music_loaded = True
                    print("Music loaded successfully!")
                except Exception as load_error:
                    print(f"ERROR loading music file: {str(load_error)}")
                    music_loaded = False
            else:
                print(f"WARNING: Music file not found at {self.music_path}")
                print("Game will continue without music")
                music_loaded = False
                
        except Exception as e:
            print(f"ERROR initializing music: {str(e)}")
            print("Game will continue without music")
            music_initialized = True  # Mark as initialized to prevent retries
            music_loaded = False
        
    def create_platform(self, x, y, width):
        platform = Platform(x, y, width, PLATFORM_HEIGHT, is_safe=True)
        self.platforms.append(platform)
        return platform
        
    def reset_game(self):
        # Store current score and powerups
        current_score = getattr(self, 'score', 0)
        current_powerups = self.player.powerups.copy() if hasattr(self, 'player') else {}
        
        # Reset player position
        self.player = Player(100, WINDOW_HEIGHT - 200, self)
        
        # Restore powerups and score
        self.player.powerups = current_powerups
        self.score = current_score
        
        # Reset platforms
        self.platforms = []
        self.create_platform(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH)  # Ground platform
        self.generate_new_platforms()
        
        # Reset chests
        self.treasure_chests = []
        self.super_chests = []
        
        # Reset camera
        self.camera_offset = [0, 0]
        self.camera_target = [0, 0]
        
        # Reset game state
        self.fall_timer = 0
        self.show_respawn = False
        self.game_over = False
        
        # Reset playtime timer
        self.start_time = time.time()
        
    def create_platforms(self):
        platforms = []
        
        # Create starting platform
        start_platform = Platform(50, WINDOW_HEIGHT - 150, 200, PLATFORM_HEIGHT, is_safe=True)
        platforms.append(start_platform)
        
        # Create initial platforms with tighter spacing
        last_x = start_platform.rect.right + 50  # Reduced gap after starting platform
        last_y = WINDOW_HEIGHT - 150
        
        for _ in range(20):
            width = random.randint(100, 150)  # Slightly smaller platforms
            x = last_x + random.randint(50, 100)  # Much tighter spacing
            
            # Keep height changes smaller for easier jumps
            max_height_change = int(JUMP_SPEED)
            min_y = int(max(100, last_y - max_height_change))
            max_y = int(min(WINDOW_HEIGHT - 100, last_y + max_height_change))
            y = random.randint(min_y, max_y)
            
            # 30% chance for safe zone (increased from 20%)
            is_safe = random.random() < 0.3
            
            platform = Platform(x, y, width, PLATFORM_HEIGHT, is_safe)
            platforms.append(platform)
            
            last_x = x + width
            last_y = y
            
            # Add coins and chests
            if random.random() < 0.7:
                coin_x = x + width // 2
                coin_y = y - 50
                self.coins.append(Coin(coin_x, coin_y))
                
            # Add chests - 15% chance for regular chest
            chest_roll = random.random()
            if chest_roll < 0.15:
                chest_x = x + width // 2
                chest_y = y - 40
                # 20% of chests will be super chests (3% of platforms)
                if random.random() < 0.2:
                    self.super_chests.append(SuperChest(chest_x, chest_y))
                else:
                    self.treasure_chests.append(TreasureChest(chest_x, chest_y))
            
        return platforms
        
    def create_coins(self):
        coins = []
        coin_positions = [
            # Left area coins
            (350, WINDOW_HEIGHT - 250),
            (550, WINDOW_HEIGHT - 350),
            (250, WINDOW_HEIGHT - 450),
            (650, WINDOW_HEIGHT - 500),
            # Middle area coins
            (850, WINDOW_HEIGHT - 300),
            (1050, WINDOW_HEIGHT - 400),
            (1250, WINDOW_HEIGHT - 250),
            # Right area coins
            (1450, WINDOW_HEIGHT - 450),
            (1650, WINDOW_HEIGHT - 350),
            (1850, WINDOW_HEIGHT - 500),
            # Upper area coins
            (450, WINDOW_HEIGHT - 600),
            (950, WINDOW_HEIGHT - 550),
            (1450, WINDOW_HEIGHT - 650),
        ]
        
        for x, y in coin_positions:
            coins.append(Coin(x, y))
            
        return coins
        
    def create_treasure_chests(self):
        chests = []
        # Place chests on specific platforms
        chest_positions = [
            (300, WINDOW_HEIGHT - 190),  # On first elevated platform
            (800, WINDOW_HEIGHT - 220),  # On middle platform
            (1500, WINDOW_HEIGHT - 320)  # On higher platform
        ]
        
        for x, y in chest_positions:
            chests.append(TreasureChest(x, y))
            
        return chests
        
    def create_super_chests(self):
        pass
        
    def draw_gradient_background(self):
        # Create a surface for the gradient
        gradient = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Define colors for the gradient (red, orange, yellow)
        color1 = (255, 69, 0)  # Red-Orange
        color2 = (255, 140, 0)  # Dark Orange
        color3 = (255, 215, 0)  # Gold
        
        # Draw the gradient in horizontal strips
        height = WINDOW_HEIGHT
        for i in range(height):
            # Calculate the ratio of completion (0 to 1)
            ratio = i / height
            
            if ratio < 0.5:
                # Blend between color1 and color2
                blend_ratio = ratio * 2
                r = int(color1[0] * (1 - blend_ratio) + color2[0] * blend_ratio)
                g = int(color1[1] * (1 - blend_ratio) + color2[1] * blend_ratio)
                b = int(color1[2] * (1 - blend_ratio) + color2[2] * blend_ratio)
            else:
                # Blend between color2 and color3
                blend_ratio = (ratio - 0.5) * 2
                r = int(color2[0] * (1 - blend_ratio) + color3[0] * blend_ratio)
                g = int(color2[1] * (1 - blend_ratio) + color3[1] * blend_ratio)
                b = int(color2[2] * (1 - blend_ratio) + color3[2] * blend_ratio)
                
            pygame.draw.line(gradient, (r, g, b), (0, i), (WINDOW_WIDTH, i))
            
        self.screen.blit(gradient, (0, 0))
        
    def draw_shop_button(self):
        # Draw button background
        pygame.draw.rect(self.screen, (50, 50, 50), self.shop_button_rect)
        
        # Draw rainbow text
        font = pygame.font.Font(None, 36)
        text_color = pygame.Color(0)
        text_color.hsva = (self.background_color, 100, 100, 100)
        shop_text = font.render("SHOP", True, text_color)
        
        # Center the text in the button
        text_rect = shop_text.get_rect(center=self.shop_button_rect.center)
        self.screen.blit(shop_text, text_rect)
        
    def draw_exit_button(self):
        # Draw button background
        pygame.draw.rect(self.screen, (50, 50, 50), self.exit_button_rect)
        
        # Draw text
        font = pygame.font.Font(None, 36)
        text_color = pygame.Color(0)
        text_color.hsva = ((self.background_color + 180) % 360, 100, 100, 100)
        exit_text = font.render("EXIT", True, text_color)
        
        # Center the text in the button
        text_rect = exit_text.get_rect(center=self.exit_button_rect.center)
        self.screen.blit(exit_text, text_rect)
        
    def draw_teleport_button(self):
        if not self.teleport_available:
            return
            
        # Create dramatic pulsing effect with high contrast colors
        pulse_rate = 10
        pulse_value = (math.sin(self.background_color / pulse_rate) + 1) * 0.5  # 0 to 1 value
        
        # Create expanding glow effect
        glow_size = int(pulse_value * 10)
        for i in range(glow_size, 0, -2):
            glow_rect = self.teleport_button_rect.inflate(i * 2, i * 2)
            alpha = 255 - (i * 15)
            if alpha < 0:
                alpha = 0
                
            # Alternate between bright colors for the glow
            if i % 4 == 0:
                glow_color = (255, 50, 50, alpha)  # Red
            else:
                glow_color = (50, 50, 255, alpha)  # Blue
                
            # Draw glow with semi-transparency
            s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, glow_color, (0, 0, glow_rect.width, glow_rect.height), 2)
            self.screen.blit(s, (glow_rect.x, glow_rect.y))
        
        # Draw flashing main button with attention-grabbing gradient
        flash_color1 = (255, 255, 0)  # Yellow
        flash_color2 = (255, 50, 0)   # Orange-red
        
        # Create gradient effect
        gradient_rect = pygame.Surface((self.teleport_button_rect.width, self.teleport_button_rect.height))
        for y in range(self.teleport_button_rect.height):
            # Calculate color at this position with flashing effect
            ratio = y / self.teleport_button_rect.height
            if pulse_value > 0.5:  # Alternate gradient direction based on pulse
                ratio = 1 - ratio
            
            r = int(flash_color1[0] * (1 - ratio) + flash_color2[0] * ratio)
            g = int(flash_color1[1] * (1 - ratio) + flash_color2[1] * ratio)
            b = int(flash_color1[2] * (1 - ratio) + flash_color2[2] * ratio)
            
            pygame.draw.line(gradient_rect, (r, g, b), (0, y), (self.teleport_button_rect.width, y))
            
        # Apply the gradient
        self.screen.blit(gradient_rect, self.teleport_button_rect)
        
        # Draw thick border
        border_color = (255, 255, 255) if pulse_value > 0.5 else (0, 0, 0)
        pygame.draw.rect(self.screen, border_color, self.teleport_button_rect, 3)
        
        # Draw large "TELEPORT!" text
        font = pygame.font.Font(None, 40)  # Much larger font
        
        # Shadow text for depth effect
        shadow_text = font.render("TELEPORT!", True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(self.teleport_button_rect.centerx + 2, self.teleport_button_rect.centery + 2))
        self.screen.blit(shadow_text, shadow_rect)
        
        # Main text with high contrast
        teleport_text = font.render("TELEPORT!", True, (255, 255, 255))
        teleport_text_rect = teleport_text.get_rect(center=self.teleport_button_rect.center)
        self.screen.blit(teleport_text, teleport_text_rect)
        
        # Add "CLICK ME" hint with animation
        hint_font = pygame.font.Font(None, 24)
        hint_offset = int(math.sin(self.background_color / 5) * 5)
        hint_text = hint_font.render("< CLICK ME >", True, (255, 255, 255))
        hint_rect = hint_text.get_rect(midbottom=(self.teleport_button_rect.centerx, 
                                                 self.teleport_button_rect.bottom + 15 + hint_offset))
        
        # Draw hint text outline
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            self.screen.blit(hint_font.render("< CLICK ME >", True, (0, 0, 0)), 
                          (hint_rect.x + dx, hint_rect.y + dy))
        self.screen.blit(hint_text, hint_rect)
        
    def draw_music_button(self):
        # Draw button background
        pygame.draw.rect(self.screen, (50, 50, 50), self.music_button_rect)
        
        # Draw rainbow text
        font = pygame.font.Font(None, 36)
        text_color = pygame.Color(0)
        text_color.hsva = (self.background_color, 100, 100, 100)
        music_text = font.render("MUTE" if not self.music_muted else "UNMUTE", True, text_color)
        
        # Center the text in the button
        text_rect = music_text.get_rect(center=self.music_button_rect.center)
        self.screen.blit(music_text, text_rect)
        
    def draw_home_button(self):
        # Draw button with blue background
        pygame.draw.rect(self.screen, (0, 0, 255), self.home_button_rect)  # Blue background
        pygame.draw.rect(self.screen, (0, 0, 0), self.home_button_rect, 2)  # Black border
        
        # Draw a house icon
        house_x = self.home_button_rect.centerx
        house_y = self.home_button_rect.centery
        
        # Draw the roof (triangle)
        roof_points = [
            (house_x - 13, house_y - 3),  # Bottom left
            (house_x, house_y - 13),      # Top
            (house_x + 13, house_y - 3)   # Bottom right
        ]
        pygame.draw.polygon(self.screen, (255, 255, 255), roof_points)  # White roof
        
        # Draw the house body (square)
        house_body = pygame.Rect(house_x - 10, house_y - 3, 20, 15)
        pygame.draw.rect(self.screen, (255, 255, 255), house_body)
        
        # Draw the door
        door = pygame.Rect(house_x - 3, house_y + 2, 6, 10)
        pygame.draw.rect(self.screen, (0, 0, 255), door)  # Blue door
        
    def draw_skins_button(self):
        # Draw button with blue background
        pygame.draw.rect(self.screen, (0, 0, 255), self.skins_button_rect)  # Blue background
        pygame.draw.rect(self.screen, (0, 0, 0), self.skins_button_rect, 2)  # Black border
        
        # Draw "SKINS" text
        font = pygame.font.Font(None, 36)
        skins_text = font.render("SKINS", True, (255, 255, 255))  # White text
        skins_rect = skins_text.get_rect(center=self.skins_button_rect.center)
        self.screen.blit(skins_text, skins_rect)
        
    def draw_skins_menu(self):
        # Draw a semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw the menu title
        font_large = pygame.font.Font(None, 60)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        title = font_large.render("SKINS", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Current coins display
        coins_text = font_medium.render(f"Your Coins: {self.score}", True, (255, 215, 0))  # Gold color
        coins_rect = coins_text.get_rect(center=(WINDOW_WIDTH // 2, 130))
        self.screen.blit(coins_text, coins_rect)
        
        # Calculate scroll limits
        item_height = 70  # Increased for better skin display
        visible_area_height = self.skins_visible_items * item_height
        content_height = len(self.skins) * item_height
        self.skins_max_scroll = max(0, content_height - visible_area_height)
        
        # Clamp scroll value
        self.skins_scroll_y = max(0, min(self.skins_scroll_y, self.skins_max_scroll))
        
        # Draw scrollbar if needed
        if content_height > visible_area_height:
            # Draw scroll area background
            scroll_area_rect = pygame.Rect(WINDOW_WIDTH - 25, 200, 15, visible_area_height)
            pygame.draw.rect(self.screen, (60, 60, 60), scroll_area_rect)
            
            # Draw scroll handle
            scroll_ratio = self.skins_scroll_y / self.skins_max_scroll
            handle_height = max(30, visible_area_height * visible_area_height / content_height)
            handle_y = 200 + scroll_ratio * (visible_area_height - handle_height)
            handle_rect = pygame.Rect(WINDOW_WIDTH - 25, handle_y, 15, handle_height)
            pygame.draw.rect(self.screen, (150, 150, 150), handle_rect)
        
        # Draw skin options
        skin_rects = []  # Store the rectangles for click detection
        up_button_rect = None
        down_button_rect = None
        
        # Create the "View Area" for skins with a border
        view_area = pygame.Rect(WINDOW_WIDTH // 2 - 200, 200, 400, visible_area_height)  # Wider for better display
        pygame.draw.rect(self.screen, (40, 40, 60), view_area)
        pygame.draw.rect(self.screen, (100, 100, 150), view_area, 2)
        
        # Draw skin category counts
        categories = {
            "Basic": (0, 10),
            "Pulsing": (11, 20),
            "Gradient": (21, 30),
            "Animated": (31, 40),
            "Particles": (41, 50),
            "Textured": (51, 60),
            "Themed": (61, 70),
            "Premium": (71, 80),
            "Elite": (81, 90),
            "Legendary": (91, 100)
        }
        
        # Draw unlocked count
        unlocked_count = sum(1 for skin in self.skins if skin["unlocked"])
        total_count = len(self.skins)
        collection_text = font_small.render(f"Collection: {unlocked_count}/{total_count}", True, (200, 200, 255))
        collection_rect = collection_text.get_rect(topright=(WINDOW_WIDTH - 40, 160))
        self.screen.blit(collection_text, collection_rect)
        
        # Draw the scroll buttons if needed
        if content_height > visible_area_height:
            # Up button
            up_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 25, 170, 50, 30)
            pygame.draw.rect(self.screen, (60, 60, 100), up_button_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), up_button_rect, 2)
            up_text = font_small.render("▲", True, (255, 255, 255))
            up_text_rect = up_text.get_rect(center=up_button_rect.center)
            self.screen.blit(up_text, up_text_rect)
            
            # Down button
            down_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 25, visible_area_height + 200, 50, 30)
            pygame.draw.rect(self.screen, (60, 60, 100), down_button_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), down_button_rect, 2)
            down_text = font_small.render("▼", True, (255, 255, 255))
            down_text_rect = down_text.get_rect(center=down_button_rect.center)
            self.screen.blit(down_text, down_text_rect)
        
        # Create a clipping rect for the skins area
        self.screen.set_clip(view_area)
        
        for i, skin in enumerate(self.skins):
            # Calculate position with scroll offset
            y_pos = 200 + i * item_height - self.skins_scroll_y
            
            # Skip items that are outside the visible area
            if y_pos + item_height < 200 or y_pos > 200 + visible_area_height:
                continue
            
            # Create rect for this skin option
            skin_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, y_pos, 400, item_height - 2)
            skin_rects.append((i, skin_rect))  # Store index and rect
            
            # Draw background (highlighted if selected)
            if i == self.current_skin:
                pygame.draw.rect(self.screen, (60, 60, 120), skin_rect)  # Highlight selected
            else:
                pygame.draw.rect(self.screen, (40, 40, 60), skin_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), skin_rect, 1)  # White border
            
            # Calculate skin category
            category = None
            for cat_name, (start, end) in categories.items():
                if start <= i <= end:
                    category = cat_name
                    break
            
            # Draw sample of the skin - bigger surface for better visibility
            sample_size = 50
            sample_rect = pygame.Rect(
                skin_rect.x + 15, 
                skin_rect.y + (item_height - sample_size) // 2, 
                sample_size, 
                sample_size
            )
            
            # Create a surface for the sample with animation
            sample_surface = pygame.Surface((sample_size, sample_size), pygame.SRCALPHA)
            
            # Draw the skin sample with the appropriate pattern - simplified version of player rendering
            pattern = skin["pattern"]
            anim_timer = (self.background_color * skin.get("anim_speed", 1.0)) % 360
            
            # Similar pattern logic as in player.draw but simplified
            if pattern == "rgb" or pattern == "rainbow_wave":
                color = pygame.Color(0)
                color.hsva = (anim_timer, 100, 100, 100)
                pygame.draw.rect(sample_surface, color, (0, 0, sample_size, sample_size))
                
            elif pattern == "pulse":
                pulse = (math.sin(anim_timer / 15) + 1) * 0.3 + 0.7
                if skin["color"] is not None:
                    pulsed_color = (
                        min(255, int(skin["color"][0] * pulse)),
                        min(255, int(skin["color"][1] * pulse)),
                        min(255, int(skin["color"][2] * pulse))
                    )
                    pygame.draw.rect(sample_surface, pulsed_color, (0, 0, sample_size, sample_size))
                    
            elif pattern == "gradient":
                if isinstance(skin["color"], list) and len(skin["color"]) >= 2:
                    color1 = skin["color"][0]
                    color2 = skin["color"][1]
                    # Create gradient
                    for y in range(sample_size):
                        ratio = (y + anim_timer) % sample_size / sample_size
                        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                        pygame.draw.line(sample_surface, (r, g, b), (0, y), (sample_size, y))
                else:
                    # Fallback
                    pygame.draw.rect(sample_surface, (100, 100, 100), (0, 0, sample_size, sample_size))
                    
            elif pattern == "sparkle":
                if skin["color"] is not None:
                    pygame.draw.rect(sample_surface, skin["color"], (0, 0, sample_size, sample_size))
                else:
                    pygame.draw.rect(sample_surface, (200, 200, 200), (0, 0, sample_size, sample_size))
                
                # Add sparkles
                for _ in range(3):
                    if random.random() < 0.5:
                        sparkle_x = random.randint(0, sample_size)
                        sparkle_y = random.randint(0, sample_size)
                        pygame.draw.circle(sample_surface, (255, 255, 255), 
                                         (sparkle_x, sparkle_y), random.randint(1, 3))
            
            elif pattern in ["black_hole", "void", "singularity"]:
                # Black hole pattern preview
                pygame.draw.rect(sample_surface, (0, 0, 0), (0, 0, sample_size, sample_size))
                
                # Add swirl
                center = sample_size // 2
                for deg in range(0, 360, 30):
                    angle = deg + anim_timer
                    radius = sample_size // 3
                    x = center + radius * math.cos(math.radians(angle))
                    y = center + radius * math.sin(math.radians(angle))
                    
                    dot_color = (100, 0, 100) if pattern == "black_hole" else \
                               (75, 0, 130) if pattern == "singularity" else \
                               (40, 40, 40)  # void
                    
                    pygame.draw.circle(sample_surface, dot_color, (int(x), int(y)), 2)
            
            elif pattern in ["galaxy", "space", "cosmic", "nebula"]:
                # Space-themed patterns
                base_color = (20, 0, 40) if pattern == "nebula" else (0, 0, 20)
                pygame.draw.rect(sample_surface, base_color, (0, 0, sample_size, sample_size))
                
                # Stars
                for _ in range(8):
                    x = random.randint(0, sample_size)
                    y = random.randint(0, sample_size)
                    pygame.draw.circle(sample_surface, (255, 255, 255), (x, y), 1)
            
            elif pattern in ["supernova", "ultimate"]:
                # Supernova/ultimate preview
                pygame.draw.rect(sample_surface, (255, 255, 255), (0, 0, sample_size, sample_size))
                
                # Rays
                center = sample_size // 2
                for angle in range(0, 360, 45):
                    color = pygame.Color(0)
                    color.hsva = ((angle + anim_timer) % 360, 100, 100, 100)
                    
                    end_x = center + (sample_size // 2) * math.cos(math.radians(angle + anim_timer))
                    end_y = center + (sample_size // 2) * math.sin(math.radians(angle + anim_timer))
                    
                    pygame.draw.line(sample_surface, color, (center, center), 
                                   (int(end_x), int(end_y)), 2)
            
            else:
                # Default for other patterns - show solid color or rgb
                if skin["color"] is not None:
                    pygame.draw.rect(sample_surface, skin["color"], (0, 0, sample_size, sample_size))
                else:
                    # RGB fallback
                    color = pygame.Color(0)
                    color.hsva = (anim_timer, 100, 100, 100)
                    pygame.draw.rect(sample_surface, color, (0, 0, sample_size, sample_size))
            
            # Draw outline
            pygame.draw.rect(sample_surface, (0, 0, 0), (0, 0, sample_size, sample_size), 2)
            
            # Draw the sample
            self.screen.blit(sample_surface, sample_rect)
            
            # Draw name and category
            name_text = font_medium.render(skin["name"], True, (255, 255, 255))
            name_rect = name_text.get_rect(midleft=(sample_rect.right + 15, skin_rect.centery - 10))
            self.screen.blit(name_text, name_rect)
            
            if category:
                category_text = font_small.render(f"({category})", True, (180, 180, 180))
                category_rect = category_text.get_rect(topleft=(name_rect.left, name_rect.bottom + 2))
                self.screen.blit(category_text, category_rect)
            
            # Draw status (unlocked, selected, or price)
            if skin["unlocked"]:
                if i == self.current_skin:
                    status_text = font_small.render("SELECTED", True, (0, 255, 0))  # Green
                else:
                    status_text = font_small.render("UNLOCKED", True, (0, 200, 200))  # Cyan
            else:
                # Determine if player can afford this skin
                can_afford = self.score >= skin["price"]
                color = (255, 215, 0) if can_afford else (255, 100, 100)  # Gold or red
                status_text = font_small.render(f"Price: {skin['price']} coins", True, color)
            
            status_rect = status_text.get_rect(midright=(skin_rect.right - 15, skin_rect.centery))
            self.screen.blit(status_text, status_rect)
        
        # Reset clipping rect
        self.screen.set_clip(None)
        
        # Draw exit button
        exit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 80, 120, 40)
        pygame.draw.rect(self.screen, (180, 50, 50), exit_rect)  # Red
        pygame.draw.rect(self.screen, (0, 0, 0), exit_rect, 2)  # Black border
        
        exit_text = font_medium.render("CLOSE", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
        
        return skin_rects, exit_rect, up_button_rect, down_button_rect  # Return the clickable areas
        
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False  # Signal to quit the game
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle save dialog if it's showing
            if self.show_save_dialog:
                if self.save_yes_rect.collidepoint(mouse_pos):
                    self.save_game()
                    self.return_to_home = True
                    self.show_save_dialog = False
                    return True
                elif self.save_no_rect.collidepoint(mouse_pos):
                    self.return_to_home = True
                    self.show_save_dialog = False
                    return True
                else:
                    # Clicking elsewhere in the dialog does nothing
                    return True
            
            # Handle teleport button click with high priority
            if self.teleport_available and self.teleport_button_rect.collidepoint(mouse_pos):
                self.perform_teleport()
                return True
                
            # Handle skins menu if open
            if self.show_skins:
                # Check if exit button was clicked
                if self.skin_exit_rect.collidepoint(mouse_pos):
                    self.show_skins = False
                    return True
                
                # Handle scroll buttons if they exist
                if self.skin_up_button and self.skin_up_button.collidepoint(mouse_pos):
                    self.skins_scroll_y = max(0, self.skins_scroll_y - self.skins_scroll_speed)
                    return True
                
                if self.skin_down_button and self.skin_down_button.collidepoint(mouse_pos):
                    self.skins_scroll_y = min(self.skins_max_scroll, self.skins_scroll_y + self.skins_scroll_speed)
                    return True
                
                # Check if a skin was clicked
                for skin_idx, skin_rect in self.skin_rects:
                    if skin_rect.collidepoint(mouse_pos):
                        skin = self.skins[skin_idx]
                        
                        # If already unlocked, select it
                        if skin["unlocked"]:
                            self.current_skin = skin_idx
                            self.show_purchase_message = True
                            self.purchase_message = f"Selected: {skin['name']} skin"
                            self.message_timer = 180
                        # Otherwise try to purchase it
                        elif self.score >= skin["price"]:
                            self.score -= skin["price"]
                            skin["unlocked"] = True
                            self.current_skin = skin_idx
                            self.show_purchase_message = True
                            self.purchase_message = f"Purchased: {skin['name']} skin"
                            self.message_timer = 180
                        else:
                            # Not enough coins
                            self.show_purchase_message = True
                            self.purchase_message = f"Not enough coins for {skin['name']} skin!"
                            self.message_timer = 180
                        return True
                
                return True  # Consumed the click in the skins menu
            
            # Handle home button click - show confirmation dialog
            if self.home_button_rect.collidepoint(mouse_pos):
                self.show_save_dialog = True
                return True
                
            # Handle skins button click
            if self.skins_button_rect.collidepoint(mouse_pos):
                self.show_skins = True
                return True
            
            # Handle music button click
            if self.music_button_rect.collidepoint(mouse_pos):
                self.toggle_music()
                return True
            
            # Handle respawn button
            if self.show_respawn:
                respawn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 25, 200, 50)
                if respawn_rect.collidepoint(mouse_pos):
                    self.reset_game()
                    self.show_respawn = False
                    self.fall_timer = 0
                    return True
            
            # Handle shop button click
            if self.shop_button_rect.collidepoint(mouse_pos):
                self.show_shop = True
                self.shop.show = True
                return True
            
            # Handle shop interactions if shop is open
            if self.show_shop:
                self.shop.handle_input(event)
                return True
            
        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Add ESC key to quit
                return False
        
        # Handle player input if shop is not open
        if not self.show_shop:
            self.player.handle_input(event)
            
        # Handle mouse wheel scrolling in skins menu
        if event.type == pygame.MOUSEWHEEL and self.show_skins:
            self.skins_scroll_y = max(0, min(self.skins_max_scroll, 
                                            self.skins_scroll_y - event.y * self.skins_scroll_speed))
            return True
            
        return True  # Continue running the game

    def show_purchase_confirmation(self, item_name):
        self.show_purchase_message = True
        self.purchase_message = f"Congratulations! You got a {item_name}!"
        self.message_timer = 180  # Show message for 3 seconds (60 fps * 3)
        self.active_items.append(item_name)

    def update_camera(self):
        # Camera directly follows player with smooth movement
        self.camera_target[0] = self.player.rect.centerx - WINDOW_WIDTH // 2
        self.camera_target[1] = self.player.rect.centery - WINDOW_HEIGHT // 2

        # Smooth camera movement
        self.camera_offset[0] += (self.camera_target[0] - self.camera_offset[0]) * 0.1
        self.camera_offset[1] += (self.camera_target[1] - self.camera_offset[1]) * 0.1

        # Remove vertical bounds to allow free movement
        self.extend_world()
        
    def extend_world(self):
        # Add new platforms if player is getting close to the end
        if self.player.rect.x > self.last_platform_x - WINDOW_WIDTH:
            self.generate_new_platforms()
            
    def generate_new_platforms(self):
        last_platform = self.platforms[-1]
        start_x = last_platform.rect.right + 130  # Fixed gap of 130 pixels
        last_x = start_x
        
        for _ in range(5):
            width = 75  # Platform width
            x = last_x  # Use the last platform's end position
            
            # Keep height changes smaller and limit maximum height
            last_y = last_platform.rect.y
            max_height_change = 60
            min_y = max(100, last_y - max_height_change)
            max_y = min(WINDOW_HEIGHT + 200, last_y + max_height_change)
            y = random.randint(min_y, max_y)
            
            platform = Platform(x, y, width, PLATFORM_HEIGHT, is_safe=random.random() < 0.3)
            self.platforms.append(platform)
            
            # Update positions for next platform
            last_platform = platform
            last_x = x + width + 130  # Add gap after the platform
            
            # Add coins above platform
            if random.random() < 0.7:
                coin_x = x + width // 2
                coin_y = y - 50
                self.coins.append(Coin(coin_x, coin_y))
                
            # Add chests - 15% chance for regular chest
            chest_roll = random.random()
            if chest_roll < 0.15:
                chest_x = x + width // 2
                chest_y = y - 40
                # 20% of chests will be super chests (3% of platforms)
                if random.random() < 0.2:
                    self.super_chests.append(SuperChest(chest_x, chest_y))
                else:
                    self.treasure_chests.append(TreasureChest(chest_x, chest_y))
                
        # Update the last platform x position
        self.last_platform_x = last_x
            
    def update(self):
        # Update message timer without freezing gameplay
        if self.show_purchase_message:
            if self.message_timer > 180:  # 3 seconds at 60 FPS
                self.show_purchase_message = False
                self.message_timer = 0
            else:
                self.message_timer += 1
                
        if self.game_over:
            return
            
        # Update player
        self.player.update(self.platforms)
        
        # Update play time if game is active
        if not self.show_respawn:
            self.play_time = int(time.time() - self.start_time)
        
        # Update coins and check for magnet collisions
        for coin in self.coins[:]:
            # Use the coin's update method for magnet attraction
            collected = coin.update(self.player)
            if collected:
                self.coins.remove(coin)
                continue
                
            # Standard collision check (for non-magnet collisions)
            if not collected and coin.collides_with(self.player):
                self.coins.remove(coin)
                self.score += 1
                
        # Check for treasure chest collisions
        for chest in self.treasure_chests[:]:
            if not chest.collected and chest.collides_with(self.player):
                chest.collected = True
                self.score += chest.coins
                # Display message without stopping gameplay
                self.show_purchase_message = True
                self.purchase_message = f"Found a treasure chest! +{chest.coins} coins!"
                self.message_timer = 0  # Reset timer
                
        # Check for super chest collisions
        for super_chest in self.super_chests[:]:
            if not super_chest.collected and super_chest.collides_with(self.player):
                super_chest.collected = True
                self.score += super_chest.coins
                # Display message without stopping gameplay
                self.show_purchase_message = True
                self.purchase_message = f"Found a superchest! +{super_chest.coins} coins!"
                self.message_timer = 0  # Reset timer
                
        # Update background color for rainbow effect
        self.background_color = (self.background_color + RGB_CYCLE_SPEED) % 360
        
        if not self.game_over:
            # Update camera
            self.update_camera()
            
            # Check for falling death
            if self.player.rect.top > WINDOW_HEIGHT:
                # Check if player has fallen at least 200 pixels from last ground position
                if hasattr(self.player, 'last_ground_y') and self.player.last_ground_y is not None:
                    fall_distance = self.player.rect.top - self.player.last_ground_y
                    # Only increment fall timer if the player has actually fallen far enough
                    if fall_distance > 200:
                        self.fall_timer += 1
                        # Require a full 2 seconds (120 frames) of falling before showing respawn
                        if self.fall_timer > 120:
                            self.show_respawn = True
                    else:
                        # Reset timer if not falling far enough
                        self.fall_timer = 0
                        self.show_respawn = False
                else:
                    # No last_ground_y, just reset timer to be safe
                    self.fall_timer = 0
                    self.show_respawn = False
            else:
                # Player is on screen, reset timer
                self.fall_timer = 0
                self.show_respawn = False
            
            # Update powerup timers
            for item in self.active_items[:]:
                item.update()
                if item.is_expired():
                    self.active_items.remove(item)
                    
            # Update shop timers
            if hasattr(self, 'shop'):
                self.shop.update()
            
            # Check if music has stopped and should restart with delay
            global music_loaded
            if music_loaded and not self.music_muted and not pygame.mixer.music.get_busy():
                if self.music_restart_timer < 120:  # 2 second delay
                    self.music_restart_timer += 1
                else:
                    # Restart after delay
                    try:
                        pygame.mixer.music.rewind()  # Rewind to start
                        pygame.mixer.music.play()    # Start playing
                        self.music_restart_timer = 0
                    except Exception as e:
                        print(f"Error restarting music: {str(e)}")
                        music_loaded = False  # Mark as not loaded if there's an error
        
    def draw(self, screen):
        # Draw gradient background
        self.draw_gradient_background()
        
        # Draw all game elements
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_offset)
            
        for coin in self.coins:
            coin.draw(self.screen, self.camera_offset)
            
        for chest in self.treasure_chests:
            chest.draw(self.screen, self.camera_offset)
            
        for super_chest in self.super_chests:
            super_chest.draw(self.screen, self.camera_offset)
            
        # Draw player if not showing respawn button
        if not self.show_respawn:
            self.player.draw(self.screen, self.camera_offset)
            
        # Draw coins collected with RGB effect
        font = pygame.font.Font(None, 36)
        coins_color = pygame.Color(0)
        coins_color.hsva = (self.background_color, 100, 100, 100)
        
        coins_text = font.render(f"Coins Collected: {self.score}", True, coins_color)
        coins_rect = coins_text.get_rect(topleft=(10, 10))
        
        # Draw black outline for better visibility
        outline_color = (0, 0, 0)
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
            self.screen.blit(font.render(f"Coins Collected: {self.score}", True, outline_color), 
                           (coins_rect.x + dx, coins_rect.y + dy))
        self.screen.blit(coins_text, coins_rect)
        
        # Group home and shop buttons together
        # Draw shop button
        pygame.draw.rect(self.screen, (0, 0, 255), self.shop_button_rect)  # Blue background
        pygame.draw.rect(self.screen, (0, 0, 0), self.shop_button_rect, 2)  # Black border
        shop_text = font.render("SHOP", True, (255, 255, 255))  # White text
        shop_text_rect = shop_text.get_rect(center=self.shop_button_rect.center)
        self.screen.blit(shop_text, shop_text_rect)
        
        # Draw home button to the left of shop button
        self.draw_home_button()
        
        # Draw teleport button if available
        if self.teleport_available:
            self.draw_teleport_button()
        
        # Draw music button
        music_color = pygame.Color(0)
        music_color.hsva = ((self.background_color + 240) % 360, 100, 100, 100)
        pygame.draw.rect(self.screen, music_color, self.music_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.music_button_rect, 2)
        music_text = font.render("MUTE" if not self.music_muted else "UNMUTE", True, (255, 255, 255))
        music_text_rect = music_text.get_rect(center=self.music_button_rect.center)
        self.screen.blit(music_text, music_text_rect)
        
        # Draw skins button
        self.draw_skins_button()
        
        # Draw purchase message if active
        if self.show_purchase_message:
            if self.message_timer > 180:  # Show for 3 seconds
                self.show_purchase_message = False
                self.message_timer = 0
            else:
                # Create RGB color for message
                message_color = pygame.Color(0)
                message_color.hsva = ((self.background_color + 180) % 360, 100, 100, 100)
                
                # Get the message
                message = self.purchase_message
                
                # Create text
                message_text = font.render(message, True, message_color)
                message_rect = message_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
                
                # Draw black outline for better visibility
                outline_color = (0, 0, 0)
                for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
                    self.screen.blit(font.render(message, True, outline_color), 
                                   (message_rect.x + dx, message_rect.y + dy))
                                   
                # Draw the message
                self.screen.blit(message_text, message_rect)
            
            # Increment message timer after drawing
            self.message_timer += 1
        
        # Draw shop if open
        if self.show_shop:
            self.shop.draw(self.screen)
            
        # Draw skins menu if open
        if self.show_skins:
            self.skin_rects, self.skin_exit_rect, self.skin_up_button, self.skin_down_button = self.draw_skins_menu()
            
        # Draw respawn button if needed
        if self.show_respawn:
            self.draw_respawn_button()
            
        # Draw save game confirmation dialog if active
        if self.show_save_dialog:
            self.draw_save_dialog()
            
    def draw_respawn_button(self):
        button_width = 200
        button_height = 50
        button_x = WINDOW_WIDTH // 2 - button_width // 2
        button_y = WINDOW_HEIGHT // 2 - button_height // 2
        
        # Create button rect
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Draw RGB background
        color = pygame.Color(0)
        color.hsva = (self.background_color, 100, 100, 100)
        pygame.draw.rect(self.screen, color, button_rect)
        
        # Draw black outline
        pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
        
        # Draw text
        font = pygame.font.Font(None, 36)
        text = font.render("RESPAWN", True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        
        # Draw play time text below the button
        play_time_font = pygame.font.Font(None, 30)
        
        # Format time as minutes:seconds
        minutes = self.play_time // 60
        seconds = self.play_time % 60
        play_time_text = play_time_font.render(f"Played for: {minutes}m {seconds}s", True, (0, 0, 0))
        play_time_rect = play_time_text.get_rect(center=(WINDOW_WIDTH // 2, button_rect.bottom + 30))
        self.screen.blit(play_time_text, play_time_rect)
        
        # Determine player title based on play time
        title = "Noob"
        if self.play_time >= 3600:  # 1 hour+
            title = "Gamer Legend"
        elif self.play_time >= 1200:  # 20 min+
            title = "Rank #1 Gamer"
        elif self.play_time >= 600:  # 10 min+
            title = "Gamer Intelligence"
        elif self.play_time >= 180:  # 3 min+
            title = "Good"
        elif self.play_time >= 60:  # 1 min+
            title = "Rookie"
            
        # Draw title text
        title_text = play_time_font.render(f"Title: {title}", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, play_time_rect.bottom + 25))
        self.screen.blit(title_text, title_rect)

    def toggle_music(self):
        global music_loaded
        
        if not music_loaded:
            self.show_purchase_message = True
            self.purchase_message = "Music not available"
            self.message_timer = 60
            return
        
        try:
            if self.music_muted:
                # Unmute
                pygame.mixer.music.unpause()
                self.music_muted = False
                self.show_purchase_message = True
                self.purchase_message = "Music Unmuted!"
                self.message_timer = 60
            else:
                # Mute
                pygame.mixer.music.pause()
                self.music_muted = True
                self.show_purchase_message = True
                self.purchase_message = "Music Muted!"
                self.message_timer = 60
        except Exception as e:
            print(f"Error toggling music: {str(e)}")
            music_loaded = False  # Mark as not loaded if there's an error

    def add_coins(self, amount):
        self.score += amount 

    def perform_teleport(self):
        # Calculate teleport distance (5 blocks)
        teleport_distance = 5 * 200  # Approximate width of 5 platforms
        
        # Store the original x position
        original_x = self.player.rect.x
        
        # Move player forward
        self.player.rect.x += teleport_distance
        
        # Find a safe platform to land on
        safe_platform = None
        closest_distance = float('inf')
        
        for platform in self.platforms:
            # Check if platform is ahead of original position and within a reasonable distance
            if platform.rect.x > original_x and platform.rect.x < self.player.rect.x + 300:
                # Check if this platform is closer to our target than previously found platforms
                distance = abs((platform.rect.x + platform.rect.width/2) - self.player.rect.x)
                if distance < closest_distance:
                    closest_distance = distance
                    safe_platform = platform
        
        # If we found a platform, position the player on it
        if safe_platform:
            self.player.rect.x = safe_platform.rect.x + safe_platform.rect.width // 4
            self.player.rect.y = safe_platform.rect.y - self.player.rect.height
            self.player.is_jumping = False
            self.player.velocity_y = 0
        
        # Collect all coins, chests, and super chests in the teleported area
        for coin in self.coins[:]:
            if coin.rect.x <= self.player.rect.x and coin.rect.x >= original_x and not coin.collected:
                coin.collected = True
                self.add_coins(1)
                
        for chest in self.treasure_chests[:]:
            if chest.rect.x <= self.player.rect.x and chest.rect.x >= original_x and not chest.collected:
                chest.collected = True
                self.add_coins(5)
                
        for chest in self.super_chests[:]:
            if chest.rect.x <= self.player.rect.x and chest.rect.x >= original_x and not chest.collected:
                chest.collected = True
                self.add_coins(10)
                self.show_purchase_message = True
                self.purchase_message = "SuperChest collected! +10 coins"
                self.message_timer = 180
                
        # Show teleport message
        self.show_purchase_message = True
        self.purchase_message = "Teleported forward! Collected all items"
        self.message_timer = 180
        
        # Make teleport single-use
        self.teleport_available = False 

    def draw_save_dialog(self):
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark semi-transparent background
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        pygame.draw.rect(self.screen, (50, 50, 50), self.save_dialog_rect)  # Dark gray background
        
        # Draw RGB border with animation
        border_color = pygame.Color(0)
        border_color.hsva = (self.background_color, 100, 100, 100)
        pygame.draw.rect(self.screen, border_color, self.save_dialog_rect, 3)  # RGB border
        
        # Draw decorative RGB corner accents
        accent_size = 15
        corner_positions = [
            (self.save_dialog_rect.left, self.save_dialog_rect.top),  # Top-left
            (self.save_dialog_rect.right, self.save_dialog_rect.top),  # Top-right
            (self.save_dialog_rect.left, self.save_dialog_rect.bottom),  # Bottom-left
            (self.save_dialog_rect.right, self.save_dialog_rect.bottom)  # Bottom-right
        ]
        
        for i, pos in enumerate(corner_positions):
            corner_color = pygame.Color(0)
            corner_color.hsva = ((self.background_color + i * 90) % 360, 100, 100, 100)
            
            if i == 0:  # Top-left
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0] - 5, pos[1]), (pos[0] + accent_size, pos[1]), 3)
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0], pos[1] - 5), (pos[0], pos[1] + accent_size), 3)
            elif i == 1:  # Top-right
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0] + 5, pos[1]), (pos[0] - accent_size, pos[1]), 3)
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0], pos[1] - 5), (pos[0], pos[1] + accent_size), 3)
            elif i == 2:  # Bottom-left
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0] - 5, pos[1]), (pos[0] + accent_size, pos[1]), 3)
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0], pos[1] + 5), (pos[0], pos[1] - accent_size), 3)
            else:  # Bottom-right
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0] + 5, pos[1]), (pos[0] - accent_size, pos[1]), 3)
                pygame.draw.line(self.screen, corner_color, 
                               (pos[0], pos[1] + 5), (pos[0], pos[1] - accent_size), 3)
        
        # Draw animated decorative dots along the borders
        dot_spacing = 20
        dot_size = 2
        dot_offset = self.background_color % dot_spacing
        
        # Top and bottom borders
        for x in range(self.save_dialog_rect.left + dot_spacing, self.save_dialog_rect.right, dot_spacing):
            # Skip near corners
            if x < self.save_dialog_rect.left + accent_size or x > self.save_dialog_rect.right - accent_size:
                continue
                
            # Top border dot
            dot_color_top = pygame.Color(0)
            dot_color_top.hsva = ((x + self.background_color) % 360, 100, 100, 100)
            pygame.draw.circle(self.screen, dot_color_top, 
                             (x + dot_offset, self.save_dialog_rect.top), dot_size)
            
            # Bottom border dot
            dot_color_bottom = pygame.Color(0)
            dot_color_bottom.hsva = ((x + self.background_color + 180) % 360, 100, 100, 100)
            pygame.draw.circle(self.screen, dot_color_bottom, 
                             (x + dot_offset, self.save_dialog_rect.bottom), dot_size)
        
        # Left and right borders
        for y in range(self.save_dialog_rect.top + dot_spacing, self.save_dialog_rect.bottom, dot_spacing):
            # Skip near corners
            if y < self.save_dialog_rect.top + accent_size or y > self.save_dialog_rect.bottom - accent_size:
                continue
                
            # Left border dot
            dot_color_left = pygame.Color(0)
            dot_color_left.hsva = ((y + self.background_color + 90) % 360, 100, 100, 100)
            pygame.draw.circle(self.screen, dot_color_left, 
                             (self.save_dialog_rect.left, y + dot_offset), dot_size)
            
            # Right border dot
            dot_color_right = pygame.Color(0)
            dot_color_right.hsva = ((y + self.background_color + 270) % 360, 100, 100, 100)
            pygame.draw.circle(self.screen, dot_color_right, 
                             (self.save_dialog_rect.right, y + dot_offset), dot_size)
        
        # Draw title text
        title_font = pygame.font.Font(None, 48)
        message_font = pygame.font.Font(None, 36)
        button_font = pygame.font.Font(None, 40)
        
        # Create bold-looking text by drawing it multiple times with slight offsets
        title_color = pygame.Color(0)
        title_color.hsva = ((self.background_color + 180) % 360, 100, 100, 100)  # RGB title
        title_text = "Are you sure?"
        
        # Draw the title with bold effect (multiple offsets)
        title_rendered = title_font.render(title_text, True, title_color)
        title_rect = title_rendered.get_rect(centerx=self.save_dialog_rect.centerx, 
                                          y=self.save_dialog_rect.y + 30)
        
        # Draw multiple copies with slight offsets for bold effect
        offsets = [(0,0), (1,0), (0,1), (1,1)]
        for dx, dy in offsets:
            self.screen.blit(title_rendered, (title_rect.x + dx, title_rect.y + dy))
        
        # Draw message text
        message_text = message_font.render("Do you want to save your game?", True, (255, 255, 255))
        message_rect = message_text.get_rect(centerx=self.save_dialog_rect.centerx,
                                          y=title_rect.bottom + 30)
        self.screen.blit(message_text, message_rect)
        
        # Draw Yes button with RGB effect
        yes_bg_color = pygame.Color(0, 150, 0)  # Green base
        yes_border_color = pygame.Color(0)
        yes_border_color.hsva = ((self.background_color + 120) % 360, 80, 100, 100)
        
        pygame.draw.rect(self.screen, yes_bg_color, self.save_yes_rect)  # Green background
        pygame.draw.rect(self.screen, yes_border_color, self.save_yes_rect, 2)  # RGB border
        
        yes_text = button_font.render("YES", True, (255, 255, 255))
        yes_rect = yes_text.get_rect(center=self.save_yes_rect.center)
        self.screen.blit(yes_text, yes_rect)
        
        # Draw No button with RGB effect
        no_bg_color = pygame.Color(150, 0, 0)  # Red base
        no_border_color = pygame.Color(0)
        no_border_color.hsva = ((self.background_color + 240) % 360, 80, 100, 100)
        
        pygame.draw.rect(self.screen, no_bg_color, self.save_no_rect)  # Red background
        pygame.draw.rect(self.screen, no_border_color, self.save_no_rect, 2)  # RGB border
        
        no_text = button_font.render("NO", True, (255, 255, 255))
        no_rect = no_text.get_rect(center=self.save_no_rect.center)
        self.screen.blit(no_text, no_rect)
        
    def save_game(self):
        """Save the current game state to a file."""
        import json
        import os
        
        # Create saves directory if it doesn't exist
        os.makedirs("saves", exist_ok=True)
        
        # Get timestamp for the save name
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create save data
        save_data = {
            "score": self.score,
            "play_time": self.play_time,
            "current_skin": self.current_skin,
            "unlocked_skins": [i for i, skin in enumerate(self.skins) if skin["unlocked"]],
            "timestamp": timestamp,
            "title": self.get_player_title()
        }
        
        # Save to file
        filename = f"saves/save_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(save_data, f)
            
        print(f"Game saved to {filename}")
        
    def get_player_title(self):
        """Get the player's title based on play time."""
        if self.play_time >= 3600:  # 1 hour+
            return "Gamer Legend"
        elif self.play_time >= 1200:  # 20 min+
            return "Rank #1 Gamer"
        elif self.play_time >= 600:  # 10 min+
            return "Gamer Intelligence"
        elif self.play_time >= 180:  # 3 min+
            return "Good"
        elif self.play_time >= 60:  # 1 min+
            return "Rookie"
        else:
            return "Noob"