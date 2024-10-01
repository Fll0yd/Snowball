import pygame
import sys
import random
import heapq

# Initialize Pygame
pygame.init()

# Set up game constants
TILE_SIZE = 20  # Size of each tile (Snake segments)
GRID_SIZE = 30  # Defines both the number of rows and columns
WINDOW_SIZE = GRID_SIZE * TILE_SIZE  # 600x600 pixels

# Set up colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)  # Snake color for survival mode
RED = (255, 0, 0)
WHITE = (255, 255, 255)
OUTLINE_COLOR = (0, 0, 0)  # Outline color for snake
NORMAL_EYE_COLOR = DARK_GREEN  # Eye color during Hamiltonian cycle
SHORTCUT_EYE_COLOR = BLACK  # Eye color during shortcut
SURVIVAL_EYE_COLOR = YELLOW  # Eye color for survival mode
DEBUG_COLOR = (128, 128, 128)  # Color for Hamiltonian cycle display
NUMBER_COLOR = WHITE  # Color for Hamiltonian cycle numbers

# Directions (UP, RIGHT, DOWN, LEFT)
DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_RIGHT: (1, 0),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
}

# Maps to restrict the snake to only move forward, left, or right
DIRECTION_OPTIONS = {
    (0, -1): [(1, 0), (-1, 0)],  # Moving up, allow only left (left) and right (right)
    (1, 0): [(0, -1), (0, 1)],   # Moving right, allow only up and down
    (0, 1): [(1, 0), (-1, 0)],   # Moving down, allow only left and right
    (-1, 0): [(0, -1), (0, 1)],  # Moving left, allow only up and down
}

# Initialize screen
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("AI Snake Game")

