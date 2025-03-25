import pygame
from .constants import *

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.is_jumping = False
        self.just_jumped = False
        self.color_offset = 0
        self.powerups = {
            "double_jump": False,
            "speed_boost": False,
            "invincibility": False
        }
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and (self.on_ground or 
                (self.powerups["double_jump"] and not self.on_ground and not self.is_jumping)):
                self.vel_y = JUMP_FORCE
                self.is_jumping = True
                self.just_jumped = True
                
    def update(self, platforms):
        # Handle keyboard input for movement
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED * (2 if self.powerups["speed_boost"] else 1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED * (2 if self.powerups["speed_boost"] else 1)
            
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Limit falling speed
        if self.vel_y > 15:
            self.vel_y = 15
            
        # Move horizontally
        self.rect.x += self.vel_x
        
        # Check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    
        # Move vertically
        self.rect.y += self.vel_y
        
        # Reset ground state
        self.on_ground = False
        
        # Check vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Moving down
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.vel_y < 0:  # Moving up
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                    
        # Keep player in bounds
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
                    
        # Update RGB glow effect
        self.color_offset = (self.color_offset + 4) % 360
        
    def draw(self, screen, offset_rect=None):
        # Create RGB glow effect
        hue = self.color_offset
        color = pygame.Color(0)
        color.hsva = (hue, 100, 100, 100)
        
        # Use the provided offset_rect if available, otherwise use self.rect
        draw_rect = offset_rect if offset_rect else self.rect
        
        # Draw outer glow
        for i in range(3):
            glow_rect = draw_rect.inflate(8 + i*4, 8 + i*4)
            glow_color = pygame.Color(0)
            glow_color.hsva = ((hue + 120*i) % 360, 100, 100, 50)
            pygame.draw.rect(screen, glow_color, glow_rect)
        
        # Draw player
        pygame.draw.rect(screen, color, draw_rect) 