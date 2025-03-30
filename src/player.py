import pygame
from .constants import *
from .jetpack import Jetpack
from .burger import Burger
import random
import math

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
        self.velocity_x = 0
        self.velocity_y = 0
        self.mask = None
        self.fall_count = 0
        self.direction = "left"
        self.animation_count = 0
        self.is_jumping = False
        self.on_ground = False
        self.burger = Burger()
        self.jetpack = Jetpack()
        self.magnet_active = False
        self.magnet_radius = 1000  # Increased from 200 to 1000
        self.magnet_strength = 15  # Increased from 5 to 15
        self.magnet_timer = 0
        self.magnet_duration = 600  # 10 seconds at 60 FPS
        self.facing_right = True
        self.coyote_timer = 0
        self.can_double_jump = False
        self.game = game
        self.current_platforms = []
        self.color_timer = 0
        self.trail_positions = []
        self.trail_update_timer = 0
        self.powerups = {}
        self.last_ground_y = y  # Track last ground position for fall detection
        self.health = 100
        self.shield_active = False
        self.shield_timer = 0
        self.just_jumped = False
        self.jump_buffer_timer = 0

    def update(self, platforms):
        # Store previous position for collision resolution
        old_x = self.rect.x
        old_y = self.rect.y
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Calculate base speed with powerups
        current_speed = PLAYER_SPEED
        if self.powerups.get("speed_boost", False):
            current_speed *= SPEED_BOOST_MULTIPLIER
        if self.burger.active:
            current_speed *= BURGER_SPEED_MULTIPLIER
            
        # Horizontal movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = max(self.velocity_x - PLAYER_ACCELERATION, -current_speed)
            self.facing_right = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = min(self.velocity_x + PLAYER_ACCELERATION, current_speed)
            self.facing_right = True
        else:
            # Apply friction
            self.velocity_x *= PLAYER_FRICTION
            if abs(self.velocity_x) < 0.1:
                self.velocity_x = 0
                
        # Update coyote time
        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
            self.last_ground_y = self.rect.y
            self.can_double_jump = True
        else:
            self.coyote_timer = max(0, self.coyote_timer - 1)
            
        # Handle jumping
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.on_ground or self.coyote_timer > 0:
                self.velocity_y = JUMP_FORCE
                self.is_jumping = True
                self.on_ground = False
                self.coyote_timer = 0
            elif self.burger.active and not self.can_double_jump:
                self.velocity_y = JUMP_FORCE * 0.8
                self.can_double_jump = True
                
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += GRAVITY
            if self.velocity_y > MAX_FALL_SPEED:
                self.velocity_y = MAX_FALL_SPEED
                
        # Apply jetpack thrust if available
        if keys[pygame.K_f] and self.jetpack.purchased:
            self.jetpack.activate(True)
            h_thrust, v_thrust = self.jetpack.get_thrust(keys)
            self.velocity_x += h_thrust
            self.velocity_y += v_thrust
        else:
            if hasattr(self, 'jetpack'):
                self.jetpack.activate(False)
            
        # Update jetpack
        if hasattr(self, 'jetpack'):
            self.jetpack.update()
        
        # Handle movement and collisions
        self.handle_movement(platforms)
        
        # Track position for trail effect
        if self.powerups.get("trail", False):
            # Only add trail points if player is moving
            if abs(self.velocity_x) > 0.5 or abs(self.velocity_y) > 0.5:
                self.trail_update_timer += 1
                if self.trail_update_timer >= 2:
                    self.trail_positions.append((self.rect.centerx, self.rect.centery))
                    self.trail_update_timer = 0
                    
                    # Limit trail length to 100 pixels
                    while len(self.trail_positions) > 1:
                        # Check if oldest point is more than 100 pixels away from newest point
                        newest = self.trail_positions[-1]
                        oldest = self.trail_positions[0]
                        distance = ((newest[0] - oldest[0])**2 + (newest[1] - oldest[1])**2)**0.5
                        if distance > 100:
                            self.trail_positions.pop(0)
                        else:
                            break
            else:
                # Clear trail when not moving
                self.trail_positions = []
        
        # Update magnet ability
        if self.powerups.get("magnet", False):
            self.magnet_active = True
            self.magnet_timer = self.magnet_duration  # Reset timer when powerup is collected
            # Remove the powerup after activation
            self.powerups["magnet"] = False
        
        # Update magnet timer
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
            self.magnet_active = True
        else:
            self.magnet_active = False
            
        # Update the burger
        self.burger.update()

    def handle_movement(self, platforms):
        # Move horizontally
        self.rect.x += int(self.velocity_x)
        
        # Handle horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    self.velocity_x = 0
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    self.velocity_x = 0
        
        # Move vertically
        self.rect.y += int(self.velocity_y)
        self.on_ground = False
        
        # Handle vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Moving down
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.velocity_y < 0:  # Moving up
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

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

        # Create a color cycling RGB block for drippy style
        self.color_timer = (self.color_timer + 2) % 360
        
        # Calculate position with camera offset
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height
        )
        
        # Draw solid colored square (Geometry Dash style)
        main_color = pygame.Color(0)
        main_color.hsva = (self.color_timer, 80, 100, 100)
        pygame.draw.rect(screen, main_color, draw_rect)
        
        # Draw black border (Geometry Dash style)
        pygame.draw.rect(screen, (0, 0, 0), draw_rect, 2)
        
        # GEOMETRY DASH FACE
        
        # Draw simple geometric eyes (squares with black eyes)
        eye_size = 10  # Slightly larger eyes
        eye_padding = 9
        eye_color = (0, 0, 0)  # Black eyes
        
        # Left eye
        left_eye_rect = pygame.Rect(
            draw_rect.left + eye_padding,
            draw_rect.top + eye_padding,
            eye_size,
            eye_size
        )
        pygame.draw.rect(screen, eye_color, left_eye_rect)
        
        # Right eye
        right_eye_rect = pygame.Rect(
            draw_rect.right - eye_padding - eye_size,
            draw_rect.top + eye_padding,
            eye_size,
            eye_size
        )
        pygame.draw.rect(screen, eye_color, right_eye_rect)
        
        # CLEAR SMILE - Simple rectangular smile (Geometry Dash style)
        mouth_width = 22
        mouth_height = 5
        mouth_y = draw_rect.top + draw_rect.height * 2 // 3
        
        # Create a simple rectangular smile
        mouth_rect = pygame.Rect(
            draw_rect.centerx - mouth_width // 2,
            mouth_y,
            mouth_width,
            mouth_height
        )
        pygame.draw.rect(screen, (0, 0, 0), mouth_rect)  # Black rectangular smile
        
        # Add speed effect when moving
        if abs(self.velocity_x) > 1 or abs(self.velocity_y) > 1:
            # Draw motion lines behind character
            line_color = pygame.Color(0)
            line_color.hsva = ((self.color_timer + 30) % 360, 60, 100, 100)
            
            # Draw 3 motion lines when moving
            for i in range(3):
                offset = 5 + i * 4
                line_y_offset = i * 5 - 5
                
                # Horizontal motion lines when moving sideways
                if abs(self.velocity_x) > 1:
                    direction = -1 if self.velocity_x > 0 else 1
                    pygame.draw.line(
                        screen,
                        line_color,
                        (draw_rect.centerx + direction * offset, draw_rect.centery + line_y_offset),
                        (draw_rect.centerx + direction * (offset + 8), draw_rect.centery + line_y_offset),
                        2
                    )
        
        # Add powerup effects - minimal clean style
        if self.powerups.get("speed_boost", False):
            # Draw speed aura
            aura_color = pygame.Color(0)
            aura_color.hsva = ((self.color_timer + 180) % 360, 80, 100, 70)  # Semi-transparent
            
            # Draw aura around character
            aura_rect = draw_rect.inflate(6, 6)
            pygame.draw.rect(screen, aura_color, aura_rect, 2)

    def draw_star(self, screen, center, size, color, points=5):
        """Draw a star shape centered at the given position"""
        outer_points = []
        inner_points = []
        
        for i in range(points * 2):
            angle = math.pi * i / points
            radius = size if i % 2 == 0 else size / 2
            x = center[0] + radius * math.sin(angle)
            y = center[1] + radius * math.cos(angle)
            
            if i % 2 == 0:
                outer_points.append((x, y))
            else:
                inner_points.append((x, y))
                
        # Combine the points alternating outer and inner
        star_points = []
        for i in range(points):
            star_points.append(outer_points[i])
            star_points.append(inner_points[i])
            
        pygame.draw.polygon(screen, color, star_points)
    
    def draw_zigzag(self, screen, start, end, segments, height, color, thickness=1):
        """Draw a zigzag line between start and end points"""
        points = [start]
        
        # Calculate segment length
        segment_length = (end[0] - start[0]) / segments
        
        # Create zigzag points
        for i in range(1, segments):
            x = start[0] + segment_length * i
            y = start[1] + (height if i % 2 == 1 else -height)
            points.append((x, y))
            
        points.append(end)
        
        # Draw the zigzag line
        pygame.draw.lines(screen, color, False, points, thickness)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                if self.on_ground or self.coyote_timer > 0:
                    self.velocity_y = JUMP_FORCE
                    self.is_jumping = True
                    self.on_ground = False
                    self.coyote_timer = 0
                elif self.burger.active and not self.can_double_jump:  # Double jump with burger
                    self.velocity_y = JUMP_FORCE * 0.8  # Slightly weaker second jump
                    self.can_double_jump = True  # Prevent more than double jump
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.burger.active and not self.burger.eaten:
                    if self.burger.eat_button_rect.collidepoint(event.pos):
                        if self.burger.eat():
                            self.can_double_jump = True

    def handle_collisions(self, platforms):
        # Handle horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    self.velocity_x = 0
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    self.velocity_x = 0
                    
        # Handle vertical collisions
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Moving down
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Moving up
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0 