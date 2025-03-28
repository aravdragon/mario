import pygame
import sys
import os
import traceback
from src.game import Game
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("RGB GlowingBlock Adventure")
    clock = pygame.time.Clock()
    game = Game(screen)
    running = True

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    # Update running based on game events
                    running = game.handle_event(event)

            game.update()
            game.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()
    
    pygame.quit()

if __name__ == "__main__":
    main() 