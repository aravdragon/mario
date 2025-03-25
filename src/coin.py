import pygame
from .constants import *
import math

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = YELLOW
        self.animation_offset = 0
        
    def collides_with(self, player):
        return self.rect.colliderect(player.rect)
        
    def draw(self, screen, offset_rect=None):
        # Add a simple floating animation
        self.animation_offset = (self.animation_offset + 0.1) % (2 * 3.14159)
        y_offset = int(math.sin(self.animation_offset) * 5)
        
        # Use the provided offset_rect if available, otherwise use self.rect
        draw_rect = offset_rect if offset_rect else self.rect.copy()
        if not offset_rect:
            draw_rect.y += y_offset
        
        # Draw coin as a circle
        pygame.draw.circle(screen, self.color, draw_rect.center, 10) 