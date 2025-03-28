import pygame
import random
from .constants import *

class Platform:
    def __init__(self, x, y, width, height, is_safe=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_safe = is_safe
        self.color_timer = random.randint(0, 360)  # Random start hue
        self.shrinking = False
        self.original_width = width
        self.shrink_timer = 0
        self.glow_size = 6  # Increased glow size

    def update(self):
        # Update RGB color cycling with faster speed
        self.color_timer = (self.color_timer + 2) % 360  # Increased speed
        
        if self.shrinking:
            self.shrink_timer += 1
            if self.shrink_timer >= 60:  # 1 second
                self.rect.width = max(0, self.rect.width - 1)
                if self.rect.width <= 0:
                    return True
        return False

    def draw(self, screen, camera_offset):
        # Calculate screen position with camera offset
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height
        )
        
        # Create vibrant RGB color that cycles
        hue = self.color_timer
        color = pygame.Color(0)
        color.hsva = (hue, 100, 100, 100)  # Full saturation and value
        
        # Draw glow effect first (for all platforms)
        glow_rect = draw_rect.inflate(self.glow_size, self.glow_size)
        glow_color = pygame.Color(0)
        glow_color.hsva = ((hue + 30) % 360, 100, 100, 100)  # Complementary color
        pygame.draw.rect(screen, glow_color, glow_rect)
        
        # Draw the main platform body with RGB color
        pygame.draw.rect(screen, color, draw_rect)
        
        # Draw black outline
        pygame.draw.rect(screen, (0, 0, 0), draw_rect, 2)
        
        # Add extra glow effect for safe zones
        if self.is_safe:
            safe_glow = draw_rect.inflate(self.glow_size * 2, self.glow_size * 2)
            pygame.draw.rect(screen, (0, 191, 255), safe_glow, 3)  # Thicker blue glow 