import numpy as np
import random
import matplotlib.pyplot as plt
from collections import deque
from core.config_loader import load_config

# Load AI learning mode settings
learning_settings = load_config('ai_learning_mode.json')

if learning_settings['enabled']:
    learning_rate = learning_settings['learning_rate']
    training_sessions = learning_settings['daily_training_sessions']

    def train_ai():
        for session in range(training_sessions):
            print(f"Training session {session + 1} with learning rate {learning_rate}")

# Deep Q-learning agent with enhancements
class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, discount_rate=0.99, 
                 exploration_rate=1.0, exploration_decay=0.995, min_exploration=0.01, 
                 min_learning_rate=0.0001, batch_size=32, memory_size=2000):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = min_exploration
        self.min_learning_rate = min_learning_rate
        self.batch_size = batch_size
        self.memory = deque(maxlen=memory_size)  # Replay buffer to store experiences
        self.q_table = np.zeros((state_size, action_size))  # Initialize Q-table
        self.history = []  # Track performance over time (e.g., scores)

    def choose_action(self, state):
        """Choose an action using the epsilon-greedy approach."""
        if np.random.rand() <= self.exploration_rate:
            return random.randrange(self.action_size)  # Explore: random action
        return np.argmax(self.q_table[state])  # Exploit: best-known action

    def remember(self, state, action, reward, next_state, done):
        """Store the experience (state transition) in the replay buffer."""
        self.memory.append((state, action, reward, next_state, done))

    def learn(self, current_state, action, reward, next_state, done):
        """Replay experiences and update the Q-table."""
        # Q-learning update: Q(s, a) = Q(s, a) + alpha * [reward + gamma * max(Q(s', a')) - Q(s, a)]
        q_update = reward
        if not done:  # Only update for non-terminal states
            q_update += self.discount_rate * np.max(self.q_table[next_state])

        self.q_table[current_state, action] += self.learning_rate * (q_update - self.q_table[current_state, action])

        # Decay exploration rate (epsilon) and learning rate after each batch
        if self.exploration_rate > self.min_exploration:
            self.exploration_rate *= self.exploration_decay

        if self.learning_rate > self.min_learning_rate:
            self.learning_rate *= self.exploration_decay

    def save_q_table(self, filename="q_table.npy"):
        """Save the Q-table to a file."""
        np.save(filename, self.q_table)

    def load_q_table(self, filename="q_table.npy"):
        """Load a Q-table from a file."""
        self.q_table = np.load(filename)

    def visualize_training(self):
        """Plot the training progress (e.g., scores over time)."""
        plt.plot(self.history)
        plt.ylabel("Score")
        plt.xlabel("Episode")
        plt.title("Agent Performance Over Time")
        plt.show()

    def update_performance(self, score):
        """Store performance after each episode."""
        self.history.append(score)

    def reset_agent(self):
        """Reset the agent's parameters (useful for restarting training)."""
        self.q_table = np.zeros((self.state_size, self.action_size))
        self.exploration_rate = 1.0
        self.history.clear()

    def save_model_checkpoint(self, checkpoint_file="agent_checkpoint.npz"):
        """Save a model checkpoint containing both Q-table and exploration rate."""
        np.savez(checkpoint_file, q_table=self.q_table, exploration_rate=self.exploration_rate)

    def load_model_checkpoint(self, checkpoint_file="agent_checkpoint.npz"):
        """Load a model checkpoint with Q-table and exploration rate."""
        checkpoint = np.load(checkpoint_file)
        self.q_table = checkpoint['q_table']
        self.exploration_rate = checkpoint['exploration_rate']
