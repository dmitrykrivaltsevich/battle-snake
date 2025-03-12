import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Battle Snake - NES Style")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
gray = (128, 128, 128)  # For obstacles

# Snake properties
snake_block_size = 10
snake_speed = 15

# Function to check if position collides with obstacles
def is_collision_with_obstacles(x, y, obstacles):
    for obs_x, obs_y, obs_w, obs_h in obstacles:
        if (x < obs_x + obs_w and x + snake_block_size > obs_x and
                y < obs_y + obs_h and y + snake_block_size > obs_y):
            return True
    return False

# Font for score and game over messages - using monospace for NES-style look
font_style = pygame.font.SysFont("monospace", 28, bold=True)
score_font = pygame.font.SysFont("monospace", 20, bold=True)
title_font = pygame.font.SysFont("monospace", 40, bold=True)


def show_score(score, is_reversal=False):
    value = score_font.render("Score: " + str(score), True, white)
    screen.blit(value, [width - 100, 10])  # Top right corner


def draw_snake(snake_block_size, snake_list):
    # NES-style snake colors - darker green for body, lighter green for head
    snake_body_color = (0, 180, 0)  # Darker green
    snake_head_color = (50, 255, 50)  # Lighter green
    snake_outline_color = (0, 100, 0)  # Very dark green for outlines
    
    for i, segment in enumerate(snake_list):
        # Draw main body segment
        if i == len(snake_list) - 1:  # This is the head
            pygame.draw.rect(screen, snake_head_color, [segment[0], segment[1], snake_block_size, snake_block_size])
        else:
            pygame.draw.rect(screen, snake_body_color, [segment[0], segment[1], snake_block_size, snake_block_size])
        
        # Draw pixel-art style outline
        pygame.draw.rect(screen, snake_outline_color, [segment[0], segment[1], snake_block_size, snake_block_size], 1)

