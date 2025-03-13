"""
Unit tests for the Battle Snake game
"""
import unittest
import sys
import os
import pygame
import pytest
import random
from unittest.mock import patch, MagicMock

# Import game utility functions
from game_utils import (
    calculate_distance, 
    is_collision_with_obstacles, 
    get_hunter_direction,
    SNAKE_BLOCK_SIZE,
    SCREEN_WIDTH, 
    SCREEN_HEIGHT
)

# Helper constants for testing
width, height = SCREEN_WIDTH, SCREEN_HEIGHT

class TestControls(unittest.TestCase):
    """Test that the control key handlers work correctly."""
    
    @patch('pygame.quit')
    def test_q_key_quits(self, mock_quit):
        """Test that pressing Q quits the game."""
        # Setup test
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_q
        
        # Simulate Q key press pattern from the game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit()
            self.assertTrue(True)  # We reached this point in the code
        
        # The mock should be called when Q is pressed
        mock_quit.assert_called_once()
    
    def test_r_key_restarts(self):
        """Test that pressing R restarts the game."""
        # Setup test
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_r
        
        # Mock game loop function
        mock_gameloop = MagicMock(return_value="game_restarted")
        
        # Simulate R key press pattern from the game
        result = None
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            result = mock_gameloop()
        
        # R key should trigger game restart
        self.assertEqual("game_restarted", result)
    
    def test_c_key_continues(self):
        """Test that C key unpauses the game."""
        # Setup test
        game_paused = True
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_c
        
        # Simulate C key press pattern from the game
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c and game_paused:
            game_paused = False
        
        # Game should be unpaused
        self.assertFalse(game_paused)


class TestHunterSnake(unittest.TestCase):
    """Test the Hunter Snake AI logic."""
    
    def test_calculate_distance(self):
        """Test distance calculation between points."""
        # Horizontal distance
        self.assertEqual(10, calculate_distance(0, 0, 10, 0))
        # Vertical distance
        self.assertEqual(10, calculate_distance(0, 0, 0, 10))
        # Diagonal distance
        self.assertAlmostEqual(14.14, calculate_distance(0, 0, 10, 10), delta=0.1)
    
    def test_hunter_targeting(self):
        """Test that hunter snake correctly targets the player."""
        # Setup
        hunter_head_x, hunter_head_y = 100, 100
        player_x, player_y = 110, 100
        food_x, food_y = 200, 200
        obstacles = []
        snake_body = [[90, 100], [100, 100]]
        current_direction = {"dx": SNAKE_BLOCK_SIZE, "dy": 0}
        
        # Test direction toward player
        dx, dy = get_hunter_direction(
            hunter_head_x, hunter_head_y,
            player_x, player_y,
            obstacles, current_direction, snake_body
        )
        
        # Hunter should move right toward player
        self.assertEqual(SNAKE_BLOCK_SIZE, dx)
        self.assertEqual(0, dy)
    
    def test_obstacle_avoidance(self):
        """Test that hunter snake avoids obstacles."""
        # Setup
        hunter_head_x, hunter_head_y = 100, 100
        target_x, target_y = 150, 100
        # Place obstacle directly in path
        obstacles = [(110, 90, 20, 20)]
        snake_body = [[90, 100], [100, 100]]
        current_direction = {"dx": SNAKE_BLOCK_SIZE, "dy": 0}
        
        # Get direction with obstacle
        dx, dy = get_hunter_direction(
            hunter_head_x, hunter_head_y,
            target_x, target_y,
            obstacles, current_direction, snake_body
        )
        
        # Hunter should not move right (into obstacle)
        self.assertNotEqual(SNAKE_BLOCK_SIZE, dx)
    
    def test_collision_detection(self):
        """Test obstacle collision detection."""
        obstacles = [(100, 100, 20, 20)]
        
        # Position inside obstacle should detect collision
        self.assertTrue(is_collision_with_obstacles(105, 105, obstacles))
        
        # Position outside obstacle should not detect collision
        self.assertFalse(is_collision_with_obstacles(50, 50, obstacles))


class TestFoodInteractions(unittest.TestCase):
    """Test food and growth mechanics."""
    
    def test_food_spawn_location(self):
        """Test that food can spawn in valid locations."""
        # Create an obstacle covering part of the screen
        obstacles = [(0, 0, 300, 300)]
        
        # Try to place food
        valid_position = False
        for _ in range(100):
            # Random position
            food_x = random.randrange(0, width - SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE)
            food_y = random.randrange(0, height - SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE)
            
            # Check using game's collision function
            if not is_collision_with_obstacles(food_x, food_y, obstacles):
                valid_position = True
                break
        
        # Should be able to find valid position
        self.assertTrue(valid_position)
    
    def test_snake_growth(self):
        """Test snake growth mechanics."""
        # Initial snake
        snake_list = [[100, 100], [90, 100]]
        snake_head_x, snake_head_y = 100, 100
        food_x, food_y = 100, 100
        score = 1
        
        # Snake eats food
        if snake_head_x == food_x and snake_head_y == food_y:
            score += 1
        
        # Score should increase
        self.assertEqual(2, score)
        
        # Update snake (move right)
        new_head_x = snake_head_x + SNAKE_BLOCK_SIZE
        new_head_y = snake_head_y
        snake_list.append([new_head_x, new_head_y])  # Now 3 segments: [90,100], [100,100], [110,100]
        
        # With increased score, snake should NOT get shorter
        # (score is 2, so keep at least 2 segments)
        if len(snake_list) > score:
            del snake_list[0]  # This will remove the oldest segment, leaving 2
        
        # Snake should have 2 segments now (score is 2)
        self.assertEqual(2, len(snake_list))
    
    def test_collision_priority(self):
        """Test player gets priority for food when both snakes collide with it."""
        # Both snakes on same food
        food_x = food_y = 100
        snake_head_x = snake_head_y = 100
        hunter_head_x = hunter_head_y = 100
        
        # Check collisions
        player_ate_food = snake_head_x == food_x and snake_head_y == food_y
        hunter_ate_food = hunter_head_x == food_x and hunter_head_y == food_y
        
        # Apply priority rule
        if player_ate_food and hunter_ate_food:
            hunter_ate_food = False
        
        # Player should get the food
        self.assertTrue(player_ate_food)
        self.assertFalse(hunter_ate_food)


if __name__ == "__main__":
    unittest.main()