# snake.py (S:/Snowball/games/snake)
 
import pygame
import random
import heapq
import os
import sys
from Snowball.decom.OLDinitializer import SnowballInitializer  # Import SnowballInitializer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
print("System Path:", sys.path)  # Debugging statement to confirm path setup

# Use the SnowballInitializer to initialize components
initializer = SnowballInitializer()

# Set up Pygame
pygame.init()

# Constants
TILE_SIZE = 20  # Size of each tile (Snake segments)
GRID_SIZE = 30  # 30x30 grid (600x600 pixels)
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
FPS = 15  # Frames per second

# Use the memory and logger from the initializer
logger = initializer.logger
memory = initializer.memory

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Snake color in normal mode
DARK_GREEN = (0, 128, 0)  # Snake color in Hamiltonian cycle mode
YELLOW = (255, 255, 0)  # Snake color in survival mode
RED = (255, 0, 0)  # Food color
WHITE = (255, 255, 255)  # Text color

# Directions (UP, RIGHT, DOWN, LEFT)
DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_RIGHT: (1, 0),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
}

# Opposite directions for easy checking
OPPOSITE_DIRECTIONS = {
    (0, -1): (0, 1),  # UP -> DOWN
    (0, 1): (0, -1),  # DOWN -> UP
    (1, 0): (-1, 0),  # RIGHT -> LEFT
    (-1, 0): (1, 0),  # LEFT -> RIGHT
}

# Initialize screen
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Snowball - Snake AI")

# Button class for Start, Play Again, and Quit buttons
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 74)
        self.color = WHITE
        self.text_color = BLACK

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Load high score from file
def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return 0

# Save high score to file
def save_high_score(high_score):
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))

# Heuristic function for A* (Manhattan distance)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# A* pathfinding algorithm
def a_star(grid, start, goal, tail):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for dx, dy in DIRECTIONS.values():
            next_pos = (current[0] + dx, current[1] + dy)

            # Ensure the next position is within bounds
            if 0 <= next_pos[0] < GRID_SIZE and 0 <= next_pos[1] < GRID_SIZE:
                # Avoid adding the current snake body but allow the tail (since it will move)
                if next_pos not in grid or next_pos == tail:
                    new_cost = cost_so_far[current] + 1
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + heuristic(goal, next_pos)
                        heapq.heappush(frontier, (priority, next_pos))
                        came_from[next_pos] = current

    # Reconstruct path
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)

        # If no valid path is found
        if current is None:
            return []  # No valid path
    path.reverse()
    return path

# Hamiltonian cycle generation
def generate_hamiltonian_cycle(grid_size):
    path = []
    x, y = 0, 0
    dx, dy = 1, 0
    visited = set()
    for _ in range(grid_size * grid_size):
        path.append((x, y))
        visited.add((x, y))
        nx, ny = x + dx, y + dy
        if not (0 <= nx < grid_size and 0 <= ny < grid_size) or (nx, ny) in visited:
            dx, dy = -dy, dx  # Change direction in a spiral
        x, y = x + dx, y + dy
    return path

