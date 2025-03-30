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

class SuperChest(TreasureChest):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.chest_color = (41, 128, 185)  # Blue for the chest
        self.metal_color = (255, 215, 0)  # Gold trim
        self.highlight_color = (52, 152, 219)  # Light blue
        self.coins = 20  # Super chest gives 20 coins
        
    def draw(self, screen, camera_offset):
        if self.collected:
            return
            
        # Enhanced glowing animation
        self.animation_offset = (self.animation_offset + 0.15) % (2 * 3.14159)
        glow_intensity = abs(math.sin(self.animation_offset))
        
        # Calculate screen position with camera offset
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height
        )
        
        # Draw chest base (blue)
        pygame.draw.rect(screen, self.chest_color, draw_rect)
        
        # Draw lid (slightly larger than base)
        lid_height = draw_rect.height // 2
        lid_rect = pygame.Rect(
            draw_rect.x - 4,
            draw_rect.y - 2,
            draw_rect.width + 8,
            lid_height + 2
        )
        pygame.draw.rect(screen, self.chest_color, lid_rect)
        
        # Draw golden trim and details
        pygame.draw.rect(screen, self.metal_color, lid_rect, 3)
        pygame.draw.rect(screen, self.metal_color, draw_rect, 3)
        
        # Draw horizontal metal bands
        band_height = 8
        for y_offset in [lid_height // 2, lid_height + draw_rect.height // 4]:
            band_rect = pygame.Rect(
                draw_rect.x - 4,
                draw_rect.y + y_offset - band_height // 2,
                draw_rect.width + 8,
                band_height
            )
            pygame.draw.rect(screen, self.metal_color, band_rect, 2)
        
        # Draw vertical metal bands
        band_width = 8
        for x_offset in [draw_rect.width // 3, 2 * draw_rect.width // 3]:
            band_rect = pygame.Rect(
                draw_rect.x + x_offset - band_width // 2,
                draw_rect.y - 2,
                band_width,
                draw_rect.height + 2
            )
            pygame.draw.rect(screen, self.metal_color, band_rect, 2)
        
        # Draw large golden lock
        lock_size = 16
        lock_rect = pygame.Rect(
            draw_rect.centerx - lock_size // 2,
            draw_rect.y + lid_height - lock_size // 2,
            lock_size, lock_size
        )
        pygame.draw.rect(screen, self.metal_color, lock_rect)
        
        # Draw golden studs on corners
        stud_size = 6
        stud_positions = [
            (draw_rect.left, draw_rect.top),
            (draw_rect.right, draw_rect.top),
            (draw_rect.left, draw_rect.bottom),
            (draw_rect.right, draw_rect.bottom),
            (lid_rect.left, lid_rect.top),
            (lid_rect.right, lid_rect.top)
        ]
        for x, y in stud_positions:
            pygame.draw.rect(screen, self.metal_color, 
                          (x - stud_size//2, y - stud_size//2, stud_size, stud_size))
        
        # Draw glowing coins peeking out (more when glowing)
        if glow_intensity > 0.3:
            num_coins = int(4 + glow_intensity * 3)
            for _ in range(num_coins):
                coin_x = draw_rect.x + random.randint(10, draw_rect.width - 10)
                coin_y = draw_rect.y + lid_height - 5
                pygame.draw.circle(screen, self.metal_color, (coin_x, coin_y), 5) 