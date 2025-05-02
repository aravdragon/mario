import pygame
import random
import os
import math
from .constants import *

class DrippyEffect:
    def __init__(self, x, y, color, speed=0.5, size=15, max_length=80):
        self.x = x
        self.y = y
        self.original_y = y
        self.hue = color.hsva[0]  # Store just the hue value
        self.speed = speed
        self.size = size
        self.length = random.randint(20, max_length)
        self.thickness = random.randint(2, 6)
        self.active = True
        self.alpha = 255
        self.fade_speed = 2

    def update(self):
        self.y += self.speed
        self.alpha -= self.fade_speed
        if self.y > self.original_y + self.length or self.alpha <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return
            
        # Create gradient effect from top to bottom
        for i in range(int(self.length)):
            pos_y = self.y - i
            # Skip if offscreen
            if pos_y < 0 or pos_y >= WINDOW_HEIGHT:
                continue
                
            # Fade alpha based on distance from origin
            fade_ratio = 1 - (i / self.length)
            current_alpha = int(self.alpha * fade_ratio)
            if current_alpha <= 0:
                continue
                
            # Create a color with this hue and alpha
            color = pygame.Color(0)
            color.hsva = (self.hue, 100, 100, 100)  # Full saturation and value
            
            # Convert to RGB for alpha blending
            r, g, b = color.r, color.g, color.b
            
            # Calculate the thickness first
            thickness = max(1, int(self.thickness * fade_ratio))
            
            # Create a surface for alpha blending
            s = pygame.Surface((thickness*2, thickness*2), pygame.SRCALPHA)
            s.fill((r, g, b, current_alpha))
            
            # Draw the drip dot with decreasing thickness
            pygame.draw.circle(s, (r, g, b, current_alpha), (thickness, thickness), thickness)
            screen.blit(s, (int(self.x)-thickness, int(pos_y)-thickness))

