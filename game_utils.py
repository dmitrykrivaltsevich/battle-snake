"""
Game utilities for Battle Snake
This module contains utility functions used by the game that can be tested independently.
"""
import math

# Constants
SNAKE_BLOCK_SIZE = 10
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def calculate_distance(x1, y1, x2, y2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def is_collision_with_obstacles(x, y, obstacles, block_size=SNAKE_BLOCK_SIZE):
    """Check if a position collides with any obstacles."""
    for obs_x, obs_y, obs_w, obs_h in obstacles:
        if (x < obs_x + obs_w and x + block_size > obs_x and
                y < obs_y + obs_h and y + block_size > obs_y):
            return True
    return False

def get_hunter_direction(head_x, head_y, target_x, target_y, obstacles, current_direction, snake_body, block_size=SNAKE_BLOCK_SIZE, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
    """Find the best direction for the hunter snake to move to reach a target while avoiding obstacles."""
    # Possible directions
    directions = [
        {"dx": -block_size, "dy": 0, "name": "LEFT"},
        {"dx": block_size, "dy": 0, "name": "RIGHT"},
        {"dx": 0, "dy": -block_size, "name": "UP"},
        {"dx": 0, "dy": block_size, "name": "DOWN"}
    ]
    
    # Filter out directions that would cause collision with obstacles
    valid_directions = []
    for direction in directions:
        new_x = head_x + direction["dx"]
        new_y = head_y + direction["dy"]
        
        # Check for teleportation at screen edges
        if new_x >= width:
            new_x = 0
        elif new_x < 0:
            new_x = width - block_size
        if new_y >= height:
            new_y = 0
        elif new_y < 0:
            new_y = height - block_size
        
        # Check for obstacle collision
        collision_with_obstacle = is_collision_with_obstacles(new_x, new_y, obstacles, block_size)
        
        # Check for self collision
        collision_with_self = False
        if len(snake_body) > 1:  # Only check if snake has more than one segment
            for i in range(len(snake_body) - 1):  # Skip checking against head
                segment = snake_body[i]
                if new_x == segment[0] and new_y == segment[1]:
                    collision_with_self = True
                    break
                
        if not (collision_with_obstacle or collision_with_self):
            # Calculate distance to target
            distance = calculate_distance(new_x, new_y, target_x, target_y)
            
            # Calculate if this is a reversal (going back the way we came)
            is_reversal = False
            if current_direction["dx"] == -direction["dx"] and current_direction["dx"] != 0:
                is_reversal = True
            if current_direction["dy"] == -direction["dy"] and current_direction["dy"] != 0:
                is_reversal = True
                
            # Add slight penalty for changing direction to make movement smoother
            direction_change_penalty = 0
            if current_direction["dx"] != direction["dx"] or current_direction["dy"] != direction["dy"]:
                # If it's not continuing in same direction, add a small penalty
                direction_change_penalty = 10
                
            # Add large penalty for reversals to avoid back-and-forth movement
            if is_reversal:
                direction_change_penalty = 50
                
            valid_directions.append({
                "dx": direction["dx"],
                "dy": direction["dy"],
                "name": direction["name"],
                "distance": distance + direction_change_penalty
            })
    
    # If no valid directions, return current direction
    if not valid_directions:
        return current_direction["dx"], current_direction["dy"]
    
    # Sort by distance to target (including penalties)
    valid_directions.sort(key=lambda x: x["distance"])
    
    # Return best direction
    best_direction = valid_directions[0]
    return best_direction["dx"], best_direction["dy"]