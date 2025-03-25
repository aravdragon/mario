import pygame
import sys
import os
from src.game import Game

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Create game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("RGB GlowingBlock Adventure")

# Create game instance
game = Game(screen)

# Game loop
clock = pygame.time.Clock()

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_events(event)
        
        # Update game state
        game.update()
        
        # Draw everything
        screen.fill((0, 0, 0))  # Fill screen with black
        game.draw()
        pygame.display.flip()
        
        # Control game speed
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 