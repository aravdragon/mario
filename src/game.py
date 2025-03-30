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
        self.game_over = False
        self.camera_offset = [0, 0]
        self.camera_target = [0, 0]
        self.background_color = 0
        self.shop_button_rect = pygame.Rect(WINDOW_WIDTH - 120, 10, 100, 40)
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
        self.teleport_button_rect = pygame.Rect(WINDOW_WIDTH - 240, 10, 100, 40)
        
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
        # Create RGB color effect
        teleport_color = pygame.Color(0)
        teleport_color.hsva = ((self.background_color + 120) % 360, 100, 100, 100)
        
        # Draw button background
        pygame.draw.rect(self.screen, (240, 240, 240), self.teleport_button_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.teleport_button_rect, 2)
        
        # Draw text with RGB effect
        font = pygame.font.Font(None, 24)
        teleport_text = font.render("TELEPORT", True, teleport_color)
        teleport_text_rect = teleport_text.get_rect(center=self.teleport_button_rect.center)
        
        # Draw text outline
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            outline_text = font.render("TELEPORT", True, (0, 0, 0))
            self.screen.blit(outline_text, (teleport_text_rect.x + dx, teleport_text_rect.y + dy))
        self.screen.blit(teleport_text, teleport_text_rect)
        
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
        
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False  # Signal to quit the game
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
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
            
            # Handle teleport button click
            if self.teleport_available and self.teleport_button_rect.collidepoint(mouse_pos):
                self.perform_teleport()
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
            width = 160  # Platform width
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
        
        # Draw shop button with RGB effect
        shop_color = pygame.Color(0)
        shop_color.hsva = ((self.background_color + 120) % 360, 100, 100, 100)
        pygame.draw.rect(self.screen, shop_color, self.shop_button_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.shop_button_rect, 2)
        shop_text = font.render("SHOP", True, (255, 255, 255))
        shop_text_rect = shop_text.get_rect(center=self.shop_button_rect.center)
        self.screen.blit(shop_text, shop_text_rect)
        
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
            
        # Draw respawn button if needed
        if self.show_respawn:
            self.draw_respawn_button()
            
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