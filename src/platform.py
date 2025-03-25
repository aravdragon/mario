import pygame
import random
from .constants import *

class Platform:
    def __init__(self, x, y, width, height):
        self.original_width = width
        self.rect = pygame.Rect(x, y, width, height)
        self.color = random.choice(PLATFORM_COLORS)
        self.color_timer = 0
        self.color_speed = 2
        
    def shrink(self):
        if self.rect.width > 20:  # Minimum platform width
            new_width = self.rect.width - SHRINK_RATE
            width_diff = self.rect.width - new_width
            self.rect.width = new_width
            self.rect.x += width_diff / 2  # Keep platform centered while shrinking
            
    def update(self):
        # Change color gradually
        self.color_timer += self.color_speed
        if self.color_timer >= 360:
            self.color_timer = 0
            self.color = random.choice(PLATFORM_COLORS)
            
    def draw(self, screen, offset_rect=None):
        # Use the provided offset_rect if available, otherwise use self.rect
        draw_rect = offset_rect if offset_rect else self.rect
        
        # Draw platform with a glowing effect
        glow_rect = draw_rect.inflate(4, 4)
        pygame.draw.rect(screen, self.color, glow_rect)
        pygame.draw.rect(screen, WHITE, draw_rect) 