def draw_title():
    font = pygame.font.Font(None, 100)
    snake_text = font.render("SNAKE", True, GREEN)
    screen.blit(snake_text, (WINDOW_SIZE // 4, WINDOW_SIZE // 4))

# Snake AI class
class SnakeAI:
    def __init__(self, high_score=0):
        self.reset_game_state(high_score)
        self.learner = initializer.q_learning_agent  # Use the Q-learning agent from initializer
        self.logger = logger  # Use logger from initializer
        self.memory = memory  # Use memory from initializer
        state_size = GRID_SIZE * GRID_SIZE * 9  # Adjust the state size based on grid and direction
        action_size = 3  # Possible actions (left, straight, right)

    def reset_game_state(self, high_score=0):
        self.snake = [(0, 0)]
        self.grid = set(self.snake)
        self.direction = (1, 0)  # Start moving to the right
        self.food = self.spawn_food()
        self.score = 0
        self.high_score = high_score
        self.learner = initializer.q_learning_agent  # Use the Q-learning agent from initializer
        self.logger = logger  # Use logger from initializer
        self.memory = memory  # Use memory from initializer
        self.cycle = generate_hamiltonian_cycle(GRID_SIZE)
        self.cycle_index = 0
        self.is_shortcut = False
        self.use_hamiltonian = False
        self.manual_mode = False
        self.show_hamiltonian = False
        self.manual_move_done = False  # Track if a move has been made in manual mode
        self.mode = "normal"  # Modes: 'normal', 'hamiltonian', 'survival'
        state_size = GRID_SIZE * GRID_SIZE * 9  # Adjust the state size based on grid and direction
        action_size = 3  # Possible actions (left, straight, right)

    def spawn_food(self):
        while True:
            food_position = (
                random.randint(0, GRID_SIZE - 1),
                random.randint(0, GRID_SIZE - 1),
            )
            if food_position not in self.snake:
                return food_position

    def move(self):
        head = self.snake[0]  # Get the head of the snake

        if not self.manual_mode:
            # Check if the snake is in a "sticky situation"
            if self.use_hamiltonian:
                self.mode = "hamiltonian"  # Hamiltonian cycle mode
            else:
                self.mode = "normal"  # Normal mode (seeking food)

            # Check if there is a path to the food
            if self.mode == "normal":
                path_to_food = a_star(self.grid, head, self.food, self.snake[-1])

                if path_to_food:
                    next_position = path_to_food[0]
                    self.is_shortcut = True
                else:
                    # Follow the Hamiltonian cycle if no path is found
                    self.logger.log_event("No valid path found to food. Falling back to Hamiltonian cycle.")
                    self.is_shortcut = False
                    next_position = self.follow_hamiltonian()

            # Check for collision with walls or itself
            if not (0 <= next_position[0] < GRID_SIZE and 0 <= next_position[1] < GRID_SIZE):
                self.logger.log_event("Collision with wall.")
                return False  # Game over - hit the wall

            if next_position in self.grid and next_position != self.snake[-1]:
                self.logger.log_event("Collision with self.")
                return False  # Game over - hit itself

            # If the snake reaches the food
            if next_position == self.food:
                self.snake.insert(0, next_position)  # Add new head (snake grows)
                self.grid.add(next_position)  # Update grid
                self.food = self.spawn_food()  # Spawn new food
                self.score += 1  # Increase score
                if self.score > self.high_score:
                    self.high_score = self.score  # Update high score if needed
                    self.logger.log_event(f"New high score: {self.high_score}")
            else:
                # Move the snake by removing the tail and adding a new head
                tail = self.snake.pop()  # Remove the last segment (tail)
                self.grid.remove(tail)  # Update the grid to remove the tail
                self.snake.insert(0, next_position)  # Add the new head
                self.grid.add(next_position)  # Update the grid with the new head

        return True  # Move successful, no collisions

    def follow_hamiltonian(self):
        self.cycle_index = self.cycle.index(self.snake[0])
        self.cycle_index = (self.cycle_index + 1) % len(self.cycle)
        return self.cycle[self.cycle_index]

    def toggle_manual_mode(self):
        self.manual_mode = not self.manual_mode
        self.manual_move_done = False  # Reset manual move flag when switching modes
        self.logger.log_event(f"Manual mode {'enabled' if self.manual_mode else 'disabled'}")

    # Enable manual control with arrow keys
    def manual_move(self, event):
        new_direction = None

        if event.key == pygame.K_UP:
            new_direction = (0, -1)
        elif event.key == pygame.K_DOWN:
            new_direction = (0, 1)
        elif event.key == pygame.K_LEFT:
            new_direction = (-1, 0)
        elif event.key == pygame.K_RIGHT:
            new_direction = (1, 0)

        # Prevent the snake from moving backwards into itself
        if new_direction and new_direction != OPPOSITE_DIRECTIONS.get(self.direction):
            self.direction = new_direction
            self.manual_move_done = True
            self.logger.log_event(f"Manual move to direction: {self.direction}")

    def manual_move_snake(self):
        """Moves the snake manually based on the current direction."""
        head = self.snake[0]
        next_position = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Check for collisions
        if not (0 <= next_position[0] < GRID_SIZE and 0 <= next_position[1] < GRID_SIZE):
            self.logger.log_event("Game Over: Collision with wall")
            print("Game Over: Collision with wall")
            return False  # Game over - hit the wall

        if next_position in self.grid and next_position != self.snake[-1]:
            self.logger.log_event("Game Over: Collision with self")
            print("Game Over: Collision with self")
            return False  # Game over - hit itself

        # If the snake reaches the food
        if next_position == self.food:
            self.snake.insert(0, next_position)  # Add new head (snake grows)
            self.grid.add(next_position)  # Update grid
            self.food = self.spawn_food()  # Spawn new food
            self.score += 1  # Increase score
            if self.score > self.high_score:
                self.high_score = self.score  # Update high score if needed
                self.logger.log_event(f"New high score: {self.high_score}")
        else:
            # Move the snake by removing the tail and adding a new head
            tail = self.snake.pop()  # Remove the last segment (tail)
            self.grid.remove(tail)  # Update the grid to remove the tail
            self.snake.insert(0, next_position)  # Add the new head
            self.grid.add(next_position)  # Update the grid with the new head

        return True  # Move successful

    # Encode the snake's head and food position into a state
    def encode_state(self, head, food_direction):
        """Encode the snake's head position and food direction as a single integer state."""
        head_index = head[0] * GRID_SIZE + head[1]
        food_index = (food_direction[0] + 1) * 3 + (food_direction[1] + 1)
        return head_index * 9 + food_index

    def get_state(self):
        """Returns an encoded version of the game state for Q-learning."""
        head = self.snake[0]
        food_direction = (self.food[0] - head[0], self.food[1] - head[1])
        return self.encode_state(head, food_direction)

    def update_q_table(self, reward, next_state):
        """Updates the Q-learning table with the reward."""
        current_state = self.get_state()
        action = self.direction  # Treat current direction as action
        done = False  # Or set it based on game over logic
        self.learner.learn(current_state, action, reward, next_state, done)

    def draw(self):
        # Change snake color based on mode
        if self.mode == "survival":
            snake_color = YELLOW  # Yellow for survival mode
        elif self.mode == "hamiltonian":
            snake_color = DARK_GREEN  # Dark green for Hamiltonian mode
        else:
            snake_color = GREEN  # Green for normal mode

        # Draw the Hamiltonian cycle if the option is enabled
        if self.show_hamiltonian:
            font = pygame.font.Font(None, 24)
            for i, pos in enumerate(self.cycle):
                x = pos[0] * TILE_SIZE
                y = pos[1] * TILE_SIZE
                pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE), 1)
                text = font.render(str(i), True, WHITE)
                screen.blit(text, (x + 5, y + 5))

        # Draw the snake
        for i, segment in enumerate(self.snake):
            x = segment[0] * TILE_SIZE
            y = segment[1] * TILE_SIZE
            if i == 0:
                # Draw the head with smaller eyes
                pygame.draw.rect(screen, snake_color, (x, y, TILE_SIZE, TILE_SIZE))
                eye_size = TILE_SIZE // 5  # Smaller eyes
                eye_offset = TILE_SIZE // 3

                if self.direction == (1, 0):  # Facing right
                    pygame.draw.circle(screen, BLACK, (x + TILE_SIZE - eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(screen, BLACK, (x + TILE_SIZE - eye_offset, y + TILE_SIZE - eye_offset), eye_size)
                elif self.direction == (-1, 0):  # Facing left
                    pygame.draw.circle(screen, BLACK, (x + eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(screen, BLACK, (x + eye_offset, y + TILE_SIZE - eye_offset), eye_size)
                elif self.direction == (0, -1):  # Facing up
                    pygame.draw.circle(screen, BLACK, (x + eye_offset, y + eye_offset), eye_size)
                    pygame.draw.circle(screen, BLACK, (x + TILE_SIZE - eye_offset, y + eye_offset), eye_size)
                elif self.direction == (0, 1):  # Facing down
                    pygame.draw.circle(screen, BLACK, (x + eye_offset, y + TILE_SIZE - eye_offset), eye_size)
                    pygame.draw.circle(screen, BLACK, (x + TILE_SIZE - eye_offset, y + TILE_SIZE - eye_offset), eye_size)
            else:
                pygame.draw.rect(screen, snake_color, (x, y, TILE_SIZE, TILE_SIZE))

        # Draw food
        food_x, food_y = self.food[0] * TILE_SIZE, self.food[1] * TILE_SIZE
        pygame.draw.rect(screen, RED, (food_x, food_y, TILE_SIZE, TILE_SIZE))

    def display_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        high_score_text = font.render(f"High Score: {self.high_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WINDOW_SIZE - 200, 10))

    def game_loop(self):
        clock = pygame.time.Clock()
        high_score = load_high_score()  # Load high score from file at the start
        snake_ai = SnakeAI(high_score)  # Pass high score to SnakeAI
        running = True
        game_active = False
        game_over = False  # Track if the game is over
        paused = False

        # Create a start button in the middle of the screen
        start_button = Button(WINDOW_SIZE // 4, WINDOW_SIZE // 2 - 40, 300, 80, "Start")
        game_over_button = None
        play_again_button = None
        quit_button = None

        while running:
            screen.fill(BLACK)

            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if game_active and not game_over:
                            if event.key == pygame.K_SPACE:
                                paused = not paused
                            elif event.key == pygame.K_h:
                                snake_ai.show_hamiltonian = not snake_ai.show_hamiltonian
                            elif event.key == pygame.K_m:
                                snake_ai.toggle_manual_mode()
                            elif snake_ai.manual_mode:
                                snake_ai.manual_move(event)  # Process single key press in manual mode

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if not game_active and start_button.is_clicked(mouse_pos):
                            game_active = True
                            game_over = False
                            snake_ai = SnakeAI(high_score)  # Pass current high score when restarting
                        elif game_over and play_again_button.is_clicked(mouse_pos):
                            game_active = True
                            game_over = False
                            snake_ai = SnakeAI(high_score)  # Pass current high score when restarting
                        elif game_over and quit_button.is_clicked(mouse_pos):
                            running = False  # Quit the game

                if snake_ai.manual_mode and snake_ai.manual_move_done:
                    snake_ai.manual_move_snake()  # Call to move the snake manually
                    snake_ai.manual_move_done = False  # Reset move flag after one step

                if not game_active:
                    draw_title()  # Draw the title "SNAKE" before the game starts
                    start_button.draw(screen)
                elif paused:
                    snake_ai.draw()  # Keep displaying the snake, food, and score
                    snake_ai.display_score()
                    font = pygame.font.Font(None, 74)
                    text = font.render("Paused", True, WHITE)
                    screen.blit(text, (WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2))
                elif game_over:
                    # Draw the final game state (snake, food, and score)
                    snake_ai.draw()
                    snake_ai.display_score()

                    # Display the game over screen on top of the final state
                    font = pygame.font.Font(None, 74)
                    text = font.render("Game Over", True, RED)
                    screen.blit(text, (WINDOW_SIZE // 4, WINDOW_SIZE // 2 - 100))
                    play_again_button = Button(WINDOW_SIZE // 4, WINDOW_SIZE // 2 + 40, 300, 80, "Play Again")
                    quit_button = Button(WINDOW_SIZE // 4, WINDOW_SIZE // 2 + 140, 300, 80, "Quit")
                    play_again_button.draw(screen)
                    quit_button.draw(screen)

                    # Assign game_over_button to play_again_button for click detection
                    game_over_button = play_again_button

                else:
                    # Move the snake and calculate the reward
                    next_state = snake_ai.get_state()
                    if not snake_ai.move():
                        # Stop game logic and trigger game over
                        game_over = True
                        # Check if a new high score was reached and save it
                        if snake_ai.score > high_score:
                            high_score = snake_ai.score
                            save_high_score(high_score)  # Save new high score
                        snake_ai.memory.store_interaction(
                            f"Game Over. Reason: Snake collided with wall or itself. Score: {snake_ai.score}",
                            "Learning new strategy."
                        )
                        snake_ai.logger.log_event(f"Game Over. Reason: Snake collided with wall or itself. Score: {snake_ai.score}")
                        print(f"Game Over. Reason: Snake collided with wall or itself")
                    else:
                        snake_ai.update_q_table(-1 if snake_ai.snake[0] != snake_ai.food else 10, next_state)

                    # Draw snake and other elements during the game
                    snake_ai.draw()
                    snake_ai.display_score()

                pygame.display.flip()
                clock.tick(FPS)

            except Exception as e:
                snake_ai.logger.log_error(f"Unhandled exception in game loop: {e}")
                running = False  # Exit the loop if there's an unhandled exception

        # Save memory on game end
        snake_ai.memory.store_interaction(f"Final Score: {snake_ai.score}", "Snake AI completed a game.")
        snake_ai.logger.log_event(f"Final Score: {snake_ai.score}")