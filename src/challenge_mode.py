import pygame
import random
import json
import os
from .constants import *

class ChallengeMode:
    def __init__(self, game):
        self.game = game
        self.challenge_data_path = os.path.join("saves", "challenge_progress.json")
        self.active_challenge = None
        self.challenge_time = 0
        self.objective_completed = False
        self.challenge_result = None  # "success", "failure", or None
        self.completed_challenges = {}  # Track completed challenges
        
        # Challenge configuration
        self.challenges = {
            # Easy challenges
            "time_trial_1": {
                "name": "Time Trial I",
                "description": "Reach 1000px distance in 60 seconds",
                "difficulty": "Easy",
                "type": "time_trial",
                "target_distance": 1000,
                "time_limit": 60 * FPS,
                "reward": 25,
                "unlocked": True
            },
            "coin_collector_1": {
                "name": "Coin Collector I",
                "description": "Collect 30 coins without falling",
                "difficulty": "Easy",
                "type": "coin_collector",
                "target_coins": 30,
                "reward": 20,
                "unlocked": True
            },
            "platform_master_1": {
                "name": "Platform Master I",
                "description": "Survive 20 jumps on shrinking platforms",
                "difficulty": "Easy",
                "type": "platform_master",
                "target_jumps": 20,
                "reward": 15,
                "unlocked": True
            },
            
            # Medium challenges
            "time_trial_2": {
                "name": "Time Trial II",
                "description": "Reach 2000px distance in 90 seconds",
                "difficulty": "Medium",
                "type": "time_trial",
                "target_distance": 2000,
                "time_limit": 90 * FPS,
                "reward": 50,
                "unlocked": False,
                "required_challenges": ["time_trial_1"]
            },
            "coin_collector_2": {
                "name": "Coin Collector II",
                "description": "Collect 60 coins without falling",
                "difficulty": "Medium",
                "type": "coin_collector",
                "target_coins": 60,
                "reward": 40,
                "unlocked": False,
                "required_challenges": ["coin_collector_1"]
            },
            "platform_master_2": {
                "name": "Platform Master II",
                "description": "Survive 40 jumps on fast-shrinking platforms",
                "difficulty": "Medium",
                "type": "platform_master",
                "target_jumps": 40,
                "platform_shrink_rate": 0.1,  # Faster shrink rate
                "reward": 35,
                "unlocked": False,
                "required_challenges": ["platform_master_1"]
            },
            "speed_run_1": {
                "name": "Speed Run I",
                "description": "Reach 1500px distance with limited jumps (20)",
                "difficulty": "Medium",
                "type": "speed_run",
                "target_distance": 1500,
                "max_jumps": 20,
                "reward": 45,
                "unlocked": False,
                "required_challenges": ["time_trial_1", "platform_master_1"]
            },
            
            # Hard challenges
            "time_trial_3": {
                "name": "Time Trial III",
                "description": "Reach 3000px distance in 100 seconds",
                "difficulty": "Hard",
                "type": "time_trial",
                "target_distance": 3000,
                "time_limit": 100 * FPS,
                "reward": 75,
                "unlocked": False,
                "required_challenges": ["time_trial_2"]
            },
            "coin_collector_3": {
                "name": "Coin Collector III",
                "description": "Collect 100 coins without falling",
                "difficulty": "Hard",
                "type": "coin_collector",
                "target_coins": 100,
                "reward": 65,
                "unlocked": False,
                "required_challenges": ["coin_collector_2"]
            },
            "platform_master_3": {
                "name": "Platform Master III",
                "description": "Survive 60 jumps on extremely fast-shrinking platforms",
                "difficulty": "Hard",
                "type": "platform_master",
                "target_jumps": 60,
                "platform_shrink_rate": 0.15,  # Even faster shrink rate
                "reward": 60,
                "unlocked": False,
                "required_challenges": ["platform_master_2"]
            },
            "speed_run_2": {
                "name": "Speed Run II",
                "description": "Reach 2500px distance with limited jumps (25)",
                "difficulty": "Hard",
                "type": "speed_run",
                "target_distance": 2500,
                "max_jumps": 25,
                "reward": 70,
                "unlocked": False,
                "required_challenges": ["speed_run_1"]
            },
            "ultimate_challenge": {
                "name": "Ultimate Challenge",
                "description": "Reach 3000px distance, collect 50 coins, with limited jumps (30)",
                "difficulty": "Hard",
                "type": "ultimate",
                "target_distance": 3000,
                "target_coins": 50,
                "max_jumps": 30,
                "reward": 100,
                "unlocked": False,
                "required_challenges": ["time_trial_3", "coin_collector_3", "platform_master_3", "speed_run_2"]
            }
        }
        
        # Ensure saves directory exists
        os.makedirs("saves", exist_ok=True)
        
        # Load progress
        self.load_progress()
    
    def load_progress(self):
        """Load challenge progress from file"""
        if os.path.exists(self.challenge_data_path):
            try:
                with open(self.challenge_data_path, "r") as f:
                    self.completed_challenges = json.load(f)
                    
                    # Update challenge unlocks based on progress
                    self.update_challenge_unlocks()
            except (json.JSONDecodeError, FileNotFoundError):
                self.completed_challenges = {}
        else:
            self.completed_challenges = {}
    
    def save_progress(self):
        """Save challenge progress to file"""
        with open(self.challenge_data_path, "w") as f:
            json.dump(self.completed_challenges, f)
    
    def update_challenge_unlocks(self):
        """Update which challenges are unlocked based on completed challenges"""
        for challenge_id, challenge in self.challenges.items():
            if challenge.get("unlocked", False):
                continue  # Skip already unlocked challenges
                
            # Check if this challenge has requirements
            required_challenges = challenge.get("required_challenges", [])
            if not required_challenges:
                continue  # No requirements, skip
                
            # Check if all required challenges are completed
            all_completed = True
            for req_id in required_challenges:
                if req_id not in self.completed_challenges:
                    all_completed = False
                    break
            
            # Unlock if all requirements are met
            if all_completed:
                self.challenges[challenge_id]["unlocked"] = True
    
    def start_challenge(self, challenge_id):
        """Start a specific challenge"""
        if challenge_id in self.challenges and self.challenges[challenge_id]["unlocked"]:
            self.active_challenge = challenge_id
            self.challenge_time = 0
            self.objective_completed = False
            self.challenge_result = None
            
            # Reset game state but keep player's coins
            player_coins = self.game.score
            self.game.reset_game()
            self.game.score = player_coins
            
            # Apply challenge-specific settings
            challenge = self.challenges[self.active_challenge]
            
            # Apply platform shrink rate if specified
            if "platform_shrink_rate" in challenge:
                for platform in self.game.platforms:
                    platform.shrink_rate = challenge["platform_shrink_rate"]
            
            return True
        
        return False
    
    def cancel_challenge(self):
        """Cancel the current challenge"""
        self.active_challenge = None
        self.challenge_time = 0
        self.objective_completed = False
        self.challenge_result = None
        
        # Reset game to normal state
        player_coins = self.game.score
        self.game.reset_game()
        self.game.score = player_coins
    
    def check_challenge_progress(self):
        """Check if the current challenge is completed or failed"""
        if not self.active_challenge:
            return
        
        challenge = self.challenges[self.active_challenge]
        
        # Increment challenge time
        self.challenge_time += 1
        
        # Check different challenge types
        if challenge["type"] == "time_trial":
            # Time trial: reach target distance within time limit
            if self.game.player.rect.x >= challenge["target_distance"]:
                self.objective_completed = True
                self.challenge_result = "success"
            elif self.challenge_time >= challenge["time_limit"]:
                self.challenge_result = "failure"
            
        elif challenge["type"] == "coin_collector":
            # Coin collector: collect target number of coins without falling
            coins_collected = len([coin for coin in self.game.coins if coin.collected])
            if coins_collected >= challenge["target_coins"]:
                self.objective_completed = True
                self.challenge_result = "success"
            elif self.game.game_over:
                self.challenge_result = "failure"
            
        elif challenge["type"] == "platform_master":
            # Platform master: survive target number of jumps
            if self.game.jumps >= challenge["target_jumps"]:
                self.objective_completed = True
                self.challenge_result = "success"
            elif self.game.game_over:
                self.challenge_result = "failure"
            
        elif challenge["type"] == "speed_run":
            # Speed run: reach target distance with limited jumps
            if self.game.player.rect.x >= challenge["target_distance"]:
                self.objective_completed = True
                self.challenge_result = "success"
            elif self.game.jumps >= challenge["max_jumps"]:
                self.challenge_result = "failure"
            elif self.game.game_over:
                self.challenge_result = "failure"
            
        elif challenge["type"] == "ultimate":
            # Ultimate: multiple objectives
            coins_collected = len([coin for coin in self.game.coins if coin.collected])
            if (self.game.player.rect.x >= challenge["target_distance"] and 
                coins_collected >= challenge["target_coins"]):
                self.objective_completed = True
                self.challenge_result = "success"
            elif self.game.jumps >= challenge["max_jumps"]:
                self.challenge_result = "failure"
            elif self.game.game_over:
                self.challenge_result = "failure"
        
        # If challenge is completed, mark it as done and give reward
        if self.challenge_result == "success" and self.active_challenge not in self.completed_challenges:
            self.completed_challenges[self.active_challenge] = {
                "completed": True,
                "time": self.challenge_time,
                "date": pygame.time.get_ticks()
            }
            
            # Give reward
            reward = challenge.get("reward", 0)
            self.game.add_coins(reward)
            
            # Show message
            self.game.show_purchase_message = True
            self.game.purchase_message = f"Challenge completed! +{reward} coins"
            self.game.message_timer = 0
            
            # Save progress
            self.save_progress()
            
            # Update unlock status
            self.update_challenge_unlocks()
    
    def draw_challenge_menu(self, screen):
        """Draw the challenge mode menu"""
        # Draw a semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw title
        font_title = pygame.font.Font(None, 48)
        text_title = font_title.render("CHALLENGE MODE", True, (255, 215, 0))
        screen.blit(text_title, (WINDOW_WIDTH // 2 - text_title.get_width() // 2, 50))
        
        # Group challenges by difficulty
        challenges_by_difficulty = {
            "Easy": [],
            "Medium": [],
            "Hard": []
        }
        
        for challenge_id, challenge in self.challenges.items():
            difficulty = challenge.get("difficulty", "Easy")
            if difficulty in challenges_by_difficulty:
                challenges_by_difficulty[difficulty].append((challenge_id, challenge))
        
        # Draw difficulty sections
        font_difficulty = pygame.font.Font(None, 36)
        font_challenge = pygame.font.Font(None, 24)
        font_description = pygame.font.Font(None, 20)
        
        y_offset = 110
        challenge_buttons = {}
        
        for difficulty, challenges in challenges_by_difficulty.items():
            # Set color based on difficulty
            if difficulty == "Easy":
                color = GREEN
            elif difficulty == "Medium":
                color = YELLOW
            else:
                color = RED
            
            # Draw difficulty header
            text_diff = font_difficulty.render(difficulty, True, color)
            screen.blit(text_diff, (WINDOW_WIDTH // 2 - 300, y_offset))
            
            # Draw horizontal line
            pygame.draw.line(screen, color, 
                             (WINDOW_WIDTH // 2 - 300, y_offset + 30),
                             (WINDOW_WIDTH // 2 + 300, y_offset + 30), 2)
            
            y_offset += 40
            
            # Draw challenges in this difficulty
            for challenge_id, challenge in challenges:
                # Determine if challenge is completed
                is_completed = challenge_id in self.completed_challenges
                
                # Determine if challenge is unlocked
                is_unlocked = challenge.get("unlocked", False)
                
                # Draw challenge box
                box_color = (100, 100, 100) if is_unlocked else (50, 50, 50)
                if is_completed:
                    box_color = (0, 100, 0)  # Green for completed
                
                box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 280, y_offset, 560, 70)
                pygame.draw.rect(screen, box_color, box_rect, 0, border_radius=5)
                challenge_buttons[challenge_id] = box_rect
                
                # Draw challenge name
                name_color = WHITE if is_unlocked else (150, 150, 150)
                text_name = font_challenge.render(challenge["name"], True, name_color)
                screen.blit(text_name, (box_rect.left + 10, box_rect.top + 10))
                
                # Draw completion status
                if is_completed:
                    text_completed = font_description.render("COMPLETED", True, (0, 255, 0))
                    screen.blit(text_completed, (box_rect.right - text_completed.get_width() - 10, box_rect.top + 10))
                
                # Draw description
                text_desc = font_description.render(challenge["description"], True, name_color)
                screen.blit(text_desc, (box_rect.left + 10, box_rect.top + 35))
                
                # Draw reward
                reward_text = f"Reward: {challenge.get('reward', 0)} coins"
                text_reward = font_description.render(reward_text, True, (255, 215, 0) if is_unlocked else (150, 150, 150))
                screen.blit(text_reward, (box_rect.right - text_reward.get_width() - 10, box_rect.top + 35))
                
                y_offset += 80
            
            y_offset += 20
        
        # Draw back button
        back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, y_offset, 100, 40)
        pygame.draw.rect(screen, RED, back_rect, 0, border_radius=5)
        font_back = pygame.font.Font(None, 32)
        text_back = font_back.render("BACK", True, WHITE)
        screen.blit(text_back, (back_rect.centerx - text_back.get_width() // 2, back_rect.centery - text_back.get_height() // 2))
        
        return challenge_buttons, back_rect
    
    def draw_challenge_status(self, screen):
        """Draw the current challenge status during gameplay"""
        if not self.active_challenge:
            return
        
        challenge = self.challenges[self.active_challenge]
        
        # Calculate progress
        progress_text = ""
        progress_value = 0
        
        if challenge["type"] == "time_trial":
            time_left = challenge["time_limit"] - self.challenge_time
            time_left_seconds = time_left // FPS
            progress_text = f"Time: {time_left_seconds}s"
            progress_value = time_left / challenge["time_limit"]
            
            # Also show distance
            distance = self.game.player.rect.x
            distance_text = f"Distance: {distance}/{challenge['target_distance']}px"
            
        elif challenge["type"] == "coin_collector":
            coins_collected = len([coin for coin in self.game.coins if coin.collected])
            progress_text = f"Coins: {coins_collected}/{challenge['target_coins']}"
            progress_value = coins_collected / challenge["target_coins"]
            
        elif challenge["type"] == "platform_master":
            progress_text = f"Jumps: {self.game.jumps}/{challenge['target_jumps']}"
            progress_value = self.game.jumps / challenge["target_jumps"]
            
        elif challenge["type"] == "speed_run":
            jumps_left = challenge["max_jumps"] - self.game.jumps
            progress_text = f"Jumps left: {jumps_left}"
            progress_value = jumps_left / challenge["max_jumps"]
            
            # Also show distance
            distance = self.game.player.rect.x
            distance_text = f"Distance: {distance}/{challenge['target_distance']}px"
            
        elif challenge["type"] == "ultimate":
            # Show multiple objectives
            jumps_left = challenge["max_jumps"] - self.game.jumps
            jumps_text = f"Jumps left: {jumps_left}"
            
            distance = self.game.player.rect.x
            distance_text = f"Distance: {distance}/{challenge['target_distance']}px"
            
            coins_collected = len([coin for coin in self.game.coins if coin.collected])
            coins_text = f"Coins: {coins_collected}/{challenge['target_coins']}"
            
            # Use the lowest progress as the overall progress
            distance_progress = min(1.0, distance / challenge["target_distance"])
            coins_progress = min(1.0, coins_collected / challenge["target_coins"])
            jumps_progress = jumps_left / challenge["max_jumps"]
            
            progress_value = min(distance_progress, coins_progress, jumps_progress)
            progress_text = jumps_text
        
        # Draw challenge name and progress
        font = pygame.font.Font(None, 24)
        challenge_text = f"Challenge: {challenge['name']}"
        text_surface = font.render(challenge_text, True, WHITE)
        screen.blit(text_surface, (10, 10))
        
        # Draw progress bar
        bar_rect = pygame.Rect(10, 40, 200, 20)
        pygame.draw.rect(screen, (100, 100, 100), bar_rect, 0, border_radius=5)
        
        # Draw filled portion
        filled_width = int(bar_rect.width * max(0, min(1, progress_value)))
        filled_rect = pygame.Rect(bar_rect.left, bar_rect.top, filled_width, bar_rect.height)
        
        # Color based on progress
        if progress_value > 0.7:
            bar_color = GREEN
        elif progress_value > 0.3:
            bar_color = YELLOW
        else:
            bar_color = RED
            
        pygame.draw.rect(screen, bar_color, filled_rect, 0, border_radius=5)
        
        # Draw progress text
        text_surface = font.render(progress_text, True, WHITE)
        screen.blit(text_surface, (10, 65))
        
        # Draw secondary progress text if needed
        if challenge["type"] in ["time_trial", "speed_run"]:
            text_surface = font.render(distance_text, True, WHITE)
            screen.blit(text_surface, (10, 90))
        
        if challenge["type"] == "ultimate":
            text_surface = font.render(distance_text, True, WHITE)
            screen.blit(text_surface, (10, 90))
            
            text_surface = font.render(coins_text, True, WHITE)
            screen.blit(text_surface, (10, 115))
        
        # Draw result if challenge is completed or failed
        if self.challenge_result:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            font_result = pygame.font.Font(None, 48)
            if self.challenge_result == "success":
                result_text = "CHALLENGE COMPLETED!"
                result_color = GREEN
            else:
                result_text = "CHALLENGE FAILED"
                result_color = RED
            
            text_surface = font_result.render(result_text, True, result_color)
            screen.blit(text_surface, (WINDOW_WIDTH // 2 - text_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
            
            # Draw continue button
            continue_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 50)
            pygame.draw.rect(screen, BLUE, continue_rect, 0, border_radius=5)
            
            font_continue = pygame.font.Font(None, 32)
            text_continue = font_continue.render("CONTINUE", True, WHITE)
            screen.blit(text_continue, (continue_rect.centerx - text_continue.get_width() // 2, continue_rect.centery - text_continue.get_height() // 2))
            
            return continue_rect
        
        return None
    
    def handle_event(self, event, challenge_buttons=None, back_rect=None, continue_rect=None):
        """Handle events for the challenge mode"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check continue button if challenge is completed/failed
            if continue_rect and continue_rect.collidepoint(mouse_pos):
                self.active_challenge = None
                self.challenge_time = 0
                self.objective_completed = False
                self.challenge_result = None
                return "continue"
            
            # Check back button in menu
            if back_rect and back_rect.collidepoint(mouse_pos):
                return "back"
            
            # Check challenge buttons in menu
            if challenge_buttons:
                for challenge_id, rect in challenge_buttons.items():
                    if rect.collidepoint(mouse_pos) and self.challenges[challenge_id]["unlocked"]:
                        return challenge_id
        
        return None 