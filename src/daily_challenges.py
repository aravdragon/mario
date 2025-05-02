import pygame
import random
import datetime
import os
import json
from .constants import *

class DailyChallenge:
    def __init__(self, game):
        self.game = game
        self.challenges = []
        self.active_challenge = None
        self.completion_status = False
        self.reward_claimed = False
        self.last_challenge_date = None
        self.challenge_data_path = os.path.join("saves", "daily_challenges.json")
        
        # Ensure saves directory exists
        os.makedirs("saves", exist_ok=True)
        
        # Load or generate new challenges
        self.load_challenges()
        
    def load_challenges(self):
        """Load saved challenge data or generate new challenges if none exist or it's a new day"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Try to load existing challenge data
        if os.path.exists(self.challenge_data_path):
            try:
                with open(self.challenge_data_path, "r") as f:
                    data = json.load(f)
                    self.last_challenge_date = data.get("date")
                    self.challenges = data.get("challenges", [])
                    self.completion_status = data.get("completed", False)
                    self.reward_claimed = data.get("reward_claimed", False)
                    self.active_challenge = data.get("active_challenge")
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupted or can't be read, generate new challenges
                self.generate_new_challenges()
                self.last_challenge_date = today
        else:
            # No existing data, generate new challenges
            self.generate_new_challenges()
            self.last_challenge_date = today
            
        # Check if it's a new day and we need new challenges
        if self.last_challenge_date != today:
            self.generate_new_challenges()
            self.last_challenge_date = today
            self.completion_status = False
            self.reward_claimed = False
            self.save_challenges()
    
    def generate_new_challenges(self):
        """Generate a set of 3 daily challenges with different difficulty levels"""
        self.challenges = []
        
        # Challenge templates by difficulty
        easy_challenges = [
            {"type": "collect_coins", "target": 20, "description": "Collect {target} coins", "reward": 10, "difficulty": "Easy"},
            {"type": "survive_jumps", "target": 10, "description": "Survive {target} jumps", "reward": 5, "difficulty": "Easy"},
            {"type": "distance", "target": 500, "description": "Travel {target} pixels distance", "reward": 8, "difficulty": "Easy"},
            {"type": "avoid_falling", "target": 30, "description": "Survive for {target} seconds without falling", "reward": 7, "difficulty": "Easy"}
        ]
        
        medium_challenges = [
            {"type": "collect_coins", "target": 50, "description": "Collect {target} coins", "reward": 25, "difficulty": "Medium"},
            {"type": "survive_jumps", "target": 30, "description": "Survive {target} jumps", "reward": 20, "difficulty": "Medium"},
            {"type": "distance", "target": 1500, "description": "Travel {target} pixels distance", "reward": 22, "difficulty": "Medium"},
            {"type": "avoid_falling", "target": 60, "description": "Survive for {target} seconds without falling", "reward": 18, "difficulty": "Medium"},
            {"type": "shrink_platforms", "target": 15, "description": "Shrink {target} platforms", "reward": 20, "difficulty": "Medium"}
        ]
        
        hard_challenges = [
            {"type": "collect_coins", "target": 100, "description": "Collect {target} coins", "reward": 50, "difficulty": "Hard"},
            {"type": "survive_jumps", "target": 75, "description": "Survive {target} jumps", "reward": 40, "difficulty": "Hard"},
            {"type": "distance", "target": 3000, "description": "Travel {target} pixels distance", "reward": 45, "difficulty": "Hard"},
            {"type": "avoid_falling", "target": 120, "description": "Survive for {target} seconds without falling", "reward": 35, "difficulty": "Hard"},
            {"type": "shrink_platforms", "target": 30, "description": "Shrink {target} platforms", "reward": 40, "difficulty": "Hard"},
            {"type": "speed_run", "target": 90, "description": "Reach 1000px distance in under {target} seconds", "reward": 60, "difficulty": "Hard"}
        ]
        
        # Add one challenge from each difficulty level
        self.challenges.append(random.choice(easy_challenges))
        self.challenges.append(random.choice(medium_challenges))
        self.challenges.append(random.choice(hard_challenges))
        
        # No active challenge initially
        self.active_challenge = None
        self.completion_status = False
        self.reward_claimed = False
    
    def save_challenges(self):
        """Save current challenge data to file"""
        data = {
            "date": self.last_challenge_date,
            "challenges": self.challenges,
            "completed": self.completion_status,
            "reward_claimed": self.reward_claimed,
            "active_challenge": self.active_challenge
        }
        
        with open(self.challenge_data_path, "w") as f:
            json.dump(data, f)
    
    def select_challenge(self, index):
        """Set the active challenge by index"""
        if 0 <= index < len(self.challenges):
            self.active_challenge = self.challenges[index]
            self.completion_status = False
            self.reward_claimed = False
            self.save_challenges()
            return True
        return False
    
    def check_progress(self, stats):
        """Check if the active challenge has been completed based on current stats"""
        if not self.active_challenge or self.completion_status:
            return self.completion_status
        
        challenge_type = self.active_challenge["type"]
        target = self.active_challenge["target"]
        
        if challenge_type == "collect_coins":
            if stats.get("coins_collected", 0) >= target:
                self.completion_status = True
        
        elif challenge_type == "survive_jumps":
            if stats.get("jumps", 0) >= target:
                self.completion_status = True
        
        elif challenge_type == "distance":
            if stats.get("distance", 0) >= target:
                self.completion_status = True
        
        elif challenge_type == "avoid_falling":
            if stats.get("time_without_falling", 0) >= target:
                self.completion_status = True
        
        elif challenge_type == "shrink_platforms":
            if stats.get("platforms_shrunk", 0) >= target:
                self.completion_status = True
        
        elif challenge_type == "speed_run":
            if stats.get("distance", 0) >= 1000 and stats.get("time", 0) <= target:
                self.completion_status = True
        
        if self.completion_status:
            self.save_challenges()
        
        return self.completion_status
    
    def claim_reward(self):
        """Claim the reward for completing the active challenge"""
        if self.completion_status and not self.reward_claimed and self.active_challenge:
            reward = self.active_challenge.get("reward", 0)
            self.game.add_coins(reward)
            self.reward_claimed = True
            self.save_challenges()
            
            # Show purchase message as feedback
            self.game.show_purchase_message = True
            self.game.purchase_message = f"Challenge completed! +{reward} coins!"
            self.game.message_timer = 0
            
            return reward
        return 0
    
    def draw(self, screen):
        """Draw the daily challenges menu"""
        # Draw a semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw title
        font_title = pygame.font.Font(None, 48)
        text_title = font_title.render("DAILY CHALLENGES", True, (255, 215, 0))
        screen.blit(text_title, (WINDOW_WIDTH // 2 - text_title.get_width() // 2, 50))
        
        # Draw date
        font_date = pygame.font.Font(None, 24)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        text_date = font_date.render(f"Today: {today}", True, WHITE)
        screen.blit(text_date, (WINDOW_WIDTH // 2 - text_date.get_width() // 2, 100))
        
        # Draw challenges
        font_challenge = pygame.font.Font(None, 32)
        font_description = pygame.font.Font(None, 24)
        font_reward = pygame.font.Font(None, 20)
        
        y_offset = 150
        for i, challenge in enumerate(self.challenges):
            # Determine if this is the active challenge
            is_active = self.active_challenge == challenge
            
            # Determine color based on difficulty
            difficulty = challenge.get("difficulty", "Easy")
            if difficulty == "Easy":
                color = GREEN
            elif difficulty == "Medium":
                color = YELLOW
            else:
                color = RED
            
            # Draw challenge box
            box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, y_offset, 500, 100)
            pygame.draw.rect(screen, color if is_active else (80, 80, 80), box_rect, 0 if is_active else 2, border_radius=10)
            
            # Draw difficulty
            text_difficulty = font_reward.render(difficulty, True, WHITE)
            screen.blit(text_difficulty, (box_rect.left + 10, box_rect.top + 10))
            
            # Draw description
            description = challenge["description"].format(target=challenge["target"])
            text_desc = font_description.render(description, True, WHITE)
            screen.blit(text_desc, (box_rect.left + 20, box_rect.top + 35))
            
            # Draw reward
            reward_text = f"Reward: {challenge['reward']} coins"
            text_reward = font_reward.render(reward_text, True, (255, 215, 0))
            screen.blit(text_reward, (box_rect.left + 20, box_rect.top + 70))
            
            # Draw status if active
            if is_active:
                status_text = "COMPLETED" if self.completion_status else "IN PROGRESS"
                claimed_text = "CLAIMED" if self.reward_claimed else ""
                text_status = font_reward.render(status_text, True, GREEN if self.completion_status else WHITE)
                text_claimed = font_reward.render(claimed_text, True, YELLOW)
                screen.blit(text_status, (box_rect.right - text_status.get_width() - 20, box_rect.top + 10))
                if self.reward_claimed:
                    screen.blit(text_claimed, (box_rect.right - text_claimed.get_width() - 20, box_rect.top + 30))
            
            # Draw select button if not active
            if not is_active:
                select_rect = pygame.Rect(box_rect.right - 100, box_rect.centery - 15, 80, 30)
                pygame.draw.rect(screen, BLUE, select_rect, 0, border_radius=5)
                text_select = font_reward.render("SELECT", True, WHITE)
                screen.blit(text_select, (select_rect.centerx - text_select.get_width() // 2, select_rect.centery - text_select.get_height() // 2))
            
            # If active and completed but not claimed, show claim button
            if is_active and self.completion_status and not self.reward_claimed:
                claim_rect = pygame.Rect(box_rect.right - 100, box_rect.bottom - 40, 80, 30)
                pygame.draw.rect(screen, GREEN, claim_rect, 0, border_radius=5)
                text_claim = font_reward.render("CLAIM", True, WHITE)
                screen.blit(text_claim, (claim_rect.centerx - text_claim.get_width() // 2, claim_rect.centery - text_claim.get_height() // 2))
            
            y_offset += 120
        
        # Draw back button
        back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, y_offset + 20, 100, 40)
        pygame.draw.rect(screen, RED, back_rect, 0, border_radius=5)
        font_back = pygame.font.Font(None, 32)
        text_back = font_back.render("BACK", True, WHITE)
        screen.blit(text_back, (back_rect.centerx - text_back.get_width() // 2, back_rect.centery - text_back.get_height() // 2))
        
        return back_rect
    
    def handle_event(self, event, screen):
        """Handle events for the daily challenges menu"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check back button
            back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, 150 + 120 * len(self.challenges) + 20, 100, 40)
            if back_rect.collidepoint(mouse_pos):
                return "back"
            
            # Check challenge selection
            y_offset = 150
            for i, challenge in enumerate(self.challenges):
                is_active = self.active_challenge == challenge
                box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, y_offset, 500, 100)
                
                # Select button
                if not is_active:
                    select_rect = pygame.Rect(box_rect.right - 100, box_rect.centery - 15, 80, 30)
                    if select_rect.collidepoint(mouse_pos):
                        self.select_challenge(i)
                        return "select"
                
                # Claim button
                if is_active and self.completion_status and not self.reward_claimed:
                    claim_rect = pygame.Rect(box_rect.right - 100, box_rect.bottom - 40, 80, 30)
                    if claim_rect.collidepoint(mouse_pos):
                        self.claim_reward()
                        return "claim"
                
                y_offset += 120
        
        return None 