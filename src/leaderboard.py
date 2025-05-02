import pygame
import os
import json
import datetime
import random
from .constants import *

class Leaderboard:
    def __init__(self, game):
        self.game = game
        self.entries = []
        self.max_entries = 10
        self.leaderboard_path = os.path.join("saves", "leaderboard.json")
        self.is_showing = False
        self.scrolling = 0
        
        # Ensure saves directory exists
        os.makedirs("saves", exist_ok=True)
        
        # Load existing leaderboard or create empty one
        self.load_leaderboard()
        
        # Example player names for random high scores
        self.example_names = [
            "CoinMaster", "JumpKing", "PlatformPro",
            "BlockRunner", "GlowingChamp", "PixelJumper",
            "RGBWarrior", "MarioFan", "CubeGlider",
            "SpeedyBlock", "BurstDasher", "ShrinkMaster",
            "NeonGlider", "TreasureHunter", "PurpleNinja"
        ]
    
    def load_leaderboard(self):
        """Load the leaderboard from file or create empty one if none exists"""
        if os.path.exists(self.leaderboard_path):
            try:
                with open(self.leaderboard_path, "r") as f:
                    self.entries = json.load(f)
                    
                    # Sort entries by score (highest first)
                    self.entries = sorted(self.entries, key=lambda x: x["score"], reverse=True)
            except (json.JSONDecodeError, FileNotFoundError):
                self.create_empty_leaderboard()
        else:
            self.create_empty_leaderboard()
    
    def create_empty_leaderboard(self):
        """Create an empty leaderboard with some example high scores"""
        self.entries = []
        
        # Generate some example high scores
        for i in range(5):
            player_name = random.choice(self.example_names)
            score = random.randint(100, 1000)
            jumps = random.randint(20, 200)
            coins = random.randint(10, 100)
            
            self.entries.append({
                "name": player_name,
                "score": score,
                "jumps": jumps,
                "coins": coins,
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "skin": random.randint(0, 10)
            })
        
        # Sort entries by score
        self.entries = sorted(self.entries, key=lambda x: x["score"], reverse=True)
        
        # Save to file
        self.save_leaderboard()
    
    def save_leaderboard(self):
        """Save the current leaderboard to file"""
        with open(self.leaderboard_path, "w") as f:
            json.dump(self.entries, f)
    
    def add_entry(self, name, score, jumps, coins, skin):
        """Add a new entry to the leaderboard"""
        # Create new entry
        new_entry = {
            "name": name,
            "score": score,
            "jumps": jumps,
            "coins": coins,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "skin": skin
        }
        
        # Add to entries
        self.entries.append(new_entry)
        
        # Sort entries by score
        self.entries = sorted(self.entries, key=lambda x: x["score"], reverse=True)
        
        # Keep only top scores
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]
        
        # Save to file
        self.save_leaderboard()
        
        # Return position of new entry (0 is top)
        for i, entry in enumerate(self.entries):
            if entry == new_entry:
                return i
        
        return -1
    
    def draw(self, screen):
        """Draw the leaderboard screen"""
        # Draw a semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw title
        font_title = pygame.font.Font(None, 48)
        text_title = font_title.render("GLOBAL LEADERBOARD", True, (255, 215, 0))
        screen.blit(text_title, (WINDOW_WIDTH // 2 - text_title.get_width() // 2, 50))
        
        # Draw column headers
        font_header = pygame.font.Font(None, 28)
        headers = ["Rank", "Player", "Score", "Jumps", "Coins", "Date"]
        header_widths = [80, 200, 100, 100, 100, 150]
        header_x = WINDOW_WIDTH // 2 - sum(header_widths) // 2
        
        for i, header in enumerate(headers):
            text_header = font_header.render(header, True, WHITE)
            screen.blit(text_header, (header_x, 120))
            header_x += header_widths[i]
        
        # Draw horizontal line below headers
        pygame.draw.line(screen, WHITE, 
                         (WINDOW_WIDTH // 2 - sum(header_widths) // 2, 150),
                         (WINDOW_WIDTH // 2 + sum(header_widths) // 2, 150), 2)
        
        # Draw entries
        font_entry = pygame.font.Font(None, 24)
        y_offset = 170
        
        for i, entry in enumerate(self.entries):
            # Determine row color (highlight first place, your score, or alternating rows)
            if i == 0:
                row_color = (255, 215, 0)  # Gold for 1st place
            elif i == 1:
                row_color = (192, 192, 192)  # Silver for 2nd place
            elif i == 2:
                row_color = (205, 127, 50)  # Bronze for 3rd place
            elif i % 2 == 0:
                row_color = (50, 50, 50)  # Dark gray for even rows
            else:
                row_color = (70, 70, 70)  # Light gray for odd rows
            
            # Draw row background
            row_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - sum(header_widths) // 2,
                y_offset - 5,
                sum(header_widths),
                30
            )
            pygame.draw.rect(screen, row_color, row_rect)
            
            # Draw rank
            rank_text = f"#{i+1}"
            text_rank = font_entry.render(rank_text, True, WHITE)
            screen.blit(text_rank, (WINDOW_WIDTH // 2 - sum(header_widths) // 2 + 30, y_offset))
            
            # Draw player name
            name_text = entry["name"]
            text_name = font_entry.render(name_text, True, WHITE)
            screen.blit(text_name, (WINDOW_WIDTH // 2 - sum(header_widths) // 2 + 80, y_offset))
            
            # Draw score
            score_text = str(entry["score"])
            text_score = font_entry.render(score_text, True, WHITE)
            screen.blit(text_score, (WINDOW_WIDTH // 2 - sum(header_widths) // 2 + 280, y_offset))
            
            # Draw jumps
            jumps_text = str(entry["jumps"])
            text_jumps = font_entry.render(jumps_text, True, WHITE)
            screen.blit(text_jumps, (WINDOW_WIDTH // 2 - sum(header_widths) // 2 + 380, y_offset))
            
            # Draw coins
            coins_text = str(entry["coins"])
            text_coins = font_entry.render(coins_text, True, WHITE)
            screen.blit(text_coins, (WINDOW_WIDTH // 2 - sum(header_widths) // 2 + 480, y_offset))
            
            # Draw date
            date_text = entry["date"]
            text_date = font_entry.render(date_text, True, WHITE)
            screen.blit(text_date, (WINDOW_WIDTH // 2 - sum(header_widths) // 2 + 580, y_offset))
            
            y_offset += 40
        
        # Draw back button
        back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 80, 100, 40)
        pygame.draw.rect(screen, RED, back_rect, 0, border_radius=5)
        font_back = pygame.font.Font(None, 32)
        text_back = font_back.render("BACK", True, WHITE)
        screen.blit(text_back, (back_rect.centerx - text_back.get_width() // 2, back_rect.centery - text_back.get_height() // 2))
        
        return back_rect
    
    def handle_event(self, event):
        """Handle events for the leaderboard screen"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check back button
            back_rect = pygame.Rect(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 80, 100, 40)
            if back_rect.collidepoint(mouse_pos):
                return "back"
        
        return None
    
    def get_player_rank(self, score):
        """Get the rank a player would have with the given score"""
        rank = 1
        for entry in self.entries:
            if score >= entry["score"]:
                return rank
            rank += 1
        
        return rank
    
    def is_high_score(self, score):
        """Check if a score would make it onto the leaderboard"""
        if len(self.entries) < self.max_entries:
            return True
        
        return score > min(entry["score"] for entry in self.entries)
    
    def draw_name_input(self, screen, name=""):
        """Draw screen for entering player name"""
        # Draw a semi-transparent background
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw title
        font_title = pygame.font.Font(None, 48)
        text_title = font_title.render("NEW HIGH SCORE!", True, (255, 215, 0))
        screen.blit(text_title, (WINDOW_WIDTH // 2 - text_title.get_width() // 2, 150))
        
        # Draw score info
        font_info = pygame.font.Font(None, 32)
        score_text = f"Score: {self.game.score}"
        text_score = font_info.render(score_text, True, WHITE)
        screen.blit(text_score, (WINDOW_WIDTH // 2 - text_score.get_width() // 2, 220))
        
        # Draw rank info
        rank = self.get_player_rank(self.game.score)
        rank_text = f"Rank: #{rank}"
        text_rank = font_info.render(rank_text, True, WHITE)
        screen.blit(text_rank, (WINDOW_WIDTH // 2 - text_rank.get_width() // 2, 260))
        
        # Draw name input box
        font_prompt = pygame.font.Font(None, 36)
        text_prompt = font_prompt.render("Enter your name:", True, WHITE)
        screen.blit(text_prompt, (WINDOW_WIDTH // 2 - text_prompt.get_width() // 2, 320))
        
        input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 360, 300, 50)
        pygame.draw.rect(screen, WHITE, input_rect, 2, border_radius=5)
        
        # Draw entered name
        if name:
            font_name = pygame.font.Font(None, 36)
            text_name = font_name.render(name, True, WHITE)
            screen.blit(text_name, (input_rect.left + 10, input_rect.centery - text_name.get_height() // 2))
        
        # Draw cursor
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_rect.left + 10 + (font_name.size(name)[0] if name else 0)
            pygame.draw.line(screen, WHITE, 
                             (cursor_x, input_rect.top + 10),
                             (cursor_x, input_rect.bottom - 10), 2)
        
        # Draw submit button
        submit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 75, 440, 150, 50)
        pygame.draw.rect(screen, GREEN, submit_rect, 0, border_radius=5)
        font_submit = pygame.font.Font(None, 32)
        text_submit = font_submit.render("SUBMIT", True, WHITE)
        screen.blit(text_submit, (submit_rect.centerx - text_submit.get_width() // 2, submit_rect.centery - text_submit.get_height() // 2))
        
        # Draw instructions
        font_instructions = pygame.font.Font(None, 24)
        text_instructions = font_instructions.render("Press ENTER to submit or ESC to cancel", True, WHITE)
        screen.blit(text_instructions, (WINDOW_WIDTH // 2 - text_instructions.get_width() // 2, 510))
        
        return input_rect, submit_rect 