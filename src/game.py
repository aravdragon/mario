import pygame
from .player import Player
from .platform import Platform
from .coin import Coin
from .shop import Shop
from .constants import *
import random

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.reset_game()
        self.shop = Shop(self)
        self.show_shop = False
        self.game_over = False
        self.camera_offset = [0, 0]  # Initialize camera offset
        self.background_color = 0
        
    def reset_game(self):
        self.player = Player(WINDOW_WIDTH // 4, WINDOW_HEIGHT - 100)
        self.platforms = self.create_platforms()
        self.coins = self.create_coins()
        self.score = 0
        self.jumps = 0
        
    def create_platforms(self):
        platforms = []
        # Ground platform
        platforms.append(Platform(0, WINDOW_HEIGHT - 40, WINDOW_WIDTH, 40))
        
        # Add floating platforms with random colors
        platform_positions = [
            (300, WINDOW_HEIGHT - 200, 100, 10),
            (500, WINDOW_HEIGHT - 300, 100, 10),
            (200, WINDOW_HEIGHT - 400, 100, 10),
            (600, WINDOW_HEIGHT - 450, 100, 10),
        ]
        
        for x, y, w, h in platform_positions:
            platforms.append(Platform(x, y, w, h))
            
        return platforms
        
    def create_coins(self):
        coins = []
        coin_positions = [
            (350, WINDOW_HEIGHT - 250),
            (550, WINDOW_HEIGHT - 350),
            (250, WINDOW_HEIGHT - 450),
            (650, WINDOW_HEIGHT - 500),
        ]
        
        for x, y in coin_positions:
            coins.append(Coin(x, y))
            
        return coins
        
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_shop = not self.show_shop
            elif event.key == pygame.K_r and self.game_over:
                self.reset_game()
                self.game_over = False
                
        if not self.show_shop:
            self.player.handle_input(event)
            
        if self.show_shop:
            self.shop.handle_input(event)
            
    def update(self):
        if self.show_shop or self.game_over:
            return
            
        # Update player and camera
        self.player.update(self.platforms)
        
        # Update camera position to follow the player
        self.camera_offset[0] = self.player.rect.centerx - WINDOW_WIDTH // 2
        self.camera_offset[1] = self.player.rect.centery - WINDOW_HEIGHT // 2
        
        # Ensure camera doesn't go out of bounds
        self.camera_offset[0] = max(0, min(self.camera_offset[0], self.player.rect.width))
        self.camera_offset[1] = max(0, min(self.camera_offset[1], self.player.rect.height))
        
        # Update platforms
        for platform in self.platforms:
            platform.update()
            if self.player.is_jumping:
                platform.shrink()
        
        # Check for coin collection
        for coin in self.coins[:]:
            if coin.collides_with(self.player):
                self.coins.remove(coin)
                self.score += 1
                
        # Check if player fell off the screen
        if self.player.rect.top > WINDOW_HEIGHT:
            self.game_over = True
            
        # Count successful jumps
        if self.player.just_jumped:
            self.jumps += 1
            self.player.just_jumped = False
            
        # Update background color
        self.background_color = (self.background_color + 1) % 360
            
    def draw(self):
        # Create bright background
        bg_color = (135, 206, 250)  # Light sky blue
        self.screen.fill(bg_color)
        
        if self.show_shop:
            self.shop.draw(self.screen)
            return
            
        # Draw game elements with camera offset
        for platform in self.platforms:
            # Create a new rect for the platform with camera offset
            platform_rect = pygame.Rect(
                platform.rect.x - self.camera_offset[0],
                platform.rect.y - self.camera_offset[1],
                platform.rect.width,
                platform.rect.height
            )
            platform.draw(self.screen, platform_rect)
            
        for coin in self.coins:
            coin_rect = coin.rect.move(-self.camera_offset[0], -self.camera_offset[1])
            coin.draw(self.screen, coin_rect)
            
        player_rect = self.player.rect.move(-self.camera_offset[0], -self.camera_offset[1])
        self.player.draw(self.screen, player_rect)
        
        # Draw score with rainbow effect
        font = pygame.font.Font(None, 36)
        score_color = pygame.Color(0)
        score_color.hsva = ((self.background_color + 180) % 360, 100, 100, 100)
        score_text = font.render(f"Coins: {self.score}", True, score_color)
        self.screen.blit(score_text, (10, 10))
        
        if self.game_over:
            game_over_color = pygame.Color(0)
            game_over_color.hsva = ((self.background_color + 90) % 360, 100, 100, 100)
            game_over_text = font.render(f"Game Over! Jumps: {self.jumps}", True, game_over_color)
            restart_text = font.render("Press R to restart", True, game_over_color)
            self.screen.blit(game_over_text, (WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 + 40)) 