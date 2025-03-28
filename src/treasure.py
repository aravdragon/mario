import pygame
from .constants import *
import math
import random

class TreasureChest:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 45)  # Made chest slightly larger
        self.wood_color = (139, 69, 19)  # Dark wood brown
        self.gold_color = (255, 215, 0)  # Gold
        self.highlight_color = (205, 133, 63)  # Light wood
        self.animation_offset = 0
        self.collected = False
        self.coins = 10
        
    def collides_with(self, player):
        return self.rect.colliderect(player.rect)
        
    def draw(self, screen, camera_offset):
        if self.collected:
            return
            
        # Add a simple glowing animation
        self.animation_offset = (self.animation_offset + 0.1) % (2 * 3.14159)
        glow_intensity = abs(math.sin(self.animation_offset))
        
        # Calculate screen position with camera offset
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height
        )
        
        # Draw chest base
        pygame.draw.rect(screen, self.wood_color, draw_rect)
        
        # Draw lid (slightly larger than base)
        lid_height = draw_rect.height // 2
        lid_rect = pygame.Rect(
            draw_rect.x - 2,
            draw_rect.y,
            draw_rect.width + 4,
            lid_height
        )
        pygame.draw.rect(screen, self.wood_color, lid_rect)
        
        # Draw wood grain lines on base (horizontal)
        for y in range(3):
            line_y = draw_rect.y + lid_height + (y + 1) * (draw_rect.height - lid_height) // 3
            pygame.draw.line(screen, self.highlight_color,
                           (draw_rect.left, line_y),
                           (draw_rect.right, line_y), 1)
        
        # Draw wood grain lines on lid (horizontal)
        for y in range(2):
            line_y = draw_rect.y + (y + 1) * lid_height // 2
            pygame.draw.line(screen, self.highlight_color,
                           (lid_rect.left, line_y),
                           (lid_rect.right, line_y), 1)
        
        # Draw gold trim
        pygame.draw.rect(screen, self.gold_color, lid_rect, 2)
        pygame.draw.rect(screen, self.gold_color, draw_rect, 2)
        
        # Draw lock
        lock_size = 12
        lock_rect = pygame.Rect(
            draw_rect.centerx - lock_size//2,
            draw_rect.y + lid_height - lock_size//2,
            lock_size, lock_size
        )
        pygame.draw.rect(screen, self.gold_color, lock_rect)
        
        # Draw coins peeking out (when glowing)
        if glow_intensity > 0.5:
            for _ in range(4):
                coin_x = draw_rect.x + random.randint(10, draw_rect.width - 10)
                coin_y = draw_rect.y + lid_height - 5
                pygame.draw.circle(screen, self.gold_color, (coin_x, coin_y), 4) 