# Battle Snake - NES Style

A retro-inspired Snake game with brick wall obstacles reminiscent of the classic Tank 1990/Battle City from the NES era.

<img width="912" alt="Screenshot 2025-03-12 at 23 28 19" src="https://github.com/user-attachments/assets/c8bece75-b931-4579-b558-818af2cf976b" />
<img width="912" alt="Screenshot 2025-03-12 at 23 28 23" src="https://github.com/user-attachments/assets/f7f2e768-d1d1-4bb5-b590-4f09a399bf99" />
<img width="912" alt="Screenshot 2025-03-12 at 23 28 36" src="https://github.com/user-attachments/assets/76a0f811-ba4f-4bf6-8cd0-37e0e4012644" />


## Features

- Classic snake gameplay with NES-style graphics
- Brick wall obstacles inspired by Tank 1990/Battle City
- Ability to perform 180° turns/reversals
- Teleportation when hitting screen edges
- Highscore tracking between sessions
- Retro-style title and game over screens

## Controls

- **Arrow Keys**: Move the snake
- **Space**: Pause game
- **C**: Continue when paused
- **R**: Restart game after game over
- **Q**: Quit game

## Game Elements

- **Green Snake**: The player-controlled character
- **Red Apple**: Food that increases your score and snake length
- **Brick Walls**: Obstacles that cause game over on collision
- **Score Display**: Shows current score in top-right corner

## Special Mechanics

- **Wall Teleportation**: When you hit a screen edge, you appear on the opposite side
- **Obstacle Generation**: Each game generates a unique layout of brick wall obstacles
- **NES-Style Graphics**: Pixel-art inspired visuals with blinking food and distinct snake head/body

## Installation & Running

1. Ensure you have Python and Pygame installed:
   ```
   pip install pygame
   ```

2. Run the game:
   ```
   python battle-snake.py
   ```

## Development Notes

- Built with Python and Pygame
- Includes collision detection for walls, self, and screen boundaries
- Implements game state tracking (playing, paused, game over)
- Uses a simple file-based highscore system

## Credits

- Brick wall design inspired by Tank 1990/Battle City for the NES
- Developed with Gemma 3 and Claud Code (Sonnet 3.7) models assistance
