import pygame
from .constants import *
import time

class Shop:
    def __init__(self, game):
        self.game = game
        self.show = False
        self.items = [
            {"name": "Jetpack", "cost": 50, "description": "Fly for 5 minutes! Press F to activate"},
            {"name": "Rainbow Trail", "cost": 30, "description": "Leave a rainbow trail behind you"},
            {"name": "Burger", "cost": 20, "description": "Double jump power! Press SPACE twice"}
        ]
        self.selected_item = None
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.powerup_timers = {}
        self.effects = {
            "burger": self.apply_burger,
            "jetpack": self.apply_jetpack,
            "speed_boost": self.apply_speed_boost,
            "shield": self.apply_shield,
            "magnet": self.apply_magnet,
            "trail": self.apply_trail
        }
        self.item_rects = []
        self.magnet_pending = False
        
    def apply_burger(self):
        if self.game.score >= 5:
            self.game.score -= 5
            self.game.player.burger.active = True
            self.game.player.can_double_jump = True
            self.powerup_timers["burger"] = time.time() + 60  # 1 minute
            self.game.show_purchase_message = True
            self.game.purchase_message = "Burger activated! Double jump for 1 minute"
            return True
        return False
        
    def apply_jetpack(self):
        if self.game.score >= 10:
            self.game.score -= 10
            self.game.player.jetpack.purchased = True
            self.game.player.jetpack.fuel = 100  # Full fuel
            self.game.player.jetpack.permanent = True  # Make jetpack permanent
            self.game.show_purchase_message = True
            self.game.purchase_message = "Jetpack purchased! Press F to fly (permanent)"
            return True
        return False
        
    def apply_speed_boost(self):
        if self.game.score >= 15:
            self.game.score -= 15
            self.game.player.powerups["speed_boost"] = True
            self.powerup_timers["speed_boost"] = time.time() + 1200  # 20 minutes
            self.game.show_purchase_message = True
            self.game.purchase_message = "Speed Boost activated! 2x speed for 20 minutes"
            return True
        return False
        
    def apply_shield(self):
        if self.game.score >= 20:
            self.game.score -= 20
            self.game.player.shield_active = True
            self.powerup_timers["shield"] = time.time() + 30  # 30 seconds
            self.game.show_purchase_message = True
            self.game.purchase_message = "Shield activated! Invincible for 30 seconds"
            return True
        return False
        
    def apply_magnet(self):
        if self.game.score >= 25:
            self.game.score -= 25
            self.game.show_purchase_message = True
            self.game.purchase_message = "Magnet purchased! Will activate for 20 seconds when shop closes."
            self.game.message_timer = 180
            self.magnet_pending = True
        
    def apply_trail(self):
        if self.game.score >= 30:
            self.game.score -= 30
            self.game.player.powerups["trail"] = True
            self.game.show_purchase_message = True
            self.game.purchase_message = "Rainbow Trail activated! Permanent effect"
            return True
        return False
        
    def update(self):
        current_time = time.time()
        
        # Update powerup timers
        for powerup, end_time in self.powerup_timers.items():
            if end_time > 0 and current_time > end_time:
                if powerup == "burger":
                    self.game.player.burger.active = False
                    self.game.player.can_double_jump = False
                elif powerup == "speed_boost":
                    self.game.player.powerups["speed_boost"] = False
                elif powerup == "shield":
                    self.game.player.shield_active = False
                elif powerup == "magnet":
                    self.game.player.powerups["magnet"] = False
                self.powerup_timers[powerup] = 0
        
        # Activate magnet when shop closes
        if not self.game.show_shop and self.magnet_pending:
            self.magnet_pending = False
            self.game.player.powerups["magnet"] = True
            pygame.time.set_timer(pygame.USEREVENT + 1, 20000)  # 20 seconds timer
        
    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check item clicks
                for i, rect in enumerate(self.item_rects):
                    if rect.collidepoint(mouse_pos):
                        item = self.items[i]
                        if item["name"] == "Jetpack":
                            self.apply_jetpack()
                        elif item["name"] == "Rainbow Trail":
                            self.apply_trail()
                        elif item["name"] == "Burger":
                            self.apply_burger()
        
    def draw(self, screen):
        if not self.show:
            return
            
        # Fill screen with white
        screen.fill((255, 255, 255))
        
        # Draw shop title with RGB effect
        title_color = pygame.Color(0)
        title_color.hsva = (self.game.background_color, 100, 100, 100)
        title = self.font.render("SHOP", True, title_color)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        
        # Draw title outline for better visibility
        for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
            outline_title = self.font.render("SHOP", True, (0, 0, 0))
            screen.blit(outline_title, (title_rect.x + dx, title_rect.y + dy))
        screen.blit(title, title_rect)
        
        # Clear item rects
        self.item_rects = []
        
        # Shop items with prices and effects
        items = [
            {"name": "Burger", "price": 5, "effect": "burger", 
             "description": "Speed boost + double jump for 1 minute"},
            {"name": "Jetpack", "price": 10, "effect": "jetpack",
             "description": "Permanent flying ability (Press F to fly)"},
            {"name": "Speed Boost", "price": 15, "effect": "speed_boost",
             "description": "2x speed for 20 minutes"},
            {"name": "Shield", "price": 20, "effect": "shield",
             "description": "Invincibility for 30 seconds"},
            {"name": "Magnet", "price": 25, "effect": "magnet",
             "description": "Attracts nearby coins for 10 seconds"},
            {"name": "Rainbow Trail", "price": 30, "effect": "trail",
             "description": "Permanent rainbow trail effect"}
        ]
        
        # Draw shop items
        for i, item in enumerate(items):
            # Calculate position
            x = WINDOW_WIDTH // 2 - 250
            y = 120 + i * 90
            
            # Create item rectangle
            item_rect = pygame.Rect(x, y, 500, 80)
            self.item_rects.append(item_rect)
            
            # Draw item background with light gray
            pygame.draw.rect(screen, (240, 240, 240), item_rect)
            pygame.draw.rect(screen, (200, 200, 200), item_rect, 2)
            
            # Calculate RGB color for text
            text_color = pygame.Color(0)
            text_color.hsva = ((self.game.background_color + i * 60) % 360, 100, 100, 100)
            
            # Draw item name with RGB effect
            name_text = self.font.render(item["name"], True, text_color)
            name_rect = name_text.get_rect(x=x + 10, y=y + 5)
            
            # Draw name outline
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                outline_name = self.font.render(item["name"], True, (0, 0, 0))
                screen.blit(outline_name, (name_rect.x + dx, name_rect.y + dy))
            screen.blit(name_text, name_rect)
            
            # Draw price
            price_text = self.font.render(f"{item['price']} coins", True, text_color)
            price_rect = price_text.get_rect(x=x + 400, y=y + 5)
            
            # Draw price outline
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                outline_price = self.font.render(f"{item['price']} coins", True, (0, 0, 0))
                screen.blit(outline_price, (price_rect.x + dx, price_rect.y + dy))
            screen.blit(price_text, price_rect)
            
            # Draw description
            desc_text = self.small_font.render(item["description"], True, (100, 100, 100))
            screen.blit(desc_text, (x + 10, y + 45))
            
            # Show if item is active/purchased
            if (item["effect"] == "jetpack" and self.game.player.jetpack.purchased) or \
               (item["effect"] == "trail" and self.game.player.powerups.get("trail", False)):
                status_text = self.small_font.render("PURCHASED", True, (0, 150, 0))
                screen.blit(status_text, (x + 400, y + 45))
            elif item["effect"] in self.powerup_timers and self.powerup_timers[item["effect"]] > time.time():
                remaining = int(self.powerup_timers[item["effect"]] - time.time())
                status_text = self.small_font.render(f"ACTIVE ({remaining}s)", True, (0, 100, 200))
                screen.blit(status_text, (x + 400, y + 45))
        
        # Draw exit button with RGB effect
        exit_color = pygame.Color(0)
        exit_color.hsva = ((self.game.background_color + 180) % 360, 100, 100, 100)
        exit_rect = pygame.Rect(WINDOW_WIDTH - 120, WINDOW_HEIGHT - 50, 100, 40)
        
        # Draw exit button background
        pygame.draw.rect(screen, (240, 240, 240), exit_rect)
        pygame.draw.rect(screen, (200, 200, 200), exit_rect, 2)
        
        # Draw exit text with RGB effect
        exit_text = self.font.render("EXIT", True, exit_color)
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        
        # Draw exit text outline
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            outline_exit = self.font.render("EXIT", True, (0, 0, 0))
            screen.blit(outline_exit, (exit_text_rect.x + dx, exit_text_rect.y + dy))
        screen.blit(exit_text, exit_text_rect)
        
        # Draw current coins
        coins_color = pygame.Color(0)
        coins_color.hsva = ((self.game.background_color + 240) % 360, 100, 100, 100)
        coins_text = self.font.render(f"Your Coins: {self.game.score}", True, coins_color)
        coins_rect = coins_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        
        # Draw coins text outline
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            outline_coins = self.font.render(f"Your Coins: {self.game.score}", True, (0, 0, 0))
            screen.blit(outline_coins, (coins_rect.x + dx, coins_rect.y + dy))
        screen.blit(coins_text, coins_rect)

    def handle_event(self, event):
        if event.type == pygame.USEREVENT + 1:
            self.game.player.powerups["magnet"] = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Stop timer 