import pygame
import math

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.gold_color = (255, 215, 0)  # Bright gold
        self.highlight_color = (255, 235, 100)  # Light gold
        self.shadow_color = (200, 150, 0)  # Dark gold
        self.animation_offset = 0
        self.collected = False
        self.velocity_x = 0
        self.velocity_y = 0
        self.attracted = False
        self.attraction_speed = 0.3  # Base attraction speed multiplier
        
    def update(self, player):
        if self.collected:
            return False
            
        # Handle magnet attraction
        if player.magnet_active:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If within magnet radius, move towards player
            if distance < player.magnet_radius:
                self.attracted = True
                
                # Calculate normalized direction vector
                if distance > 0:  # Avoid division by zero
                    # Speed increases as coin gets closer to player (inverse relationship)
                    # Closer coins move faster than farther ones
                    proximity_factor = (player.magnet_radius - distance) / player.magnet_radius
                    speed = player.magnet_strength * (1 + proximity_factor * 5) * self.attraction_speed
                    
                    # Accelerate attraction over time
                    self.attraction_speed += 0.02
                    
                    # Calculate velocity with acceleration
                    self.velocity_x = (dx / distance) * speed
                    self.velocity_y = (dy / distance) * speed
                    
                    # Apply velocity
                    self.rect.x += int(self.velocity_x)
                    self.rect.y += int(self.velocity_y)
                    
                    # Check if coin touched player after moving
                    if self.collides_with(player):
                        self.collected = True
                        player.game.add_coins(1)
                        return True
                    
                    # If very close to player but not touching, accelerate faster
                    if distance < 50:
                        self.attraction_speed = 1.0
                        
                return False
        
        # Reset attraction factors if not being attracted
        if not self.attracted:
            self.attraction_speed = 0.3
            
        return False
        
    def collides_with(self, player):
        return self.rect.colliderect(player.rect)
        
    def draw(self, screen, camera_offset):
        if self.collected:
            return
            
        # Add a simple bobbing animation (only if not attracted)
        if not self.attracted:
            self.animation_offset = (self.animation_offset + 0.1) % (2 * 3.14159)
            y_offset = math.sin(self.animation_offset) * 3
        else:
            # For attracted coins, create a spinning effect by modifying the animation
            self.animation_offset = (self.animation_offset + 0.3) % (2 * 3.14159)
            y_offset = math.sin(self.animation_offset) * 2
        
        # Calculate screen position with camera offset
        center_x = self.rect.centerx - camera_offset[0]
        center_y = self.rect.centery - camera_offset[1] + y_offset
        
        # Create draw rect for the coin
        draw_rect = pygame.Rect(
            center_x - self.rect.width // 2,
            center_y - self.rect.height // 2,
            self.rect.width,
            self.rect.height
        )
        
        # Draw main coin circle
        pygame.draw.circle(screen, self.gold_color, (center_x, center_y), self.rect.width // 2)
        
        # Draw highlight (top-left arc)
        pygame.draw.arc(screen, self.highlight_color, draw_rect, 
                       math.pi/4, 5*math.pi/4, 2)
        
        # Draw shadow (bottom-right arc)
        pygame.draw.arc(screen, self.shadow_color, draw_rect, 
                       5*math.pi/4, math.pi/4, 2)
        
        # Draw dollar sign
        font = pygame.font.Font(None, draw_rect.height - 4)
        text = font.render("$", True, self.shadow_color)
        text_rect = text.get_rect(center=(center_x, center_y))
        screen.blit(text, text_rect) 