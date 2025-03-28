import pygame
import math
import random
from .constants import *

class Jetpack:
    def __init__(self):
        self.fuel = 100
        self.max_fuel = 100
        self.purchased = False
        self.permanent = False
        self.total_time = 18000  # 5 minutes at 60 FPS (60 * 60 * 5)
        self.time_remaining = 18000
        self.active = False
        self.fuel_consumption_rate = 0.2  # Reduced fuel consumption
        self.fuel_recovery_rate = 0.4  # Increased fuel recovery
        self.vertical_thrust = 1.2  # Increased vertical thrust
        self.horizontal_thrust = 0.5
        self.particles = []
        self.fly_button_rect = pygame.Rect(10, 60, 80, 40)
        self.color_timer = 0

    def update(self):
        if self.purchased and self.active:
            if self.time_remaining > 0:
                self.time_remaining -= 1
                if self.time_remaining <= 0:
                    self.purchased = False
                    self.permanent = False
            
            if not self.permanent:
                self.fuel = max(0, self.fuel - 0.5)  # Consume fuel
            elif self.fuel < self.max_fuel:
                self.fuel = min(self.max_fuel, self.fuel + 0.25)  # Recover fuel when not in use

        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
        # Generate new particles when active
        if self.active and (self.permanent or self.fuel > 0):
            self.particles.append({
                'x': random.randint(-10, 10),
                'y': random.randint(5, 15),
                'life': 20
            })

    def activate(self, button_pressed):
        if self.purchased and self.time_remaining > 0:
            self.active = button_pressed and (self.permanent or self.fuel > 0)
        else:
            self.active = False

    def is_active(self):
        return self.active and self.time_remaining > 0

    def get_time_remaining(self):
        minutes = self.time_remaining // 3600
        seconds = (self.time_remaining % 3600) // 60
        return f"{minutes}:{seconds:02d}"

    def get_thrust(self, keys):
        if not self.active or (not self.permanent and self.fuel <= 0):
            return 0, 0
            
        # Calculate vertical thrust
        vertical = -self.vertical_thrust if keys[pygame.K_f] else 0
        
        # Calculate horizontal thrust based on A/D keys
        horizontal = 0
        if keys[pygame.K_a]:
            horizontal = -self.horizontal_thrust
        elif keys[pygame.K_d]:
            horizontal = self.horizontal_thrust
            
        return horizontal, vertical

    def draw(self, screen, rect):
        if not self.purchased:
            # Draw "BUY JET" text
            font = pygame.font.Font(None, 36)
            text = font.render("BUY JET", True, (255, 20, 147))
            screen.blit(text, (rect.x, rect.y))
        else:
            # Draw "FLY (F)" text with RGB effect
            font = pygame.font.Font(None, 36)
            color = pygame.Color(0)
            color.hsva = (self.color_timer, 100, 100, 100)
            text = font.render("FLY (F)", True, color)
            screen.blit(text, (rect.x, rect.y))
            
        # Only draw fuel gauge if purchased and not permanent
        if self.purchased and not self.permanent:
            gauge_width = 100
            gauge_height = 10
            gauge_x = 10
            gauge_y = 60
            
            # Draw background
            pygame.draw.rect(screen, (50, 50, 50), (gauge_x, gauge_y, gauge_width, gauge_height))
            
            # Draw fuel level with RGB effect
            fuel_width = int((self.fuel / self.max_fuel) * gauge_width)
            if fuel_width > 0:
                color = pygame.Color(0)
                color.hsva = ((self.color_timer + 180) % 360, 100, 100, 100)
                pygame.draw.rect(screen, color, (gauge_x, gauge_y, fuel_width, gauge_height))
                
        # Draw jetpack flames
        if self.active and (self.permanent or self.fuel > 0):
            for particle in self.particles:
                pos_x = rect.centerx + particle['x']
                pos_y = rect.bottom + particle['y']
                size = int((particle['life'] / 20) * 6)
                
                # RGB flame effect
                flame_color = pygame.Color(0)
                flame_color.hsva = ((self.color_timer + particle['life'] * 5) % 360, 100, 100, 100)
                pygame.draw.circle(screen, flame_color, (pos_x, pos_y), size)
            
            self.color_timer = (self.color_timer + 2) % 360

    def can_fly(self):
        return self.purchased and (self.permanent or self.fuel > 0)

    def purchase(self):
        self.purchased = True
        self.permanent = True  # Make jetpack permanent when purchased
        self.fuel = self.max_fuel
        return True 