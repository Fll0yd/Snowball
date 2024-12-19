import numpy as np
import random
import matplotlib.pyplot as plt
from collections import deque
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.losses import MeanSquaredError
from keras.optimizers import Adam
import os
from Snowball.decom.OLDinitializer import SnowballInitializer


class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, discount_rate=0.99,
                 exploration_rate=1.0, exploration_decay=0.995, min_exploration=0.01,
                 min_learning_rate=0.0001, batch_size=32, memory_size=2000):
        initializer = SnowballInitializer()
        self.logger = initializer.logger
        self.memory = initializer.memory
        
        # Initialize parameters
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = min_exploration
        self.min_learning_rate = min_learning_rate
        self.batch_size = batch_size
        self.memory_buffer = deque(maxlen=memory_size)  # Replay buffer to store experiences
        self.q_table = np.zeros((state_size, action_size))  # Initialize Q-table
        self.history = []  # Track performance over time (e.g., scores)
        self.model = self.build_model()

    def build_model(self):
        """Build a neural network for Q-learning."""
        try:
            model = Sequential()
            model.add(Dense(64, input_dim=self.state_size, activation='relu'))
            model.add(Dense(64, activation='relu'))
            model.add(Dense(self.action_size, activation='linear'))
            optimizer = Adam(learning_rate=self.learning_rate)
            model.compile(loss='mse', optimizer=optimizer)
            self.logger.log_event("Model built and compiled successfully.")
            return model
        except Exception as e:
            self.logger.log_error(f"Error building model: {e}")
            raise

    def choose_action(self, state):
        """Choose an action using the epsilon-greedy approach."""
        if np.random.rand() <= self.exploration_rate:
            action = random.randrange(self.action_size)  # Explore: random action
            self.logger.log_event(f"Exploration: Random action chosen - {action}")
            return action
        action = np.argmax(self.q_table[state])  # Exploit: best-known action
        self.logger.log_event(f"Exploitation: Best-known action chosen - {action}")
        return action

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer."""
        self.memory_buffer.append((state, action, reward, next_state, done))
        self.logger.log_event(f"Stored experience in memory buffer - State: {state}, Action: {action}, Reward: {reward}")

    def learn(self, current_state, action, reward, next_state, done):
        """Update Q-table using the Bellman equation."""
        q_update = reward
        if not done:
            q_update += self.discount_rate * np.max(self.q_table[next_state])

        # Update Q-table
        self.q_table[current_state, action] += self.learning_rate * (q_update - self.q_table[current_state, action])
        self.logger.log_event(f"Updated Q-table - State: {current_state}, Action: {action}, Q-value: {self.q_table[current_state, action]}")

        # Decay exploration rate (epsilon) after each batch
        if self.exploration_rate > self.min_exploration:
            self.exploration_rate *= self.exploration_decay
            self.logger.log_event(f"Exploration rate updated: {self.exploration_rate}")

    def replay(self):
        """Train the model using a random batch from the replay buffer."""
        if len(self.memory_buffer) < self.batch_size:
            return  # Not enough experiences in the buffer to train

        minibatch = random.sample(self.memory_buffer, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.discount_rate * np.amax(self.model.predict(next_state.reshape(1, -1))[0])
            target_f = self.model.predict(state.reshape(1, -1))
            target_f[0][action] = target  # Update Q-value for the chosen action
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)

        # Decay exploration rate
        if self.exploration_rate > self.min_exploration:
            self.exploration_rate *= self.exploration_decay
            self.logger.log_event(f"Exploration rate updated: {self.exploration_rate}")

    def fine_tune_model(self, interaction_data):
        """Fine-tune the model based on user interactions."""
        for interaction in interaction_data:
            user_input = interaction.get('user_input', None)
            if user_input is None:
                continue
            state = self.extract_state_from_input(user_input)
            action = self.choose_action(state)
            reward = self.calculate_reward_from_response(interaction['ai_response'])

            # Store in memory for learning
            self.remember(state, action, reward, state, done=False)
            self.learn(state, action, reward, state, done=False)
        self.replay()

    def extract_state_from_input(self, user_input):
        """Convert user input to a game state representation."""
        # Placeholder logic to derive game state from user input
        return np.random.rand(self.state_size)

    def calculate_reward_from_response(self, ai_response):
        """Determine reward based on AI response to user input."""
        if "good job" in ai_response.lower():
            return 1  # Positive reinforcement
        else:
            return -1  # Negative reinforcement

    def save_model(self, file_name="qlearning_model.keras"):
        """Save the current model to a file."""
        try:
            self.model.save(file_name)
            self.logger.log_event(f"Model saved to file: {file_name}")
        except Exception as e:
            self.logger.log_error(f"Error saving model: {e}")

    def load_model(self, file_name="qlearning_model.keras"):
        """Load a previously saved model from a file."""
        try:
            if os.path.exists(file_name):
                self.model = load_model(file_name, custom_objects={'mse': MeanSquaredError()})
                self.logger.log_event(f"Model loaded from file: {file_name}")
            else:
                self.logger.log_event(f"Model file not found: {file_name}")
        except Exception as e:
            self.logger.log_error(f"Error loading model: {e}")

    def visualize_training(self):
        """Plot the training progress (e.g., scores over time)."""
        plt.plot(self.history)
        plt.ylabel("Score")
        plt.xlabel("Episode")
        plt.title("Agent Performance Over Time")
        plt.show()

    def reset_agent(self):
        """Reset the agent's parameters (useful for restarting training)."""
        self.q_table = np.zeros((self.state_size, self.action_size))
        self.exploration_rate = 1.0
        self.history.clear()
        self.logger.log_event("Agent parameters reset.")

    def save_q_table(self, filename="q_table.npy"):
        """Save the Q-table to a file."""
        try:
            np.save(filename, self.q_table)
            self.logger.log_event(f"Q-table saved to file: {filename}")
        except Exception as e:
            self.logger.log_error(f"Error saving Q-table: {e}")

    def load_q_table(self, filename="q_table.npy"):
        """Load a Q-table from a file."""
        try:
            self.q_table = np.load(filename)
            self.logger.log_event(f"Q-table loaded from file: {filename}")
        except Exception as e:
            self.logger.log_error(f"Error loading Q-table: {e}")

    def save_model_checkpoint(self, checkpoint_file="agent_checkpoint.npz"):
        """Save a model checkpoint containing both Q-table and exploration rate."""
        try:
            np.savez(checkpoint_file, q_table=self.q_table, exploration_rate=self.exploration_rate)
            self.logger.log_event(f"Model checkpoint saved to file: {checkpoint_file}")
        except Exception as e:
            self.logger.log_error(f"Error saving model checkpoint: {e}")

    def load_model_checkpoint(self, checkpoint_file="agent_checkpoint.npz"):
        """Load a model checkpoint with Q-table and exploration rate."""
        try:
            checkpoint = np.load(checkpoint_file)
            self.q_table = checkpoint['q_table']
            self.exploration_rate = checkpoint['exploration_rate']
            self.logger.log_event(f"Loaded model checkpoint from {checkpoint_file}")
        except FileNotFoundError:
            self.logger.log_warning(f"Checkpoint file {checkpoint_file} not found.")
        except Exception as e:
            self.logger.log_error(f"Error loading model checkpoint: {e}")

    def play_game(self, state):
        """Simulate playing a game by choosing an action based on the current state."""
        action = self.choose_action(state)
        self.logger.log_event(f"Playing game, chosen action: {action}")
        return action

    def update_game_state(self, state):
        """Update the game state history."""
        self.game_state_history.append(state)
        self.logger.log_event(f"Updated game state: {state}")

    def get_last_game_performance(self):
        """Log the last game performance (score, etc.)."""
        last_score = random.randint(0, 100)  # Placeholder for actual game performance
        self.logger.log_event(f"Last game performance score: {last_score}")
        return last_score

    def adjust_learning_parameters(self, param, value):
        """Adjust AI learning parameters dynamically."""
        if param == "exploration_rate":
            self.exploration_rate = value
            self.logger.log_event(f"Exploration rate adjusted to: {value}")
        elif param == "learning_rate":
            self.learning_rate = value
            self.model.optimizer.learning_rate.assign(value)
            self.logger.log_event(f"Learning rate adjusted to: {value}")
        else:
            self.logger.log_warning(f"Unknown parameter adjustment requested: {param}")

    def save_game_state(self, file_name="game_state.npz"):
        """Save the game state to a file."""
        try:
            np.savez(file_name, game_state_history=self.game_state_history)
            self.logger.log_event(f"Game state saved to {file_name}")
        except Exception as e:
            self.logger.log_error(f"Error saving game state: {e}")

    def load_game_state(self, file_name="game_state.npz"):
        """Load a game state from a file."""
        try:
            if os.path.exists(file_name):
                checkpoint = np.load(file_name, allow_pickle=True)
                self.game_state_history = checkpoint['game_state_history'].tolist()
                self.logger.log_event(f"Loaded game state from {file_name}")
            else:
                self.logger.log_warning(f"Game state file {file_name} not found.")
        except Exception as e:
            self.logger.log_error(f"Error loading game state: {e}")

    def evaluate_policy(self, episodes=10):
        """Evaluate the policy of the agent over a number of episodes."""
        total_score = 0
        for episode in range(episodes):
            state = np.random.rand(self.state_size)  # Placeholder for initial state
            score = 0
            done = False
            while not done:
                action = self.choose_action(state)
                next_state = np.random.rand(self.state_size)  # Placeholder for next state
                reward = random.uniform(-1, 1)  # Placeholder for reward
                score += reward
                done = random.choice([True, False])  # Randomly decide if episode ends
                state = next_state
            total_score += score
            self.logger.log_event(f"Episode {episode + 1}/{episodes} score: {score}")
        average_score = total_score / episodes
        self.logger.log_event(f"Average policy score over {episodes} episodes: {average_score}")
        return average_score

    def adaptive_learning_rate(self, performance_threshold=50):
        """Adapt the learning rate based on the performance of the agent."""
        last_performance = self.get_last_game_performance()
        if last_performance < performance_threshold:
            new_learning_rate = max(self.learning_rate * 0.9, self.min_learning_rate)
            self.adjust_learning_parameters("learning_rate", new_learning_rate)
        else:
            new_learning_rate = min(self.learning_rate * 1.1, 0.01)
            self.adjust_learning_parameters("learning_rate", new_learning_rate)
        self.logger.log_event(f"Adaptive learning rate set to: {new_learning_rate}")

    def evaluate_and_adjust(self):
        """Periodically evaluate the agent's performance and adjust learning parameters."""
        avg_score = self.evaluate_policy()
        if avg_score < 50:
            self.logger.log_event("Performance below threshold, increasing exploration.")
            self.adjust_learning_parameters("exploration_rate", min(self.exploration_rate * 1.1, 1.0))
        else:
            self.logger.log_event("Performance above threshold, decreasing exploration.")
            self.adjust_learning_parameters("exploration_rate", max(self.exploration_rate * 0.9, self.min_exploration))

    def train_with_user_feedback(self, feedback_data):
        """Incorporate user feedback into training to refine the agent's policy."""
        for feedback in feedback_data:
            state = self.extract_state_from_input(feedback['user_input'])
            action = self.choose_action(state)
            reward = feedback['rating']  # Assume feedback rating is used as reward
            self.remember(state, action, reward, state, done=True)
            self.learn(state, action, reward, state, done=True)
        self.logger.log_event("Training with user feedback completed.")
        self.replay()  # Replay to consolidate learning

