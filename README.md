# Battle Snake - NES Style

A retro-inspired Snake game with brick wall obstacles reminiscent of the classic Tank 1990/Battle City from the NES era, now featuring an AI-controlled hunter snake!

<img width="868" alt="Screenshot 2025-03-13 at 00 10 44" src="https://github.com/user-attachments/assets/1d6ef88e-025f-43fd-89bf-b755a7e06ad8" />
<img width="912" alt="Screenshot 2025-03-13 at 00 15 46" src="https://github.com/user-attachments/assets/7945292e-6c77-4e51-b39d-e49679606c9f" />
<img width="912" alt="Screenshot 2025-03-12 at 23 28 36" src="https://github.com/user-attachments/assets/76a0f811-ba4f-4bf6-8cd0-37e0e4012644" />


## Features

- Classic snake gameplay with NES-style graphics
- AI-controlled hunter snake that targets player or food
- Two food items on screen simultaneously
- Brick wall obstacles inspired by Tank 1990/Battle City
- Ability to perform 180° turns/reversals
- Teleportation when hitting screen edges
- Highscore tracking between sessions
- Retro-style title and game over screens

## Controls

- **Arrow Keys**: Move the snake
- **Space**: Pause game
- **C**: Continue game (anytime)
- **R**: Restart game (anytime)
- **Q**: Quit game (anytime)

## Game Elements

- **Green Snake**: The player-controlled character
- **Orange Snake**: The AI-controlled hunter snake that chases player or food
- **Red Apples**: Food that increases your score and snake length (two on screen)
- **Brick Walls**: Obstacles that cause game over on collision
- **Score Display**: Shows current score in top-right corner

## Special Mechanics

- **Hunter Snake AI**: Intelligently targets player or food with commitment-based decisions
- **Wall Teleportation**: When you hit a screen edge, you appear on the opposite side
- **Obstacle Avoidance**: Hunter snake intelligently navigates around obstacles
- **Predator/Prey Dynamics**: Hunter snake can eat the player to end the game
- **Dual Growth System**: Both snakes can grow by eating food items
- **Obstacle Generation**: Each game generates a unique layout of brick wall obstacles
- **NES-Style Graphics**: Pixel-art inspired visuals with blinking food and distinct snake head/body

## Installation & Running

1. Ensure you have Python and Pygame installed:
   ```
   # Using uv (recommended)
   pip install uv
   uv venv
   uv pip install -r requirements.txt
   
   # Or using standard venv
   python -m venv .venv
   source .venv/bin/activate
   pip install pygame pytest
   ```

2. Run the game:
   ```
   python battle-snake.py
   ```

## Testing

The game includes unit tests to prevent regression bugs, especially for the control keys (C, R, Q).

### Running tests
```bash
# Install uv if needed
pip install uv

# Then run the tests script
./run_tests.sh
```

The test suite verifies:
- Control key functionality (C, R, Q)
- Hunter snake targeting logic
- Food interaction mechanics
- Collision detection

## Development Notes

- Built with Python and Pygame
- Features advanced pathfinding for the hunter snake
- Includes collision detection for walls, self, other snake, and screen boundaries
- Implements game state tracking (playing, paused, game over)
- Uses a simple file-based highscore system

## Credits

- Brick wall design inspired by Tank 1990/Battle City for the NES
- Developed with Gemma 3 and Claude Code (Sonnet 3.7) models assistance