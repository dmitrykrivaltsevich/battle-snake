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

def get_hunter_direction(head_x, head_y, target_x, target_y, obstacles, current_direction, snake_body, 
                    block_size=SNAKE_BLOCK_SIZE, width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                    food_positions=None, player_position=None):
    """Find the best direction for the hunter snake to move to reach a target while avoiding obstacles.
    
    Args:
        head_x, head_y: Current hunter head position
        target_x, target_y: Target position to move toward
        obstacles: List of obstacles to avoid
        current_direction: Current movement direction
        snake_body: List of hunter snake body segments
        block_size: Size of snake blocks
        width, height: Screen dimensions
        food_positions: Optional list of food positions [(x1, y1), (x2, y2), ...] 
        player_position: Optional player position (x, y)
    """
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
    
    # CRITICAL FIX: Check if target is (0,0) which means we need to choose a target
    # This happens when the hunter is first activated and no target has been chosen yet
    target_not_set = (target_x == 0 and target_y == 0)
    
    if target_not_set and (food_positions or player_position):
        # We need to choose a target immediately instead of going to (0,0)
        candidates = []
        
        # Add food positions as potential targets
        if food_positions:
            for food_x, food_y in food_positions:
                distance = calculate_distance(head_x, head_y, food_x, food_y)
                candidates.append({"x": food_x, "y": food_y, "distance": distance, "type": "food"})
        
        # Add player position as potential target
        if player_position:
            player_x, player_y = player_position
            distance = calculate_distance(head_x, head_y, player_x, player_y)
            candidates.append({"x": player_x, "y": player_y, "distance": distance, "type": "player"})
        
        # Sort candidates by distance (closest first)
        candidates.sort(key=lambda c: c["distance"])
        
        # Use closest target
        if candidates:
            closest = candidates[0]
            target_x, target_y = closest["x"], closest["y"]
    
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
    
    # Enhanced cycle detection logic for complex maze structures
    # Basic detection - any position visited multiple times
    basic_cycling = any(count > 1 for count in position_counts.values())
    
    # Advanced detection - positions visited many times (strong evidence of cycling)
    extreme_cycling = any(count > 2 for count in position_counts.values())
    
    # Super advanced detection - majority of recent positions are repeats
    if len(snake_body) > 5:
        recent_positions = previous_positions[-5:]  # Last 5 positions
        unique_recent = len(set(recent_positions))
        recent_cycling = unique_recent <= 2  # Only 1-2 unique positions in last 5 moves
    else:
        recent_cycling = False
    
    # Combine detection methods
    cycling_detected = basic_cycling or extreme_cycling or recent_cycling
    
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
    
    # Detect complex obstacle shapes - T-shaped, L-shaped, and other configurations
    # that might cause the hunter to get stuck
    complex_obstacles = []
    horizontal_obstacles = []
    vertical_obstacles = []
    
    # Classify obstacles as horizontal or vertical based on their dimensions
    for obs in obstacles:
        x, y, w, h = obs
        if w > h:
            horizontal_obstacles.append(obs)
        elif h > w:
            vertical_obstacles.append(obs)
    
    # First, look for T-shaped configurations (horizontal with vertical attached)
    for h_obs in horizontal_obstacles:
        h_x, h_y, h_w, h_h = h_obs
        for v_obs in vertical_obstacles:
            v_x, v_y, v_w, v_h = v_obs
            
            # Check if vertical piece is connected to horizontal piece forming a T
            if (v_x >= h_x and v_x + v_w <= h_x + h_w and  # Vertical piece within horizontal width
                abs(v_y - (h_y + h_h)) <= block_size):      # Vertical piece starts near horizontal bottom
                
                # T-shape detected
                complex_obstacles.append({
                    "type": "T",
                    "horizontal": h_obs,
                    "vertical": v_obs,
                    "center_x": v_x + v_w/2
                })
                
    # Also look for L-shaped configurations (vertical with horizontal at end)
    for v_obs in vertical_obstacles:
        v_x, v_y, v_w, v_h = v_obs
        for h_obs in horizontal_obstacles:
            h_x, h_y, h_w, h_h = h_obs
            
            # Check if horizontal piece is connected to the end of vertical piece forming an L
            # Two possible L orientations: ┐ or ┌
            l_right = (abs(h_x - v_x) <= block_size and  # Horizontal starts near vertical left side
                        abs(h_y - v_y) <= block_size)     # Horizontal at top of vertical
                        
            l_left = (abs(h_x + h_w - (v_x + v_w)) <= block_size and  # Horizontal ends near vertical right side
                       abs(h_y - v_y) <= block_size)                  # Horizontal at top of vertical
            
            if l_right or l_left:
                # L-shape detected
                complex_obstacles.append({
                    "type": "L",
                    "horizontal": h_obs,
                    "vertical": v_obs,
                    "orientation": "right" if l_right else "left"
                })
    
    # Special handling for complex obstacles (T and L shapes)
    for obs in complex_obstacles:
        obstacle_type = obs["type"]
        h_x, h_y, h_w, h_h = obs["horizontal"]
        v_x, v_y, v_w, v_h = obs["vertical"]
        
        # Different handling based on obstacle type
        if obstacle_type == "T":
            # T-shaped obstacle handling
            t_center_x = obs["center_x"]
            
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
                                
        elif obstacle_type == "L":
            # L-shaped obstacle handling
            orientation = obs["orientation"]  # "left" or "right"
            
            # Determine key points of the L
            l_corner_x = v_x if orientation == "right" else v_x + v_w
            l_corner_y = v_y
            
            # Check hunter position relative to the L
            hunter_inside_l = (orientation == "right" and head_x > l_corner_x and head_y > l_corner_y) or \
                              (orientation == "left" and head_x < l_corner_x and head_y > l_corner_y)
                              
            target_outside_l = not ((orientation == "right" and target_x > l_corner_x and target_y > l_corner_y) or \
                                   (orientation == "left" and target_x < l_corner_x and target_y > l_corner_y))
            
            # Determine if hunter is near the inside corner of the L
            hunter_near_corner = abs(head_x - l_corner_x) < 3*block_size and abs(head_y - l_corner_y) < 3*block_size
            
            # If hunter is caught in L's "pocket" and target is outside, or cycling is detected
            # Enhanced to handle both simple L-shapes and complex maze structures
            if (cycling_detected or (hunter_inside_l and target_outside_l)):
                # Choose escape strategy based on orientation
                if orientation == "right":  # ┐-shaped L
                    # Best strategy: move left away from the vertical part, then up/down based on target
                    for direction in directions:
                        if direction["name"] == "LEFT":
                            direction["bias"] = -1200  # Very strong bias to move away
                        elif direction["name"] == "UP" and head_y > v_y + block_size:
                            # Prioritize moving up if in a maze-like structure
                            direction["bias"] = -800
                        elif head_x < v_x - 2*block_size:  # Once clear of vertical, allow up/down
                            if target_y < head_y and direction["name"] == "UP":
                                direction["bias"] = -700
                            elif target_y > head_y and direction["name"] == "DOWN":
                                direction["bias"] = -700
                else:  # ┌-shaped L
                    # Best strategy: move right away from the vertical part
                    for direction in directions:
                        if direction["name"] == "RIGHT":
                            direction["bias"] = -1200  # Increased from -900
                        elif direction["name"] == "UP" and head_y > v_y + block_size:
                            # Prioritize moving up if in a maze-like structure
                            direction["bias"] = -800
                        elif head_x > v_x + v_w + 2*block_size:  # Once clear of vertical, allow up/down
                            if target_y < head_y and direction["name"] == "UP":
                                direction["bias"] = -700
                            elif target_y > head_y and direction["name"] == "DOWN":
                                direction["bias"] = -700
                
                # Additional escape strategy for complex maze structures with multiple L-shapes
                if cycling_detected:
                    # If we're cycling, prioritize getting away from obstacles and visited positions
                    for direction in directions:
                        new_x = head_x + direction["dx"]
                        new_y = head_y + direction["dy"]
                        
                        # Check if this is a previously unvisited position
                        if (new_x, new_y) not in previous_positions:
                            direction["bias"] -= 300  # Strong bonus for trying new paths
                        
                        # If target is higher up, prioritize moving up
                        if target_y < head_y and direction["name"] == "UP":
                            direction["bias"] -= 200
            
            # Special case: if near the inside corner, force a more decisive escape
            elif hunter_near_corner and hunter_inside_l:
                # Always prioritize moving away from the corner first
                if orientation == "right":  # ┐-shaped L
                    # Move left and/or down
                    for direction in directions:
                        if direction["name"] == "LEFT":
                            direction["bias"] = -800
                        elif direction["name"] == "DOWN":
                            direction["bias"] = -600
                else:  # ┌-shaped L
                    # Move right and/or down
                    for direction in directions:
                        if direction["name"] == "RIGHT":
                            direction["bias"] = -800
                        elif direction["name"] == "DOWN":
                            direction["bias"] = -600
    
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
                # Count how many times this position has been visited
                visit_count = position_counts.get((new_x, new_y), 0)
                
                # Increase penalty for revisiting positions - exponential penalty based on visit count
                position_repeat_penalty = 80 * (visit_count + 1)
                
                # If we're in a detected cycle, apply even stronger penalty
                if cycling_detected:
                    position_repeat_penalty = 300 * (visit_count + 1)
                    
                # Special case for L-shaped obstacle test - extra penalty when we detect extreme cycling
                if extreme_cycling:
                    position_repeat_penalty += 500
                
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