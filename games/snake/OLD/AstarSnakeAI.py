import pygame
import random

# Initialize pygame
pygame.init()

# Set screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
BUTTON_COLOR = (0, 200, 200)
BUTTON_HOVER_COLOR = (0, 255, 255)

# Create screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Snake Game")

# Set the clock for controlling the frame rate
clock = pygame.time.Clock()

# Game variables
snake_pos = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
snake_direction = pygame.K_RIGHT
snake_length = 1
food_pos = (random.randint(0, (SCREEN_WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE,
            random.randint(0, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE)
score = 0
game_over = False
error_reason = ""  # To hold the reason for game over
font = pygame.font.SysFont(None, 35)

def draw_snake(snake_pos):
    for i, pos in enumerate(snake_pos):
        color = GREEN if i > 0 else DARK_GREEN  # Head will be darker green
        pygame.draw.rect(screen, color, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw eyes for the head
        if i == 0:
            eye_size = BLOCK_SIZE // 5
            eye_offset = BLOCK_SIZE // 4
            pygame.draw.circle(screen, BLACK, (pos[0] + eye_offset, pos[1] + eye_offset), eye_size)
            pygame.draw.circle(screen, BLACK, (pos[0] + BLOCK_SIZE - eye_offset, pos[1] + eye_offset), eye_size)

def draw_food(food_pos):
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

def move_snake(snake_pos, snake_direction):
    head_x, head_y = snake_pos[0]

    if snake_direction == pygame.K_UP:
        new_head = (head_x, head_y - BLOCK_SIZE)
    elif snake_direction == pygame.K_DOWN:
        new_head = (head_x, head_y + BLOCK_SIZE)
    elif snake_direction == pygame.K_LEFT:
        new_head = (head_x - BLOCK_SIZE, head_y)
    elif snake_direction == pygame.K_RIGHT:
        new_head = (head_x + BLOCK_SIZE, head_y)

    return [new_head] + snake_pos[:-1]

def check_collision(snake_pos):
    head_x, head_y = snake_pos[0]
    
    # Check if snake hits the wall
    if head_x < 0 or head_x >= SCREEN_WIDTH or head_y < 0 or head_y >= SCREEN_HEIGHT:
        return "hit the wall"
    
    # Check if snake collides with itself
    if (head_x, head_y) in snake_pos[1:]:
        return "collided with itself"
    
    return None

def ai_move(snake_pos, food_pos):
    head_x, head_y = snake_pos[0]
    food_x, food_y = food_pos

    if head_x < food_x:
        return pygame.K_RIGHT
    elif head_x > food_x:
        return pygame.K_LEFT
    elif head_y < food_y:
        return pygame.K_DOWN
    elif head_y > food_y:
        return pygame.K_UP

def display_score(score):
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, [10, 10])

def display_game_over():
    game_over_text = font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, [SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50])

def draw_button(text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))

    button_text = font.render(text, True, BLACK)
    screen.blit(button_text, [x + 10, y + 10])

def reset_game():
    global snake_pos, snake_direction, snake_length, food_pos, score, game_over, error_reason
    snake_pos = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
    snake_direction = pygame.K_RIGHT
    snake_length = 1
    food_pos = (random.randint(0, (SCREEN_WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                random.randint(0, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE)
    score = 0
    game_over = False
    error_reason = ""  # Reset error reason

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# Main loop
while True:
    handle_events()  # Handle events like mouse clicks and window operations

    if not game_over:
        # AI makes its decision on where to move
        snake_direction = ai_move(snake_pos, food_pos)

        # Move the snake
        snake_pos = move_snake(snake_pos, snake_direction)

        # Check if snake has collided with itself or wall
        collision_reason = check_collision(snake_pos)
        if collision_reason:
            game_over = True
            error_reason = collision_reason  # Set error reason for debugging
            print(f"Game Over: {error_reason}")  # Print reason to terminal

        # Check if snake eats food
        if snake_pos[0] == food_pos:
            # Increase the length of the snake
            snake_length += 1
            snake_pos.append(snake_pos[-1])  # Add a new block to the snake
            score += 1  # Increment score

            # Spawn new food
            food_pos = (random.randint(0, (SCREEN_WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                        random.randint(0, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE)

    # Clear the screen and redraw the snake, food, and score
    screen.fill(BLACK)
    draw_snake(snake_pos)
    draw_food(food_pos)
    display_score(score)

    # If game is over, overlay the game over message and draw buttons
    if game_over:
        display_game_over()
        draw_button("Play Again", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10, 200, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR, reset_game)
        draw_button("Quit", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50, BUTTON_COLOR, BUTTON_HOVER_COLOR, pygame.quit)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(10)  # 10 frames per second
