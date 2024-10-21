import os
import sys
import threading
import time
import json
import random
import warnings

# Suppress Deprecation Warnings for third-party libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add the parent directory of the 'core' and 'interface' modules to the system path
current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Debugging: Print the sys.path to verify that the project root has been added
print("Current sys.path:")
for path in sys.path:
    print(f" - {path}")

class SnowballAI:
    def __init__(self):
        self.running_event = threading.Event()
        self.name = None

        # Lazy initialization of core components to avoid circular imports
        self._initialize_logger()
        self._initialize_core_components()

        self.name = self.generate_name()
        self.logger.log_event("SnowballAI initialized with provided API key.")

    def _initialize_logger(self):
        """Initialize the logger to track events."""
        try:
            from core.logger import SnowballLogger
            self.logger = SnowballLogger()
            self.logger.log_event("Logger initialized successfully.")
        except ImportError as e:
            print(f"Failed to initialize logger: {e}")
            sys.exit(1)

    def _initialize_core_components(self):
        """Initialize all core components normally."""
        try:
            from core.initializer import SnowballInitializer
            self.initializer = SnowballInitializer()

            # Initialize components directly from initializer
            self.memory = self.initializer.memory
            self.config_loader = self.initializer.config_loader
            self.conversation_module = self.initializer.conversation_module
            self.sentiment_analysis_module = self.initializer.sentiment_analysis
            self.vision_module = self.initializer.vision
            self.decision_maker = self.initializer.decision_maker
            self.file_monitor = self.initializer.file_monitor
            self.reinforcement_module = self.initializer.q_learning_agent
            self.system_monitor = self.initializer.system_monitor
            self.voice_module = self.initializer.voice_interface
        
        except ModuleNotFoundError as e:
            self.logger.log_event(f"Error: {e}. Make sure 'core' and 'interface' directories exist and are accessible.")
            sys.exit(1)
        except Exception as e:
            self.logger.log_event(f"Unexpected error during core component initialization: {e}")
            sys.exit(1)

    def load_api_key(self):
        """Load OpenAI API key from configuration file."""
        try:
            with open('S:/Snowball/config/account_integrations.json', 'r') as f:
                config = json.load(f)
                return config['api_keys'].get('openai_api_key', 'YOUR_API_KEY_HERE')
        except FileNotFoundError as e:
            self.logger.log_event(f"Error loading OpenAI API key: {e}")
            sys.exit(1)

    def generate_name(self):
        """Generate a name for the AI instance by considering suggestions from a .txt file."""
        names_file_path = 'S:/Snowball/docs/names.txt'
        suggested_names = []
        try:
            if os.path.exists(names_file_path):
                with open(names_file_path, 'r', encoding='utf-8') as file:
                    suggested_names = [line.strip() for line in file if line.strip()]
                self.logger.log_event(f"Loaded {len(suggested_names)} suggested names from {names_file_path}")
            else:
                self.logger.log_event(f"Names file not found at {names_file_path}")
        except Exception as e:
            self.logger.log_event(f"Error reading names file: {e}")

        if suggested_names and random.random() < 0.7:
            return random.choice(suggested_names)
        else:
            return self.conversation_module.generate_name(suggested_names)

    def push_notifications_loop(self):
        """Push notifications to the user on mobile."""
        while not self.running_event.is_set():
            self.logger.log_event("Initiating push notification cycle.")
            time.sleep(60)
            self.logger.log_event("Pushing notifications to the user...")

    def system_monitor_loop(self):
        """Monitor system health and send alerts when thresholds are crossed."""
        while not self.running_event.is_set():
            try:
                system_status = self.system_monitor.get_system_health()
                if system_status['alert']:
                    self.logger.log_event("System alert: " + system_status['message'])
                    self.voice_module.speak(system_status['message'])
            except Exception as e:
                self.logger.log_event(f"Error in system monitor loop: {e}")
            time.sleep(10)

    def heartbeat_loop(self):
        """Continuously monitor and log the status of all modules."""
        while not self.running_event.is_set():
            try:
                self.logger.log_event("Heartbeat check: All modules are being monitored...")
                if self.voice_module and not self.voice_module.is_active():
                    self.logger.log_event("Warning: Voice Module is not active.")
                if self.vision_module and not self.vision_module.is_active():
                    self.logger.log_event("Warning: Vision Module is not active.")
            except Exception as e:
                self.logger.log_event(f"Error in heartbeat loop: {e}")
            time.sleep(60)  # Perform status checks every 60 seconds

    def interact(self, user_input):
        """Process user input and generate a response."""
        try:
            sentiment = self.sentiment_analysis_module.analyze(user_input)
            facial_emotion = self.vision_module.get_current_emotion()
            self.logger.log_event(f"User sentiment: {sentiment}, Facial emotion: {facial_emotion}")

            response = self.get_best_response(user_input, sentiment, facial_emotion)
            self.logger.log_event(f"Generated response: {response}")
            self.voice_module.speak(response)
        except Exception as e:
            self.logger.log_event(f"Error during interaction: {e}")
            self.voice_module.speak("I'm sorry, something went wrong while processing your request.")

    def get_best_response(self, user_input, sentiment, facial_emotion):
        """Dynamically select the best response from multiple NLP models."""
        try:
            responses = [
                ("OpenAI", self.conversation_module.process_input(user_input)),
                ("GPT-J", self.conversation_module.process_input_with_gptj(user_input)),
                ("BERT", self.conversation_module.process_input_with_bert(user_input))
            ]
            # Rank responses based on sentiment analysis or other criteria
            responses_ranked = sorted(responses, key=lambda r: self.sentiment_analysis_module.analyze_response_quality(r[1]), reverse=True)
            best_response = responses_ranked[0]
            self.logger.log_event(f"Selected best response from {best_response[0]}: {best_response[1]}")
            return best_response[1]
        except Exception as e:
            self.logger.log_event(f"Error selecting the best response: {e}")
            return "I'm having trouble generating a response."

    def run_reinforcement_learning(self):
        """Run the reinforcement learning module to train the AI in games."""
        self.logger.log_event("Starting reinforcement learning for games.")
        try:
            self.reinforcement_module.train()
        except Exception as e:
            self.logger.log_event(f"Error in reinforcement learning module: {e}")

    def toggle_module(self, module_name, enable=True):
        """Enable or disable individual AI modules."""
        modules = {
            'voice': self.voice_module,
            'vision': self.vision_module,
            'reinforcement': self.reinforcement_module
        }
        try:
            if module_name in modules:
                if enable:
                    modules[module_name].start()
                    self.logger.log_event(f"{module_name} module enabled.")
                else:
                    modules[module_name].stop()
                    self.logger.log_event(f"{module_name} module disabled.")
            else:
                self.logger.log_event(f"Module '{module_name}' not found.")
        except AttributeError as e:
            self.logger.log_event(f"Error toggling module '{module_name}': {e}")
    
    def start(self):
        """Main loop to start interaction, system monitoring, and multitasking."""
        self.logger.log_event("SnowballAI started.")
        # Start threads for each module's main functionality
        try:
            if self.voice_module:
                threading.Thread(target=self.voice_module.listen_and_respond, args=(self.conversation_module,), daemon=True).start()
            if self.reinforcement_module:
                threading.Thread(target=self.reinforcement_module.train, daemon=True).start()
            threading.Thread(target=self.push_notifications_loop, daemon=True).start()
            if self.vision_module:
                threading.Thread(target=self.vision_module.start_facial_recognition, daemon=True).start()
            threading.Thread(target=self.system_monitor_loop, daemon=True).start()
            if self.file_monitor:
                threading.Thread(target=self.file_monitor.start_monitoring, daemon=True).start()
            threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        except AttributeError as e:
            self.logger.log_event(f"Error starting module threads: {e}")

    def stop(self):
        """Gracefully stop all AI processes and threads."""
        self.logger.log_event("Shutting down SnowballAI...")
        self.running_event.set()  # Stop the main loop
        self.logger.log_event("SnowballAI has been shut down.")

if __name__ == "__main__":
    ai = SnowballAI()
    try:
        ai.start()
    except KeyboardInterrupt:
        ai.stop()
