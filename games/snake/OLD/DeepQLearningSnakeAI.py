import pygame
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import threading
import time

# Initialize pygame
pygame.init()

# Game Variables
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
action_space = 4  # [UP, DOWN, LEFT, RIGHT]
vision_size = 5  # Vision grid size (5x5 surrounding grid)
state_size = vision_size * vision_size  # Snake vision grid size flattened for neural network input

# Define colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Create screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake AI with Vision Grid")

# DQL Model
def build_model():
    model = Sequential()
    model.add(Dense(64, input_dim=state_size, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(action_space, activation='linear'))
    model.compile(optimizer='adam', loss='mse')
    return model

# Game Environment (Snake)
class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.snake = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.food = self.spawn_food()
        self.direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.score = 0
        self.done = False
        return self.get_state()

    def get_state(self):
        return self.get_vision_grid().flatten()

    def get_vision_grid(self):
        head_x, head_y = self.snake[0]

        # Create a vision grid (e.g., 5x5 around the snake head)
        vision_grid = np.zeros((vision_size, vision_size))

        half_grid = vision_size // 2

        for i in range(-half_grid, half_grid + 1):
            for j in range(-half_grid, half_grid + 1):
                grid_x = head_x + i * BLOCK_SIZE
                grid_y = head_y + j * BLOCK_SIZE

                # If the coordinates are out of bounds (wall)
                if grid_x < 0 or grid_x >= SCREEN_WIDTH or grid_y < 0 or grid_y >= SCREEN_HEIGHT:
                    vision_grid[i + half_grid, j + half_grid] = -1  # Wall
                # If the coordinates are the food
                elif (grid_x, grid_y) == self.food:
                    vision_grid[i + half_grid, j + half_grid] = 1  # Food
                # If the coordinates are the snake's body
                elif (grid_x, grid_y) in self.snake:
                    vision_grid[i + half_grid, j + half_grid] = -0.5  # Snake body

        return vision_grid

    def spawn_food(self):
        return (random.randint(0, (SCREEN_WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                random.randint(0, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE)

    def step(self, action):
        head = self.snake[0]

        if action == 0:  # UP
            new_head = (head[0], head[1] - BLOCK_SIZE)
        elif action == 1:  # DOWN
            new_head = (head[0], head[1] + BLOCK_SIZE)
        elif action == 2:  # LEFT
            new_head = (head[0] - BLOCK_SIZE, head[1])
        elif action == 3:  # RIGHT
            new_head = (head[0] + BLOCK_SIZE, head[1])

        # Check if the game is over
        if (new_head in self.snake) or (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT):
            self.done = True
            return self.get_state(), -10, self.done  # Large penalty for death

        # Move snake
        self.snake = [new_head] + self.snake[:-1]
        reward = -0.1  # Small penalty for each step

        # Check if the snake eats the food
        if self.snake[0] == self.food:
            self.snake.append(self.snake[-1])
            self.food = self.spawn_food()
            reward = 10  # Reward for eating food
            self.score += 1

        return self.get_state(), reward, self.done

    def draw_snake(self, snake_pos):
        for pos in snake_pos:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

    def draw_food(self, food_pos):
        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

# DQL Agent
class DQLAgent:
    def __init__(self):
        self.model = build_model()
        self.memory = []
        self.epsilon = 1.0  # Exploration
        self.gamma = 0.95  # Discount factor
        self.batch_size = 64
        self.max_memory = 2000

    def act(self, state):
        if np.random.rand() < self.epsilon:
            return random.choice([0, 1, 2, 3])
        q_values = self.model.predict(state[np.newaxis])
        return np.argmax(q_values[0])

    def remember(self, state, action, reward, next_state, done):
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in batch:
            q_update = reward
            if not done:
                q_update += self.gamma * np.max(self.model.predict(next_state[np.newaxis])[0])

            q_values = self.model.predict(state[np.newaxis])
            q_values[0][action] = q_update

            self.model.fit(state[np.newaxis], q_values, epochs=1, verbose=0)

        if self.epsilon > 0.1:
            self.epsilon *= 0.995  # Decrease exploration over time

# Handle events
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# Training Loop with Visualization in a Separate Thread
def training_thread(game, agent, episodes):
    for e in range(episodes):
        state = game.reset()
        done = False
        total_reward = 0

        while not done:
            action = agent.act(state)
            next_state, reward, done = game.step(action)
            total_reward += reward

            agent.remember(state, action, reward, next_state, done)
            state = next_state

            if done:
                print(f"Episode: {e+1}/{episodes}, Score: {game.score}, Total Reward: {total_reward}, Epsilon: {agent.epsilon}")

            agent.replay()

            # Add delay to slow down the training for visibility
            time.sleep(0.1)

# Main loop
def main():
    game = SnakeGame()
    agent = DQLAgent()
    episodes = 1000

    # Run training in a separate thread
    threading.Thread(target=training_thread, args=(game, agent, episodes)).start()

    while True:
        handle_events()

        # Render the game environment to the screen
        screen.fill(BLACK)
        game.draw_snake(game.snake)
        game.draw_food(game.food)
        score_text = pygame.font.SysFont(None, 35).render(f"Score: {game.score}", True, WHITE)
        screen.blit(score_text, [10, 10])
        pygame.display.flip()

        # Add delay for better frame rendering
        pygame.time.delay(50)

if __name__ == "__main__":
    main()
