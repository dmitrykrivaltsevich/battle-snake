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
    
    # Initialize bias for each direction
    for direction in directions:
        direction["bias"] = 0
    
    # Track previous positions to detect cycling
    previous_positions = []
    position_counts = {}  # Count how many times each position was visited
    
    for segment in snake_body:
        pos = (segment[0], segment[1])
        previous_positions.append(pos)
        
        if pos in position_counts:
            position_counts[pos] += 1
        else:
            position_counts[pos] = 1
    
    # Detect if we're in a cycle by looking for positions visited multiple times
    cycling_detected = any(count > 1 for count in position_counts.values())
    
    # Calculate distances to each side of the screen from head position
    distance_to_left = head_x
    distance_to_right = width - head_x
    distance_to_top = head_y
    distance_to_bottom = height - head_y
    
    # Calculate direct line distance to target
    direct_distance_to_target = calculate_distance(head_x, head_y, target_x, target_y)
    
    # Global direction differences (where target is relative to hunter)
    x_diff = target_x - head_x
    y_diff = target_y - head_y
    
    # Detect T-shaped obstacles - look for both horizontal and vertical segments
    t_obstacles = []
    horizontal_obstacles = []
    vertical_obstacles = []
    
    # Classify obstacles as horizontal or vertical based on their dimensions
    for obs in obstacles:
        x, y, w, h = obs
        if w > h:
            horizontal_obstacles.append(obs)
        elif h > w:
            vertical_obstacles.append(obs)
    
    # Look for T-shaped configurations (horizontal with vertical attached)
    for h_obs in horizontal_obstacles:
        h_x, h_y, h_w, h_h = h_obs
        for v_obs in vertical_obstacles:
            v_x, v_y, v_w, v_h = v_obs
            
            # Check if vertical piece is connected to horizontal piece
            if (v_x >= h_x and v_x + v_w <= h_x + h_w and  # Vertical piece within horizontal width
                abs(v_y - (h_y + h_h)) <= block_size):      # Vertical piece starts near horizontal bottom
                
                # T-shape detected
                t_obstacles.append({
                    "horizontal": h_obs,
                    "vertical": v_obs,
                    "center_x": v_x + v_w/2
                })
    
    # Special handling for T-shaped obstacles
    for t_obs in t_obstacles:
        h_x, h_y, h_w, h_h = t_obs["horizontal"]
        v_x, v_y, v_w, v_h = t_obs["vertical"]
        t_center_x = t_obs["center_x"]
        
        # Check if hunter is in a problematic position relative to this T
        hunter_left_of_t = head_x < t_center_x
        hunter_right_of_t = head_x > t_center_x
        hunter_below_t = head_y > h_y + h_h
        hunter_near_vertical = abs(head_x - t_center_x) < 2*block_size
        
        target_left_of_t = target_x < t_center_x
        target_right_of_t = target_x > t_center_x
        
        # T obstacle is blocking direct path between hunter and target?
        t_blocking_path = (hunter_left_of_t and target_right_of_t) or (hunter_right_of_t and target_left_of_t)
        
        # If hunter is stuck in a cycle, near a vertical piece, with target on other side
        if cycling_detected and hunter_near_vertical and t_blocking_path and hunter_below_t:
            # IMPLEMENT ESCAPE PLAN - force the hunter to go down to navigate around
            # This is based on the successful navigation pattern observed in tests
            
            # Move down to get out of the trap zone
            for direction in directions:
                if direction["name"] == "DOWN":
                    direction["bias"] = -1000  # Strong bonus
                # Prevent left/right movement near the obstacle
                elif direction["name"] in ["LEFT", "RIGHT"]:
                    direction["bias"] = 500  # Penalty
        
        # If hunter is already below the T and needs to go to other side
        # Encourage horizontal movement to get past the vertical part
        elif hunter_below_t and t_blocking_path:
            # For left->right case
            if hunter_left_of_t and target_right_of_t:
                # Hunter should move right if far enough below the T
                if head_y > v_y + block_size*2:
                    for direction in directions:
                        if direction["name"] == "RIGHT":
                            direction["bias"] = -200
            # For right->left case
            elif hunter_right_of_t and target_left_of_t:
                # Hunter should move left if far enough below the T
                if head_y > v_y + block_size*2:
                    for direction in directions:
                        if direction["name"] == "LEFT":
                            direction["bias"] = -200
    
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
            # Calculate distance to target from the new position
            new_distance_to_target = calculate_distance(new_x, new_y, target_x, target_y)
            
            # Calculate if we're getting closer to the target
            distance_improvement = direct_distance_to_target - new_distance_to_target
            
            # Calculate if this is a reversal (going back the way we came)
            is_reversal = False
            if current_direction["dx"] == -direction["dx"] and current_direction["dx"] != 0:
                is_reversal = True
            if current_direction["dy"] == -direction["dy"] and current_direction["dy"] != 0:
                is_reversal = True
                
            # Add penalty for changing direction 
            direction_change_penalty = 0
            if current_direction["dx"] != direction["dx"] or current_direction["dy"] != direction["dy"]:
                direction_change_penalty = 10
                
            # Add large penalty for reversals to avoid back-and-forth movement
            if is_reversal:
                direction_change_penalty = 50
                
            # Check if this position has been visited before (anti-cycle penalty)
            position_repeat_penalty = 0
            if (new_x, new_y) in previous_positions:
                # Increase penalty for revisiting positions
                position_repeat_penalty = 80
                # If we're in a detected cycle, apply stronger penalty
                if cycling_detected:
                    position_repeat_penalty = 200
                
            # Give a bonus for moving in a direction that improves distance to target
            distance_improvement_bonus = 0
            if distance_improvement > 0:
                distance_improvement_bonus = -30  # Negative penalty = bonus
            
            valid_directions.append({
                "dx": direction["dx"],
                "dy": direction["dy"],
                "name": direction["name"],
                "distance": new_distance_to_target + 
                           direction_change_penalty + 
                           position_repeat_penalty + 
                           direction["bias"] +
                           distance_improvement_bonus
            })
    
    # If no valid directions, return current direction
    if not valid_directions:
        return current_direction["dx"], current_direction["dy"]
    
    # Sort by score (lower score is better)
    valid_directions.sort(key=lambda x: x["distance"])
    
    # Return best direction
    best_direction = valid_directions[0]
    return best_direction["dx"], best_direction["dy"]