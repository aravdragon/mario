# RGB GlowingBlock Adventure

A Mario-style platformer game featuring an RGB glowing block as the main character. Collect coins, buy power-ups, and survive as long as you can on shrinking platforms!

## Setup

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

Run the game:
```bash
python main.py
```

### Controls

- **Left Arrow** or **A**: Move left
- **Right Arrow** or **D**: Move right
- **Space**: Jump (Double jump available with Jetpack power-up)
- **ESC**: Open/Close shop

### Gameplay

- Collect coins scattered throughout the level
- Platforms will shrink as you jump on them
- Don't fall into the holes!
- Visit the shop (ESC key) to buy power-ups:
  - Burger: Restore health
  - Jetpack: Enable double jump
  - Car: Increase movement speed
  - Shield: Temporary invincibility

### Scoring

- Collect coins to increase your score
- The more jumps you survive, the higher your final score
- Use coins in the shop to buy power-ups

### Game Over

- Game ends when you fall off the platforms
- Your final score is based on the number of successful jumps
- Press R to restart the game

## Features

- RGB glowing main character
- Dynamic platform shrinking mechanics
- Coin collection system
- Shop with power-ups
- Jump counter
- Smooth controls
- Visual effects 