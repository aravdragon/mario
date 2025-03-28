import pygame
from .constants import *
from .jetpack import Jetpack
from .burger import Burger
import random

# Constants
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 40
PLAYER_SPEED = 4  # Slightly reduced for better control
GRAVITY = 0.4  # Reduced for smoother falling
JUMP_FORCE = -12  # Negative value for upward movement
MAX_FALL_SPEED = 10  # Limit falling speed
PLAYER_ACCELERATION = 0.5
PLAYER_FRICTION = 0.9

class Player:
    def __init__(self, x, y, game):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.on_ground = False
        self.is_jumping = False
        self.just_jumped = False
        self.can_double_jump = False
        self.health = 100
        self.shield_active = False
        self.shield_timer = 0
        self.current_platforms = []
        self.color_timer = 0
        self.trail_positions = []  # Store positions for trail
        self.powerups = {}
        self.color = (255, 255, 255)  # White color for player
        self.jetpack = Jetpack()
        self.burger = Burger()
        self.facing_right = True
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.last_ground_y = y
        self.game = game

    def update(self, platforms):
        # Store previous position for trail
        if self.powerups.get("trail", False) and (abs(self.x_vel) > 0.1 or abs(self.y_vel) > 0.1):
            self.trail_positions.append((self.rect.centerx, self.rect.centery))
            # Keep only last 75 pixels worth of positions
            while len(self.trail_positions) > 0:
                if abs(self.trail_positions[-1][0] - self.trail_positions[0][0]) > 75 or \
                   abs(self.trail_positions[-1][1] - self.trail_positions[0][1]) > 75:
                    self.trail_positions.pop(0)
                else:
                    break
        else:
            self.trail_positions = []

        keys = pygame.key.get_pressed()
        
        # Calculate base speed with powerups
        current_speed = PLAYER_SPEED
        if self.powerups.get("speed_boost", False):
            current_speed *= 2.0  # Double speed with speed boost
        if self.burger.active:
            current_speed *= 1.5  # 50% speed increase with burger

        # Get jetpack thrust
        if self.jetpack.purchased and (keys[pygame.K_f] or keys[pygame.K_LSHIFT]):
            jetpack_dx = 0
            jetpack_dy = -1.0 if self.jetpack.fuel > 0 else 0
            if self.jetpack.permanent or self.jetpack.fuel > 0:
                self.jetpack.activate(True)
        else:
            jetpack_dx = 0
            jetpack_dy = 0
            
        # Horizontal movement with acceleration
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x_vel = max(self.x_vel - PLAYER_ACCELERATION, -current_speed)
            self.facing_right = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x_vel = min(self.x_vel + PLAYER_ACCELERATION, current_speed)
            self.facing_right = True
        else:
            # Apply friction
            self.x_vel *= PLAYER_FRICTION
            if abs(self.x_vel) < 0.1:
                self.x_vel = 0

        # Add jetpack horizontal thrust
        self.x_vel += jetpack_dx

        # Update coyote time
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
            self.last_ground_y = self.rect.bottom
            self.can_double_jump = True  # Reset double jump when on ground
        else:
            self.coyote_timer = max(0, self.coyote_timer - 1)

        # Handle jumping
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.on_ground or self.coyote_timer > 0:
                self.y_vel = JUMP_FORCE
                self.is_jumping = True
                self.on_ground = False
                self.coyote_timer = 0
            elif self.burger.active and not self.can_double_jump:  # Double jump with burger
                self.y_vel = JUMP_FORCE * 0.8  # Slightly weaker second jump
                self.can_double_jump = True  # Prevent more than double jump

        # Apply gravity and jetpack vertical thrust
        if not self.on_ground:
            self.y_vel += GRAVITY
            if self.y_vel > MAX_FALL_SPEED:
                self.y_vel = MAX_FALL_SPEED

        # Add jetpack vertical thrust
        self.y_vel += jetpack_dy * 0.8  # Reduced jetpack power for better control

        # Update jetpack
        self.jetpack.update()

        # Move and check collisions
        self.handle_movement(platforms)

        # Update magnet ability
        if self.powerups.get("magnet", False):
            for coin in self.game.coins[:]:
                dx = self.rect.centerx - coin.rect.centerx
                dy = self.rect.centery - coin.rect.centery
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < 100000:  # Extended range to 100000 pixels
                    speed = 15  # Faster coin movement
                    coin.rect.x += (dx / dist) * speed
                    coin.rect.y += (dy / dist) * speed

    def handle_movement(self, platforms):
        # Move horizontally
        self.rect.x += int(self.x_vel)
        
        # Handle horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.x_vel > 0:  # Moving right
                    self.rect.right = platform.rect.left
                elif self.x_vel < 0:  # Moving left
                    self.rect.left = platform.rect.right
                self.x_vel = 0
        
        # Move vertically
        self.rect.y += int(self.y_vel)
        self.on_ground = False
        
        # Handle vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_vel > 0:  # Moving down
                    self.rect.bottom = platform.rect.top
                    self.y_vel = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.y_vel < 0:  # Moving up
                    self.rect.top = platform.rect.bottom
                    self.y_vel = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                if self.on_ground or self.coyote_timer > 0:
                    self.y_vel = JUMP_FORCE
                    self.is_jumping = True
                    self.on_ground = False
                    self.coyote_timer = 0
                elif self.burger.active and not self.can_double_jump:  # Double jump with burger
                    self.y_vel = JUMP_FORCE * 0.8  # Slightly weaker second jump
                    self.can_double_jump = True  # Prevent more than double jump
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.burger.active and not self.burger.eaten:
                    if self.burger.eat_button_rect.collidepoint(event.pos):
                        if self.burger.eat():
                            self.can_double_jump = True

    def draw(self, screen, camera_offset):
        # Draw rainbow trail if active
        if self.powerups.get("trail", False) and len(self.trail_positions) > 1:
            for i in range(len(self.trail_positions) - 1):
                # Calculate color with RGB cycle
                color = pygame.Color(0)
                color.hsva = ((self.color_timer + i * 10) % 360, 100, 100, 100)
                
                # Calculate trail thickness (thicker at start, thinner at end)
                thickness = int(15 * (1 - i / len(self.trail_positions)))  # Increased base thickness from 8 to 15
                thickness = max(thickness, 5)  # Minimum thickness of 5 pixels
                
                # Draw trail segment
                start_pos = (self.trail_positions[i][0] - camera_offset[0],
                            self.trail_positions[i][1] - camera_offset[1])
                end_pos = (self.trail_positions[i + 1][0] - camera_offset[0],
                          self.trail_positions[i + 1][1] - camera_offset[1])
                pygame.draw.line(screen, color, start_pos, end_pos, thickness)

        # Calculate screen position with camera offset
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height
        )
        
        # Draw the player with RGB color cycling
        self.color_timer = (self.color_timer + 2) % 360
        color = pygame.Color(0)
        color.hsva = (self.color_timer, 100, 100, 100)
        pygame.draw.rect(screen, color, draw_rect)
        
        # Draw black outline
        pygame.draw.rect(screen, (0, 0, 0), draw_rect, 2)
        
        # Draw health bar above player
        health_width = draw_rect.width
        health_height = 5
        health_rect = pygame.Rect(draw_rect.x, draw_rect.y - 10, health_width, health_height)
        
        # Background of health bar
        pygame.draw.rect(screen, (50, 50, 50), health_rect)
        
        # Current health
        current_health_width = int((self.health / 100) * health_width)
        if current_health_width > 0:
            current_health_rect = pygame.Rect(draw_rect.x, draw_rect.y - 10, current_health_width, health_height)
            health_color = (0, 255, 0) if self.health > 50 else (255, 165, 0) if self.health > 25 else (255, 0, 0)
            pygame.draw.rect(screen, health_color, current_health_rect)
            
        # Draw shield effect if active
        if self.shield_active:
            shield_rect = draw_rect.inflate(10, 10)
            pygame.draw.rect(screen, (0, 191, 255), shield_rect, 2)
            
        # Draw jetpack flames if active
        if hasattr(self, 'jetpack') and self.jetpack.is_active():
            flame_height = 20
            flame_width = 10
            flame_x = draw_rect.centerx - flame_width // 2
            flame_y = draw_rect.bottom
            
            # Create flickering flame effect
            flame_points = [
                (flame_x, flame_y),
                (flame_x + flame_width, flame_y),
                (flame_x + flame_width // 2, flame_y + flame_height + random.randint(-5, 5))
            ]
            
            # Draw flame with RGB color
            flame_color = pygame.Color(0)
            flame_color.hsva = ((self.color_timer + 180) % 360, 100, 100, 100)
            pygame.draw.polygon(screen, flame_color, flame_points)

    def handle_collisions(self, platforms):
        # Handle horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.x_vel > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    self.x_vel = 0
                elif self.x_vel < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    self.x_vel = 0
                    
        # Handle vertical collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_vel > 0:  # Moving down
                    self.rect.bottom = platform.rect.top
                    self.y_vel = 0
                    self.on_ground = True
                elif self.y_vel < 0:  # Moving up
                    self.rect.top = platform.rect.bottom
                    self.y_vel = 0 