import pygame
from .player import Player
from .platform import Platform
from .coin import Coin
from .shop import Shop
from .treasure import TreasureChest
from .constants import *
import random
import math

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.coins = []
        self.treasure_chests = []  # Initialize treasure_chests list
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
        self.show_purchase_message = False
        self.purchase_message = ""
        self.message_timer = 0
        self.active_items = []
        self.last_platform_x = WINDOW_WIDTH * 3
        self.fall_timer = 0
        self.max_fall_time = 300
        self.show_respawn = False
        
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
                
            # Add more treasure chests (15% chance per platform)
            if random.random() < 0.15:
                chest_x = x + width // 2
                chest_y = y - 40
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
        
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False  # Signal to quit the game
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
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
                
            # Add treasure chests (15% chance per platform)
            if random.random() < 0.15:
                chest_x = x + width // 2
                chest_y = y - 40
                self.treasure_chests.append(TreasureChest(chest_x, chest_y))
                
        # Update the last platform x position
        self.last_platform_x = last_x
            
    def update(self):
        # Update background color for rainbow effect
        self.background_color = (self.background_color + RGB_CYCLE_SPEED) % 360
        
        if not self.game_over:
            # Update player
            self.player.update(self.platforms)
            
            # Update camera
            self.update_camera()
            
            # Check coin collection
            for coin in self.coins[:]:
                if coin.rect.colliderect(self.player.rect):
                    self.coins.remove(coin)
                    self.score += 1
            
            # Check treasure chest collection
            for chest in self.treasure_chests[:]:
                if not chest.collected and chest.rect.colliderect(self.player.rect):
                    chest.collected = True
                    self.score += 5
                    self.show_purchase_message = True
                    self.purchase_message = "Found a treasure chest! +5 coins!"
                    self.message_timer = 120
            
            # Check for falling death
            if self.player.rect.top > WINDOW_HEIGHT:
                self.fall_timer += 1
                if self.fall_timer >= 126:  # 2.1 seconds
                    self.show_respawn = True
            else:
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
        
        # Draw purchase message if active
        if self.show_purchase_message:
            self.message_timer += 1
            if self.message_timer > 180:  # Show for 3 seconds
                self.show_purchase_message = False
                self.message_timer = 0
            else:
                message_color = pygame.Color(0)
                message_color.hsva = ((self.background_color + 180) % 360, 100, 100, 100)
                message_text = font.render(self.purchase_message, True, message_color)
                message_rect = message_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
                self.screen.blit(message_text, message_rect)
        
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