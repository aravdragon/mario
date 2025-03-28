import pygame
from .constants import *
import math

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.gold_color = (255, 215, 0)  # Bright gold
        self.highlight_color = (255, 235, 100)  # Light gold
        self.shadow_color = (200, 150, 0)  # Dark gold
        self.animation_offset = 0
        self.collected = False
        
    def collides_with(self, player):
        return self.rect.colliderect(player.rect)
        
    def draw(self, screen, camera_offset):
        if self.collected:
            return
            
        # Add a simple bobbing animation
        self.animation_offset = (self.animation_offset + 0.1) % (2 * 3.14159)
        y_offset = math.sin(self.animation_offset) * 3
        
        # Calculate screen position with camera offset
        center_x = self.rect.centerx - camera_offset[0]
        center_y = self.rect.centery - camera_offset[1] + y_offset
        
        # Create draw rect for the coin
        draw_rect = pygame.Rect(
            center_x - self.rect.width // 2,
            center_y - self.rect.height // 2,
            self.rect.width,
            self.rect.height
        )
        
        # Draw main coin circle
        pygame.draw.circle(screen, self.gold_color, (center_x, center_y), self.rect.width // 2)
        
        # Draw highlight (top-left arc)
        pygame.draw.arc(screen, self.highlight_color, draw_rect, 
                       math.pi/4, 5*math.pi/4, 2)
        
        # Draw shadow (bottom-right arc)
        pygame.draw.arc(screen, self.shadow_color, draw_rect, 
                       5*math.pi/4, math.pi/4, 2)
        
        # Draw dollar sign
        font = pygame.font.Font(None, draw_rect.height - 4)
        text = font.render("$", True, self.shadow_color)
        text_rect = text.get_rect(center=(center_x, center_y))
        screen.blit(text, text_rect) 