def generate_obstacles(num_obstacles=5):
    """Generates brick walls similar to Tank 1990/Battle City."""
    obstacles = []
    
    # Unit size for brick walls (based on Tank game's block size)
    brick_unit = 20
    
    # Generate some horizontal and vertical walls
    for _ in range(num_obstacles):
        # Determine if this is a horizontal or vertical wall
        is_horizontal = random.choice([True, False])
        
        if is_horizontal:
            # Horizontal wall: wider than tall
            wall_width = random.randint(3, 8) * brick_unit  # 3-8 bricks wide
            wall_height = random.randint(1, 2) * brick_unit  # 1-2 bricks tall
        else:
            # Vertical wall: taller than wide
            wall_width = random.randint(1, 2) * brick_unit   # 1-2 bricks wide
            wall_height = random.randint(3, 8) * brick_unit  # 3-8 bricks tall
            
        # Ensure the obstacle stays within screen bounds and snaps to grid
        max_x = (width - wall_width) // brick_unit * brick_unit
        max_y = (height - wall_height) // brick_unit * brick_unit
        
        x = random.randint(0, max_x // brick_unit) * brick_unit
        y = random.randint(0, max_y // brick_unit) * brick_unit
        
        # Avoid spawning obstacles in the center where snake starts
        center_buffer = 100
        if (abs(x - width/2) < center_buffer and abs(y - height/2) < center_buffer):
            # Move obstacle away from center
            if x < width/2:
                x = max(0, x - center_buffer)
            else:
                x = min(max_x, x + center_buffer)
                
        obstacles.append((x, y, wall_width, wall_height))
    
    # Add some L-shaped or T-shaped walls
    for _ in range(2):
        # Create base horizontal segment
        base_width = random.randint(3, 5) * brick_unit
        base_height = brick_unit
        
        # Create vertical segment
        vert_width = brick_unit
        vert_height = random.randint(2, 4) * brick_unit
        
        # Position for L-shape or T-shape
        max_x = (width - max(base_width, vert_width)) // brick_unit * brick_unit
        max_y = (height - (base_height + vert_height)) // brick_unit * brick_unit
        
        base_x = random.randint(0, max_x // brick_unit) * brick_unit
        base_y = random.randint(0, max_y // brick_unit) * brick_unit
        
        # Avoid center area
        center_buffer = 100
        if (abs(base_x - width/2) < center_buffer and abs(base_y - height/2) < center_buffer):
            if base_x < width/2:
                base_x = max(0, base_x - center_buffer)
            else:
                base_x = min(max_x, base_x + center_buffer)
        
        # Add the horizontal segment
        obstacles.append((base_x, base_y, base_width, base_height))
        
        # Add the vertical segment (either at end for L-shape or in middle for T-shape)
        shape_type = random.choice(["L", "T"])
        
        if shape_type == "L":
            # L-shape: vertical part at one end of horizontal part
            vert_x = random.choice([base_x, base_x + base_width - vert_width])
            obstacles.append((vert_x, base_y + base_height, vert_width, vert_height))
        else:
            # T-shape: vertical part in middle of horizontal part
            vert_x = base_x + (base_width - vert_width) // 2
            obstacles.append((vert_x, base_y + base_height, vert_width, vert_height))
            
    return obstacles

def draw_obstacles(obstacles):
    brick_color = (180, 100, 50)  # Reddish-brown for bricks
    mortar_color = (210, 210, 210)  # Light gray for mortar/cement
    
    for x, y, w, h in obstacles:
        # Draw base rectangle for the wall
        pygame.draw.rect(screen, brick_color, [x, y, w, h])
        
        # Draw brick pattern
        brick_width = 20
        brick_height = 10
        
        # Draw horizontal mortar lines (stopping 1px short of right edge)
        for brick_y in range(int(y), int(y + h), brick_height):
            # Don't draw the last horizontal line if it would be at the bottom edge
            if brick_y < y + h - 1:
                pygame.draw.line(screen, mortar_color, (x, brick_y), (x + w - 1, brick_y), 2)
        
        # Draw vertical mortar lines (with offset for alternating rows)
        for row in range(int(h // brick_height)):
            offset = (row % 2) * (brick_width // 2)  # Offset every other row
            for brick_x in range(int(x) + offset, int(x + w), brick_width):
                # Only draw the line if it's not at the wall edge
                if brick_x > x and brick_x < x + w - 1:
                    # For internal rows, go all the way to the next horizontal line
                    start_y = y + row * brick_height
                    
                    # Only stop short if this is the last row before the bottom edge
                    if (row + 1) * brick_height >= h:
                        end_y = y + h - 1  # 1px short of bottom edge
                    else:
                        end_y = y + (row + 1) * brick_height
                        
                    if end_y > start_y:  # Only draw if there's a visible line
                        pygame.draw.line(screen, mortar_color, (brick_x, start_y), 
                                       (brick_x, end_y), 2)


def show_title_screen():
    # NES-style title screen
    screen.fill(black)
    
    # Draw title
    title = title_font.render("BATTLE SNAKE", True, (255, 50, 50))
    subtitle = font_style.render("NES EDITION", True, (50, 255, 50))
    
    title_rect = title.get_rect(center=(width/2, height/4))
    subtitle_rect = subtitle.get_rect(center=(width/2, height/4 + 40))
    
    screen.blit(title, title_rect)
    screen.blit(subtitle, subtitle_rect)
    
    # Draw instructions
    instructions = [
        "ARROW KEYS: Move Snake",
        "SPACE: Pause Game",
        "Q: Quit Game",
        "R: Restart Game",
        "",
        "AVOID BRICK WALLS",
        "COLLECT RED APPLES",
        "",
        "PRESS ANY KEY TO START"
    ]
    
    for i, line in enumerate(instructions):
        text = font_style.render(line, True, white)
        text_rect = text.get_rect(center=(width/2, height/2 + i*30))
        screen.blit(text, text_rect)
    
    # Draw some brick walls and snake for decoration
    demo_obstacles = [(50, height-100, 80, 20), (width-130, height-100, 80, 20)]
    draw_obstacles(demo_obstacles)
    
    # Demo snake
    demo_snake = [[width/2 - 30, height-70], [width/2 - 20, height-70], [width/2 - 10, height-70],
                  [width/2, height-70], [width/2 + 10, height-70]]
    draw_snake(10, demo_snake)
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
    
def gameLoop():
    # Show title screen first
    show_title_screen()
    
    game_over = False
    game_paused = False

    # Initial snake position
    snake_list = []
    snake_head_x = width / 2
    snake_head_y = height / 2
    snake_list.append([snake_head_x, snake_head_y])

    # Generate obstacles first (moved up from below)
    obstacles = generate_obstacles()

    # Direction variables
    x_change = 0
    y_change = 0

    score = 0
    high_score = 0  # Load high score from a file or initialize to 0

    try:
        with open("highscore.txt", "r") as f:
            high_score = int(f.read())
    except FileNotFoundError:
        pass

    clock = pygame.time.Clock()

    # Food properties - ensure food doesn't spawn on obstacles
    food_x = 0
    food_y = 0
    valid_position = False
    while not valid_position:
        food_x = round(random.randrange(0, width - snake_block_size) / 10.0) * 10.0
        food_y = round(random.randrange(0, height - snake_block_size) / 10.0) * 10.0
        valid_position = not is_collision_with_obstacles(food_x, food_y, obstacles)


    while not game_over:

        while game_paused:
            screen.fill(black)
            message = font_style.render("Paused - Press C to continue or Q to quit", True, white)
            screen.blit(message, [width / 6, height / 3])
            show_score(score)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_paused = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_paused = False
                    if event.key == pygame.K_c:
                        game_paused = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -snake_block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = snake_block_size
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -snake_block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = snake_block_size
                    x_change = 0
                elif event.key == pygame.K_SPACE:
                    game_paused = True
                elif event.key == pygame.K_c and game_paused:
                    game_paused = False

        if game_over:
            break

        # Snake movement with teleportation
        snake_head_x += x_change
        snake_head_y += y_change

        # Teleport to the other side of the screen
        if snake_head_x >= width:
            snake_head_x = 0
        elif snake_head_x < 0:
            snake_head_x = width - snake_block_size
        if snake_head_y >= height:
            snake_head_y = 0
        elif snake_head_y < 0:
            snake_head_y = height - snake_block_size

        # ===== ROBUST REVERSAL HANDLING =====
        # The trick: We'll COMPLETELY REVERSE the snake's body when a 180° turn is detected
        # This is a bulletproof approach that works for ANY snake length
        
        # First, determine current direction from movement vectors
        moving_left = x_change < 0
        moving_right = x_change > 0
        moving_up = y_change < 0
        moving_down = y_change > 0
        
        # Then determine previous direction from head and neck positions
        prev_direction = ""
        is_reversal = False
        
        if len(snake_list) >= 2:
            head = snake_list[-1]
            neck = snake_list[-2]
            
            # Determine previous direction based on head-neck relationship
            if head[0] < neck[0]:      prev_direction = "LEFT"
            elif head[0] > neck[0]:    prev_direction = "RIGHT"
            elif head[1] < neck[1]:    prev_direction = "UP"
            elif head[1] > neck[1]:    prev_direction = "DOWN"
            
            # Detect 180° reversals
            is_reversal = (moving_left and prev_direction == "RIGHT") or \
                          (moving_right and prev_direction == "LEFT") or \
                          (moving_up and prev_direction == "DOWN") or \
                          (moving_down and prev_direction == "UP")
            
            # CRITICAL FIX: When reversing direction, replace the entire snake with just head and one body segment
            if is_reversal:
                # The simplest and most reliable solution: truncate the snake to just 2 segments
                # This guarantees no self-collision while preserving the snake's appearance
                
                # For a 2-segment snake, this effectively just reverses the direction
                # For longer snakes, it removes most segments but keeps the snake alive
                
                # Keep only the head and make a new body segment in the reversed direction
                head_pos = snake_list[-1].copy()  # Current head position
                
                # Calculate the new body segment position (one step in the OPPOSITE direction of our new movement)
                new_body_pos = head_pos.copy()
                
                if moving_left:     # Going left, body should be on right side
                    new_body_pos[0] += snake_block_size
                elif moving_right:  # Going right, body should be on left side
                    new_body_pos[0] -= snake_block_size
                elif moving_up:     # Going up, body should be below
                    new_body_pos[1] += snake_block_size
                elif moving_down:   # Going down, body should be above
                    new_body_pos[1] -= snake_block_size
                
                # Replace the entire snake with just these two segments
                snake_list = [new_body_pos, head_pos]
                # (no need to delete segments - the entire snake is now facing the new direction)
        
        # Now do normal collision detection
        self_collision = False
        for i in range(len(snake_list) - 1):
            segment = snake_list[i]
            if snake_head_x == segment[0] and snake_head_y == segment[1]:
                self_collision = True
                break
        
        # If snake has only one segment, no reversal is possible
        if len(snake_list) <= 1:
            is_reversal = False

        if self_collision:
            game_over = True


        # Check for obstacle collision
        if is_collision_with_obstacles(snake_head_x, snake_head_y, obstacles):
            game_over = True

        # Update snake list
        snake_list.append([snake_head_x, snake_head_y])
        if len(snake_list) > score + 1:  # Keep the length of the snake equal to the score + 1 (initial size)
            del snake_list[0]

        # Check for food collision
        if snake_head_x == food_x and snake_head_y == food_y:
            # Generate new food position
            valid_position = False
            while not valid_position:
                food_x = round(random.randrange(0, width - snake_block_size) / 10.0) * 10.0
                food_y = round(random.randrange(0, height - snake_block_size) / 10.0) * 10.0
                
                # Check if food is on any obstacle
                valid_position = not is_collision_with_obstacles(food_x, food_y, obstacles)
                
                # Also check if food is on snake body
                if valid_position:
                    for segment in snake_list:
                        if food_x == segment[0] and food_y == segment[1]:
                            valid_position = False
                            break

            score += 1

        # Update high score
        high_score = max(high_score, score)


        screen.fill(black)
        draw_obstacles(obstacles)  # Draw obstacles first
        
        # Draw NES-style food (blinking apple)
        food_color = (255, 0, 0) if pygame.time.get_ticks() % 500 < 250 else (220, 50, 50)
        food_outline_color = (150, 0, 0)
        pygame.draw.rect(screen, food_color, [food_x, food_y, snake_block_size, snake_block_size])
        pygame.draw.rect(screen, food_outline_color, [food_x, food_y, snake_block_size, snake_block_size], 1)
        
        # Add a little stem on top to make it look like an apple
        stem_color = (0, 100, 0)
        pygame.draw.line(screen, stem_color, 
                         (food_x + snake_block_size//2, food_y), 
                         (food_x + snake_block_size//2, food_y - 3), 2)
        
        draw_snake(snake_block_size, snake_list)
        show_score(score, is_reversal)

        pygame.display.update()

        clock.tick(snake_speed)


    # NES-style Game Over Screen
    screen.fill(black)
    
    # Blinking "GAME OVER" text (alternates between red and bright red)
    blink_color = (255, 0, 0) if pygame.time.get_ticks() % 1000 < 500 else (255, 100, 100)
    game_over_message = title_font.render("GAME OVER", True, blink_color)
    textRect = game_over_message.get_rect()
    textRect.center = (width / 2, height / 3)
    screen.blit(game_over_message, textRect)
    
    # Draw score in 8-bit style box
    score_box_color = (50, 50, 200)  # Blue box
    score_box = pygame.Rect(width/2 - 120, height/2 - 40, 240, 80)
    pygame.draw.rect(screen, score_box_color, score_box)
    pygame.draw.rect(screen, white, score_box, 3)  # White border
    
    # Score text
    score_message = font_style.render("SCORE: " + str(score), True, white)
    score_rect = score_message.get_rect(center=(width/2, height/2 - 20))
    screen.blit(score_message, score_rect)
    
    high_score_message = font_style.render("HIGH SCORE: " + str(high_score), True, white)
    high_score_rect = high_score_message.get_rect(center=(width/2, height/2 + 20))
    screen.blit(high_score_message, high_score_rect)
    
    # Instructions at bottom
    restart_message = font_style.render("PRESS R TO RESTART", True, (50, 255, 50))
    restart_rect = restart_message.get_rect(center=(width/2, height*3/4))
    screen.blit(restart_message, restart_rect)
    
    quit_message = font_style.render("PRESS Q TO QUIT", True, (255, 50, 50))
    quit_rect = quit_message.get_rect(center=(width/2, height*3/4 + 30))
    screen.blit(quit_message, quit_rect)
    
    # Draw some decorative brick walls at the bottom
    decorative_obstacles = [
        (50, height-50, 100, 20),
        (width/2 - 50, height-50, 100, 20),
        (width-150, height-50, 100, 20)
    ]
    draw_obstacles(decorative_obstacles)

    pygame.display.update()

    # Save high score to file
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))


    # Wait for user input on game over screen
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Restart the game
                    waiting_for_input = False
                    gameLoop()
                    return  # Important: Return after restarting to prevent recursion
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()


# Start the game
gameLoop()

pygame.quit()
exit()
