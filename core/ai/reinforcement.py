import numpy as np
import random
from collections import deque
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
import os
class QLearningAgent:
    def __init__(self, state_size, action_size, logger=None, memory=None,
                 learning_rate=0.001, discount_rate=0.99,
                 exploration_rate=1.0, exploration_decay=0.995, min_exploration=0.01,
                 batch_size=32, memory_size=2000):
        self.logger = logger
        self.memory = memory

        # Parameters
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = min_exploration
        self.batch_size = batch_size
        self.memory_buffer = deque(maxlen=memory_size)

        # Neural Network Model
        self.model = self.build_model()

    def build_model(self):
        """Build a neural network for Q-learning."""
        model = Sequential([
            Dense(64, input_dim=self.state_size, activation='relu'),
            Dense(64, activation='relu'),
            Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        self.logger.log_event("Neural network model initialized.")
        return model

    def choose_action(self, state):
        """Choose an action using the epsilon-greedy approach."""
        if np.random.rand() <= self.exploration_rate:
            action = random.randrange(self.action_size)  # Explore
        else:
            action = np.argmax(self.model.predict(state.reshape(1, -1), verbose=0)[0])  # Exploit
        self.logger.log_event(f"Action chosen: {action} (Exploration: {np.random.rand() <= self.exploration_rate})")
        return action

    def remember(self, state, action, reward, next_state, done):
        """Store an experience in the replay buffer."""
        self.memory_buffer.append((state, action, reward, next_state, done))
        self.logger.log_event(f"Stored experience: State={state}, Action={action}, Reward={reward}.")

    def replay(self):
        """Train the model using random experiences from the replay buffer."""
        if len(self.memory_buffer) < self.batch_size:
            return

        minibatch = random.sample(self.memory_buffer, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.discount_rate * np.amax(self.model.predict(next_state.reshape(1, -1), verbose=0)[0])

            target_f = self.model.predict(state.reshape(1, -1), verbose=0)
            target_f[0][action] = target
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)

        # Decay exploration rate
        if self.exploration_rate > self.min_exploration:
            self.exploration_rate *= self.exploration_decay
            self.logger.log_event(f"Exploration rate decayed to {self.exploration_rate}.")

    def learn_from_interaction(self, interaction):
        """Learn from an interaction (e.g., user input, file analysis)."""
        state = self.extract_state(interaction)
        action = self.choose_action(state)
        reward = self.calculate_reward(interaction)
        next_state = self.extract_next_state(interaction)
        done = interaction.get('done', False)

        self.remember(state, action, reward, next_state, done)
        self.replay()

    def extract_state(self, interaction):
        """Convert interaction data into a numerical state representation."""
        state_vector = np.zeros(self.state_size)
        if "sentiment" in interaction:
            sentiment_score = 1 if interaction["sentiment"] == "Positive" else -1
            state_vector[0] = sentiment_score
        if "metadata" in interaction:
            state_vector[1:3] = interaction["metadata"][:2]
        return state_vector

    def extract_next_state(self, interaction):
        """Generate a placeholder for the next state."""
        return np.random.rand(self.state_size)  # Placeholder

    def calculate_reward(self, interaction):
        """Calculate a reward based on interaction outcomes."""
        if interaction.get("success", False):
            return 1
        elif interaction.get("error", False):
            return -1
        return 0

    def save_model(self, file_name="qlearning_model.keras"):
        """Save the trained model to a file."""
        try:
            self.model.save(file_name)
            self.logger.log_event(f"Model saved to {file_name}.")
        except Exception as e:
            self.logger.log_error(f"Error saving model: {e}")

    def load_model(self, file_name="qlearning_model.keras"):
        """Load a pre-trained model from a file."""
        try:
            if os.path.exists(file_name):
                self.model = load_model(file_name, custom_objects={'mse': MeanSquaredError()})
                self.logger.log_event(f"Model loaded from {file_name}.")
            else:
                self.logger.log_warning(f"Model file {file_name} not found.")
        except Exception as e:
            self.logger.log_error(f"Error loading model: {e}")
            
    def visualize_training(self):
        """Visualize the training performance over time."""
        plt.plot(self.history)
        plt.ylabel("Reward")
        plt.xlabel("Episode")
        plt.title("Training Performance Over Time")
        plt.show()

    def adjust_learning_parameters(self, param, value):
        """Adjust learning parameters dynamically."""
        if param == "exploration_rate":
            self.exploration_rate = value
            self.logger.log_event(f"Exploration rate adjusted to {value}.")
        elif param == "learning_rate":
            self.learning_rate = value
            self.model.optimizer.learning_rate.assign(value)
            self.logger.log_event(f"Learning rate adjusted to {value}.")
        else:
            self.logger.log_warning(f"Unknown parameter adjustment: {param}")

if __name__ == "__main__":
    logger = SnowballLogger()
    memory = Memory(logger=logger)

    agent = QLearningAgent(state_size=10, action_size=3, logger=logger, memory=memory)

    # Example interaction
    interaction = {
        "user_input": "Analyze this file.",
        "sentiment": "Positive",
        "metadata": [1024, 1680000000],  # Example file size, timestamp
        "success": True
    }

    agent.learn_from_interaction(interaction)
    agent.save_model()
