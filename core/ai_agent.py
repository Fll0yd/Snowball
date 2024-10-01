import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.losses import MeanSquaredError
from collections import deque
import random
import os
import threading
from core.voice_interface import VoiceInterface
from core.system_monitor import SystemMonitor
from core.file_monitor import FileMonitor
from core.mobile_integration import MobileIntegration
from core.memory import Memory
from core.decision_maker import DecisionMaker
from core.logger import SnowballLogger
from core.config_loader import load_config

# Load user customization settings
customizations = load_config('user_customizations.json')
interaction_settings = load_config('interaction_settings.json')

nickname = customizations['nickname']
response_tone = customizations['response_tone']
response_length = customizations['response_length']

class GameAI:
    def __init__(self):
        self.state_size = 11  # State size (customize as per game needs)
        self.action_size = 3  # Left, Straight, Right
        self.memory = deque(maxlen=2000)  # Replay buffer to store experiences
        self.gamma = 0.95  # Discount rate for Q-learning
        self.epsilon = 1.0  # Exploration rate (starts high and decays)
        self.epsilon_min = 0.01  # Minimum exploration rate
        self.epsilon_decay = 0.995  # Decay rate for exploration
        self.learning_rate = 0.001
        self.model = self.build_model()  # Build the neural network

    def build_model(self):
        """Build the neural network for Q-learning."""
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))  # Left, Straight, Right
        model.compile(loss='mse', optimizer='adam')
        return model

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state):
        """Choose an action (exploration vs exploitation)."""
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)  # Explore (random action)
        action_values = self.model.predict(state.reshape(1, -1))  # Predict Q-values
        return np.argmax(action_values[0])  # Exploit (best action based on learned Q-values)

    def replay(self, batch_size=32):
        """Train the model using a random batch from the replay buffer."""
        if len(self.memory) < batch_size:
            return  # Not enough experiences in the buffer to train

        # Sample a batch from memory
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.gamma * np.amax(self.model.predict(next_state.reshape(1, -1))[0])
            target_f = self.model.predict(state.reshape(1, -1))
            target_f[0][action] = target  # Update Q-value for the chosen action
            self.model.fit(state.reshape(1, -1), target_f, epochs=1, verbose=0)

        # Decay the exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self, file_name="snake_ai_model.keras"):
        """Save the current model to a file using the new Keras format."""
        self.model.save(file_name)

    def load_model(self, file_name="snake_ai_model.keras"):
        """Load a previously saved model from a file."""
        if os.path.exists(file_name):
            self.model = load_model(file_name, custom_objects={'mse': MeanSquaredError()})

    def get_last_game_performance(self):
        """Log the last game performance (score, etc.)."""
        return random.randint(0, 100)  # Placeholder for actual performance metrics

    def adjust_learning_parameters(self, param, value):
        """Adjust AI learning parameters dynamically."""
        if param == "exploration_rate":
            self.epsilon = value
        elif param == "learning_rate":
            self.model.optimizer.learning_rate.assign(value)

    def play_game(self, state):
        """Simulate playing a game by choosing an action based on the current state."""
        return self.choose_action(state)

    def save_game_state(self):
        print("Game state saved.")

    def load_game_state(self):
        print("Game state loaded.")


class SnowballAI:
    def __init__(self):
        self.name = self.generate_name()
        self.memory = Memory()
        self.voice = VoiceInterface()
        self.monitor = SystemMonitor()
        self.file_monitor = FileMonitor()
        self.mobile = MobileIntegration()
        self.game = GameAI()
        self.logger = SnowballLogger()
        self.nlp = self.NLPEngine()  # Integrated NLP engine
        self.decision_maker = DecisionMaker()
        self.running_event = threading.Event()

    class NLPEngine:
        def __init__(self):
            # Initialize NLP model and configurations
            pass

        def process_input(self, user_input):
            # Simple NLP processing (Placeholder for actual NLP logic)
            # Here you could implement tokenization, intent recognition, etc.
            return f"Processed: {user_input}"  # Placeholder response

    def generate_name(self):
        """Generate a name for the AI."""
        return f"Snowball AI {random.randint(1, 1000)}"

    def respond_to_user(self, user_message):
        """Generate a response to the user based on customizations and NLP processing."""
        processed_message = self.nlp.process_input(user_message)
        response = f"Hello {nickname}, here's your answer: {processed_message}"

        if response_tone == 'casual':
            response = f"Hey {nickname}, let me help you with that! {processed_message}"
        
        if response_length == 'concise':
            response = response.split('.')[0]  # Keep response short
        
        return response

    def start(self):
        """Main loop to start interaction, system monitoring, file monitoring, and multitasking."""
        self.logger.logger.info(f"Snowball AI ({self.name}) started.")
        
        # Start threads for monitoring and interaction
        threading.Thread(target=self.monitor.start_system_monitoring, daemon=True).start()
        threading.Thread(target=self.file_monitor.start_monitoring, daemon=True).start()
        threading.Thread(target=self.handle_mobile_requests, daemon=True).start()
        threading.Thread(target=self.push_notifications_loop, daemon=True).start()
        
        self.interact()

    def interact(self):
        """Interact with the user, handling both voice and text inputs."""
        while not self.running_event.is_set():
            try:
                user_input = self.voice.listen()

                if user_input:
                    response = self.process_input(user_input)
                    self.voice.speak(response)

            except Exception as e:
                self.logger.logger.error(f"Error in interaction: {e}")

    def process_input(self, user_input):
        """Process user input, triggering appropriate actions or games."""
        # Log interaction in memory
        self.memory.store_interaction(user_input, None)
        
        # Use integrated NLP to get a response
        nlp_response = self.nlp.process_input(user_input)

        # Process game commands
        if "play game" in user_input.lower():
            state = np.random.rand(self.game.state_size)  # Example game state
            action = self.game.play_game(state)
            return f"Playing game with action: {action}. {nlp_response}"
        
        return nlp_response

    def handle_mobile_requests(self):
        """Handle requests from mobile devices."""
        pass  # Implementation for handling mobile requests

    def push_notifications_loop(self):
        """Loop for pushing notifications to the user."""
        while not self.running_event.is_set():
            time.sleep(10)  # Placeholder for actual notification logic
            self.logger.logger.info("Pushing notifications...")

# To run the Snowball AI
if __name__ == "__main__":
    ai = SnowballAI()
    ai.start()
