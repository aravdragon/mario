import pygame
import math
from .constants import *

class Burger:
    def __init__(self):
        self.active = False
        self.eaten = False
        self.effect_timer = 0
        self.max_effect_time = 3600  # 60 seconds at 60 FPS
        self.eat_button_rect = pygame.Rect(10, 110, 80, 40)  # Position for Eat button
        
    def draw(self, screen, item_rect=None):
        if not self.active:
            return
            
        if item_rect:
            # Draw burger icon in the bottom bar
            self.draw_burger_icon(screen, item_rect)
            
        # Draw Eat button if not eaten
        if not self.eaten:
            self.draw_eat_button(screen)
            
        # Draw effect timer if eaten
        if self.eaten and self.effect_timer > 0:
            self.draw_timer(screen)
            
    def draw_burger_icon(self, screen, rect):
        # Draw bun (top)
        pygame.draw.ellipse(screen, (255, 198, 115),  # Light brown
                          (rect.x + 5, rect.y + 5, rect.width - 10, rect.height//3))
        
        # Draw lettuce
        pygame.draw.ellipse(screen, (50, 205, 50),  # Green
                          (rect.x + 3, rect.y + rect.height//3, rect.width - 6, rect.height//4))
        
        # Draw meat patty
        pygame.draw.ellipse(screen, (139, 69, 19),  # Brown
                          (rect.x + 3, rect.y + rect.height//2, rect.width - 6, rect.height//4))
        
        # Draw cheese
        pygame.draw.ellipse(screen, (255, 215, 0),  # Gold
                          (rect.x + 3, rect.y + rect.height//2 + 5, rect.width - 6, rect.height//6))
        
        # Draw bun (bottom)
        pygame.draw.ellipse(screen, (255, 198, 115),  # Light brown
                          (rect.x + 5, rect.y + rect.height - rect.height//3, rect.width - 10, rect.height//3))
        
    def draw_eat_button(self, screen):
        button_color = (50, 50, 50)
        pygame.draw.rect(screen, button_color, self.eat_button_rect)
        
        # Draw text
        font = pygame.font.Font(None, 36)
        text = font.render("EAT", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.eat_button_rect.center)
        screen.blit(text, text_rect)
        
    def draw_timer(self, screen):
        # Draw timer bar
        bar_rect = pygame.Rect(100, 110, 100, 20)
        pygame.draw.rect(screen, (50, 50, 50), bar_rect)
        
        # Draw remaining time
        time_width = int((self.effect_timer / self.max_effect_time) * bar_rect.width)
        time_rect = pygame.Rect(bar_rect.x, bar_rect.y, time_width, bar_rect.height)
        pygame.draw.rect(screen, (0, 255, 0), time_rect)
        
    def update(self):
        if self.eaten and self.effect_timer > 0:
            self.effect_timer -= 1
            if self.effect_timer <= 0:
                self.eaten = False
                
    def eat(self):
        if self.active and not self.eaten:
            self.eaten = True
            self.effect_timer = self.max_effect_time
            return True
        return False
        
    def is_active(self):
        return self.eaten and self.effect_timer > 0 