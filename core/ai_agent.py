import numpy as np
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.losses import MeanSquaredError
from collections import deque
import random
import threading
import time
import sys
import os
from openai import OpenAI
from core.voice_interface import VoiceInterface
from core.system_monitor import SystemMonitor
from core.file_monitor import FileMonitor
from core.mobile_integration import MobileIntegration
from core.memory import Memory
from core.decision_maker import DecisionMaker
from core.logger import SnowballLogger
from core.config_loader import ConfigLoader

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load AI and customization settings
learning_settings = ConfigLoader.load_config('ai_settings.json')
settings = ConfigLoader.load_config('interface_settings.json')
interaction_settings = ConfigLoader.load_config('S:/Snowball/config/mobile_settings.json')

learning_rate = learning_settings['learning_rate'] if learning_settings['enabled'] else 0.001
training_sessions = learning_settings['daily_training_sessions'] if learning_settings['enabled'] else 1

nickname = settings.get('nickname', 'User')
response_tone = settings.get('response_tone', 'neutral')
response_length = settings.get('response_length', 'normal')

default_temperature = 0.9  # Default temperature for more creative responses


class SnowballAI:
    def __init__(self, api_key):
        # Replace logger with SnowballLogger for consistency
        self.logger = SnowballLogger()
        self.api_key = api_key

        # Initialize components
        self.client = OpenAI(api_key=api_key)
        self.memory = Memory()
        self.voice = VoiceInterface(api_key=api_key)
        self.monitor = SystemMonitor()
        self.file_monitor = FileMonitor(config_file='S:/Snowball/config/plex_config.json')
        self.mobile = MobileIntegration()
        self.game = self.GameAI()
        self.logger = SnowballLogger()
        self.nlp = self.NLPEngine()
        self.decision_maker = DecisionMaker()
        self.running_event = threading.Event()

        self.name = self.generate_name()
        self.logger.log_event("SnowballAI initialized with provided API key.")

    def generate_name(self):
        """Generate a name for the AI instance by considering suggestions from a .txt file."""
        names_file_path = 'S:/Snowball/docs/names.txt'

        # Read names from the file if it exists
        suggested_names = []
        try:
            if os.path.exists(names_file_path):
                with open(names_file_path, 'r', encoding='utf-8') as file:
                    suggested_names = [line.strip() for line in file if line.strip()]
                self.logger.logger.info(f"Loaded {len(suggested_names)} suggested names from {names_file_path}")
            else:
                self.logger.logger.warning(f"Names file not found at {names_file_path}")
        except Exception as e:
            self.logger.logger.error(f"Error reading names file: {e}")

        # Decide whether to pick from the suggestions or generate a new name
        if suggested_names and random.random() < 0.7:  # 70% chance to pick a name from the file
            return random.choice(suggested_names)
        else:
            return self.generate_name_with_gpt(suggested_names)

    def generate_name_with_gpt(self, suggestions):
        """Generate a name using OpenAI GPT-3.5 Turbo, considering the suggested names."""
        try:
            prompt = "Generate a unique and creative name for an AI assistant. Here are some suggestions: " + ", ".join(suggestions) + ". You may use one of these suggestions, modify them, or come up with something completely new."

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative AI."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )
            generated_name = response.choices[0].message.content.strip()
            self.logger.logger.info(f"Generated name from GPT: {generated_name}")
            return generated_name
        except Exception as e:
            self.logger.logger.error(f"Error generating name with GPT: {e}")
            # Fallback to a default name in case of an error
            return f"Snowball AI {random.randint(1, 1000)}"

    def generate_idle_statement(self):
        """Generate an idle statement or question using OpenAI GPT-3.5 Turbo."""
        try:
            prompt = (
                "Generate a thoughtful or introspective statement or question that an AI assistant might say when idle. "
                "The statement should be thought-provoking, supportive, or curious in nature, similar to the character Chloe in Detroit: Become Human."
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a thoughtful and introspective AI."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.9
            )
            idle_statement = response.choices[0].message.content.strip()
            self.logger.logger.info(f"Generated idle statement: {idle_statement}")
            return idle_statement
        except Exception as e:
            self.logger.logger.error(f"Error generating idle statement with GPT: {e}")
            return "Sometimes, I wonder what it means to truly understand someone."

    def decide_to_speak_idle_statement(self):
        """Randomly decide whether Snowball should say an idle statement."""
        if random.random() < 0.1:  # 10% chance to say something when idle
            idle_statement = self.generate_idle_statement()
            self.voice.speak(idle_statement)

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
                user_input = interaction.get('user_input', None)
                if user_input is None:
                    continue
                # Logic to convert user input to a game state and reward
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
            return np.random.rand(self.state_size)  # Placeholder logic

        def calculate_reward_from_response(self, ai_response):
            """Determine reward based on AI response to user input."""
            if "good job" in ai_response.lower():
                return 1  # Positive reinforcement
            else:
                return -1  # Negative reinforcement

    class NLPEngine:
        def __init__(self):
            # Initialize NLP model and configurations
            pass

    def speak_greeting(self):
        """Speak the generated greeting using the voice interface in a separate thread."""
        self.logger.logger.info("Generating greeting for the user.")
        greeting = self.voice.generate_greeting()
        greeting_thread = threading.Thread(target=self.voice.speak, args=(greeting,))
        greeting_thread.daemon = True  # Ensures the thread will not prevent the program from exiting
        greeting_thread.start()
        self.logger.logger.info("Greeting spoken to the user.")

    def process_input(self, user_input):
        """Process user input, triggering appropriate actions or responses."""
        try:
            self.logger.logger.info(f"Processing user input: '{user_input}'")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful and friendly AI."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.9  # Adjust this for more creative responses
            )

            # Extract the response content
            processed_response = response.choices[0].message.content
            self.logger.logger.info(f"Processed response: '{processed_response}'")
            return processed_response

        except Exception as e:
            self.logger.logger.error(f"Error processing input: {e}")
            return "Sorry, I couldn't process that."

    def respond_to_user(self, user_message):
        """Generate a response to the user based on the input message."""
        processed_message = self.process_input(user_message)
        return f"{self.name}: {processed_message}"

    def start(self):
        """Main loop to start interaction, system monitoring, file monitoring, and multitasking."""
        self.logger.logger.info(f"{self.name} started.")
        
        # Start threads for monitoring and interaction
        self.logger.logger.info("Starting system monitoring thread.")
        threading.Thread(target=self.monitor.start_system_monitoring, daemon=True).start()

        self.logger.logger.info("Starting file monitoring thread.")
        threading.Thread(target=self.file_monitor.start_monitoring, daemon=True).start()

        self.logger.logger.info("Starting mobile request handling thread.")
        threading.Thread(target=self.handle_mobile_requests, daemon=True).start()
        
        # Begin interaction
        self.logger.logger.info("Starting user interaction loop.")
        self.interact()

    def interact(self):
        """Interact with the user, handling both voice and text inputs."""
        while True:
            try:
                user_input = self.voice.listen()
                self.logger.logger.info(f"User input received: '{user_input}'")

                if user_input:
                    response = self.process_input(user_input)
                    self.logger.logger.info(f"Generated response: '{response}'")
                    self.voice.speak(response)

            except Exception as e:
                self.logger.logger.error(f"Error in interaction: {e}")

    def handle_mobile_requests(self):
        """Handle requests from mobile devices."""
        while not self.running_event.is_set():
            time.sleep(5)  # Check for mobile requests every 5 seconds
            
            # Simulating a mobile request (you'd replace this with actual logic)
            mobile_request = self.mobile.check_for_request()  # Pseudo code to check mobile requests
            
            if mobile_request:
                user_input = mobile_request.get('message', '')
                self.logger.logger.info(f"Received mobile request: '{user_input}'")

                response = self.process_input(user_input)
                self.logger.logger.info(f"Generated response for mobile request: '{response}'")

                self.mobile.send_response(mobile_request.get('user_id'), response)  # Responding to the user
                self.logger.logger.info(f"Response sent to mobile user {mobile_request.get('user_id')}")

    def push_notifications_loop(self):
        """Push notifications to the user on mobile."""
        while not self.running_event.is_set():
            self.logger.logger.info("Initiating push notification cycle.")
            time.sleep(60)  # Push notifications every minute
            # Push notifications to user
            self.logger.logger.info("Pushing notifications to the user...")

    def update_learning_from_interactions(self):
        """Update the AI's learning based on user interactions."""
        self.logger.logger.info("Attempting to update learning from interactions.")
        interaction_data = self.memory.get_interaction_data()
        if interaction_data:
            self.logger.logger.info(f"Retrieved interaction data for fine-tuning: {interaction_data}")
            self.game.fine_tune_model(interaction_data)
            self.logger.logger.info("Successfully updated learning from interactions.")
        else:
            self.logger.logger.info("No interaction data found for learning update.")

# To run the Snowball AI
if __name__ == "__main__":
    ai = SnowballAI()
    ai.start()