# Heuristic function for A* (Manhattan distance)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# A* algorithm for pathfinding
def a_star(grid, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for dx, dy in DIRECTIONS.values():
            next = (current[0] + dx, current[1] + dy)
            if (
                0 <= next[0] < GRID_SIZE
                and 0 <= next[1] < GRID_SIZE
                and next not in grid
            ):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return []  # No path found
    path.reverse()
    return path

# Enhanced Hamiltonian cycle to give more maze-like appearance
def generate_prioritized_hamiltonian_cycle(grid_size):
    path = []
    x, y = 0, 0
    dx, dy = 1, 0
    visited = set()
    for i in range(grid_size * grid_size):
        path.append((x, y))
        visited.add((x, y))
        nx, ny = x + dx, y + dy
        if not (0 <= nx < grid_size and 0 <= ny < grid_size) or (nx, ny) in visited:
            dx, dy = -dy, dx  # Change direction in a spiral
        x, y = x + dx, y + dy
    return path

# Snake AI class with Hamiltonian cycle, A* shortcuts, and Manual Mode
class SnakeAI:
    def __init__(self):
        self.snake = [(0, 0)]  # Start at top-left
        self.grid = set(self.snake)  # Track snake's body for collision detection
        self.direction = (1, 0)  # Initial movement to the right
        self.food = self.spawn_food()  # Spawn food
        self.score = 0  # Initialize score
        self.death_reason = None  # Track the reason for game failure
        self.cycle = generate_prioritized_hamiltonian_cycle(GRID_SIZE)  # Precomputed Hamiltonian cycle
        self.cycle_index = 0  # Start at the beginning of the cycle
        self.is_shortcut = False  # Track whether the snake is taking a shortcut
        self.use_hamiltonian = False  # Only use Hamiltonian cycle after score reaches 100
        self.survival_mode = False  # Track if the snake is in survival mode
        self.display_cycle = False  # Track if the Hamiltonian cycle should be displayed
        self.manual_mode = False  # Manual mode flag
        self.manual_move = False  # Manual move flag (controls one step at a time)

    def spawn_food(self):
        while True:
            food_position = (
                random.randint(0, GRID_SIZE - 1),
                random.randint(0, GRID_SIZE - 1),
            )
            if food_position not in self.snake:
                return food_position
            
    def move(self):
        if self.manual_mode and not self.manual_move:
            return True  # If in manual mode and no move was made, do nothing

        head = self.snake[0]
        if not self.manual_mode:
            print(f"Snake's current head position: {head}")

            # Check if score threshold for Hamiltonian cycle is reached
            if self.score >= 100:
                self.use_hamiltonian = True

            # Two-stage decision-making
            path_to_food = a_star(self.grid, head, self.food)
            if path_to_food:
                next_position = path_to_food[0]
                self.is_shortcut = True
                print(f"Taking shortcut to food: {next_position}")
            else:
                # Fallback to Hamiltonian cycle if A* is unsafe or unavailable
                self.survival_mode = True
                next_position = self.follow_hamiltonian()
                print(f"No path to food, entering survival mode. Following Hamiltonian cycle to: {next_position}")
                self.is_shortcut = False

            # Prevent snake from reversing into itself
            if len(self.snake) > 1 and next_position == self.snake[1]:
                self.death_reason = "Reversed into itself"
                return False
        else:
            # In manual mode, use direction set by arrow keys
            next_position = (head[0] + self.direction[0], head[1] + self.direction[1])
            self.manual_move = False  # Reset manual move flag after moving

        # Check for wall collision (Game Over condition)
        if (
            next_position[0] < 0
            or next_position[0] >= GRID_SIZE
            or next_position[1] < 0
            or next_position[1] >= GRID_SIZE
        ):
            self.death_reason = "Hit the wall"
            return False  # End game if wall is hit

        # Check if the snake runs into itself
        if next_position in self.grid:
            self.death_reason = "Hit itself"
            return False

        # Check if food is eaten and update score before any grid movement
        if next_position == self.food:
            print("Food eaten!")
            self.score += 1
            self.food = self.spawn_food()  # Respawn food
            self.snake.insert(0, next_position)  # Extend snake directly
            self.grid.add(next_position)
        else:
            tail = self.snake.pop()  # Remove the tail if no food is eaten
            self.grid.remove(tail)
            self.snake.insert(0, next_position)
            self.grid.add(next_position)

        return True  # Continue the game

    def handle_manual_movement(self, key):
        if key in DIRECTIONS:
            new_direction = DIRECTIONS[key]
            # Ensure the snake cannot move backward into itself
            if new_direction == (-self.direction[0], -self.direction[1]):
                return  # Ignore reverse movements
            self.direction = new_direction
            self.manual_move = True  # Flag to allow manual movement

    def follow_hamiltonian(self):
        self.cycle_index = self.cycle.index(self.snake[0])
        self.cycle_index = (self.cycle_index + 1) % len(self.cycle)
        return self.cycle[self.cycle_index]

    def draw(self, game_over=False):
        # First draw the entire snake without the outline
        for i, segment in enumerate(self.snake):
            x = segment[0] * TILE_SIZE
            y = segment[1] * TILE_SIZE

            # Draw the body of the snake
            if i == 0:
                # Snake head
                pygame.draw.rect(
                    screen,
                    YELLOW if self.survival_mode else GREEN,
                    (x, y, TILE_SIZE, TILE_SIZE),
                )
                eye_color = (
                    SURVIVAL_EYE_COLOR
                    if self.survival_mode
                    else (SHORTCUT_EYE_COLOR if self.is_shortcut else NORMAL_EYE_COLOR)
                )
                eye_size = 4
                pygame.draw.circle(screen, eye_color, (x + 6, y + 6), eye_size)
                pygame.draw.circle(screen, eye_color, (x + TILE_SIZE - 6, y + 6), eye_size)
            else:
                # Draw the body segments
                pygame.draw.rect(
                    screen, YELLOW if self.survival_mode else GREEN, (x, y, TILE_SIZE, TILE_SIZE)
                )

        # Now draw a single outline around the entire snake's outer edge
        outline_points = []
        for segment in self.snake:
            x = segment[0] * TILE_SIZE
            y = segment[1] * TILE_SIZE
            outline_points.append((x + TILE_SIZE // 2, y + TILE_SIZE // 2))

        if len(outline_points) > 1:
            pygame.draw.lines(screen, OUTLINE_COLOR, False, outline_points, 1)  # Adjust thickness as needed

        # Draw the food
        pygame.draw.rect(screen, RED, (self.food[0] * TILE_SIZE, self.food[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        # Display Hamiltonian cycle numbers if toggled
        if self.display_cycle:
            font = pygame.font.Font(None, 18)
            for index, (row, col) in enumerate(self.cycle):
                text = font.render(f"{index}", True, NUMBER_COLOR)
                screen.blit(text, (row * TILE_SIZE + 5, col * TILE_SIZE + 5))

    def display_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

# Game Over Screen
def draw_game_over(snake_ai):
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, 50)
    game_over_text = font.render("Game Over", True, WHITE)
    score_text = font.render(f"Score: {snake_ai.score}", True, WHITE)
    
    # Move the Game Over and score text down a bit and center
    game_over_rect = game_over_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 3))
    score_rect = score_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2.5))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)

    # Draw the buttons and move them to the bottom of the screen
    button_width = WINDOW_SIZE // 2
    button_height = 50
    button_y_offset = WINDOW_SIZE // 2 + 70
    play_again_rect = pygame.Rect(WINDOW_SIZE // 4, button_y_offset, button_width, button_height)
    quit_rect = pygame.Rect(WINDOW_SIZE // 4, button_y_offset + 70, button_width, button_height)

    pygame.draw.rect(screen, WHITE, play_again_rect)
    pygame.draw.rect(screen, WHITE, quit_rect)

    play_again_text = font.render("Play Again", True, BLACK)
    quit_text = font.render("Quit", True, BLACK)

    screen.blit(play_again_text, (WINDOW_SIZE // 3, button_y_offset + 10))
    screen.blit(quit_text, (WINDOW_SIZE // 3 + 30, button_y_offset + 80))

    return play_again_rect, quit_rect

def button_click(mouse_pos, rect):
    return rect.collidepoint(mouse_pos)

def game_loop():
    clock = pygame.time.Clock()
    snake_ai = SnakeAI()
    running = True
    game_over = False
    paused = False

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_m:
                    snake_ai.manual_mode = not snake_ai.manual_mode
                if event.key == pygame.K_h:
                    snake_ai.display_cycle = not snake_ai.display_cycle  # Toggle Hamiltonian cycle display
                if snake_ai.manual_mode and event.key in DIRECTIONS:
                    snake_ai.handle_manual_movement(event.key)

        if not game_over and not paused:
            if not snake_ai.move():
                game_over = True
            snake_ai.draw()
            snake_ai.display_score()

        elif paused:
            snake_ai.draw()
            font = pygame.font.Font(None, 50)
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, (WINDOW_SIZE // 2.5, WINDOW_SIZE // 2))
            snake_ai.display_score()

        else:
            snake_ai.draw()
            play_again_rect, quit_rect = draw_game_over(snake_ai)
            pygame.display.flip()  # Ensure display is updated before waiting for user input
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if button_click(mouse_pos, play_again_rect):
                            waiting_for_input = False  # Exit inner loop to restart game
                            game_loop()  # Restart the game
                        elif button_click(mouse_pos, quit_rect):
                            pygame.quit()
                            sys.exit()

        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    game_loop()
