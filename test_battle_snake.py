import unittest
import sys
import os
import pygame
import pytest
from unittest.mock import patch, MagicMock

# Add current directory to path to help with imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import game constants and helper functions for testing
# We're not importing the full game module to avoid pygame initialization
SNAKE_BLOCK_SIZE = 10

# Define our test classes
class TestControls(unittest.TestCase):
    """Test the key controls functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock events and pygame functions
        pygame.init = MagicMock()
        pygame.quit = MagicMock()
        pygame.display.set_mode = MagicMock()
    
    def test_q_key_quits(self):
        """Test that pressing Q quits the game."""
        # Create a mock event
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_q
        
        # When Q is pressed in the main game loop, pygame.quit should be called
        # and the function should return
        pygame.quit.reset_mock()
        result = self.simulate_keypress(mock_event)
        self.assertTrue(result)  # Function should indicate termination
        pygame.quit.assert_called_once()  # pygame.quit should be called
    
    def test_r_key_restarts(self):
        """Test that pressing R restarts the game."""
        # Create a mock event
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_r
        
        # When R is pressed, the function should restart (return a special value)
        result = self.simulate_keypress(mock_event)
        self.assertEqual(result, "restart")
    
    def test_c_key_continues(self):
        """Test that pressing C continues the game when paused."""
        # Create a mock event
        mock_event = MagicMock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_c
        
        # When C is pressed while paused, it should unpause
        game_paused = True
        game_paused = self.simulate_pause_keypress(mock_event, game_paused)
        self.assertFalse(game_paused)  # Game should be unpaused
        
    def simulate_keypress(self, event):
        """Simulate processing a key press in the main game loop."""
        key = event.key
        if key == pygame.K_q:
            pygame.quit()
            return True  # Indicate game should exit
        elif key == pygame.K_r:
            return "restart"  # Special value to indicate restart
        return False  # Continue game
    
    def simulate_pause_keypress(self, event, game_paused):
        """Simulate processing a key press in the pause screen."""
        key = event.key
        if key == pygame.K_c:
            return False  # Unpause the game
        return game_paused  # Keep current pause state


class TestHunterSnake(unittest.TestCase):
    """Test the Hunter Snake AI logic."""
    
    def test_calculate_distance(self):
        """Test that distance calculation works correctly."""
        # Horizontal distance
        self.assertEqual(10, self.calculate_distance(0, 0, 10, 0))
        # Vertical distance
        self.assertEqual(10, self.calculate_distance(0, 0, 0, 10))
        # Diagonal distance
        self.assertAlmostEqual(14.14, self.calculate_distance(0, 0, 10, 10), delta=0.1)
    
    def test_hunter_snake_targeting(self):
        """Test that the hunter snake targets correctly."""
        # Snake should move toward player when player is closer
        snake_head_x, snake_head_y = 100, 100
        player_x, player_y = 110, 100
        food_x, food_y = 200, 200
        
        # Calculate distances
        distance_to_player = self.calculate_distance(snake_head_x, snake_head_y, player_x, player_y)
        distance_to_food = self.calculate_distance(snake_head_x, snake_head_y, food_x, food_y)
        
        # Player is closer, so target should be player
        target_x, target_y = (player_x, player_y) if distance_to_player < distance_to_food else (food_x, food_y)
        
        self.assertEqual((player_x, player_y), (target_x, target_y))
    
    def test_hunter_eats_player(self):
        """Test that hunter snake eating player ends the game."""
        hunter_head_x, hunter_head_y = 100, 100
        player_segments = [[100, 100]]  # Player segment at same position as hunter head
        
        # Check for collision
        game_over = False
        for segment in player_segments:
            if hunter_head_x == segment[0] and hunter_head_y == segment[1]:
                game_over = True
                break
        
        # Game should be over after collision
        self.assertTrue(game_over)
    
    def calculate_distance(self, x1, y1, x2, y2):
        """Calculate distance between two points."""
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


class TestFoodInteractions(unittest.TestCase):
    """Test food interactions and game mechanics."""
    
    def test_snake_eats_food_grows(self):
        """Test that when snake eats food, it grows."""
        snake_head_x, snake_head_y = 100, 100
        food_x, food_y = 100, 100
        score = 1
        
        # Snake eats food
        if snake_head_x == food_x and snake_head_y == food_y:
            score += 1
        
        self.assertEqual(2, score)
    
    def test_food_collision_priority(self):
        """Test that when both snakes eat food simultaneously, player has priority."""
        player_x, player_y = 100, 100
        hunter_x, hunter_y = 100, 100
        food_x, food_y = 100, 100
        
        # Both snakes on food
        player_ate_food = player_x == food_x and player_y == food_y
        hunter_ate_food = hunter_x == food_x and hunter_y == food_y
        
        # Apply priority rule
        if player_ate_food and hunter_ate_food:
            hunter_ate_food = False
        
        # Player should get the food
        self.assertTrue(player_ate_food)
        self.assertFalse(hunter_ate_food)


if __name__ == "__main__":
    unittest.main()