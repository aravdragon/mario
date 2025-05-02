import pygame
import sys
import os
import traceback
from src.game import Game
from src.home_screen import HomeScreen
from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("RGB GlowingBlock Adventure")
    clock = pygame.time.Clock()
    
    # Create home screen and game
    home_screen = HomeScreen(screen)
    game = None
    running = True
    game_started = False

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif not game_started:
                    # Handle home screen events
                    result = home_screen.handle_event(event)
                    if result is True:
                        # Start new game if result is True
                        game_started = True
                        game = Game(screen)  # Initialize game when start is clicked
                    elif isinstance(result, dict):
                        # Load saved game if result is a save data dictionary
                        game_started = True
                        game = Game(screen)
                        load_saved_game(game, result)
                else:
                    # Update running based on game events
                    running = game.handle_event(event)
                    
                    # Check if we need to return to home screen
                    if game.return_to_home:
                        game_started = False
                        home_screen.show = True
                        home_screen = HomeScreen(screen)  # Create fresh home screen
                        game.return_to_home = False

            if not game_started:
                # Update and draw home screen
                home_screen.update()
                home_screen.draw(screen)
            else:
                # Update and draw game
                game.update()
                game.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()
    
    pygame.quit()

def load_saved_game(game, save_data):
    """Load a saved game into the game instance."""
    print(f"Loading saved game with score: {save_data.get('score', 0)} and title: {save_data.get('title', 'Noob')}")
    
    # Load basic stats
    game.score = save_data.get("score", 0)
    game.play_time = save_data.get("play_time", 0)
    game.start_time = pygame.time.get_ticks() / 1000 - game.play_time  # Adjust start time to maintain play time
    
    # Load unlocked skins
    unlocked_skins = save_data.get("unlocked_skins", [0])  # Default to just the first skin
    for skin_idx in unlocked_skins:
        if 0 <= skin_idx < len(game.skins):
            game.skins[skin_idx]["unlocked"] = True
    
    # Set current skin
    current_skin = save_data.get("current_skin", 0)
    if 0 <= current_skin < len(game.skins) and game.skins[current_skin]["unlocked"]:
        game.current_skin = current_skin
    
    # Show welcome back message
    game.show_purchase_message = True
    game.purchase_message = f"Welcome back, {save_data.get('title', 'Player')}!"
    game.message_timer = 0

if __name__ == "__main__":
    main() 