class FloatingObject:
    def __init__(self, size=None, color=None, speed=1):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        self.original_y = self.y
        self.speed_x = random.uniform(-0.5, 0.5) * speed
        self.speed_y = random.uniform(-0.5, 0.5) * speed
        self.size = size or random.randint(10, 30)
        self.color = color or (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.phase = random.uniform(0, 2 * math.pi)
        self.amplitude = random.randint(5, 20)
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-1, 1)

    def update(self):
        # Update position with slight waviness
        self.x += self.speed_x
        self.phase += 0.03
        self.y = self.original_y + math.sin(self.phase) * self.amplitude
        self.original_y += self.speed_y
        self.rotation += self.rotation_speed
        
        # Wrap around screen
        if self.x < -self.size:
            self.x = WINDOW_WIDTH + self.size
        elif self.x > WINDOW_WIDTH + self.size:
            self.x = -self.size
            
        if self.original_y < -self.size:
            self.original_y = WINDOW_HEIGHT + self.size
        elif self.original_y > WINDOW_HEIGHT + self.size:
            self.original_y = -self.size

    def draw(self, screen):
        # Draw a shape with RGB color
        color = pygame.Color(0)
        color.hsva = ((pygame.time.get_ticks() // 20) % 360, 100, 100, 100)
        
        # Draw a shape (square or circle)
        if random.random() < 0.5:
            # Rotate square
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surface, color, (0, 0, self.size, self.size))
            rotated = pygame.transform.rotate(surface, self.rotation)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size//2)

class HomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.color_timer = 0
        self.background_offset = 0
        self.background_speed = 0.5  # Speed of background color movement
        self.show = True
        
        # Load Pacifico font
        try:
            font_path = os.path.join(os.getcwd(), "assets", "fonts", "Pacifico-Regular.ttf")
            if os.path.exists(font_path):
                self.title_font = pygame.font.Font(font_path, 90)
                print("Loaded Pacifico font!")
            else:
                self.title_font = pygame.font.Font(None, 90)
                print(f"Font not found at {font_path}")
        except Exception as e:
            print(f"Error loading font: {str(e)}")
            self.title_font = pygame.font.Font(None, 90)
            
        # Use standard font for Play button with a larger size for better visibility
        self.button_font = pygame.font.Font(None, 80)
        
        # Create button - smaller size to match screenshot
        self.play_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT // 2, 240, 80)
        
        # Previously played button (below the Play button) - increased vertical spacing by 30 pixels
        self.prev_played_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 130, 300, 60)
        
        # Saved games menu properties
        self.show_saved_games = False
        self.saved_games = []
        self.saved_games_scroll_y = 0
        self.saved_games_max_scroll = 0
        self.saved_game_rects = []
        self.saved_game_back_rect = None
        self.load_saved_games_list()
        
        # Trail properties - moving from left to right
        self.trail_timer = 0
        self.trail_segments = []
        self.segment_width = 30
        self.segment_height = 20
        self.max_segments = 20
        self.trail_speed = 6
        self.trail_x = -self.segment_width  # Start off-screen
        
        # Scene transition - set to always use cyberpunk grid (scene 3)
        self.scene_timer = 0
        self.max_scene_time = 300  # frames per scene (5 seconds at 60fps)
        self.current_scene = 2  # Start with cyberpunk grid scene (index 2)
        self.total_scenes = 3
        self.transition_alpha = 0
        self.transitioning = False
        self.transition_direction = 1  # 1 for fade in, -1 for fade out
        
        # Music-reactive liquid setup
        self.liquid_height = 100
        self.liquid_base_y = WINDOW_HEIGHT - self.liquid_height
        self.liquid_points = []
        self.init_liquid_points()
        
        # Music visualization properties
        self.audio_sample = [0.1] * 10  # Initial audio sample values
        self.target_level = 0.2  # Target water level (0.0 to 1.0)
        self.current_level = 0.2  # Current water level
        self.level_smooth_factor = 0.1  # Smoothing factor for level changes
        self.wave_height = 20  # Maximum wave height
        self.droplet_timer = 0
        self.droplets = []  # Store active water droplets
        self.bubble_timer = 0
        self.bubbles = []  # Store active bubbles
        
        # Initialize character offsets for wavy text
        self.title_chars_offset = []
        for i in range(20):  # Pre-allocate enough for typical text lengths
            self.title_chars_offset.append(random.uniform(0, math.pi*2))
        
    def init_liquid_points(self):
        # Create liquid surface points for wave simulation
        points_count = WINDOW_WIDTH // 20  # One point every 20 pixels
        for i in range(points_count + 2):  # +2 for edges
            x = i * 20 - 20  # Start before screen edge
            self.liquid_points.append({
                'x': x,
                'y': 0,
                'speed': random.uniform(0.05, 0.15),
                'amplitude': random.uniform(5, 15),
                'phase': random.uniform(0, math.pi*2)
            })

    def update(self):
        # Update color timer for RGB effects
        self.color_timer = (self.color_timer + 1) % 360
        
        # Disable scene transitions to keep cyberpunk grid background
        # self.scene_timer += 1
        # if self.scene_timer >= self.max_scene_time and not self.transitioning:
        #     self.transitioning = True
        #     self.transition_direction = -1  # Start fading out
        
        # Handle scene transition (only for fade effects, not changing scenes)
        if self.transitioning:
            self.transition_alpha += self.transition_direction * 5
            if self.transition_alpha >= 255:  # Fully faded in
                self.transition_direction = -1  # Start fading out
            elif self.transition_alpha <= 0:  # Fully faded out
                self.transition_direction = 1  # Start fading in
                # self.current_scene = (self.current_scene + 1) % self.total_scenes
                self.scene_timer = 0
                self.transitioning = False
                
            # Clamp alpha value
            self.transition_alpha = max(0, min(255, self.transition_alpha))
        
        # Get audio data for music reactivity
        if pygame.mixer.music.get_busy():
            # Simulate audio sample data - in a real implementation, use pygame.mixer.music.get_volume()
            # and FFT analysis on pygame.mixer.get_raw() to extract audio amplitude/frequency data
            music_volume = pygame.mixer.music.get_volume()
            
            # Shift audio samples
            self.audio_sample.pop(0)
            
            # Add some randomness to the audio data for a more dynamic effect
            # We create a value between 0.1 (quiet) and 1.0 (loud) based on current volume
            base_intensity = music_volume * 0.5  # Base intensity from volume
            beat_intensity = base_intensity + random.uniform(-0.1, 0.3)  # Add some randomness
            
            # Use a sine wave to simulate beats
            beat_pulse = 0.3 * math.sin(self.color_timer / 10) + 0.2
            
            new_sample = max(0.1, min(1.0, base_intensity + beat_intensity + beat_pulse))
            self.audio_sample.append(new_sample)
            
            # Calculate average intensity for the water level
            avg_intensity = sum(self.audio_sample) / len(self.audio_sample)
            self.target_level = 0.2 + avg_intensity * 0.6  # Map to 0.2-0.8 range
        else:
            # If no music is playing, simulate gentle waves
            self.target_level = 0.2 + 0.1 * math.sin(self.color_timer / 30)
        
        # Smoothly adjust current water level
        self.current_level += (self.target_level - self.current_level) * self.level_smooth_factor
        
        # Update liquid floor with music reactivity
        for point in self.liquid_points:
            point['phase'] += point['speed'] * (0.5 + self.current_level)  # Speed affected by music
            
            # Calculate wave height based on music intensity
            wave_height = self.wave_height * (0.5 + self.current_level)
            point['y'] = math.sin(point['phase']) * point['amplitude'] * (0.5 + self.current_level)
        
        # Update droplets
        self.droplet_timer += 1
        if self.droplet_timer > 30 / (1 + self.current_level * 2):  # More frequent droplets with louder music
            self.droplet_timer = 0
            if random.random() < 0.3 + self.current_level * 0.5:  # More likely with louder music
                # Create a droplet at a random x position
                self.droplets.append({
                    'x': random.randint(0, WINDOW_WIDTH),
                    'y': self.liquid_base_y - 20 - random.randint(0, 40),
                    'size': random.randint(2, 6),
                    'speed': random.uniform(0.5, 2.0),
                    'alpha': 255
                })
        
        # Update existing droplets
        for droplet in self.droplets[:]:
            droplet['y'] += droplet['speed']
            
            # When droplet hits water, create splash and remove
            if droplet['y'] >= self.liquid_base_y - (self.liquid_height * self.current_level):
                # Create splash (bubbles)
                for _ in range(3):
                    self.bubbles.append({
                        'x': droplet['x'] + random.uniform(-10, 10),
                        'y': self.liquid_base_y - (self.liquid_height * self.current_level),
                        'size': random.randint(1, 4),
                        'speed': random.uniform(0.2, 1.0),
                        'lifetime': random.randint(20, 60),
                        'alpha': 200
                    })
                self.droplets.remove(droplet)
            elif droplet['y'] > WINDOW_HEIGHT:
                self.droplets.remove(droplet)
        
        # Update bubbles
        for bubble in self.bubbles[:]:
            bubble['y'] -= bubble['speed']
            bubble['lifetime'] -= 1
            bubble['alpha'] = int(bubble['alpha'] * 0.95)
            
            if bubble['lifetime'] <= 0 or bubble['alpha'] < 10:
                self.bubbles.remove(bubble)

    def draw_liquid_floor(self, screen):
        # Calculate the liquid height based on music intensity
        liquid_top = WINDOW_HEIGHT - (self.liquid_height * self.current_level)
        
        # Create an array of points for the polygon
        points = []
        
        # Add top surface points with wave effect
        for i, point in enumerate(self.liquid_points):
            y_pos = liquid_top + point['y']
            points.append((point['x'], y_pos))
            
        # Add bottom corners to complete the polygon
        points.append((WINDOW_WIDTH + 20, WINDOW_HEIGHT + 20))
        points.append((-20, WINDOW_HEIGHT + 20))
        
        # Determine liquid color based on music intensity
        liquid_color = pygame.Color(0)
        hue_base = 220  # Blue base
        hue_range = 140  # Range to shift through as volume increases
        
        # Calculate hue based on intensity - higher volumes shift toward red/purple
        hue = (hue_base - (hue_range * self.current_level)) % 360
        saturation = 80 + int(self.current_level * 20)  # More saturated with volume
        value = 80 + int(self.current_level * 20)  # Brighter with volume
        
        liquid_color.hsva = (hue, saturation, value, 100)
        
        # Draw the liquid as a polygon
        pygame.draw.polygon(screen, liquid_color, points)
        
        # Draw black outline for the top of the water
        for i in range(len(points) - 3):
            pygame.draw.line(screen, (0, 0, 0), points[i], points[i+1], 2)
        
        # Draw highlights on the liquid surface
        highlight_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for i in range(len(self.liquid_points) - 1):
            point1 = (self.liquid_points[i]['x'], liquid_top + self.liquid_points[i]['y'])
            point2 = (self.liquid_points[i+1]['x'], liquid_top + self.liquid_points[i+1]['y'])
            
            # Draw a semi-transparent highlight
            if random.random() < 0.1 + self.current_level * 0.2:  # More highlights with volume
                highlight_alpha = int(100 + self.current_level * 155)  # Brighter with volume
                pygame.draw.line(
                    highlight_surface, 
                    (255, 255, 255, highlight_alpha),  # Semi-transparent white
                    point1, point2, 2
                )
                
        # Add droplets to the highlight surface
        for droplet in self.droplets:
            pygame.draw.circle(
                highlight_surface,
                (255, 255, 255, droplet['alpha']),
                (int(droplet['x']), int(droplet['y'])),
                droplet['size']
            )
            
            # Draw black outline for droplets
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (int(droplet['x']), int(droplet['y'])),
                droplet['size'] + 1,
                1
            )
        
        # Add bubbles to the highlight surface
        for bubble in self.bubbles:
            # Draw bubble interior
            pygame.draw.circle(
                highlight_surface,
                (255, 255, 255, bubble['alpha']),
                (int(bubble['x']), int(bubble['y'])),
                bubble['size']
            )
            
            # Draw black outline for bubbles
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (int(bubble['x']), int(bubble['y'])),
                bubble['size'] + 1,
                1
            )
        
        # Blit the highlight surface to the screen
        screen.blit(highlight_surface, (0, 0))

    def draw_scene(self, screen):
        # Different background based on current scene
        if self.current_scene == 0:
            # Scene 1: RGB gradient background
            for y in range(WINDOW_HEIGHT):
                # Calculate color at this position
                hue = (y / WINDOW_HEIGHT * 360 + self.color_timer) % 360
                color = pygame.Color(0)
                color.hsva = (hue, 90, 90, 100)
                pygame.draw.line(screen, color, (0, y), (WINDOW_WIDTH, y))
                
        elif self.current_scene == 1:
            # Scene 2: Deep blue with particles
            screen.fill((5, 10, 30))
            
            # Draw particles
            for _ in range(50):
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)
                size = random.randint(1, 3)
                brightness = random.randint(100, 255)
                pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
                
        else:
            # Scene 3: Cyberpunk grid
            screen.fill((0, 0, 0))
            
            # Draw grid lines
            grid_spacing = 40
            grid_offset = (self.color_timer // 5) % grid_spacing
            
            # Horizontal lines
            for y in range(-grid_offset, WINDOW_HEIGHT, grid_spacing):
                grid_color = pygame.Color(0)
                grid_color.hsva = ((y + self.color_timer) % 360, 100, 50, 100)
                pygame.draw.line(screen, grid_color, (0, y), (WINDOW_WIDTH, y), 2)
                
            # Vertical lines
            for x in range(-grid_offset, WINDOW_WIDTH, grid_spacing):
                grid_color = pygame.Color(0)
                grid_color.hsva = ((x + self.color_timer) % 360, 100, 50, 100)
                pygame.draw.line(screen, grid_color, (x, 0), (x, WINDOW_HEIGHT), 2)
                
        # Draw the liquid floor in all scenes
        self.draw_liquid_floor(screen)

    def draw_wavy_text(self, screen, text, font, x, y, color):
        # Render each character with its own wave animation
        text_surface = pygame.Surface((font.size(text)[0] + 20, font.size("Tg")[1] * 2), pygame.SRCALPHA)
        x_offset = 0
        
        for i, char in enumerate(text):
            if i >= len(self.title_chars_offset):
                # Ensure we have enough offsets if text is longer than expected
                self.title_chars_offset.append(random.uniform(0, math.pi*2))
                
            # Calculate y offset for this character based on wave
            char_y_offset = math.sin(self.title_chars_offset[i]) * 10
            
            # Render this character
            char_surface = font.render(char, True, color)
            text_surface.blit(char_surface, (x_offset, char_y_offset + font.size("T")[1] // 2))
            
            # Move to next character position
            x_offset += char_surface.get_width()
        
        # Center the entire text at the specified position
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
        
        return text_rect

    def draw(self, screen):
        if not self.show:
            return
            
        # Draw the current scene
        self.draw_scene(screen)
        
        # Draw "Pixel Dash" title with RGB effect and wavy animation
        title_color = pygame.Color(0)
        title_color.hsva = (self.color_timer, 100, 100, 100)
        
        # Draw title with wavy text effect
        title_rect = self.draw_wavy_text(
            screen, 
            "Pixel Dash", 
            self.title_font, 
            WINDOW_WIDTH // 2, 
            WINDOW_HEIGHT // 3,
            title_color
        )
        
        # Draw "Play" button with clean design
        button_color = pygame.Color(0)
        button_color.hsva = ((self.color_timer + 120) % 360, 100, 100, 100)
        
        # Draw button background (darker)
        pygame.draw.rect(screen, (10, 10, 20), self.play_button_rect)
        
        # Draw button border with glow
        for offset in range(10, 0, -2):
            glow_rect = self.play_button_rect.inflate(offset * 2, offset * 2)
            glow_color = pygame.Color(0)
            glow_color.hsva = ((self.color_timer + offset * 5) % 360, 100, 100, 100 - offset * 5)
            pygame.draw.rect(screen, glow_color, glow_rect, 2)
        
        # Draw button main border
        pygame.draw.rect(screen, (0, 255, 255), self.play_button_rect, 3)  # Cyan border
        
        # Draw button text as regular centered text - use smaller size for Pacifico font
        small_pacifico = pygame.font.Font(os.path.join(os.getcwd(), "assets", "fonts", "Pacifico-Regular.ttf"), 60)
        play_text = small_pacifico.render("Play", True, (0, 0, 255))  # Blue text with Pacifico font
        play_text_rect = play_text.get_rect(center=self.play_button_rect.center)
        screen.blit(play_text, play_text_rect)
        
        # Draw Previously Played button (below the Play button) with RGB effects
        # Background and border for the button
        rgb_border_color = pygame.Color(0)
        rgb_border_color.hsva = (self.color_timer, 100, 100, 100)
        
        # Draw button background and RGB-colored border
        pygame.draw.rect(screen, (30, 30, 50), self.prev_played_button_rect)  # Dark background
        pygame.draw.rect(screen, rgb_border_color, self.prev_played_button_rect, 3)  # RGB border
        
        # Draw "Previously Played" text with RGB color
        prev_played_font = pygame.font.Font(None, 40)
        prev_text = "PREVIOUSLY PLAYED"
        
        text_color = pygame.Color(0)
        text_color.hsva = ((self.color_timer + 60) % 360, 100, 100, 100)
        
        # Draw text with bold effect by rendering multiple times with slight offsets
        prev_rendered = prev_played_font.render(prev_text, True, text_color)
        prev_rect = prev_rendered.get_rect(center=self.prev_played_button_rect.center)
        
        # Draw multiple copies with slight offsets for bold effect
        offsets = [(0,0), (1,0), (0,1), (1,1)]
        for dx, dy in offsets:
            screen.blit(prev_rendered, (prev_rect.x + dx, prev_rect.y + dy))
        
        # Draw scene transition overlay if needed
        if self.transitioning:
            # Use a different approach for the overlay
            transition_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            transition_surface.fill((0, 0, 0, self.transition_alpha))
            screen.blit(transition_surface, (0, 0))
            
        # Draw saved games menu if active
        if self.show_saved_games:
            self.draw_saved_games_menu(screen)

    def handle_event(self, event):
        """Handle pygame events for the home screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            mouse_pos = pygame.mouse.get_pos()
            
            # If showing saved games menu
            if self.show_saved_games:
                # Check if back button was clicked
                if self.saved_game_back_rect and self.saved_game_back_rect.collidepoint(mouse_pos):
                    self.show_saved_games = False
                    return False
                
                # Check if a saved game was clicked
                for idx, rect in enumerate(self.saved_game_rects):
                    if rect.collidepoint(mouse_pos) and idx < len(self.saved_games):
                        # Return the saved game data to load
                        return self.saved_games[idx]
                        
                # Clicking elsewhere does nothing
                return False
                
            # Check if Play button was clicked
            if self.play_button_rect.collidepoint(mouse_pos):
                return True  # Start a new game
                
            # Check if Previously Played button was clicked
            if self.prev_played_button_rect.collidepoint(mouse_pos):
                self.show_saved_games = True
                return False
                
        return False

    def draw_saved_games_menu(self, screen):
        """Draw the menu of saved games."""
        # Draw semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Dark semi-transparent background
        screen.blit(overlay, (0, 0))
        
        # Draw title with RGB effect
        title_font = pygame.font.Font(None, 60)
        title_color = pygame.Color(0)
        title_color.hsva = (self.color_timer, 100, 100, 100)
        title_text = title_font.render("SAVED GAMES", True, title_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Reset saved game rects
        self.saved_game_rects = []
        
        # Check if there are any saved games
        if not self.saved_games:
            msg_font = pygame.font.Font(None, 40)
            msg_text = msg_font.render("No saved games found", True, (200, 200, 200))
            msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(msg_text, msg_rect)
        else:
            # Draw saved games list
            game_font = pygame.font.Font(None, 30)
            item_height = 80
            visible_area_height = 400
            
            # Create the view area with RGB border
            view_area = pygame.Rect(WINDOW_WIDTH // 2 - 250, 150, 500, visible_area_height)
            pygame.draw.rect(screen, (40, 40, 60), view_area)
            
            # RGB border for saved games list
            border_color = pygame.Color(0)
            border_color.hsva = ((self.color_timer + 90) % 360, 100, 100, 100)
            pygame.draw.rect(screen, border_color, view_area, 2)
            
            # Calculate maximum scroll
            content_height = len(self.saved_games) * item_height
            self.saved_games_max_scroll = max(0, content_height - visible_area_height)
            
            # Clamp scroll value
            self.saved_games_scroll_y = max(0, min(self.saved_games_scroll_y, self.saved_games_max_scroll))
            
            # Set up clipping for the list area
            screen.set_clip(view_area)
            
            for i, save_data in enumerate(self.saved_games):
                # Calculate position with scroll
                y_pos = 150 + i * item_height - self.saved_games_scroll_y
                
                # Skip if outside visible area
                if y_pos + item_height < 150 or y_pos > 150 + visible_area_height:
                    continue
                    
                # Create item rect
                item_rect = pygame.Rect(WINDOW_WIDTH // 2 - 240, y_pos, 480, item_height - 5)
                self.saved_game_rects.append(item_rect)
                
                # Draw item background with RGB-tinged color
                item_bg_color = pygame.Color(60, 60, 90)
                # Slightly tint the color with rgb effect
                item_color = pygame.Color(0)
                item_color.hsva = ((self.color_timer + i * 30) % 360, 40, 70, 100)
                item_bg = (
                    item_bg_color.r + (item_color.r - item_bg_color.r) // 4,
                    item_bg_color.g + (item_color.g - item_bg_color.g) // 4,
                    item_bg_color.b + (item_color.b - item_bg_color.b) // 4
                )
                pygame.draw.rect(screen, item_bg, item_rect)
                
                # Draw RGB border for each item
                item_border_color = pygame.Color(0)
                item_border_color.hsva = ((self.color_timer + i * 20) % 360, 100, 100, 100)
                pygame.draw.rect(screen, item_border_color, item_rect, 1)
                
                # Format timestamp
                try:
                    timestamp = save_data.get("timestamp", "Unknown")
                    if timestamp != "Unknown":
                        from datetime import datetime
                        dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                        formatted_time = dt.strftime("%b %d, %Y - %I:%M %p")
                    else:
                        formatted_time = "Unknown date"
                except:
                    formatted_time = "Unknown date"
                
                # Draw save info - timestamp with lighter color
                time_text = game_font.render(formatted_time, True, (220, 220, 255))
                time_rect = time_text.get_rect(topleft=(item_rect.x + 15, item_rect.y + 10))
                screen.blit(time_text, time_rect)
                
                # Draw details - score and title with RGB-tinged color
                score = save_data.get("score", 0)
                title = save_data.get("title", "Noob")
                play_time = save_data.get("play_time", 0)
                
                # Format time as minutes:seconds
                minutes = play_time // 60
                seconds = play_time % 60
                time_text = f"{minutes}m {seconds}s"
                
                # Calculate RGB color for details
                details_color = pygame.Color(0)
                details_color.hsva = ((self.color_timer + 140) % 360, 40, 100, 100)
                
                details_text = game_font.render(f"Score: {score} | Title: {title} | Time: {time_text}", 
                                            True, (255, 255, 200))
                details_rect = details_text.get_rect(topleft=(item_rect.x + 15, time_rect.bottom + 10))
                screen.blit(details_text, details_rect)
            
            # Reset clipping
            screen.set_clip(None)
            
        # Draw back button with RGB effects
        back_button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 80, 200, 50)
        self.saved_game_back_rect = back_button_rect
        
        # RGB border for back button
        back_border_color = pygame.Color(0)
        back_border_color.hsva = ((self.color_timer + 180) % 360, 100, 100, 100)
        
        pygame.draw.rect(screen, (150, 50, 50), back_button_rect)  # Red button
        pygame.draw.rect(screen, back_border_color, back_button_rect, 2)  # RGB border
        
        back_font = pygame.font.Font(None, 40)
        back_text = back_font.render("BACK", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        
    def load_saved_games_list(self):
        """Load the list of saved games."""
        import os
        import json
        
        self.saved_games = []
        
        # Check if saves directory exists
        if not os.path.exists("saves"):
            return
            
        # List all save files
        for filename in os.listdir("saves"):
            if filename.endswith(".json") and filename.startswith("save_"):
                try:
                    with open(os.path.join("saves", filename), "r") as f:
                        save_data = json.load(f)
                        self.saved_games.append(save_data)
                except Exception as e:
                    print(f"Error loading save file {filename}: {str(e)}")
                    
        # Sort saved games by timestamp (newest first)
        self.saved_games.sort(key=lambda x: x.get("timestamp", ""), reverse=True) 