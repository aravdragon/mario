import pygame
from .constants import *
import math
import time

class Monster:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.color = (255, 0, 0)  # Red color
        self.speed = 5
        self.start_time = time.time()
        self.active = False  # Start inactive
        self.spawn_timer = 60 * 60  # 60 FPS * 60 seconds = 1 minute before spawn
        self.target_distance = 300  # Exact distance to maintain
        
    def update(self, player_pos):
        # Wait for spawn timer
        if not self.active:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.active = True
            return
            
        # Check if 10 minutes have passed
        if time.time() - self.start_time >= 600:  # 600 seconds = 10 minutes
            self.active = False
            return
            
        # Calculate direction to player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
            
        # Normalize direction
        dx = dx / distance
        dy = dy / distance
        
        # Calculate target position (300 pixels away from player)
        target_x = player_pos[0] - dx * self.target_distance
        target_y = player_pos[1] - dy * self.target_distance
        
        # Move smoothly to target position
        lerp_factor = 0.1
        self.rect.centerx += (target_x - self.rect.centerx) * lerp_factor
        self.rect.centery += (target_y - self.rect.centery) * lerp_factor
        
    def collides_with(self, player):
        if not self.active:
            return False
            
        # Check if player is in a safe zone
        for platform in player.current_platforms:
            if hasattr(platform, 'is_safe') and platform.is_safe:
                return False
                
        return self.rect.colliderect(player.rect)
        
    def draw(self, screen, offset_rect=None):
        if not self.active:
            return
            
        draw_rect = offset_rect if offset_rect else self.rect
        
        # Draw monster body
        pygame.draw.rect(screen, self.color, draw_rect)
        
        # Draw glowing effect
        glow_surface = pygame.Surface((draw_rect.width + 10, draw_rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*self.color, 128), (5, 5, draw_rect.width, draw_rect.height))
        screen.blit(glow_surface, (draw_rect.x - 5, draw_rect.y - 5)) 