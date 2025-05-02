import pygame
import random
import math
from .constants import *
from .jetpack import Jetpack
from .burger import Burger

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
        # Draw player character based on selected skin
        
        # Get the current skin from the game
        current_skin = self.game.skins[self.game.current_skin]
        
        # Apply camera offset
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height
        )
        
        # Initialize colors and pattern variables
        outline_color = (0, 0, 0)  # Black outline for all skins
        main_color = (255, 255, 255)  # Default color if none specified
        pattern = current_skin["pattern"]
        anim_speed = current_skin.get("anim_speed", 1.0)
        
        # Update color timer for animations
        self.color_timer = (self.color_timer + anim_speed) % 360
        
        # Determine the main color based on the pattern
        if current_skin["color"] is not None:
            if isinstance(current_skin["color"], list):
                # For gradient patterns, use the first color as main color
                main_color = current_skin["color"][0]
            else:
                main_color = current_skin["color"]
        
        # Create a surface for our player with per-pixel alpha
        player_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw different patterns based on skin type
        if pattern == "solid":
            # Simple solid color with embossed look
            pygame.draw.rect(player_surface, main_color, (0, 0, self.rect.width, self.rect.height))
            # Add highlight and shadow for 3D effect
            pygame.draw.line(player_surface, self.lighten_color(main_color), (0, 0), (self.rect.width-1, 0), 2)
            pygame.draw.line(player_surface, self.lighten_color(main_color), (0, 0), (0, self.rect.height-1), 2)
            pygame.draw.line(player_surface, self.darken_color(main_color), (1, self.rect.height-1), (self.rect.width-1, self.rect.height-1), 2)
            pygame.draw.line(player_surface, self.darken_color(main_color), (self.rect.width-1, 1), (self.rect.width-1, self.rect.height-1), 2)
            
        elif pattern == "rgb" or pattern == "rainbow_wave":
            # Rainbow wave effect with flowing pattern
            color = pygame.Color(0)
            color.hsva = (self.color_timer, 100, 100, 100)
            pygame.draw.rect(player_surface, color, (0, 0, self.rect.width, self.rect.height))
            
            # Add wave pattern overlay
            for i in range(5):
                wave_color = pygame.Color(0)
                wave_color.hsva = ((self.color_timer + i * 30) % 360, 100, 100, 50)
                offset = i * 3
                y_pos = (self.color_timer / 5 + i * 5) % self.rect.height
                pygame.draw.line(player_surface, wave_color, 
                               (0, y_pos), 
                               (self.rect.width, y_pos), 2)
            
        elif pattern == "pulse":
            # Pulsing effect with concentric shapes
            pulse = (math.sin(self.color_timer / 15) + 1) * 0.3 + 0.7  # 0.7 to 1.3 range
            pulsed_color = (
                min(255, int(main_color[0] * pulse)),
                min(255, int(main_color[1] * pulse)),
                min(255, int(main_color[2] * pulse))
            )
            pygame.draw.rect(player_surface, pulsed_color, (0, 0, self.rect.width, self.rect.height))
            
            # Add concentric squares with pulse effect
            for i in range(1, 5):
                pulse_offset = (math.sin(self.color_timer / 10 + i) + 1) / 2
                size = int(self.rect.width * (0.8 - i * 0.15) * pulse)
                offset = (self.rect.width - size) // 2
                inner_color = self.lighten_color(pulsed_color, 0.2 * i)
                pygame.draw.rect(player_surface, inner_color, 
                               (offset, offset, size, size), 
                               max(1, i))
                               
        elif pattern == "gradient":
            # Gradient with added diagonal stripes
            if isinstance(current_skin["color"], list) and len(current_skin["color"]) >= 2:
                color1 = current_skin["color"][0]
                color2 = current_skin["color"][1]
                
                # Create gradient surface
                for y in range(self.rect.height):
                    # Calculate ratio based on position (with animation)
                    ratio = (y + self.color_timer) % self.rect.height / self.rect.height
                    # Interpolate between the two colors
                    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                    pygame.draw.line(player_surface, (r, g, b), (0, y), (self.rect.width, y))
                
                # Add diagonal stripes
                for i in range(-self.rect.height, self.rect.width, 8):
                    pos = (i + int(self.color_timer / 2)) % (self.rect.width + self.rect.height) - self.rect.height
                    pygame.draw.line(player_surface, color2, 
                                   (max(0, pos), max(0, -pos)), 
                                   (min(self.rect.width, pos + self.rect.height), 
                                    min(self.rect.height, self.rect.height - (pos - self.rect.width))), 
                                   1)
            else:
                # Fallback if no proper gradient colors
                pygame.draw.rect(player_surface, main_color, (0, 0, self.rect.width, self.rect.height))
        
        elif pattern == "rgb_cycle":
            # RGB cycle with checkerboard pattern
            r = int(127 * math.sin(self.color_timer / 30) + 128)
            g = int(127 * math.sin(self.color_timer / 30 + 2) + 128)
            b = int(127 * math.sin(self.color_timer / 30 + 4) + 128)
            base_color = (r, g, b)
            pygame.draw.rect(player_surface, base_color, (0, 0, self.rect.width, self.rect.height))
            
            # Draw checkerboard pattern
            alt_color = (255-r, 255-g, 255-b)
            cell_size = 10
            offset = int(self.color_timer / 10) % cell_size
            for x in range(-offset, self.rect.width, cell_size):
                for y in range(-offset, self.rect.height, cell_size):
                    if (x // cell_size + y // cell_size) % 2 == 0:
                        pygame.draw.rect(player_surface, alt_color, 
                                       (x, y, cell_size, cell_size))
            
        elif pattern == "matrix":
            # Matrix-like pattern with digital rain and symbols
            pygame.draw.rect(player_surface, main_color, (0, 0, self.rect.width, self.rect.height))
            
            # Add grid lines
            for x in range(0, self.rect.width, 8):
                pygame.draw.line(player_surface, self.lighten_color(main_color), 
                               (x, 0), (x, self.rect.height), 1)
            
            # Add falling digital bits
            symbols = ["0", "1", "?", "!", "$", "%", "#"]
            font = pygame.font.Font(None, 14)
            
            for i in range(5):
                x = ((i * 8) + int(self.color_timer / 5)) % self.rect.width
                y = (self.color_timer * (i+1)) % self.rect.height
                symbol = symbols[(i + int(self.color_timer / 10)) % len(symbols)]
                symbol_surf = font.render(symbol, True, (255, 255, 255))
                player_surface.blit(symbol_surf, (x, y))
                
        elif pattern == "glitch":
            # Glitch effect with more realistic digital artifacts
            pygame.draw.rect(player_surface, (0, 0, 150), (0, 0, self.rect.width, self.rect.height))
            
            # Add scan lines
            for y in range(0, self.rect.height, 3):
                alpha = 100 + int(math.sin(y + self.color_timer / 5) * 50)
                scan_color = (200, 200, 200, alpha)
                pygame.draw.line(player_surface, scan_color, (0, y), (self.rect.width, y), 1)
            
            # Add random glitch blocks with offset components
            for _ in range(5):
                if random.random() < 0.8:
                    glitch_x = random.randint(0, self.rect.width - 5)
                    glitch_y = random.randint(0, self.rect.height - 5)
                    glitch_w = random.randint(3, 15)
                    glitch_h = random.randint(2, 8)
                    
                    # RGB shift effect - offset red and blue components
                    red_surface = pygame.Surface((glitch_w, glitch_h), pygame.SRCALPHA)
                    red_surface.fill((255, 0, 0, 150))
                    player_surface.blit(red_surface, (glitch_x - 2, glitch_y))
                    
                    blue_surface = pygame.Surface((glitch_w, glitch_h), pygame.SRCALPHA)
                    blue_surface.fill((0, 0, 255, 150))
                    player_surface.blit(blue_surface, (glitch_x + 2, glitch_y))
                    
        elif pattern == "tech":
            # Tech-themed pattern with circuit board design
            pygame.draw.rect(player_surface, main_color, (0, 0, self.rect.width, self.rect.height))
            
            # Draw circuit lines
            for i in range(5):
                start_x = random.randint(0, self.rect.width // 2)
                start_y = random.randint(0, self.rect.height)
                end_x = random.randint(self.rect.width // 2, self.rect.width)
                end_y = random.randint(0, self.rect.height)
                
                # Draw a segmented line with right angles
                if i % 2 == 0:
                    mid_x = (start_x + end_x) // 2
                    pygame.draw.line(player_surface, (200, 200, 0), 
                                   (start_x, start_y), (mid_x, start_y), 2)
                    pygame.draw.line(player_surface, (200, 200, 0), 
                                   (mid_x, start_y), (mid_x, end_y), 2)
                    pygame.draw.line(player_surface, (200, 200, 0), 
                                   (mid_x, end_y), (end_x, end_y), 2)
                else:
                    mid_y = (start_y + end_y) // 2
                    pygame.draw.line(player_surface, (200, 200, 0), 
                                   (start_x, start_y), (start_x, mid_y), 2)
                    pygame.draw.line(player_surface, (200, 200, 0), 
                                   (start_x, mid_y), (end_x, mid_y), 2)
                    pygame.draw.line(player_surface, (200, 200, 0), 
                                   (end_x, mid_y), (end_x, end_y), 2)
                
                # Add circuit nodes
                pygame.draw.circle(player_surface, (200, 0, 0), (start_x, start_y), 3)
                pygame.draw.circle(player_surface, (200, 0, 0), (end_x, end_y), 3)
        
        elif pattern == "sparkle":
            # Sparkle effect with diamond facets
            pygame.draw.rect(player_surface, main_color, (0, 0, self.rect.width, self.rect.height))
            
            # Create diamond facet look
            center_x, center_y = self.rect.width // 2, self.rect.height // 2
            
            # Draw diamond facets
            pygame.draw.polygon(player_surface, self.lighten_color(main_color), 
                              [(center_x, 0), (self.rect.width, center_y), 
                               (center_x, self.rect.height), (0, center_y)])
            
            # Add sparkles - more elaborate with different sizes
            for _ in range(8):
                if random.random() < 0.7:
                    sparkle_x = random.randint(2, self.rect.width - 3)
                    sparkle_y = random.randint(2, self.rect.height - 3)
                    sparkle_size = random.randint(1, 3)
                    
                    # Add glow effect
                    for i in range(3):
                        glow_size = sparkle_size + i
                        alpha = 200 - i * 60
                        glow_color = (255, 255, 255, alpha)
                        pygame.draw.circle(player_surface, glow_color, 
                                         (sparkle_x, sparkle_y), glow_size)
                    
                    # Draw star shape for some sparkles
                    if random.random() < 0.3:
                        self.draw_star(player_surface, (sparkle_x, sparkle_y), 
                                      sparkle_size * 2, (255, 255, 255))
        
        elif pattern == "flames":
            # Flame effect with more realistic fire
            # Dark base for contrast
            pygame.draw.rect(player_surface, (40, 0, 0), (0, 0, self.rect.width, self.rect.height))
            
            # Draw fire gradient from bottom to top
            for y in range(self.rect.height, 0, -1):
                ratio = y / self.rect.height
                # Mix red and yellow based on height
                if ratio < 0.3:  # Top of flames (yellow)
                    r, g, b = 255, 255, 100
                elif ratio < 0.6:  # Middle of flames (orange)
                    r, g, b = 255, 165, 0
                else:  # Base of flames (red)
                    r, g, b = 255, 0, 0
                
                # Add flickering effect
                flicker = random.randint(-30, 30)
                r = max(0, min(255, r + flicker))
                g = max(0, min(255, g + flicker))
                
                # Calculate alpha (transparency) based on height
                alpha = int(255 * (1 - (1 - ratio) * 2))
                alpha = max(0, min(255, alpha))
                
                # Only draw if visible
                if alpha > 10:
                    flame_color = (r, g, b, alpha)
                    # Draw with variable width based on height
                    width = int(self.rect.width * (0.5 + ratio * 0.5))
                    x_offset = (self.rect.width - width) // 2
                    
                    # Add waviness based on timer
                    wave_offset = int(math.sin((self.color_timer / 5) + y * 0.2) * (10 * (1-ratio)))
                    x_offset += wave_offset
                    
                    pygame.draw.line(player_surface, flame_color, 
                                   (x_offset, y), (x_offset + width, y), 1)
            
            # Add individual flame particles
            for i in range(15):
                flame_x = random.randint(5, self.rect.width - 5)
                flame_base_y = self.rect.height - 5
                flame_height = random.randint(10, 30)
                flame_speed = random.uniform(0.7, 1.5)
                
                # Calculate current position based on animation
                current_y = flame_base_y - ((self.color_timer * flame_speed + i * 10) % flame_height)
                
                # Only draw if within bounds
                if 0 <= current_y < self.rect.height:
                    # Choose color based on height
                    progress = (flame_base_y - current_y) / flame_height
                    if progress < 0.3:
                        flame_color = (255, 0, 0)
                    elif progress < 0.7:
                        flame_color = (255, 165, 0)
                    else:
                        flame_color = (255, 255, 0)
                        
                    # Draw particle
                    size = max(1, int(3 * (1 - progress)))
                    pygame.draw.circle(player_surface, flame_color, 
                                     (flame_x, int(current_y)), size)
        
        elif pattern in ["galaxy", "space", "cosmic", "nebula"]:
            # Space-themed pattern with stars and cosmic effects
            
            # Choose base color and effects based on specific pattern
            if pattern == "nebula":
                base_color = (20, 0, 40)
                dust_colors = [(138, 43, 226, 100), (75, 0, 130, 100), (153, 50, 204, 100)]
                star_density = 20
                dust_density = 5
            elif pattern == "galaxy":
                base_color = (0, 0, 20)
                dust_colors = [(100, 100, 255, 80), (255, 100, 255, 80), (255, 255, 100, 80)]
                star_density = 25
                dust_density = 8
            elif pattern == "cosmic":
                base_color = (40, 0, 60)
                dust_colors = [(0, 255, 255, 80), (255, 0, 255, 80), (255, 255, 0, 80)]
                star_density = 15
                dust_density = 10
            else:  # space
                base_color = (0, 0, 20)
                dust_colors = [(100, 100, 255, 50), (150, 150, 255, 50)]
                star_density = 30
                dust_density = 3
            
            # Draw background
            pygame.draw.rect(player_surface, base_color, (0, 0, self.rect.width, self.rect.height))
            
            # Add spiral galaxy effect for galaxy pattern
            if pattern == "galaxy":
                center_x, center_y = self.rect.width // 2, self.rect.height // 2
                for angle in range(0, 360, 15):
                    # Create spiral arms
                    for i in range(1, 10):
                        rad = i * 2.5
                        # Position along spiral arm
                        spiral_angle = angle + (self.color_timer / 10) + (i * 10)
                        x = center_x + rad * math.cos(math.radians(spiral_angle))
                        y = center_y + rad * math.sin(math.radians(spiral_angle))
                        
                        if 0 <= x < self.rect.width and 0 <= y < self.rect.height:
                            # Color varies along arm
                            arm_color = pygame.Color(0)
                            arm_color.hsva = ((spiral_angle + self.color_timer) % 360, 70, 100, 90)
                            
                            # Size decreases away from center
                            size = max(1, 4 - i // 3)
                            pygame.draw.circle(player_surface, arm_color, 
                                             (int(x), int(y)), size)
            
            # Add cosmic dust clouds
            for _ in range(dust_density):
                cloud_x = int((self.color_timer * 0.2 + _ * 20) % self.rect.width)
                cloud_y = int((self.color_timer * 0.1 + _ * 15) % self.rect.height)
                cloud_color = random.choice(dust_colors)
                
                # Create a nebula cloud with gradient
                for i in range(3):
                    size = random.randint(3, 8)
                    offset_x = random.randint(-5, 5)
                    offset_y = random.randint(-5, 5)
                    # Adjust color with random variance
                    r, g, b, a = cloud_color
                    r = min(255, max(0, r + random.randint(-20, 20)))
                    g = min(255, max(0, g + random.randint(-20, 20)))
                    b = min(255, max(0, b + random.randint(-20, 20)))
                    pygame.draw.circle(player_surface, (r, g, b, a), 
                                     (cloud_x + offset_x, cloud_y + offset_y), size)
            
            # Add stars with different brightness and sizes
            for _ in range(star_density):
                star_x = random.randint(0, self.rect.width)
                star_y = random.randint(0, self.rect.height)
                
                # Vary star brightness with time
                brightness = 150 + int(50 * math.sin(self.color_timer / 20 + _ * 0.5))
                star_color = (brightness, brightness, brightness)
                
                # Most stars are small dots
                if random.random() < 0.8:
                    size = random.randint(1, 2)
                    pygame.draw.circle(player_surface, star_color, (star_x, star_y), size)
                else:
                    # Some stars get a glow effect
                    size = random.randint(1, 3)
                    # Draw glow
                    for i in range(3):
                        glow_size = size + i
                        alpha = 150 - i * 50
                        pygame.draw.circle(player_surface, star_color + (alpha,), 
                                         (star_x, star_y), glow_size)
                    
                    # Draw star center
                    pygame.draw.circle(player_surface, (255, 255, 255), 
                                     (star_x, star_y), size)
        
        elif pattern in ["black_hole", "void", "singularity"]:
            # Enhanced black hole patterns with more dramatic effects
            
            # Draw black background with subtle gradient
            if pattern == "black_hole":
                for y in range(self.rect.height):
                    ratio = y / self.rect.height
                    color = (int(10 * ratio), 0, int(40 * ratio))
                    pygame.draw.line(player_surface, color, (0, y), (self.rect.width, y))
            else:
                pygame.draw.rect(player_surface, (0, 0, 0), (0, 0, self.rect.width, self.rect.height))
            
            # Add a gravitational lens effect around the center
            center_x = self.rect.width // 2
            center_y = self.rect.height // 2
            
            # Event horizon ring
            horizon_radius = 10
            
            # Draw distortion rings
            max_rings = 8 if pattern == "black_hole" else 12 if pattern == "singularity" else 5
            for i in range(max_rings):
                ring_radius = horizon_radius + i * 2 + int(math.sin(self.color_timer / 10) * 2)
                
                if pattern == "black_hole":
                    # Purple accretion disk
                    ring_color = (100 - i * 10, 0, 100 - i * 5, 150 - i * 15)
                elif pattern == "singularity":
                    # Shifting cosmic colors
                    ring_color = pygame.Color(0)
                    ring_color.hsva = ((self.color_timer + i * 30) % 360, 100, 100, 60 - i * 5)
                else:  # void
                    # Dark emptiness
                    brightness = 40 - i * 4
                    ring_color = (brightness, brightness, brightness, 100 - i * 10)
                
                pygame.draw.circle(player_surface, ring_color, 
                                 (center_x, center_y), ring_radius, 1)
            
            # Add swirling matter effect
            for i in range(0, 360, 10):
                angle = i + self.color_timer
                
                # Inner spiral
                for j in range(1, 5):
                    radius = horizon_radius + j * 4 + int(math.sin(self.color_timer / 20 + j) * 3)
                    
                    # Spiral gets further out with angle
                    radius += i // 20
                    
                    x = center_x + radius * math.cos(math.radians(angle))
                    y = center_y + radius * math.sin(math.radians(angle))
                    
                    # Different particle colors for different black hole types
                    if pattern == "black_hole":
                        particle_color = (150, 0, 150) if j % 2 == 0 else (100, 0, 100)
                    elif pattern == "singularity":
                        hue = (angle + self.color_timer) % 360
                        color = pygame.Color(0)
                        color.hsva = (hue, 100, 100, 100)
                        particle_color = color
                    else:  # void
                        brightness = 40 + j * 10
                        particle_color = (brightness, brightness, brightness)
                    
                    # Draw the particle
                    size = 1 if j < 3 else 2
                    pygame.draw.circle(player_surface, particle_color, (int(x), int(y)), size)
            
            # Draw the central black hole
            pygame.draw.circle(player_surface, (0, 0, 0), (center_x, center_y), horizon_radius)
            
            # Add light-bending distortion at the edge of the event horizon
            if pattern in ["black_hole", "singularity"]:
                horizon_glow = pygame.Color(255, 255, 255, 100)
                pygame.draw.circle(player_surface, horizon_glow, 
                                 (center_x, center_y), horizon_radius + 1, 1)
        
        elif pattern in ["supernova", "ultimate"]:
            # Super bright explosive pattern with radial rays
            if pattern == "ultimate":
                # Ultimate has a more complex, shifting base
                base_color = pygame.Color(0)
                base_color.hsva = (self.color_timer, 100, 100, 100)
                pygame.draw.rect(player_surface, base_color, (0, 0, self.rect.width, self.rect.height))
                
                # Add geometric pattern overlay
                for i in range(3):
                    size = self.rect.width - i * 8
                    offset = (self.rect.width - size) // 2
                    rot_offset = int(self.color_timer / 4) % 360
                    points = []
                    
                    # Create rotating polygons
                    for angle in range(rot_offset, rot_offset + 360, 45):
                        rad = size / 2
                        x = center_x + rad * math.cos(math.radians(angle))
                        y = center_y + rad * math.sin(math.radians(angle))
                        points.append((int(x), int(y)))
                    
                    # Create a color for this layer
                    poly_color = pygame.Color(0)
                    poly_color.hsva = ((self.color_timer + i * 120) % 360, 100, 100, 70)
                    
                    pygame.draw.polygon(player_surface, poly_color, points, 2)
            else:
                # Supernova has a bright center with radial glow
                pygame.draw.rect(player_surface, (255, 255, 255), (0, 0, self.rect.width, self.rect.height))
            
            # Add colorful explosive rays
            center_x = self.rect.width // 2
            center_y = self.rect.height // 2
            
            # Number of rays depends on pattern type
            ray_count = 16 if pattern == "ultimate" else 8
            
            for i in range(0, 360, 360 // ray_count):
                angle = i + self.color_timer * 2
                # Rays pulse in and out
                length = 20 + 10 * math.sin(self.color_timer / 10 + i / 20)
                end_x = center_x + length * math.cos(math.radians(angle))
                end_y = center_y + length * math.sin(math.radians(angle))
                
                # Vibrant colors for rays
                hue = (i + self.color_timer * 3) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 100, 100, 100)
                
                # Ultimate has thicker rays
                thickness = 3 if pattern == "ultimate" else 2
                pygame.draw.line(player_surface, color, 
                              (center_x, center_y), (int(end_x), int(end_y)), thickness)
                
                # Ultimate has additional effects
                if pattern == "ultimate":
                    # Add particle bursts at ray ends
                    for j in range(3):
                        particle_x = end_x + random.randint(-5, 5)
                        particle_y = end_y + random.randint(-5, 5)
                        particle_size = random.randint(1, 3)
                        particle_color = pygame.Color(0)
                        particle_color.hsva = ((hue + j * 30) % 360, 100, 100, 100)
                        pygame.draw.circle(player_surface, particle_color, 
                                        (int(particle_x), int(particle_y)), particle_size)
            
            # Add a pulsing center
            pulse = (math.sin(self.color_timer / 5) + 1) * 0.5
            center_radius = 5 + int(pulse * 5)
            
            if pattern == "ultimate":
                # Ultimate has a shifting core color
                core_color = pygame.Color(0)
                core_color.hsva = ((self.color_timer * 2) % 360, 100, 100, 100)
            else:
                # Supernova has a white-hot center
                core_color = (255, 255, 255)
                
            pygame.draw.circle(player_surface, core_color, (center_x, center_y), center_radius)
            
            # Add a glow effect for the core
            for i in range(3):
                glow_radius = center_radius + i * 2
                if pattern == "ultimate":
                    glow_color = pygame.Color(0)
                    glow_color.hsva = ((self.color_timer * 2 + 180) % 360, 100, 100, 100 - i * 30)
                else:
                    glow_color = (255, 255, 200, 150 - i * 40)
                pygame.draw.circle(player_surface, glow_color, (center_x, center_y), glow_radius)
        
        else:
            # Default RGB effect for unknown patterns
            color = pygame.Color(0)
            color.hsva = (self.color_timer, 100, 100, 100)
            pygame.draw.rect(player_surface, color, (0, 0, self.rect.width, self.rect.height))
        
        # Add black outline to all skins
        pygame.draw.rect(player_surface, outline_color, (0, 0, self.rect.width, self.rect.height), 2)
        
        # Draw the player surface on the screen
        screen.blit(player_surface, draw_rect)
        
        # Draw trail effect if enabled
        if self.powerups.get("trail", False) and self.trail_positions:
            # Create diminishing trail points
            for i, pos in enumerate(self.trail_positions):
                # Size decreases as we go further back in the trail
                size = int(self.rect.width * 0.7 * (i / len(self.trail_positions)))
                
                # Adjust for camera offset
                trail_x = pos[0] - camera_offset[0] 
                trail_y = pos[1] - camera_offset[1]
                
                # Color based on current skin but more transparent
                if pattern == "rgb" or pattern == "rainbow_wave":
                    trail_color = pygame.Color(0)
                    trail_color.hsva = ((self.color_timer + i * 10) % 360, 100, 100, 50)
                else:
                    # For other skins, use a semi-transparent version of the main color
                    alpha = int(150 * (i / len(self.trail_positions)))
                    if isinstance(main_color, tuple) and len(main_color) >= 3:
                        trail_color = main_color + (alpha,) if len(main_color) == 3 else main_color
                    else:
                        trail_color = (255, 255, 255, alpha)
                
                # Draw trail dot
                trail_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, trail_color, (size // 2, size // 2), size // 2)
                screen.blit(trail_surf, (trail_x - size // 2, trail_y - size // 2))
        
        # Draw additional effects if needed
        if self.shield_active:
            self.draw_shield(screen, draw_rect)
            
        # Draw the jetpack if active
        if hasattr(self, 'jetpack') and self.jetpack.active:
            self.jetpack.draw(screen, 
                             draw_rect.x + (0 if self.facing_right else self.rect.width), 
                             draw_rect.y + self.rect.height // 2,
                             self.facing_right)

    def draw_star(self, surface, center, size, color, points=5):
        """Draw a star shape centered at the given position on the specified surface"""
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
            
        pygame.draw.polygon(surface, color, star_points)
    
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

    def draw_shield(self, screen, rect):
        # Draw shield effect around the player
        shield_radius = max(rect.width, rect.height) + 8  # Slightly larger than player
        
        # Create pulsing effect for the shield
        pulse = (math.sin(self.color_timer / 20) + 1) * 0.2 + 0.8  # 0.8 to 1.2 scale
        
        # Create RGB color for shield
        shield_color = pygame.Color(0)
        shield_color.hsva = ((self.color_timer) % 360, 70, 100, 60)  # Semi-transparent
        
        # Create a surface for the shield
        shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
        
        # Draw outer ring with animation
        pygame.draw.circle(shield_surface, shield_color, 
                          (shield_radius, shield_radius), 
                          int(shield_radius * pulse), 3)
                          
        # Draw inner glow
        inner_color = pygame.Color(shield_color)
        inner_color.a = 30  # More transparent
        pygame.draw.circle(shield_surface, inner_color, 
                          (shield_radius, shield_radius), 
                          shield_radius - 2)
        
        # Position shield centered on player
        shield_x = rect.centerx - shield_radius
        shield_y = rect.centery - shield_radius
        
        # Draw shield surface
        screen.blit(shield_surface, (shield_x, shield_y))

    def lighten_color(self, color, amount=0.3):
        """Lighten the given color by the given amount"""
        r, g, b = color[:3]
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return (r, g, b)
        
    def darken_color(self, color, amount=0.3):
        """Darken the given color by the given amount"""
        r, g, b = color[:3]
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        return (r, g, b) 