import pygame
from .constants import *

class Shop:
    def __init__(self, game):
        self.game = game
        self.selected_item = 0
        self.font = pygame.font.Font(None, 36)
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(SHOP_ITEMS)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(SHOP_ITEMS)
            elif event.key == pygame.K_RETURN:
                self.purchase_item()
                
    def purchase_item(self):
        item = SHOP_ITEMS[self.selected_item]
        if self.game.score >= item["price"]:
            self.game.score -= item["price"]
            effect = item["effect"]
            if effect in self.game.player.powerups:
                self.game.player.powerups[effect] = True
                
    def draw(self, screen):
        # Draw semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Draw shop title
        title = self.font.render("SHOP", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - 50, 50))
        
        # Draw current coins
        coins_text = self.font.render(f"Coins: {self.game.score}", True, YELLOW)
        screen.blit(coins_text, (WINDOW_WIDTH//2 - 70, 100))
        
        # Draw items
        for i, item in enumerate(SHOP_ITEMS):
            color = GREEN if i == self.selected_item else WHITE
            text = f"{item['name']} - {item['price']} coins"
            if item["effect"] in self.game.player.powerups and self.game.player.powerups[item["effect"]]:
                text += " (Active)"
            item_text = self.font.render(text, True, color)
            screen.blit(item_text, (WINDOW_WIDTH//2 - 100, 150 + i * 50))
            
        # Draw instructions
        instructions = self.font.render("Use UP/DOWN to select, ENTER to buy, ESC to exit", True, WHITE)
        screen.blit(instructions, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT - 50)) 