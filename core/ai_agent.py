import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.losses import MeanSquaredError
from collections import deque
import random
import threading
import time
import matplotlib.pyplot as plt
from core.voice_interface import VoiceInterface
from core.system_monitor import SystemMonitor
from core.file_monitor import FileMonitor
from core.mobile_integration import MobileIntegration
from core.memory import Memory
from core.decision_maker import DecisionMaker
from core.logger import SnowballLogger
from core.config_loader import ConfigLoader
import openai
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load AI learning mode settings
learning_settings = ConfigLoader.load_config('ai_learning_mode.json')
learning_rate = learning_settings['learning_rate'] if learning_settings['enabled'] else 0.001
training_sessions = learning_settings['daily_training_sessions'] if learning_settings['enabled'] else 1

# Load user customization settings
customizations = ConfigLoader.load_config('user_customizations.json')
interaction_settings = ConfigLoader.load_config('interaction_settings.json')

# GPT 3.5 turbo for NLP engine
openai.api_key = os.getenv("OPENAI_API_KEY")

nickname = customizations.get('nickname', 'User')
response_tone = customizations.get('response_tone', 'neutral')
response_length = customizations.get('response_length', 'normal')

class SnowballAI:
    def __init__(self):
        self.name = self.generate_name()
        self.memory = Memory()
        self.voice = VoiceInterface()
        self.monitor = SystemMonitor()

        # Pass config file to FileMonitor
        file_monitor_config = 'S:/Snowball/config/plex_config.json'  # Corrected path
        self.file_monitor = FileMonitor(config_file=file_monitor_config)

        self.mobile = MobileIntegration()
        self.game = GameAI()
        self.logger = SnowballLogger()
        self.nlp = self.NLPEngine()  # Integrated NLP engine
        self.decision_maker = DecisionMaker()
        self.running_event = threading.Event()

    class GameAI:
        def __init__(self):
            self.state_size = 11  # Customize for your game
            self.action_size = 3  # Left, Straight, Right (example actions)
            self.memory = deque(maxlen=2000)
            self.gamma = 0.95
            self.epsilon = 1.0
            self.epsilon_min = 0.01
            self.epsilon_decay = 0.995
            self.learning_rate = learning_rate
            self.model = self.build_model()
            self.game_state_history = []  # Track game state history
            self.q_table = np.zeros((self.state_size, self.action_size))  # Initialize Q-table
            self.history = []  # Track performance over time (e.g., scores)

        def build_model(self):
            """Build a neural network for Q-learning."""
            model = Sequential()
            model.add(Dense(32, input_dim=self.state_size, activation='relu'))
            model.add(Dense(32, activation='relu'))
            model.add(Dense(self.action_size, activation='linear'))
            model.compile(loss='mse', optimizer='adam')
            return model

        def remember(self, state, action, reward, next_state, done):
            """Store experience in replay buffer."""
            self.memory.append((state, action, reward, next_state, done))

        def learn(self, current_state, action, reward, next_state, done):
            """Replay experiences and update the Q-table."""
            q_update = reward
            if not done:  # Only update for non-terminal states
                q_update += self.gamma * np.max(self.q_table[next_state])

            self.q_table[current_state, action] += self.learning_rate * (q_update - self.q_table[current_state, action])

            # Decay exploration rate (epsilon) after each batch
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

        def fine_tune_model(self, interaction_data):
            """Fine-tune the model based on user interactions."""
            for interaction in interaction_data:
                # Extract relevant information from interactions
                user_input = interaction['user_input']
                # Logic to convert user input to a game state and reward
                # This is highly context-dependent, customize as needed
                state = self.extract_state_from_input(user_input)  
                action = self.choose_action(state)
                reward = self.calculate_reward_from_response(interaction['ai_response'])

                # Store in memory for learning
                self.remember(state, action, reward, state, done=False)
                self.learn(state, action, reward, state, done=False)
            
            # Optionally, perform a replay after storing interactions
            self.replay()

        def choose_action(self, state):
            """Choose an action using the epsilon-greedy approach."""
            if np.random.rand() <= self.epsilon:
                return random.randrange(self.action_size)  # Explore: random action
            action_values = self.model.predict(state.reshape(1, -1))  # Predict Q-values
            return np.argmax(self.q_table[state])  # Exploit: best-known action

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

        def update_game_state(self, state):
            """Update the game state history."""
            self.game_state_history.append(state)

        def get_last_game_performance(self):
            """Log the last game performance (score, etc.)."""
            return random.randint(0, 100)
        
        def adjust_learning_parameters(self, param, value):
            """Adjust AI learning parameters dynamically."""
            if param == "exploration_rate":
                self.epsilon = value
            elif param == "learning_rate":
                self.model.optimizer.learning_rate.assign(value)

        def play_game(self, state):
            """Simulate playing a game by choosing an action based on the current state."""
            self.update_game_state(state)  # Track the game state
            action = self.choose_action(state)
            return action

        def save_game_state(self):
            print("Game state saved.")

        def load_game_state(self):
            print("Game state loaded.")

        def extract_state_from_input(self, user_input):
            """Convert user input to a game state representation."""
            # Logic to derive game state from user input (depends on your game)
            # This could involve parsing commands, understanding context, etc.
            return np.random.rand(self.state_size)  # Placeholder logic

        def calculate_reward_from_response(self, ai_response):
            """Determine reward based on AI response to user input."""
            # Define how you want to reward based on the AI's response
            if "good job" in ai_response.lower():
                return 1  # Positive reinforcement
            else:
                return -1  # Negative reinforcement

    class NLPEngine:
        def __init__(self):
            # Initialize NLP model and configurations
            pass

        def process_input(self, user_input):
            """Process user input using GPT 3.5 Turbo."""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "You are a helpful AI assistant."},
                              {"role": "user", "content": user_input}]
                )
                return response.choices[0].message['content']
            except Exception as e:
                print(f"Error processing NLP input: {e}")
                return "Sorry, I couldn't process that."

    def generate_name(self):
        """Generate a name for the AI."""
        return f"Snowball AI {random.randint(1, 1000)}"

    def respond_to_user(self, user_message):
        """Generate a response to the user based on customizations and NLP processing."""
        processed_message = self.nlp.process_input(user_message)
        response = f"Hello {nickname}, here's your answer: {processed_message}"

        if response_tone == 'casual':
            response = f"Hey {nickname}, here's what I found: {processed_message}"
        
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
        self.logger.logger.info(f"User input: {user_input}")

        # Use integrated NLP to get a response
        nlp_response = self.nlp.process_input(user_input)

        # Process game commands
        if "play game" in user_input.lower():
            state = np.random.rand(self.game.state_size)  # Example game state
            action = self.game.play_game(state)
            return f"Playing game with action: {action}. {nlp_response}"
        
        # Call the respond_to_user function
        return self.respond_to_user(user_input)
        return nlp_response

    def handle_mobile_requests(self):
        """Handle requests from mobile devices."""
        while not self.running_event.is_set():
            time.sleep(5)  # Check for mobile requests every 5 seconds
            
            # Simulating a mobile request (you'd replace this with actual logic)
            mobile_request = self.mobile.check_for_request()  # Pseudo code to check mobile requests
            
            if mobile_request:
                user_input = mobile_request.get('message', '')
                response = self.process_input(user_input)
                self.mobile.send_response(mobile_request.get('user_id'), response)  # Responding to the user

    def push_notifications_loop(self):
        """Push notifications to the user on mobile."""
        while not self.running_event.is_set():
            time.sleep(60)  # Push notifications every minute
            # Push notifications to user
            self.logger.logger.info("Pushing notifications...")

    def update_learning_from_interactions(self):
        """Update the AI's learning based on user interactions."""
        # This is a placeholder for actual interaction data collection logic
        interaction_data = self.memory.get_interaction_data()
        if interaction_data:
            self.game.fine_tune_model(interaction_data)

# To run the Snowball AI
if __name__ == "__main__":
    ai = SnowballAI()
    ai.start()
